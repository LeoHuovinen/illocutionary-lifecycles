"""Three functions that return the recorded utterances of a conversation as ``TurnView`` objects, one of the three read
modules in ``illocutionary_lifecycles/core/system_state`` beside ``user_memory_state`` and ``static_prompt_library``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and both the analyzers that check the user's answers and the composer
that builds the model's prompt read the conversation so far through this module, in the folder ``core``, from the
record of the folder ``memory``, the analyzers of the folder ``analyzers`` receiving it from the cycle, and the
adapters of the folder ``server`` through the provider. ``ConversationStateWindow`` returns the current state's
utterances and is what the cycle in ``illocutionary_lifecycles.core.turn_taking`` hands every analyzer.
``ConversationStateWindowRecent`` keeps the last two of each role of those and is what
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` shows the model.
``ConversationHistoryWindow`` returns the whole conversation, for a state with ``global_history_window`` and for
``illocutionary_lifecycles.core.session_provider.SessionProvider.ConversationHistoryWindow``.

Each function takes the session's ``illocutionary_lifecycles.memory.memory.Memory`` and reads only its in-memory copy,
writes nothing and knows no session. Interrupted assistant utterances are recorded under their own category,
``InterruptedUtteranceEvent``, and are not returned here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TurnView:
    """One recorded utterance as the analyzers and the composer read it, built by the functions of this module, as the
    module docstring above explains.

    ``role`` holds "user" or "assistant", ``transcription`` holds the text of the utterance, and ``truncated`` holds
    whether an interruption cut the utterance short. The object is frozen and carries no refresh index.
    """

    role: str
    transcription: str
    truncated: bool


def _views_from(stream: list) -> list[TurnView]:
    """Return one ``TurnView`` per recorded utterance dict in ``stream``, in the same order. Called by the functions of
    this module."""
    return [
        TurnView(
            role=loaded.get("role", ""),
            transcription=loaded.get("transcription", ""),
            truncated=loaded.get("truncated", False),
        )
        for loaded in stream
    ]


def _turn_views(Record: Any) -> list[TurnView]:
    """Return every utterance of the conversation in ``Record`` as ``TurnView`` objects, or an empty list for a
    ``Record`` of ``None``. Called only by ``ConversationHistoryWindow`` in this module."""
    if Record is None:
        return []
    return _views_from(Record.UtteranceStream())


def ConversationStateWindow(Record: Any) -> list[TurnView]:
    """Return the utterances of the current conversation state from ``Record``, both roles, in order, as ``TurnView``
    objects, or an empty list for a ``Record`` of ``None``.

    Utterances of earlier states are left out, except the one user utterance that led to the current state, which the
    new state replies to. The boundary is set by
    ``illocutionary_lifecycles.memory.memory.Memory.CurrentConversationStateUtteranceStream``. The cycle in
    ``illocutionary_lifecycles.core.turn_taking`` passes this function, bound to the record, to every analyzer as
    ``WindowFace``, and ``SessionProvider.IncrementalPhraseTick`` passes it to the incremental settle.
    """
    if Record is None or not hasattr(Record, "CurrentConversationStateUtteranceStream"):
        return []
    return _views_from(Record.CurrentConversationStateUtteranceStream())


def ConversationStateWindowRecent(Record: Any, LastN: int) -> list[TurnView]:
    """Return what ``ConversationStateWindow`` returns for ``Record``, keeping only the last ``LastN`` user utterances
    and the last ``LastN`` assistant utterances, in their original order.

    While the state has no more than ``LastN`` of each role, the result is the whole state's window. In a long state
    the cut keeps the prompt on the current exchange.
    ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` calls it with ``LastN`` set
    to 2 for every prompt, unless the state sets ``global_history_window``.
    """
    views = ConversationStateWindow(Record)
    users = [v for v in views if getattr(v, "role", "") == "user"]
    asst = [v for v in views if getattr(v, "role", "") != "user"]
    if len(users) <= LastN and len(asst) <= LastN:
        return views
    keep = set(id(v) for v in users[-LastN:]) | set(id(v) for v in asst[-LastN:])
    return [v for v in views if id(v) in keep]


def ConversationHistoryWindow(Record: Any, LastN: int | None = None) -> list[TurnView]:
    """Return the utterances of the whole conversation from ``Record``, both roles, in order, as ``TurnView`` objects,
    keeping only the last ``LastN`` when ``LastN`` is given and all of them when it is ``None``, or an empty list for a
    ``Record`` of ``None``.

    ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` calls it with
    ``global_history_turns`` for a state that sets ``global_history_window``, and
    ``illocutionary_lifecycles.core.session_provider.SessionProvider.start`` binds it to the record as the provider's
    ``ConversationHistoryWindow``.
    """
    turns = _turn_views(Record)
    return turns if LastN is None else turns[-LastN:]
