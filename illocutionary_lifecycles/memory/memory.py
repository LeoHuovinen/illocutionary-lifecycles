"""``Memory``, the record of one conversation, to which every recorded event is added and in which none is ever
changed, and the recorded event classes, whose class names are the record's categories.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this module, in the folder ``memory``, keeps everything that happens
in it, each utterance, each analyzer result, each remembered answer, the state values after each refresh, each
composed prompt and each change of state, so the conversation can be read back at any point without running it again.
Of the package's four folders, ``core`` holds the record as ``SystemState.Record`` and is the only writer,
``analyzers`` never reach it, and ``server`` reads it through the session for the cards and the event streams. The
word "memory" means the whole record in ``Memory`` and one remembered answer in ``MemoryEvent``.

``Memory`` gives every recorded event a refresh index when it is added. The remembered answers and the state values
saved by one refresh share one index, and every other event gets an index of its own, so the index orders the events
and does not count turns, since one turn causes several refreshes. The record has two copies. The in-memory copy,
``ReadCache``, holds the event objects not yet stored and every event's dict by category, and the running conversation
reads only that copy. ``drain`` writes the events not yet stored to the storage vendor in one batch, and
``reinit_log_from_disk`` fills the in-memory copy from the vendor once at session start. Every ``Upsert`` method except
``UpsertRefreshEvents`` drains at once, and ``UpsertAnalyzerEvent`` drains only when asked, so one turn makes several
vendor writes and a tick of the incremental settle makes one.

Every ``Upsert`` method only adds. The
analyzer's registered name is stored as ``PragmaticAnalyzerType`` on ``AnalyzerEvent`` and ``MemoryEvent`` and as
``AnalyzerType`` on ``TransitionCriteriaEvent`` and inside a result entry, and the two spellings hold one value and are
part of the stored record, so neither is renamed. The category names and field names are read by name in
``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader`` and in ``EventCardReader`` and
``AdapterCallbackHandlerHelpers`` beside it in the folder ``server``, so a renamed class or field breaks them at run
time. ``Memory`` does not interpret events, and the flow is held by ``SystemState`` and stored here once as a
``ConversationInitEvent``.
"""
from __future__ import annotations

import copy
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, Iterable

logger = logging.getLogger(__name__)


def _by_event_refresh(loaded: dict[str, Any]) -> int:
    """Return the refresh index of the event dict ``loaded``, or ``-1`` when it has none, as the sort key that orders
    each category's stream, with events of one index kept in the order they were added. Used by ``ReadCache`` in this
    module."""
    return loaded.get("event_refresh_idx", -1)


@dataclass
class ConversationEvent:
    """The base class of every recorded event, the unit the record of a conversation is made of, as the module
    docstring above explains.

    A subclass sets the class attribute ``CATEGORY``, the name its events are grouped and stored under, and declares
    its own fields. ``event_refresh_idx`` holds the event's refresh index, ``-1`` on a new event until ``Memory`` sets
    it when the event is added. A storage vendor stores ``CATEGORY`` with every event, because ``dataclasses.asdict``
    leaves class attributes out.
    """

    CATEGORY: ClassVar[str] = "event"

    event_refresh_idx: int = -1


@dataclass
class UtteranceEvent(ConversationEvent):
    """One utterance of the conversation, by the user or by the assistant, recorded under the category
    "UtteranceEvent".

    The user's utterance is recorded by ``ResponseProcessing`` in ``illocutionary_lifecycles.core.turn_taking`` when
    the turn arrives, once even when a move has a second state process it, and the assistant's reply by
    ``SessionProvider.TTSUtteranceSave`` once it has been delivered. ``role`` holds "user" or "assistant",
    ``transcription`` holds the text, ``truncated`` holds whether an interruption cut it short, and
    ``source_refresh_idx`` holds, for an assistant utterance, the refresh index of the ``ComposedPromptEvent`` it was
    written from, and ``-1`` otherwise. Which user utterance a reply answers is not stored.
    """

    CATEGORY: ClassVar[str] = "UtteranceEvent"

    role: str = ""
    transcription: str = ""
    truncated: bool = False
    source_refresh_idx: int = -1


