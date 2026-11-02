"""The streams and the cards of one session, read from the in-memory copy of its record through its
``SessionProvider``, with ``event_streams`` returning every recorded category and ``event_cards`` the cards a person
reads.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a program that reviews a session, a flow's author looking at what
happened, reads the record through this module, in the folder ``server``, rather than reaching
into the folder ``memory`` or ``core``. Each function takes the session's
``illocutionary_lifecycles.core.session_provider.SessionProvider`` and reads ``SystemState.Record``, holds no state
and writes nothing, and ``analyzers`` are never called. The card text is worded by
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``. ``EVENT_STREAM_CATEGORIES`` lists the ten recorded categories by class name, so a new recorded event class
needs its category added here.
"""
from __future__ import annotations

from typing import Any

# Every category of recorded event.
EVENT_STREAM_CATEGORIES = (
    "ConversationInit", "PragmaticStates", "AnalyzerEvent", "MemoryEvent",
    "UtteranceEvent", "InterruptedUtteranceEvent", "ConversationStateEvent",
    "TransitionCriteriaEvent", "ComposedPromptEvent", "ManualPromptChangeEvent",
)


def _read_stream(SessionProvider: Any, EventCategory: str) -> list:
    """Return a copy of the list of recorded event dicts of ``EventCategory`` for the session of ``SessionProvider``,
    read from the record's in-memory copy, or an empty list when the session has not started. Called by ``event_streams`` in this module."""
    Record = getattr(getattr(SessionProvider, "SystemState", None), "Record", None)
    if Record is None:
        return []
    read_cache = getattr(Record, "read_cache", None)
    if read_cache is not None and hasattr(read_cache, "streams"):
        return list((read_cache.streams() or {}).get(EventCategory) or [])
    return []


def event_streams(SessionProvider: Any) -> dict:
    """Return a dict from each category in ``EVENT_STREAM_CATEGORIES`` to the session's list of recorded event dicts of
    that category, an empty list for a category with none, for the session of ``SessionProvider``. Called by
    ``event_cards`` in this module."""
    return {EventCategory: _read_stream(SessionProvider, EventCategory) for EventCategory in EVENT_STREAM_CATEGORIES}


def event_cards(SessionProvider: Any, card_forms: Any = None) -> list:
    """Return the cards of the session of ``SessionProvider``, what
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader.all_event_cards`` returns for its
    streams with a ``FlowDesign`` built from the session's flow, each card a dict with ``key``, ``label``, ``summary``,
    ``links`` and ``forms``. ``card_forms`` is a dict from category to the form names wanted, and ``None`` keeps every
    form. Called by a program that reviews a session."""
    from illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader import all_event_cards
    from illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerHelpers import FlowDesign
    bundle = getattr(getattr(SessionProvider, "SystemState", None), "ConversationStateInitBundle", None)
    init = bundle if isinstance(bundle, dict) else {}
    return all_event_cards(event_streams(SessionProvider), FlowDesign(init), card_forms)
