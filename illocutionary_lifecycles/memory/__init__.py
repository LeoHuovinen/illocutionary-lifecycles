"""The folder that holds the record of a conversation, every recorded event added and never changed, and the storage
vendors that keep it beyond the running process.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every utterance, analyzer result, remembered answer, state value,
composed prompt and state change of it is kept here as a recorded event, so a finished conversation can be read back,
reviewed and shown as cards. Of the package's four folders, ``core`` writes every event through this folder and reads
the conversation back from it, ``analyzers`` never reach it, and ``server`` reads it for the cards and the event
streams through the session. Nothing in this folder imports ``core`` or ``server``, except that the Cosmos DB vendor
reads its settings through ``illocutionary_lifecycles.core.environment.Required``.

The word "memory" names two things here, and each docstring says which. The folder and the class
``illocutionary_lifecycles.memory.memory.Memory`` are the whole record, held by a session as ``SystemState.Record``.
A ``MemoryEvent`` is one remembered answer, and ``MemoryEvent.memory`` its dict. The module ``memory`` holds
``Memory`` and every recorded event class, whose class names are the record's categories. The module ``MemoryWriter``
holds the writer that turns one refresh into remembered answers and state values. The folder ``persistence`` holds the
storage vendors, chosen per session by name. The folder ``MemoryReadTools`` holds three functions that read event dicts
and prompt blocks they are given, which are plain functions and not tools a language model calls. ``Memory``,
``MemoryWriter`` and the event classes are re-exported here.
"""
from illocutionary_lifecycles.memory.memory import (
    Memory,
    ConversationEvent,
    UtteranceEvent,
    InterruptedUtteranceEvent,
    AnalyzerEvent,
    MemoryEvent,
    ComposedPromptEvent,
    PragmaticStatesEvent,
    ConversationStateEvent,
    TransitionCriteriaEvent,
    ManualPromptChangeEvent,
    ConversationInitEvent,
)
from illocutionary_lifecycles.memory.MemoryWriter import MemoryWriter

__all__ = [
    "Memory",
    "MemoryWriter",
    "ConversationEvent",
    "UtteranceEvent",
    "InterruptedUtteranceEvent",
    "AnalyzerEvent",
    "MemoryEvent",
    "ComposedPromptEvent",
    "PragmaticStatesEvent",
    "ConversationStateEvent",
    "TransitionCriteriaEvent",
    "ManualPromptChangeEvent",
    "ConversationInitEvent",
]