@dataclass
class AnalyzerEvent(ConversationEvent):
    """The result of one analyzer run, recorded under the category "AnalyzerEvent" by the cycles in
    ``illocutionary_lifecycles.core.turn_taking.sync_cycle``.

    ``results`` holds a dict with one entry, the result key, the registered name with the position or the instance
    identifier after two colons where there is one, mapped to a dict with ``success``, ``value``, ``AnalyzerType``,
    ``AnalyzerId`` and ``prompt`` and, for a question checker or a listed criterion, ``WithinConversationStateOrdinal``.
    ``PragmaticAnalyzerType`` holds the analyzer's registered name, the same value a result entry holds as
    ``AnalyzerType``. ``PragmaticAnalyzerInstance`` holds what tells this run apart from other runs of the same
    analyzer, the registered name, two colons and the question's position for a question checker, the instance
    identifier for an incremental run, and the registered name alone for every other analyzer, listed criteria
    included.
    ``prompt`` is left empty by the cycles, which keep the analyzer's prompt inside the result entry.
    ``analyzed_utterance_idx`` holds the refresh index of the user utterance analyzed, and ``-1`` for a run on the
    speech so far, whose utterance is not finished, which
    ``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerHelpers.TurnClusters`` uses to
    attach such runs to the utterance that follows.
    """

    CATEGORY: ClassVar[str] = "AnalyzerEvent"

    results: dict[str, Any] = field(default_factory=dict)
    PragmaticAnalyzerType: str | None = None
    PragmaticAnalyzerInstance: str | None = None
    prompt: str = ""
    analyzed_utterance_idx: int = -1


@dataclass
class PragmaticStatesEvent(ConversationEvent):
    """The pragmatic state's values as they stood after one refresh, recorded under the category "PragmaticStates" by
    ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter`` with the same refresh index as that refresh's
    remembered answers. ``values`` holds the dict of every p-prefixed field from
    ``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.pragmatic_values``, and a ``ComposedPromptEvent``
    names the one it was composed from by its refresh index."""

    CATEGORY: ClassVar[str] = "PragmaticStates"

    values: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryEvent(ConversationEvent):
    """One remembered answer, shared by the whole conversation, recorded under the category "MemoryEvent" by
    ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter`` for every analyzer result that reported a non-empty
    answer.

    ``memory`` holds a dict whose key ``answer`` is the answer sentence, and
    ``illocutionary_lifecycles.core.system_state.user_memory_state.UserMemoryState`` returns these dicts for the
    composer. ``PragmaticAnalyzerType`` holds the registered name of the analyzer that produced it, and
    ``PragmaticAnalyzerInstance`` the ``AnalyzerId`` of that run.
    """

    CATEGORY: ClassVar[str] = "MemoryEvent"

    memory: dict[str, Any] = field(default_factory=dict)
    PragmaticAnalyzerType: str | None = None
    PragmaticAnalyzerInstance: str | None = None


@dataclass
class ComposedPromptEvent(ConversationEvent):
    """One prompt as the composer built it for a reply, recorded under the category "ComposedPromptEvent" by
    ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing`` before the model is called.

    The finished prompt is kept because it contains text the state values and the authored blocks alone do not
    determine, such as the utterances shown. ``prompt`` holds the prompt text, and ``source_state_idx`` holds the
    refresh index of the newest saved ``PragmaticStatesEvent``, the values it was composed from, or ``-1`` when unknown.
    The reply written from it records this event's index as its ``source_refresh_idx``.
    """

    CATEGORY: ClassVar[str] = "ComposedPromptEvent"

    prompt: str = ""
    source_state_idx: int = -1


