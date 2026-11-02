"""The functions that shape a conversation's record for the cards and for review, ``FlowDesign``, which looks up the
flow's authored question texts by index, the card units and their links, the merged order of the record, the clusters
of events around each user utterance, and the saved utterances.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record, kept by the folder ``memory``, refers to things by
index, a state index, a question's position, a refresh index, so a person reading about a session needs those turned
back into the flow's words and linked to where they came from. This module, in the folder ``server``, does that over
recorded event dicts it is given and writes nothing, renders no card text and knows no wire, while the card text
itself is worded by ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``, its only caller in
the package. The folders ``core`` and ``analyzers`` never call it.

``FlowDesign``, ``index_by_refresh``, ``state_of`` and ``build_card_units`` serve the card reader. ``build_card_units``
links each unit only to units recorded at or before it, a remembered answer to the analyzer run that produced it, an
analyzer result to the user utterance it analyzed, a criterion's record to its analyzer result, a state change and a
composed prompt to the state values of their refresh, and an assistant utterance to the prompt it came from. Each
unit keeps its event's refresh index under the key "idx". ``merged_events``, ``TurnClusters`` and ``turns`` are for
programs that review a session.
"""
from __future__ import annotations

from typing import Any


class FlowDesign:
    """The lookup of the flow's authored question texts by state index and position, built from the flow's
    ``ConversationStates``, as the module docstring above explains. Built by
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader.event_cards`` and passed to every card
    function as ``FlowDesign``."""

    def __init__(self, init_values: dict[str, Any] | None) -> None:
        """Keep the ``ConversationStates`` of the flow ``init_values``, or an empty dict when the flow is ``None`` or
        has none, for the lookups of this class."""
        v = init_values or {}
        self._states: dict[str, Any] = v.get("ConversationStates", {}) or {}

    def _state(self, state_idx: Any) -> dict[str, Any]:
        """Return the flow's entry for the state ``state_idx``, looked up as a string, or an empty dict when the index is
        ``None`` or names no state. Called by ``question_text`` in this class."""
        if state_idx is None:
            return {}
        sec = self._states.get(str(state_idx))
        return sec if isinstance(sec, dict) else {}

    def question_text(self, state_idx: Any, ordinal: Any = 0) -> str:
        """Return the text of the question at position ``ordinal`` in the ``questions`` of the state ``state_idx``, the
        string itself or the ``question`` of a dict entry, or an empty string when the state or the position is unknown.
        The position is among all the state's questions as the flow lists them. Called by the card functions of
        ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``."""
        qs = self._state(state_idx).get("questions") or []
        try:
            entry = qs[int(ordinal)]
        except (TypeError, ValueError, IndexError):
            return ""
        if isinstance(entry, dict):
            return str(entry.get("question", ""))
        return str(entry)

def index_by_refresh(streams: dict[str, list[dict[str, Any]]]) -> dict[Any, dict[str, dict[str, Any]]]:
    """Return a dict from each refresh index in ``streams`` to a dict from category to the event dict recorded under
    that index, keeping the last when several events of one category share an index. Called by ``all_event_cards`` in
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``, and read by ``state_of`` in this
    module."""
    by_idx: dict[Any, dict[str, dict[str, Any]]] = {}
    for EventCategory, events in (streams or {}).items():
        for EventDict in events or []:
            RefreshIndex = EventDict.get("event_refresh_idx")
            by_idx.setdefault(RefreshIndex, {})[EventCategory] = EventDict
    return by_idx


def state_of(EventDict: dict[str, Any], by_idx: dict[Any, dict[str, dict[str, Any]]]) -> Any:
    """Return the ``pConversationState`` of the ``PragmaticStates`` event recorded under the same refresh index as
    ``EventDict``, read through ``by_idx`` from ``index_by_refresh``, or ``None`` when no state values were recorded at
    that index. A remembered answer shares its refresh's index with the state values, so its state is found this way.
    Called by the card reader in
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``."""
    prag = (by_idx.get(EventDict.get("event_refresh_idx"), {}) or {}).get("PragmaticStates", {}) or {}
    return (prag.get("values", {}) or {}).get("pConversationState")


def _unit_key(EventCategory: str, RefreshIndex: Any, sub: Any = None) -> str:
    """Return the key of one card unit, the category, an at sign and the refresh index, followed by a hash sign and
    ``sub``, the result key, for one result of an analyzer event. Called by ``build_card_units`` in this module."""
    base = f"{EventCategory}@{RefreshIndex}"
    return f"{base}#{sub}" if sub is not None else base


