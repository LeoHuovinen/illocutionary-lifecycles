"""The processing of one finished user utterance, ``ResponseProcessing``, from saving it to the reply, and
``ComposeCurrentPrompt``, which builds the prompt the model writes the reply from.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), keeping the questions outside the model, and this module, in the folder
``core``, is the order in which one turn is handled. First the utterance is saved to the record of the folder
``memory``. Then the cycle ``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs the state's
analyzers from the folder ``analyzers`` and the refresher updates the pragmatic state. Then the composer builds the
prompt, the prompt is saved, and
``illocutionary_lifecycles.core.clients.PostComposerLLMCallHelper.PostComposerLLMCallHelper`` sends it to the model as
one user message. The reply is returned and not saved, and the adapter in the folder ``server`` saves it once it has
been delivered.

Both functions take the session's ``illocutionary_lifecycles.core.system_state.system_state.SystemState`` as ``self``,
because the ``SystemState`` methods of the same names call them and hold no logic of their own. Nothing here sets when
a spoken turn ends, which the assembler in the folder ``server`` does.
"""
from __future__ import annotations

import functools
from typing import Any


async def ResponseProcessing(
    self: Any, UserUtteranceText: str, skip_TransitionCriteria: bool = False,
    static_reply: str | None = None, ReuseUserUtteranceIdx: int | None = None,
) -> dict:
    """Process one user utterance for the session ``self`` and return a dict with the reply under ``reply``, whether
    the conversation moved to another state under ``ConversationStateAdvanced``, and the utterance's refresh index under
    ``UserUtteranceIdx``.

    This is the order of one turn the module docstring above lays out. The reply is a ``ComposedReply`` that carries
    the refresh index of the prompt it came from, so the saved assistant utterance can be traced to that prompt. When
    the cycle moves the conversation, no prompt is composed and no model is called for the state just left, and the
    reply is an empty string, because ``SessionProvider.ResponseProcessing`` then has the new state reply through
    ``SystemState.EstablishConversationStateAndFirstReply``.

    ``UserUtteranceText`` holds what the user said or typed. An empty string saves no utterance and runs no analyzer,
    saves the state values once and composes a reply, which is how the conversation is opened, and
    ``UserUtteranceIdx`` is then ``None``. ``skip_TransitionCriteria``, when true, runs no transition criterion, so the
    conversation cannot leave its state in this call. ``static_reply``, when given, is returned as the reply without
    composing or saving a prompt or calling the model, while the utterance is still saved and analyzed, and a move
    made by the cycle is still reported. ``ReuseUserUtteranceIdx`` is the refresh index of an utterance already saved,
    which is then analyzed again without being saved a second time, as a state just entered does with the utterance
    that led to it. Before the pragmatic state exists the function returns a dict holding only an empty ``reply``.
    """
    PragmaticState = getattr(self, "PragmaticState", None)
    if PragmaticState is None:
        return {"reply": ""}

    Memory = getattr(self, "Record", None)

    ConversationStateAdvanced = False
    if not UserUtteranceText:
        self.SaveRefreshResult(analyzer_results={})
    else:
        # The index the utterance receives is read before saving it. The cycle saves it with
        # every analyzer event, as the utterance that was analyzed.
        if ReuseUserUtteranceIdx is not None:
            UserUtteranceIdx = ReuseUserUtteranceIdx
        else:
            UserUtteranceIdx = getattr(Memory, "_next_refresh_idx", -1) if Memory is not None else -1
            if Memory is not None:
                Memory.UpsertUtteranceEvent(role="user", transcription=UserUtteranceText)

        # The analyzers read the same window the composer shows: the current state's
        # utterances.
        from illocutionary_lifecycles.core.system_state.conversation_history_window import (
            ConversationStateWindow,
        )
        from illocutionary_lifecycles.core.system_state.user_memory_state import UserMemoryState
        UserMemoryFace = functools.partial(UserMemoryState, Memory)
        WindowFace = functools.partial(ConversationStateWindow, Memory)
        SettledResults = await self.PragmaticState.SyncCycle(
            self, UserMemoryFace, WindowFace,
            skip_TransitionCriteria=skip_TransitionCriteria,
            UserUtteranceIdx=UserUtteranceIdx,
        )
        ConversationStateAdvanced = bool((SettledResults or {}).get("ConversationStateAdvanced"))

    if ConversationStateAdvanced and static_reply is None:
        # The state just left composes nothing. The new state replies to this utterance.
        return {"reply": ComposedReply("", source_refresh_idx=-1), "ConversationStateAdvanced": True,
                "UserUtteranceIdx": UserUtteranceIdx}

    if static_reply is None:
        from illocutionary_lifecycles.core.clients.PostComposerLLMCallHelper import (
            PostComposerLLMCallHelper,
        )
        prompt = await self.ComposeCurrentPrompt()
        # The composed prompt is saved. The reply carries the prompt's refresh index, so that
        # the saved assistant utterance can be traced to the prompt it came from.
        source_refresh_idx = -1
        if Memory is not None and hasattr(Memory, "UpsertComposedPromptEvent"):
            # The state values the prompt was composed from are the newest ones saved.
            state_idx = Memory._next_refresh_idx - 1 if hasattr(Memory, "_next_refresh_idx") else -1
            source_refresh_idx = Memory.UpsertComposedPromptEvent(
                prompt if isinstance(prompt, str) else "", source_state_idx=state_idx)
        Reply = ComposedReply(
            await PostComposerLLMCallHelper(getattr(self, "llm_client", None), prompt),
            source_refresh_idx=source_refresh_idx,
        )
    else:
        Reply = ComposedReply(static_reply, source_refresh_idx=-1)

    return {"reply": Reply, "ConversationStateAdvanced": ConversationStateAdvanced,
            "UserUtteranceIdx": UserUtteranceIdx if UserUtteranceText else None}