@dataclass
class InterruptedUtteranceEvent(UtteranceEvent):
    """An assistant utterance the user interrupted, recorded under its own category "InterruptedUtteranceEvent", so
    the windows of ``illocutionary_lifecycles.core.system_state.conversation_history_window`` never return it.

    ``transcription`` holds the whole generated reply, ``truncated`` is true, and ``heard`` holds the part spoken
    before the interruption, which the caller works out. ``Memory.UpsertInterruptedUtteranceEvent`` records it.
    """

    CATEGORY: ClassVar[str] = "InterruptedUtteranceEvent"

    heard: str = ""


@dataclass
class ConversationStateEvent(ConversationEvent):
    """One move of the conversation to another state, recorded under the category "ConversationStateEvent" by
    ``SystemState.set_current_conversation_state``.

    ``conversation_state`` holds the index of the state entered and ``previous_conversation_state`` the index of the
    state left. The newest of these events is the boundary of the current state's utterances in
    ``Memory.CurrentConversationStateUtteranceStream``, and ``SessionProvider`` sends one
    ``ConversationStateChangedAdapterCallbackHandlerEvent`` for each. The first state is entered without such an
    event. The record it belongs to is described in the module docstring above.
    """

    CATEGORY: ClassVar[str] = "ConversationStateEvent"

    conversation_state: int = -1
    previous_conversation_state: int | None = None


@dataclass
class TransitionCriteriaEvent(ConversationEvent):
    """One listed transition criterion that reported its state may be left, recorded under the category
    "TransitionCriteriaEvent" by ``SyncCycle`` in ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` before the
    refresher sets whether the conversation moves, so several may be recorded after one utterance while at most one
    move follows.

    ``AnalyzerType`` holds the criterion's registered name, the value an ``AnalyzerEvent`` holds as
    ``PragmaticAnalyzerType``. ``WithinConversationStateOrdinal`` holds the entry's position in the state's criteria
    list, and ``analyzer_event_idx`` the refresh index of the ``AnalyzerEvent`` that holds the result, or ``-1``.
    """

    CATEGORY: ClassVar[str] = "TransitionCriteriaEvent"

    AnalyzerType: str = ""
    WithinConversationStateOrdinal: int = -1
    analyzer_event_idx: int = -1


@dataclass
class ManualPromptChangeEvent(ConversationEvent):
    """One replacement of an authored prompt block while the conversation runs, recorded under the category
    "ManualPromptChangeEvent" by ``Memory.UpsertManualPromptChangeEvent``, which
    ``illocutionary_lifecycles.core.system_state.system_state.SystemState.ApplyPromptChange`` calls in the same step as
    the replacement, so that no change of an authored text goes unrecorded and a reopened session can see from which
    refresh index on each prompt was composed from the new text.

    ``block_key`` holds the top-level entry of ``PromptBlocks`` that changed, ``block_sub_key`` the key inside a nested
    entry, a state index under ``IllocutionaryPrompt`` or a condition name under ``memory_callback``, or ``None`` for a
    flat entry, ``previous_value`` the entry before the change, ``value`` the entry after it, and ``source`` the label
    the caller gave. The record it belongs to is described in the module docstring above.
    """

    CATEGORY: ClassVar[str] = "ManualPromptChangeEvent"

    block_key: str = ""
    block_sub_key: str | None = None
    previous_value: Any = None
    value: Any = None
    source: str = ""