def build_card_units(streams: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Return the recorded ``streams`` as a list of card units ordered by refresh index, one unit per recorded event and
    one per result for an analyzer event, each linked to the earlier units it came from as the module docstring above
    lists.

    Every unit is a dict with ``key``, ``category``, ``idx``, the event's refresh index, ``event``, the event dict, and
    ``links``, the keys of the units it came from. An analyzer unit also has ``result_key``, ``result``, the result's
    value, ``result_prompt``, ``result_name``, the registered name, and ``label_override``, which is "State Completion"
    for a transition criterion and the words IncrementalPhrase, a colon and the instance for an incremental
    analyzer, and has ``AnalyzedUtteranceText`` when it analyzed a user utterance. A remembered answer links to the
    newest analyzer run of the same instance recorded at or before it. Called by ``all_event_cards`` in
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``.
    """
    flat: list[tuple[int, int, dict[str, Any]]] = []
    seq = 0
    for EventCategory, events in (streams or {}).items():
        for EventDict in events or []:
            RefreshIndex = EventDict.get("event_refresh_idx")
            order = RefreshIndex if isinstance(RefreshIndex, int) else -1
            if EventCategory == "AnalyzerEvent":
                for rkey, rval in (EventDict.get("results", {}) or {}).items():
                    result_name = (rval or {}).get("AnalyzerType", "") or ""
                    # Transition criteria and incremental phrase analyzers get their own card labels.
                    label_override = ("State Completion"
                                      if result_name.endswith("ConversationStateTransitionCriteria") else "")
                    if "IncrementalPhrase" in result_name:
                        _instance = str(EventDict.get("PragmaticAnalyzerInstance") or "").strip()
                        label_override = (f"IncrementalPhrase: {_instance}" if _instance
                                          else f"IncrementalPhrase: {result_name}")
                    flat.append((order, seq, {
                        "key": _unit_key(EventCategory, RefreshIndex, rkey),
                        "category": EventCategory, "idx": RefreshIndex, "event": EventDict,
                        "result_key": rkey, "result": (rval or {}).get("value", {}) or {},
                        "result_prompt": (rval or {}).get("prompt", "") or "",
                        "result_name": result_name,
                        "label_override": label_override,
                        "links": [],
                    }))
                    seq += 1
            else:
                flat.append((order, seq, {
                    "key": _unit_key(EventCategory, RefreshIndex), "category": EventCategory, "idx": RefreshIndex,
                    "event": EventDict, "links": [],
                }))
                seq += 1
    flat.sort(key=lambda t: t[0])
    units = [u for _o, _s, u in flat]

    by_pos: dict[tuple, list[dict[str, Any]]] = {}
    by_key: dict[str, dict[str, Any]] = {}
    for u in units:
        by_pos.setdefault((u["idx"], u["category"]), []).append(u)
        by_key[u["key"]] = u

    def link(a: dict[str, Any], b_key: str) -> None:
        """Add ``b_key`` to the ``links`` of the unit ``a`` once, when that key names another existing unit, for the
        enclosing ``build_card_units``."""
        # A link points from a unit to the unit it came from, never the other way.
        if b_key in by_key and b_key != a["key"] and b_key not in a["links"]:
            a["links"].append(b_key)

    # A memory and the analyzer run that produced it share an instance name, not a refresh
    # index. The memory links to the newest run of that instance recorded at or before it.
    analyzer_by_instance: dict[Any, list[dict[str, Any]]] = {}
    for u in units:
        if u["category"] == "AnalyzerEvent":
            inst = u["event"].get("PragmaticAnalyzerInstance")
            if inst is None:
                inst = u.get("result_key")
            if inst is not None:
                analyzer_by_instance.setdefault(inst, []).append(u)

    for u in units:
        RefreshIndex, EventCategory, EventDict = u["idx"], u["category"], u["event"]
        if EventCategory == "MemoryEvent":
            inst = EventDict.get("PragmaticAnalyzerInstance")
            runs = [a for a in analyzer_by_instance.get(inst, [])
                    if isinstance(a["idx"], int) and isinstance(RefreshIndex, int) and a["idx"] <= RefreshIndex]
            if runs:
                link(u, runs[-1]["key"])
        elif EventCategory == "AnalyzerEvent":
            # ``analyzed_utterance_idx`` is -1 when the analyzer analyzed no utterance.
            au = EventDict.get("analyzed_utterance_idx")
            if isinstance(au, int) and au >= 0:
                for o in by_pos.get((au, "UtteranceEvent"), []):
                    if o["event"].get("role") == "user":
                        link(u, o["key"])
                        u["AnalyzedUtteranceText"] = str(o["event"].get("transcription", "") or "")
        elif EventCategory == "TransitionCriteriaEvent":
            ae = EventDict.get("analyzer_event_idx")
            if isinstance(ae, int) and ae >= 0:
                for o in by_pos.get((ae, "AnalyzerEvent"), []):
                    link(u, o["key"])
        elif EventCategory == "ConversationStateEvent":
            for o in by_pos.get((RefreshIndex, "PragmaticStates"), []):
                link(u, o["key"])
        elif EventCategory == "ComposedPromptEvent":
            si = EventDict.get("source_state_idx")
            if isinstance(si, int) and si >= 0:
                for o in by_pos.get((si, "PragmaticStates"), []):
                    link(u, o["key"])
        elif EventCategory == "UtteranceEvent" and EventDict.get("role") == "assistant":
            src = EventDict.get("source_refresh_idx")
            if isinstance(src, int) and src >= 0:
                for o in by_pos.get((src, "ComposedPromptEvent"), []):
                    link(u, o["key"])
    return units


# ---- the merged order of the events and the turn clusters ----

# Order of events that share one refresh index: the utterance, then the analyzers that analyzed
# it, then the memories and state they produced, then the composed prompt.
_CATEGORY_RANK = {"ConversationInit": 0, "UtteranceEvent": 1, "InterruptedUtteranceEvent": 1,
                  "AnalyzerEvent": 2, "MemoryEvent": 3, "PragmaticStates": 4,
                  "TransitionCriteriaEvent": 4, "ConversationStateEvent": 5,
                  "ManualPromptChangeEvent": 6, "ComposedPromptEvent": 7}


def merged_events(streams: dict) -> list:
    """Return every event of ``streams`` except the stored flow as one list of triples, the refresh index, the category
    and the event dict, sorted by refresh index and then by the category's rank in ``_CATEGORY_RANK``, which puts an
    utterance before the analyzers that read it and those before what they produced. Called only by ``TurnClusters`` in
    this module."""
    merged = []
    for EventCategory, events in (streams or {}).items():
        if EventCategory == "ConversationInit":
            continue
        for EventDict in events or []:
            merged.append((EventDict.get("event_refresh_idx", -1),
                           _CATEGORY_RANK.get(EventCategory, 9), EventCategory, EventDict))
    merged.sort(key=lambda entry: (entry[0], entry[1]))
    return [(RefreshIndex, EventCategory, EventDict) for RefreshIndex, _rank, EventCategory, EventDict in merged]


def TurnClusters(streams: dict) -> list[dict]:
    """Return the conversation in ``streams`` as a list of clusters, one per user utterance after an opening cluster
    for everything before the first, each cluster a dict with ``anchor_idx``, the user utterance's refresh index or
    ``None`` for the opening, and ``events``, a list of dicts with ``idx``, ``category`` and ``event``.

    Analyzer events recorded while the user was still speaking, whose ``analyzed_utterance_idx`` is ``-1``, are moved
    from the end of the previous cluster into the cluster of the utterance they were spoken in. A composed prompt's entry
    also has ``spoken``, false when no assistant utterance was written from it. Empty clusters are left out.
    """
    merged = merged_events(streams)
    spoken_sources = {EventDict.get("source_refresh_idx")
                      for _i, EventCategory, EventDict in merged
                      if EventCategory == "UtteranceEvent" and EventDict.get("role") == "assistant"}
    clusters: list[dict] = [{"anchor_idx": None, "events": []}]
    for RefreshIndex, EventCategory, EventDict in merged:
        is_user = EventCategory == "UtteranceEvent" and EventDict.get("role") == "user"
        if is_user:
            # The trailing incremental phrase results of the previous cluster belong to this utterance.
            ticks = []
            previous = clusters[-1]["events"]
            while previous and previous[-1][1] == "AnalyzerEvent" \
                    and previous[-1][2].get("analyzed_utterance_idx") == -1:
                ticks.insert(0, previous.pop())
            clusters.append({"anchor_idx": RefreshIndex, "events": ticks})
        entry = (RefreshIndex, EventCategory, EventDict)
        clusters[-1]["events"].append(entry)
    out = []
    for cluster in clusters:
        events = [{"idx": RefreshIndex, "category": EventCategory, "event": EventDict,
                   **({"spoken": EventDict.get("event_refresh_idx") in spoken_sources}
                      if EventCategory == "ComposedPromptEvent" else {})}
                  for RefreshIndex, EventCategory, EventDict in cluster["events"]]
        if events:
            out.append({"anchor_idx": cluster["anchor_idx"], "events": events})
    return out


# ---- the saved utterances ----


def turns(SessionProvider: Any) -> list[dict]:
    """Return what ``SessionProvider.ConversationHistoryTurns`` returns for ``SessionProvider``, every saved utterance
    in order as a dict with ``role``, ``text`` and ``truncated``."""
    return SessionProvider.ConversationHistoryTurns()