async def ComposeCurrentPrompt(self: Any) -> str:
    """Return the prompt the composer builds for the current state of the session ``self``, saving nothing and calling
    no model, or an empty string before the pragmatic state exists.

    The function gathers the three inputs of
    ``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.PragmaticState.Composer`` and calls it. The
    remembered answers come as data from ``UserMemoryState``. The utterances to show are the last two of each role in
    the current state, from ``ConversationStateWindowRecent``, or the last ``global_history_turns`` of the whole
    conversation, from ``ConversationHistoryWindow``, when the state set ``global_history_window``. The authored texts
    come from ``StaticPromptLibrary`` bound to the flow's ``PromptBlocks``. Called by ``ResponseProcessing`` in this
    module through ``SystemState.ComposeCurrentPrompt``, and by ``SessionProvider`` for the ``prompt`` field of the
    save-time adapter callbacks.
    """
    PragmaticState = getattr(self, "PragmaticState", None)
    if PragmaticState is None:
        return ""
    Memory = getattr(self, "Record", None)
    # The memories are read here and passed on as data, not as a callable.
    from illocutionary_lifecycles.core.system_state.conversation_history_window import (
        ConversationHistoryWindow,
        ConversationStateWindowRecent,
    )
    from illocutionary_lifecycles.core.system_state.static_prompt_library import StaticPromptLibrary
    from illocutionary_lifecycles.core.system_state.user_memory_state import UserMemoryState
    UserMemoryFace = UserMemoryState(Memory)
    if getattr(self, "global_history_window", False):
        WindowFace = functools.partial(ConversationHistoryWindow, Memory,
                                       int(getattr(self, "global_history_turns", 10) or 10))
    else:
        def WindowFace() -> list:
            """Return the last two utterances of each role of the current state for the composer, leaving out the
            utterance the record carries in from the state before while this state has processed no user turn of
            its own, which is the case in a state entered under ``session_first_reply_flag`` set to ignore its entry
            utterance. The analyzers still see the carried-in utterance through ``ConversationStateWindow``, and a
            state that processes its entry utterance counts it as its first turn, so its prompt shows it."""
            views = ConversationStateWindowRecent(Memory, 2)
            if Memory is None or int(getattr(PragmaticState, "pConversationStateTurnCountState", 0) or 0) > 0:
                return views
            from illocutionary_lifecycles.memory.memory import ConversationStateEvent
            changes = Memory.read_cache._category_stream(ConversationStateEvent.CATEGORY)
            boundary = changes[-1].get("event_refresh_idx", -1) if changes else -1
            stream = Memory.CurrentConversationStateUtteranceStream()
            if stream and boundary >= 0 and stream[0].get("event_refresh_idx", -1) < boundary and views \
                    and views[0].transcription == stream[0].get("transcription", ""):
                views = views[1:]
            return views
    BlocksFace = functools.partial(StaticPromptLibrary, self.PromptBlocks())
    prompt = await PragmaticState.Composer(
        window=WindowFace, memories=UserMemoryFace, blocks=BlocksFace,
    )
    return prompt if isinstance(prompt, str) else ""


class ComposedReply(str):
    """A reply string that also carries, as ``source_refresh_idx``, the refresh index of the composed prompt it came
    from, or ``-1`` when the reply did not come from a composed prompt.

    The class behaves as a plain string everywhere, so adapters and wires pass it on as text, and
    ``illocutionary_lifecycles.memory.memory.Memory.UpsertUtteranceEvent`` reads the index when the adapter saves the
    delivered reply, which links the saved assistant utterance to its prompt in the record. Built only by
    ``ResponseProcessing`` in this module.
    """

    source_refresh_idx: int

    def __new__(cls, text: str, *, source_refresh_idx: int = -1) -> "ComposedReply":
        """Return the string ``text`` carrying ``source_refresh_idx``, the refresh index of the prompt it came from, as the
        class above describes."""
        obj = super().__new__(cls, text)
        obj.source_refresh_idx = source_refresh_idx
        return obj