@dataclass
class ReadCache:
    """The in-memory copy of one conversation's record, the only copy the running conversation reads, held by
    ``Memory`` as ``read_cache``, as the module docstring above explains.

    ``SessionVendorConnection`` holds the storage vendor, or ``None``, set by ``Memory`` and read once by ``build``.
    The private ``_streams`` holds every event of the conversation as a dict, stored ones and new ones, grouped by
    category and ordered by refresh index. ``EventStreamCache`` holds the event objects added in this process, in the
    order added, from which ``Memory.drain`` takes the ones not yet stored.
    """

    SessionVendorConnection: Any = None
    _streams: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    EventStreamCache: list["ConversationEvent"] = field(default_factory=list)

    def build(self, SessionConversationId: str) -> None:
        """Add every stored event of the conversation ``SessionConversationId``, read once from the storage vendor's
        ``read_persistent_batch``, to the streams by its ``CATEGORY``, sort each stream by refresh index, and return
        ``None``, doing nothing without a vendor. Called only by ``Memory.reinit_log_from_disk`` in this module, once
        when a session starts or resumes."""
        if self.SessionVendorConnection is None:
            return
        VisibleMemoryWindow = self.SessionVendorConnection.read_persistent_batch(
            SessionConversationId,
        )
        for loaded in VisibleMemoryWindow:
            self._streams.setdefault(loaded.get("CATEGORY"), []).append(loaded)
        for EventCategory in self._streams:
            self._streams[EventCategory].sort(key=_by_event_refresh)

    def append_event(self, RecordedEvent: "ConversationEvent") -> None:
        """Keep ``RecordedEvent``, which already has its refresh index, in ``EventStreamCache`` for ``Memory.drain`` to
        store, add its dict with ``CATEGORY`` to the stream of its category, re-sort that stream, and return ``None``.
        Called only by ``Memory.append`` in this module."""
        self.EventStreamCache.append(RecordedEvent)
        stored = asdict(RecordedEvent)
        stored["CATEGORY"] = type(RecordedEvent).CATEGORY
        self._streams.setdefault(stored.get("CATEGORY"), []).append(stored)
        self._streams[stored.get("CATEGORY")].sort(key=_by_event_refresh)

    def events_at_or_after_idx(self, RefreshIndex: int) -> list["ConversationEvent"]:
        """Return the event objects added in this process whose refresh index is ``RefreshIndex`` or higher, in the
        order added. Called by ``Memory.drain`` in this module with the first index not yet stored."""
        return [e for e in self.EventStreamCache if e.event_refresh_idx >= RefreshIndex]

    def streams(self) -> dict[str, list[dict[str, Any]]]:
        """Return the dict from each category to its list of event dicts ordered by refresh index, the object itself and
        not a copy. Read by ``SessionProvider`` for the ``streams`` of the save-time callbacks, by
        ``SystemState.RecoverInit`` and by ``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader``."""
        return self._streams

    def _category_stream(self, EventCategory: str) -> list[dict[str, Any]]:
        """Return a copy of the list of event dicts of ``EventCategory``, ordered by refresh index, or an empty list,
        through ``illocutionary_lifecycles.memory.MemoryReadTools.FilterByCategoryTool.filter_by_category``. Called by
        the read methods of ``Memory`` in this module."""
        from illocutionary_lifecycles.memory.MemoryReadTools import filter_by_category
        return filter_by_category(self._streams, EventCategory)


