"""``SessionProvider``, the one object through which every adapter, and so every connecting program, speaks to one
session, which is one conversation from its start to its end.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), with each state's questions checked outside the model, and this module
is the single entry to that conversation from outside the folder ``core``. A mount in the folder ``server`` builds one
provider per connection through
``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase.AdapterMountBase.NewConversationSession``, an
adapter in the same folder passes every call to it, and the provider reaches ``SystemState`` in
``illocutionary_lifecycles.core.system_state.system_state``, which has the checks of the folder ``analyzers`` run on
every turn and writes every event to the record in the folder ``memory``. A process that serves several conversations
holds one provider for each.

The calls an adapter makes fall into six kinds. ``ResponseProcessing`` gives the session one finished user utterance and
returns the reply. ``TTSUtteranceSave`` saves an assistant reply once it has been delivered. ``set_ignore_memories``
and ``SetQuestionAnswerHook`` switch two settings. ``ConversationHistoryWindow`` and ``ConversationHistoryTurns`` read
the recorded utterances. ``IncrementalPhraseTick`` hands over the speech so far while the user is still speaking,
schedules the incremental settle and never waits for it, so a reply is never delayed by it. ``ApplyPromptChange``
replaces one authored prompt block while the conversation runs.

When a user utterance moves the conversation to another state, the provider has the new state process the same
utterance through ``SystemState.EstablishConversationStateAndFirstReply``, passing the utterance's refresh index as
``ReuseUserUtteranceIdx`` so the utterance is not saved twice. The new state's reply is the one returned, so the user's
turn is not spent on the move, and the hand-over repeats at most as many times as the flow has
states plus one.

After every save the provider runs the handlers registered on its adapters, first with a
``RefreshCycleSavedAdapterCallbackHandlerEvent``, then with one ``ConversationStateChangedAdapterCallbackHandlerEvent``
per state change not sent before, and, while the question-answer hook is on, one ``QuestionAnsweredAdapterCallbackHandlerEvent`` per
answered question not sent before. The save callback carries the whole record. On its way to a connecting program
``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase.AdapterMountBase.RelayAdapterCallback`` drops it and
strips ``turns`` and ``prompt`` from the others, while ``AdapterMountBase.LogRelay`` sends every callback in full, the
save callback included, as a separate log line marked with the key ``log``, which the browser scripts hand to
``log.js`` for the console and never to the page's views. These three dataclasses and the incremental one are imported from
``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerEvents``, which is the one import from
the folder ``server`` into the folder ``core``, kept there because the page scripts under ``examples/*/page`` match the
callbacks by those class names.

A typed conversation, with ``flow`` as the dict loaded from a flow file, runs as in the lines below.

    provider = SessionProvider(ConversationStateInitBundle=flow)
    adapter = TextAdapter(provider)
    adapter.open_session()
    opening = await adapter.opening_reply()
    adapter.save_assistant(opening)
    reply = await adapter.on_user_turn("a burger, please")
    adapter.save_assistant(reply)
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from illocutionary_lifecycles.core.system_state import SystemState as _SystemStateClass

logger = logging.getLogger(__name__)


@dataclass
class SessionProvider:
    """One session, the conversation of one user, from its start to its end, and the only object adapters call.

    The class passes each call on to the session's ``SystemState`` and sends the adapter callbacks after every save, as
    the module docstring above explains. The constructor takes five fields by keyword. ``session_id`` holds the session's id, and ``start`` generates
    one when it is empty. ``memory_vendor`` holds the registered name of the storage vendor, such as "local", "cosmos",
    "local-readonly" or "cosmos-readonly", and ``None`` keeps the record in memory only. ``vendor_session_address``
    holds where that vendor stores, a directory path for the local vendors and, for the Cosmos DB ones, a dict whose
    key ``prefix`` names the container.
    ``ConversationStateInitBundle`` holds the flow, the dict with ``PromptBlocks`` and ``ConversationStates``, and a
    flow stored for this session id before is used in its place. ``InitSystemSetterSettings`` holds a dict from
    ``SystemState`` attribute names to values applied before the first state is entered, for example
    ``QuestionAnswerHook`` set to true, and a key that is not such an attribute is ignored.

    ``start`` sets two further fields. ``SystemState`` holds the session's
    ``illocutionary_lifecycles.core.system_state.system_state.SystemState``. ``ConversationHistoryWindow`` holds a
    callable that returns every recorded utterance as
    ``illocutionary_lifecycles.core.system_state.conversation_history_window.TurnView`` objects and takes an optional
    ``LastN`` to keep only the last ones. The private list ``_OverlaidAdapters`` holds the adapters created on this
    session, whose handlers receive the adapter callbacks, and the two private counters remember what was already
    sent so each state change and answered question is sent once.
    """

    session_id: str = ""
    memory_vendor: str | None = None
    vendor_session_address: Any = None
    ConversationStateInitBundle: Any = None
    InitSystemSetterSettings: Any = None

    SystemState: Any = field(default=None, repr=False)

    ConversationHistoryWindow: Any = field(default=None, repr=False)

    # The adapters created on this session. Their handlers receive the adapter callbacks.
    _OverlaidAdapters: list = field(default_factory=list, repr=False)

    # The refresh index of the last sent change of state, and the number of answered
    # questions already sent, so that each is sent once.
    _BroadcastConversationStateEventIdx: int = field(default=-1, repr=False)
    _BroadcastAnsweredQuestionCount: int = field(default=0, repr=False)

    def OverlaySessionAdapter(self, adapter: Any) -> None:
        """Add ``adapter`` to ``_OverlaidAdapters`` unless it is already there, so its handlers receive this session's
        adapter callbacks, and return ``None``. Called by
        ``illocutionary_lifecycles.server.adapters.AdapterBase.AdapterBase.__post_init__`` when an adapter is created,
        so creating an adapter is what attaches it to the session."""
        if adapter not in self._OverlaidAdapters:
            self._OverlaidAdapters.append(adapter)

    def start(self) -> SystemState:
        """Return the session's ``SystemState``, building it on the first call and returning the same one on every later
        call.

        The first call generates ``session_id`` when it is empty, builds ``SystemState`` with the storage vendor and the
        flow, and runs ``illocutionary_lifecycles.core.ConversationInit.ConversationInit`` on it, which loads the stored
        record, checks the flow, requires its analyzers and enters the first state. Every error those steps raise for a
        malformed flow, a missing analyzer, a missing model key or a missing vendor setting reaches the caller from here.
        The call then sets ``ConversationHistoryWindow`` and gives the session's
        ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter`` the method
        ``RunAdapterCallbackHandlerEventsForRefreshSave`` to schedule after every save. Called by ``ResponseProcessing``
        when the session has not started, and by ``illocutionary_lifecycles.server.adapters.AdapterBase.AdapterBase.open_session``.
        """
        if self.SystemState is not None:
            return self.SystemState

        if not self.session_id:
            self.session_id = uuid.uuid4().hex

        SystemState = _SystemStateClass(
            chat_id=self.session_id,
            StorageVendorName=self.memory_vendor,
            StorageVendorAddress=self.vendor_session_address,
            ConversationStateInitBundle=self.ConversationStateInitBundle,
        )
        from illocutionary_lifecycles.core.ConversationInit import ConversationInit
        ConversationInit(SystemState, InitSystemSetterSettings=self.InitSystemSetterSettings)

        self.SystemState = SystemState
        import functools
        from illocutionary_lifecycles.core.system_state.conversation_history_window import (
            ConversationHistoryWindow,
        )
        self.ConversationHistoryWindow = functools.partial(ConversationHistoryWindow, SystemState.Record)

        # After every save the writer schedules the provider's adapter callback.
        writer = getattr(SystemState, "memory_writer", None)
        if writer is not None:
            writer.RunAdapterCallbackHandlerEventsForRefreshSave = (
                self.RunAdapterCallbackHandlerEventsForRefreshSave
            )

        logger.info("Started session %s", self.session_id)
        return SystemState

    async def RunAdapterCallbackHandlerEventsForRefreshSave(self) -> None:
        """Run the handlers registered on every adapter of this session with the adapter callbacks of one save, and
        return ``None``.

        This is the step that tells the server, and through the mount a connected page or app, what the save
        changed, as the module docstring above explains. The callbacks go in a fixed order. First comes one
        ``RefreshCycleSavedAdapterCallbackHandlerEvent``. Then comes one ``ConversationStateChangedAdapterCallbackHandlerEvent``
        for every recorded ``ConversationStateEvent`` not sent before, with the indexes and the ``name`` values of the
        state entered and the state left. Last, while ``SystemState.QuestionAnswerHook`` is true, comes one ``QuestionAnsweredAdapterCallbackHandlerEvent``
        for every answered question that
        ``illocutionary_lifecycles.memory.MemoryReadTools.AnsweredQuestionFactsTool.AnsweredQuestionFacts`` finds in the
        recorded analyzer results and that was not sent before.

        Every one of these callbacks carries ``turns``, every saved utterance as a dict, ``streams``, every recorded
        category from the in-memory copy of the record, and ``prompt``, the prompt composed for the current state at this
        moment. A handler that raises is logged as a warning and the other handlers still run. With no adapter on the
        session nothing is read and nothing is sent.
        ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter.save_refresh_result`` schedules this method after
        every refresh's save, and ``TTSUtteranceSave`` schedules it after an assistant utterance is saved.
        """
        from illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerEvents import (
            QuestionAnsweredAdapterCallbackHandlerEvent,
            RefreshCycleSavedAdapterCallbackHandlerEvent,
            ConversationStateChangedAdapterCallbackHandlerEvent,
        )
        adapters = list(self._OverlaidAdapters or [])
        if not adapters:
            return

        async def RunHandlers(payload: dict) -> None:
            """Await ``RunAdapterCallbackHandlers`` of every adapter with ``payload``, one adapter callback as a dict,
            logging a handler that raises as a warning and going on with the next, for the
            enclosing ``RunAdapterCallbackHandlerEventsForRefreshSave``."""
            for adapter in adapters:
                run = getattr(adapter, "RunAdapterCallbackHandlers", None)
                if run is not None:
                    try:
                        await run(payload)
                    except Exception as e:
                        logger.warning(
                            "%s handler raised for %s: %s",
                            payload.get("type", ""), self.session_id, e,
                        )

        streams = self._event_streams()
        turns = self.ConversationHistoryTurns()
        prompt = await self._composed_prompt()
        await RunHandlers(RefreshCycleSavedAdapterCallbackHandlerEvent(
            turns=turns, streams=streams, prompt=prompt,
        ).wire())

        for ConversationStateRecord in (streams.get("ConversationStateEvent") or []):
            RecordIdx = ConversationStateRecord.get("event_refresh_idx", -1)
            if not isinstance(RecordIdx, int) or RecordIdx <= self._BroadcastConversationStateEventIdx:
                continue
            self._BroadcastConversationStateEventIdx = RecordIdx
            await RunHandlers(ConversationStateChangedAdapterCallbackHandlerEvent(
                conversation_state=ConversationStateRecord.get("conversation_state", -1),
                previous_conversation_state=ConversationStateRecord.get("previous_conversation_state"),
                conversation_state_name=self._conversation_state_name(
                    ConversationStateRecord.get("conversation_state")),
                previous_conversation_state_name=self._conversation_state_name(
                    ConversationStateRecord.get("previous_conversation_state")),
                turns=turns, streams=streams, prompt=prompt,
            ).wire())

        if getattr(self.SystemState, "QuestionAnswerHook", False):
            from illocutionary_lifecycles.memory.MemoryReadTools import AnsweredQuestionFacts
            Facts = AnsweredQuestionFacts(streams.get("AnalyzerEvent") or [])
            NewFacts = Facts[self._BroadcastAnsweredQuestionCount:]
            self._BroadcastAnsweredQuestionCount = len(Facts)
            for Fact in NewFacts:
                await RunHandlers(QuestionAnsweredAdapterCallbackHandlerEvent(
                    answer=Fact["answer"], choice=Fact["choice"],
                    AnalyzerType=Fact["AnalyzerType"], AnalyzerInstance=Fact["AnalyzerInstance"],
                    turns=turns, streams=streams, prompt=prompt,
                ).wire())

    def _conversation_state_name(self, index: Any) -> str:
        """Return the ``name`` the flow gives the conversation state at ``index``, or an empty string when the index
        is ``None`` or names no state. Called only by ``RunAdapterCallbackHandlerEventsForRefreshSave`` in this module."""
        entries = getattr(self.SystemState, "ConversationStates", None) or {}
        entry = entries.get(str(index)) if index is not None else None
        return str(entry.get("name", "") or "") if isinstance(entry, dict) else ""

    def ConversationHistoryTurns(self) -> list:
        """Return every saved utterance of the conversation, in order, as a dict with the keys ``role``, ``text`` and
        ``truncated``, or an empty list before ``start``. Interrupted utterances are not included. The list is the
        ``turns`` field of the save-time adapter callbacks built by ``RunAdapterCallbackHandlerEventsForRefreshSave`` in
        this module, and ``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerHelpers.turns``
        returns it for programs that review a session."""
        window = self.ConversationHistoryWindow
        items = list(window()) if window is not None else []
        return [
            {"role": getattr(t, "role", ""), "text": getattr(t, "transcription", ""),
             "truncated": getattr(t, "truncated", False)}
            for t in items
        ]

    def _event_streams(self) -> dict:
        """Return a dict from each recorded category to a copy of its list of event dicts, read from the in-memory
        copy of the record, so it includes events not yet stored and works without a storage vendor, or an empty dict
        before ``start``. Called only by ``RunAdapterCallbackHandlerEventsForRefreshSave`` in this module, whose
        callbacks carry it as ``streams``."""
        Record = getattr(self.SystemState, "Record", None) if self.SystemState is not None else None
        read_cache = getattr(Record, "read_cache", None) if Record is not None else None
        if read_cache is None or not hasattr(read_cache, "streams"):
            return {}
        live = read_cache.streams() or {}
        return {EventCategory: list(events) for EventCategory, events in live.items()}

    async def _composed_prompt(self) -> str:
        """Return the prompt ``SystemState.ComposeCurrentPrompt`` composes for the current state, saving nothing and
        calling no model, or an empty string before ``start`` or when composing raises, which is logged as a warning.
        Called only by ``RunAdapterCallbackHandlerEventsForRefreshSave`` in this module, whose callbacks carry it as
        ``prompt``."""
        if self.SystemState is None:
            return ""
        try:
            return await self.SystemState.ComposeCurrentPrompt()
        except Exception as e:
            logger.warning("composed-prompt recompute failed for %s: %s", self.session_id, e)
            return ""


    async def ResponseProcessing(self, UserUtteranceText: str, static_reply: str | None = None) -> dict:
        """Give the session one finished user utterance and return a dict with the reply under ``reply``, whether the
        conversation moved to another state under ``ConversationStateAdvanced``, and the utterance's refresh index under
        ``UserUtteranceIdx``, which is ``None`` for an empty utterance.

        This is the call every adapter makes for a user turn, as the module docstring above explains, and it starts the
        session first when ``start`` has not run. ``UserUtteranceText`` holds what the user said or typed, and an empty
        string produces a reply with no user utterance, as the opening of the conversation does. ``static_reply``, when
        given, is returned as the reply without composing a prompt or calling the model, while the utterance is still
        saved and analyzed.

        The work is done by ``SystemState.ResponseProcessing``, which runs
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing``. When that moves the
        conversation, the state left composes no reply, and this method has the new state process the same utterance
        through ``SystemState.EstablishConversationStateAndFirstReply`` with ``ReuseUserUtteranceIdx``, so the utterance
        is saved once and the user's turn is not spent on the move. When the new state moves on at once, the next state
        processes the utterance in turn, at most as many times as the flow has states plus one, so a flow whose states
        hand the utterance round in a circle still returns.
        """
        if self.SystemState is None:
            self.start()
        result = await self.SystemState.ResponseProcessing(UserUtteranceText, static_reply=static_reply)
        moved = False
        # The utterance is already saved. Its refresh index is passed on so that it is not
        # saved again. The hop count is capped so that a design whose states hand the
        # utterance round in a circle still returns.
        for _hop in range(len(getattr(self.SystemState, "ConversationStates", None) or {}) + 1):
            if not (isinstance(result, dict) and result.get("ConversationStateAdvanced")):
                break
            moved = True
            result = await self.SystemState.EstablishConversationStateAndFirstReply(
                UserUtteranceText, ReuseUserUtteranceIdx=result.get("UserUtteranceIdx"),
                static_reply=static_reply)
        if moved and isinstance(result, dict):
            result["ConversationStateAdvanced"] = True
        return result

    def TTSUtteranceSave(
        self, transcription: str, truncated: bool = False,
    ) -> int:
        """Save one assistant utterance as an ``UtteranceEvent`` with the role "assistant" and return its refresh index,
        or ``-1`` before ``start``.

        A reply is returned by ``ResponseProcessing`` and not saved, and the adapter calls this once the reply has been
        delivered, shown on the page or spoken by TTS, so the record holds what the user actually got.
        ``transcription`` holds the reply text, and when it is the
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposedReply`` that ``ResponseProcessing``
        returned, the index of the prompt it came from is saved with it. ``truncated`` is true when an interruption cut
        the reply short. After the save, the save-time adapter callbacks are scheduled without waiting, and a mount
        passes the save callback to the server's handlers and to its log line, never to a page's views. Called by
        ``illocutionary_lifecycles.server.adapters.text_adapters.TextAdapter.TextAdapter.save_assistant`` and
        ``illocutionary_lifecycles.server.adapters.voice_adapters.PipecatVoiceAdapter.PipecatVoiceAdapter.save_assistant``.
        """
        if self.SystemState is None:
            return -1
        Record = getattr(self.SystemState, "Record", None)
        if Record is None:
            return -1
        idx = Record.UpsertUtteranceEvent(
            role="assistant", transcription=transcription, truncated=truncated,
        )
        self._RunAdapterCallbackHandlersAfterSave()
        return idx

    def _RunAdapterCallbackHandlersAfterSave(self) -> None:
        """Schedule ``RunAdapterCallbackHandlerEventsForRefreshSave`` on the running event loop, asyncio's scheduler that runs every coroutine of the process in turn, without waiting for it,
        and return ``None``, scheduling nothing when no event loop is running. Called only by ``TTSUtteranceSave`` in this
        module, for the one save that does not go through a refresh."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self.RunAdapterCallbackHandlerEventsForRefreshSave())

    def IncrementalPhraseTick(self, IncrementalPhraseTickInputs: dict) -> None:
        """Schedule ``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` on the speech so
        far and return ``None`` at once, without waiting for any analyzer, so a reply is never delayed by it.

        This is how the user's unfinished words reach the incremental analyzers while the user is still speaking, as the
        module docstring above explains. ``IncrementalPhraseTickInputs`` is a dict whose key ``IncrementalPhrase`` holds
        the speech so far, and an empty dict, a value that is not a dict, a session that has not started or the absence
        of a running event loop schedules nothing. The settle receives ``RunAdapterCallbackHandlersForIncrementalPhraseResult``
        in this module to send each pick. Called by
        ``illocutionary_lifecycles.server.adapters.voice_adapters.PipecatVoiceAdapter.PipecatVoiceAdapter.incremental_phrase_tick``
        on each new interim transcription, on both speech ways.
        """
        if self.SystemState is None or not isinstance(IncrementalPhraseTickInputs, dict):
            return
        if not IncrementalPhraseTickInputs:
            return
        Record = getattr(self.SystemState, "Record", None)
        if Record is None:
            return
        import asyncio
        import functools
        from illocutionary_lifecycles.core.system_state.conversation_history_window import (
            ConversationStateWindow,
        )
        from illocutionary_lifecycles.core.turn_taking.sync_cycle import DeferredIncrementalSettle
        from illocutionary_lifecycles.core.system_state.user_memory_state import UserMemoryState
        UserMemoryFace = functools.partial(UserMemoryState, Record)
        WindowFace = functools.partial(ConversationStateWindow, Record)
        try:
            asyncio.ensure_future(DeferredIncrementalSettle(
                self.SystemState, UserMemoryFace, WindowFace, dict(IncrementalPhraseTickInputs),
                RunAdapterCallbackHandlersForIncrementalPhraseResult=self.RunAdapterCallbackHandlersForIncrementalPhraseResult))
        except RuntimeError:
            return  # No running event loop.

    async def RunAdapterCallbackHandlersForIncrementalPhraseResult(self, AnalyzerType: str, InstanceIdentifier: str,
                                                                    value: dict, SpokenPhraseSoFar: str) -> None:
        """Run the handlers registered on every adapter of this session with one
        ``IncrementalPhraseAdapterCallbackHandlerEvent`` built from one incremental pick, and return ``None``.

        The callback carries ``AnalyzerType``, the instance's ``InstanceIdentifier``, the picked option as ``category``,
        ``gate`` and ``SpokenPhraseSoFar``, taken from ``value``, the analyzer's result dict, and from the speech so far,
        and carries nothing of the record, so it is small enough to send on every pick. A handler that raises is logged
        as a warning and the other handlers still run. ``DeferredIncrementalSettle`` in
        ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` calls it the moment one instance's model call returns a
        pick that is not "none" and not a repeat, after the pick has been recorded and placed on the pragmatic state."""
        from illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerEvents import (
            IncrementalPhraseAdapterCallbackHandlerEvent,
        )
        payload = IncrementalPhraseAdapterCallbackHandlerEvent(
            AnalyzerType=AnalyzerType, InstanceIdentifier=InstanceIdentifier,
            category=str((value or {}).get("category") or ""), gate=str((value or {}).get("gate") or ""),
            SpokenPhraseSoFar=str(SpokenPhraseSoFar or "")).wire()
        for adapter in list(self._OverlaidAdapters or []):
            run = getattr(adapter, "RunAdapterCallbackHandlers", None)
            if run is not None:
                try:
                    await run(payload)
                except Exception as e:
                    logger.warning("%s handler raised for %s: %s", payload.get("type", ""), self.session_id, e)

    def set_ignore_memories(self, Enabled: bool) -> bool:
        """Keep the remembered answers out of every prompt when ``Enabled`` is true, or show them again when it is false,
        and return whether the setting was applied, which is false before ``start``.

        The remembered answers are still recorded either way, and only the composed prompt changes. The setting is
        passed to ``SystemState.set_ignore_memories``, which sets or deletes the pragmatic field
        ``pIgnoreMemoriesState``, and a flow state can set the same with its key ``ignore_memories``. This is one of the two
        setters the module docstring above lists."""
        if self.SystemState is None:
            return False
        return self.SystemState.set_ignore_memories(bool(Enabled))

    def SetQuestionAnswerHook(self, Enabled: bool) -> bool:
        """Set ``SystemState.QuestionAnswerHook`` to ``Enabled`` and return true, or return false before ``start``.

        While the hook is on, every newly answered question is sent to the adapters' handlers as a
        ``QuestionAnsweredAdapterCallbackHandlerEvent`` after the save that recorded it. The mounts turn it on for every
        session they build, and
        ``illocutionary_lifecycles.server.adapters.AdapterBase.SessionProviderSetters.SetQuestionAnswerHook`` passes an
        adapter's call here."""
        if self.SystemState is None:
            return False
        self.SystemState.QuestionAnswerHook = bool(Enabled)
        return True

    def ApplyPromptChange(self, block_key: str, value: Any, block_sub_key: str | None = None,
                          source: str = "server") -> int:
        """Replace one entry of the flow's ``PromptBlocks`` while the conversation runs, so that every prompt composed
        from now on reads the new entry, and return the refresh index of the ``ManualPromptChangeEvent`` that records it, or
        ``-1`` before ``start`` or when the change could not be made. ``block_key``, ``value`` and ``block_sub_key``
        are as ``illocutionary_lifecycles.core.system_state.system_state.SystemState.ApplyPromptChange`` takes them, and
        ``source`` is the label recorded with the change. A server calls this from an adapter callback handler, after a
        state change, to set what the entered state says; the prompt of the reply already being composed is not
        affected, the next one is. One of the session calls the module docstring above lists."""
        if self.SystemState is None:
            return -1
        return self.SystemState.ApplyPromptChange(block_key, value, block_sub_key=block_sub_key, source=source)