@dataclass
class Memory:
    """The record of one conversation, held by a session as ``SystemState.Record`` and built by
    ``SystemState.InitializeMemoryClasses``, as the module docstring above explains.

    ``SessionConversationId`` holds the session's id, under which the vendor stores the events.
    ``SessionVendorConnection`` holds the storage vendor from
    ``illocutionary_lifecycles.memory.persistence.build_persistent_connection``, or ``None`` to keep the events in
    memory only. ``read_cache`` holds the in-memory copy, a ``ReadCache``. The private ``_persisted_idx`` holds the first
    refresh index not yet stored, and ``_next_refresh_idx`` the index the next event or group of events receives, which
    ``ResponseProcessing`` reads to learn a user utterance's index before saving it. The ``Upsert`` methods add events,
    ``drain`` stores them, ``reinit_log_from_disk`` loads the stored ones, and the stream methods read them.
    """

    SessionConversationId: str
    SessionVendorConnection: Any = None

    read_cache: ReadCache = field(default_factory=ReadCache)

    # Events with a refresh index below this are already stored.
    _persisted_idx: int = 0

    # The refresh index the next added event, or group of events, receives.
    _next_refresh_idx: int = 0

    def __post_init__(self) -> None:
        """Give the in-memory copy the same storage vendor, so ``ReadCache.build`` in this module reads from it."""
        self.read_cache.SessionVendorConnection = self.SessionVendorConnection

    def UpsertConversationInitEvent(self, values: dict[str, Any]) -> None:
        """Write the flow ``values`` straight to the storage vendor as one ``ConversationInitEvent``, deep-copied, and
        return ``None``, writing nothing without a vendor.

        The event is not added to the in-memory copy and gets no refresh index, because ``SystemState`` holds the flow
        while the session runs, and ``SystemState.RecoverInit`` finds it in the stored record when the session is
        reopened. Called only by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit`` for a session with
        no stored flow.
        """
        if self.SessionVendorConnection is not None:
            self.SessionVendorConnection.save_persistent_batch(
                self.SessionConversationId,
                [ConversationInitEvent(values=copy.deepcopy(values))],
            )

    def append(self, RecordedEvent: ConversationEvent) -> None:
        """Add ``RecordedEvent``, which already has its refresh index, to the in-memory copy through
        ``ReadCache.append_event``, and return ``None``. Called by every ``Upsert`` method of this class."""
        self.read_cache.append_event(RecordedEvent)

    def UpsertUtteranceEvent(self, role: str, transcription: str,
                             truncated: bool = False) -> int:
        """Record one ``UtteranceEvent`` under a refresh index of its own, write it to the vendor at once, and return
        that index.

        ``role`` is "user" or "assistant". ``transcription`` is the text, and when it carries a ``source_refresh_idx``
        attribute, as the ``ComposedReply`` of ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing`` does,
        that index is recorded with the utterance. ``truncated`` is whether an interruption cut it short. Called by
        ``ResponseProcessing`` in that module for the user's utterance and by ``SessionProvider.TTSUtteranceSave`` for
        the assistant's reply.
        """
        composed_idx = getattr(transcription, "source_refresh_idx", None)
        event = UtteranceEvent(
            role=role, transcription=str(transcription), truncated=truncated,
            **({"source_refresh_idx": composed_idx} if composed_idx is not None else {}),
        )
        event.event_refresh_idx = self._next_refresh_idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()
        return event.event_refresh_idx

    def UpsertInterruptedUtteranceEvent(self, full: str, heard: str) -> int:
        """Record one ``InterruptedUtteranceEvent`` with the role "assistant" under a refresh index of its own, write it
        to the vendor at once, and return that index. ``full`` is the whole generated reply and ``heard`` the part spoken
        before the interruption."""
        event = InterruptedUtteranceEvent(
            role="assistant", transcription=str(full), heard=str(heard),
            truncated=True,
        )
        event.event_refresh_idx = self._next_refresh_idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()
        return event.event_refresh_idx

    def UpsertAnalyzerEvent(self, results: dict, prompt: str = "",
                            analyzed_utterance_idx: int = -1,
                            PragmaticAnalyzerType: str | None = None,
                            PragmaticAnalyzerInstance: str | None = None,
                            drain: bool = True) -> int:
        """Record one ``AnalyzerEvent`` under a refresh index of its own and return that index, with the arguments
        stored as the event's fields of the same names, which the class docstring of ``AnalyzerEvent`` describes.

        ``drain`` is whether the event is written to the vendor now, true by default, and the incremental settle in
        ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` passes false for each result of a tick and drains once
        after the tick. Called by ``SyncCycle`` and ``DeferredIncrementalSettle`` in that module.
        """
        event = AnalyzerEvent(
            results=results, prompt=prompt, analyzed_utterance_idx=analyzed_utterance_idx,
            PragmaticAnalyzerType=PragmaticAnalyzerType, PragmaticAnalyzerInstance=PragmaticAnalyzerInstance,
        )
        idx = self._next_refresh_idx
        event.event_refresh_idx = idx
        self._next_refresh_idx += 1
        self.append(event)
        if drain:
            self.drain()
        return idx

    def UpsertComposedPromptEvent(self, prompt: str, source_state_idx: int = -1) -> int:
        """Record one ``ComposedPromptEvent`` with ``prompt`` and ``source_state_idx`` under a refresh index of its own,
        write it to the vendor at once, and return that index, which the reply written from the prompt carries as its
        ``source_refresh_idx``. Called only by ``ResponseProcessing`` in
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing``."""
        event = ComposedPromptEvent(prompt=prompt, source_state_idx=source_state_idx)
        idx = self._next_refresh_idx
        event.event_refresh_idx = idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()
        return idx

    def UpsertConversationStateEvent(self, conversation_state: int,
                                     previous_conversation_state: int | None = None) -> None:
        """Record one ``ConversationStateEvent`` with the state entered, ``conversation_state``, and the state left,
        ``previous_conversation_state``, under a refresh index of its own, write it to the vendor at once, and return
        ``None``. Called only by ``SystemState.set_current_conversation_state``, as the class docstring of
        ``ConversationStateEvent`` in this module says."""
        event = ConversationStateEvent(conversation_state=conversation_state,
                                       previous_conversation_state=previous_conversation_state)
        event.event_refresh_idx = self._next_refresh_idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()

    def UpsertTransitionCriteriaEvent(self, AnalyzerType: str,
                                      WithinConversationStateOrdinal: int = -1,
                                      analyzer_event_idx: int = -1) -> int:
        """Record one ``TransitionCriteriaEvent`` with the three arguments as its fields of the same names under a
        refresh index of its own, write it to the vendor at once, and return that index. Called only by ``SyncCycle`` in
        ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` for every listed criterion that reported done."""
        event = TransitionCriteriaEvent(
            AnalyzerType=AnalyzerType,
            WithinConversationStateOrdinal=WithinConversationStateOrdinal,
            analyzer_event_idx=analyzer_event_idx,
        )
        idx = self._next_refresh_idx
        event.event_refresh_idx = idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()
        return idx

    def UpsertManualPromptChangeEvent(self, block_key: str, block_sub_key: str | None,
                                previous_value: Any, value: Any, source: str = "") -> int:
        """Record one ``ManualPromptChangeEvent`` with ``block_key``, ``block_sub_key``, ``previous_value``, ``value`` and
        ``source`` under a refresh index of its own, write it to the vendor at once, and return that index. Called only
        by ``illocutionary_lifecycles.core.system_state.system_state.SystemState.ApplyPromptChange``, as the class
        docstring of ``ManualPromptChangeEvent`` in this module says."""
        event = ManualPromptChangeEvent(
            block_key=str(block_key), block_sub_key=block_sub_key,
            previous_value=previous_value, value=value, source=str(source or ""),
        )
        idx = self._next_refresh_idx
        event.event_refresh_idx = idx
        self._next_refresh_idx += 1
        self.append(event)
        self.drain()
        return idx

    def UpsertRefreshEvents(self, RecordedEvents: Iterable[ConversationEvent]) -> None:
        """Give every event in ``RecordedEvents`` the same new refresh index, add each to the in-memory copy, and return
        ``None``, without writing to the vendor, which the caller does with ``drain``. Called only by
        ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter.save_refresh_result`` for one refresh's remembered
        answers and state values."""
        idx = self._next_refresh_idx
        self._next_refresh_idx += 1
        for event in RecordedEvents:
            event.event_refresh_idx = idx
            self.append(event)

    def drain(self) -> None:
        """Write every event object whose refresh index is at or after the first index not yet stored to the storage
        vendor in one ``save_persistent_batch`` call, mark everything up to the next index as stored, and return
        ``None``, doing nothing without a vendor or when everything is stored. A reading-only vendor raises
        ``ReadOnlyStoreError`` from here on the first write. Called by the ``Upsert`` methods of this class, by
        ``MemoryWriter.save_refresh_result`` and once per tick by the incremental settle."""
        if self.SessionVendorConnection is None:
            return
        pending = self.read_cache.events_at_or_after_idx(self._persisted_idx)
        if not pending:
            return
        self.SessionVendorConnection.save_persistent_batch(
            self.SessionConversationId, pending,
        )
        self._persisted_idx = self._next_refresh_idx

    def reinit_log_from_disk(self) -> None:
        """Load the conversation's stored events into the in-memory copy through ``ReadCache.build``, set the next
        refresh index after the highest stored one so a resumed session never reuses an index, count everything loaded
        as stored, and return ``None``. Called only by
        ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``, before anything reads the record. The
        recorded state changes are not replayed into ``SystemState``, so a reopened session gets the record and not its
        position."""
        self.read_cache.build(self.SessionConversationId)
        HighestStored = max(
            (loaded.get("event_refresh_idx", -1)
             for stream in self.read_cache.streams().values() for loaded in stream
             if isinstance(loaded.get("event_refresh_idx", -1), int)),
            default=-1,
        )
        self._next_refresh_idx = max(self._next_refresh_idx, HighestStored + 1)
        self._persisted_idx = self._next_refresh_idx

    def RelevantMemoryOfKind(self, EventCategory: str) -> list[dict[str, Any]]:
        """Return the ``memory`` dict of every recorded event of ``EventCategory`` that has one, in order. The only
        caller, ``illocutionary_lifecycles.core.system_state.user_memory_state.UserMemoryState``, passes "MemoryEvent",
        so the result is the remembered answers."""
        return [
            loaded.get("memory")
            for loaded in self.read_cache._category_stream(EventCategory)
            if isinstance(loaded.get("memory"), dict)
        ]

    def UtteranceStream(self) -> list[dict[str, Any]]:
        """Return a copy of the list of every recorded ``UtteranceEvent`` dict of the conversation, in order, without
        the interrupted utterances, which are another category. Called by
        ``illocutionary_lifecycles.core.system_state.conversation_history_window`` for the whole conversation."""
        return list(self.read_cache._category_stream(UtteranceEvent.CATEGORY))

    def CurrentConversationStateUtteranceStream(self) -> list[dict[str, Any]]:
        """Return the recorded ``UtteranceEvent`` dicts of the current conversation state, in order.

        These are the utterances whose refresh index is at or after the newest ``ConversationStateEvent``, with the
        one utterance just below it put first, because the move followed from analyzing that utterance, so it is saved
        before the move, and the new state is the one that replies to it. Before any move every utterance is returned.
        Called by ``ConversationStateWindow`` in
        ``illocutionary_lifecycles.core.system_state.conversation_history_window``, which every analyzer and the
        composer read through.
        """
        StateChangeRecords = self.read_cache._category_stream(ConversationStateEvent.CATEGORY)
        boundary_idx = StateChangeRecords[-1].get("event_refresh_idx", -1) if StateChangeRecords else -1
        Utterances = list(self.read_cache._category_stream(UtteranceEvent.CATEGORY))
        InCurrentState = [u for u in Utterances if u.get("event_refresh_idx", -1) >= boundary_idx]
        # A change of state follows from analyzing an utterance, so that utterance is saved
        # before the change. It is included here because the new state is the one that
        # replies to it.
        Below = [u for u in Utterances if u.get("event_refresh_idx", -1) < boundary_idx]
        if boundary_idx >= 0 and Below:
            InCurrentState = [Below[-1]] + InCurrentState
        return InCurrentState

@dataclass
class ConversationInitEvent(ConversationEvent):
    """The flow a conversation was started with, stored under the category "ConversationInit" once, by
    ``Memory.UpsertConversationInitEvent``, and read back by ``SystemState.RecoverInit`` when the session is reopened.
    ``values`` holds the whole flow dict, with ``PromptBlocks`` and ``ConversationStates``. The module docstring above explains why the
    flow is stored once and not kept in the in-memory copy."""

    CATEGORY: ClassVar[str] = "ConversationInit"

    values: dict[str, Any] = field(default_factory=dict)
