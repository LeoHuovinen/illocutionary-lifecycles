"""The refresher, ``refresh``, the one function that updates the pragmatic state from analyzer results and moves the
conversation to another state when a transition criterion reports done.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the analyzers of the folder ``analyzers`` only return results, so
this function, in the folder ``core``, is where those results take effect on the values the next prompt is composed
from. The cycles in ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` call it after every pass and after every
incremental pick, through the pragmatic state's ``Refresher`` field. The values it updates are saved by the caller to
the record of the folder ``memory``, and the folder ``server`` learns of a move it made from the adapter callback the
session sends after that save.

The function does its work in a fixed order. First it keeps every incremental result whose registered name contains
``IncrementalPhrase`` on the field named p, then that name, then State, under the instance identifier. Then, when the
caller asks, it raises the turn count ``pConversationStateTurnCountState`` by one. Then it removes each question the
question checker reported answered from ``pConversationStateRemainingQuestions``, by position, and adds a reported
``choice`` to ``pCategoricalAnswerState``. Last, when listed transition criteria report done, it moves the
conversation to the ``TargetConversationState`` of the lowest-positioned of their entries through
``illocutionary_lifecycles.core.system_state.system_state.SystemState.set_current_conversation_state``, at most one
move per call, and deletes ``pCategoricalAnswerState``, whose choices belong to the state just left.

The refresher reads which result is which from the endings of the registered names and from the result keys
``answered``, ``choice``, ``done`` and ``WithinConversationStateOrdinal``, so a rename of a registered name or a key in
the folder ``analyzers`` breaks it at run time. The refresher never reads what the user said and saves nothing, and its
caller saves the refreshed values through ``SystemState.SaveRefreshResult``.
"""
from __future__ import annotations

from typing import Any


def refresh(
    SystemState: Any,
    *,
    analyzer_results: dict[str, Any] | None = None,
    TurnCounter: bool = True,
) -> dict[str, Any]:
    """Update the pragmatic state of ``SystemState`` from one set of analyzer results in the order the module
    docstring above lays out, and return a dict whose one key ``ConversationStateAdvanced`` holds whether this call
    moved the conversation to another state, false when the session has no pragmatic state.

    ``analyzer_results`` is the dict of results by result key, each result a dict with ``success``, ``value``,
    ``AnalyzerType``, ``AnalyzerId`` and, for a question checker or a listed criterion,
    ``WithinConversationStateOrdinal``, and a result without a true ``success`` is skipped. ``TurnCounter`` is whether
    this call counts a user turn, and a caller that refreshes more than once for one utterance passes false on the later
    calls, as the second pass and the incremental settle do. A move to the current state itself raises the
    ``ValueError`` of ``SystemState.set_current_conversation_state``.
    """
    PragmaticState = getattr(SystemState, "PragmaticState", None)
    if PragmaticState is None:
        return {"ConversationStateAdvanced": False}
    results = analyzer_results or {}

    # A result from an incremental phrase analyzer, one whose name contains ``IncrementalPhrase``,
    # is kept in that analyzer's own field,
    # ``p<AnalyzerType>State``, under its instance name, for the question checker to read as
    # context.
    for entry in results.values():
        if not isinstance(entry, dict) or not entry.get("success"):
            continue
        IncrementalAnalyzerType = str(entry.get("AnalyzerType", "") or "")
        IncrementalValue = entry.get("value")
        if "IncrementalPhrase" not in IncrementalAnalyzerType or not isinstance(IncrementalValue, dict):
            continue
        if IncrementalAnalyzerType:
            IncrementalFieldName = f"p{IncrementalAnalyzerType}State"
            IncrementalField = dict(getattr(PragmaticState, IncrementalFieldName, {}) or {})
            IncrementalField[str(entry.get("AnalyzerId") or IncrementalAnalyzerType)] = \
                dict(IncrementalValue)
            setattr(PragmaticState, IncrementalFieldName, IncrementalField)

    if TurnCounter:
        PragmaticState.pConversationStateTurnCountState += 1

    # An answered question is removed by its position among the remaining questions. Positions
    # are removed from the highest down, so that the positions still to remove stay valid.
    remaining = getattr(PragmaticState, "pConversationStateRemainingQuestions", None)
    if remaining is not None:
        answered_ordinals = []
        for entry in (results or {}).values():
            if not isinstance(entry, dict) or not entry.get("success"):
                continue
            # An analyzer whose name ends in "QuestionCompleteCriteria" is a question checker.
            if not str(entry.get("AnalyzerType", "")).endswith("QuestionCompleteCriteria"):
                continue
            answer = entry.get("value") or {}
            ordinal = entry.get("WithinConversationStateOrdinal")
            if answer.get("answered") and isinstance(ordinal, int) and 0 <= ordinal < len(remaining):
                answered_ordinals.append(ordinal)
                # The chosen option is recorded for the CategoricalAnswer transition criterion.
                _Choice = str(answer.get("choice") or "")
                if _Choice:
                    _Chosen = list(getattr(PragmaticState, "pCategoricalAnswerState", None) or [])
                    if _Choice not in _Chosen:
                        _Chosen.append(_Choice)
                    PragmaticState.pCategoricalAnswerState = _Chosen
        for ordinal in sorted(set(answered_ordinals), reverse=True):
            del remaining[ordinal]

    # The transition criteria that report done. A criterion from a state's ordered list carries
    # its position in the list, and the lowest position wins. The conversation then moves to
    # that entry's ``TargetConversationState``. At most one move happens per call.
    ConversationStateAdvanced = False
    PrioritizedDoneOrdinals: list = []
    for entry in (results or {}).values():
        if not isinstance(entry, dict) or not entry.get("success"):
            continue
        answer = entry.get("value") or {}
        if not (isinstance(answer, dict) and answer.get("done")):
            continue
        if not str(entry.get("AnalyzerType", "")).endswith("ConversationStateTransitionCriteria"):
            continue
        ordinal = entry.get("WithinConversationStateOrdinal")
        if isinstance(ordinal, int) and ordinal >= 0:
            PrioritizedDoneOrdinals.append(ordinal)
    if PrioritizedDoneOrdinals:
        current = SystemState.current_conversation_state()
        declared = (current.get("ConversationStateTransitionCriteria")
                    if isinstance(current, dict) else None) or []
        winner = min(PrioritizedDoneOrdinals)
        target = (declared[winner] or {}).get("TargetConversationState") if 0 <= winner < len(declared) else None
        if target is not None:
            ConversationStateAdvanced = bool(SystemState.set_current_conversation_state(target))
            # The recorded choices belong to the state just left.
            if ConversationStateAdvanced and hasattr(PragmaticState, "pCategoricalAnswerState"):
                del PragmaticState.pCategoricalAnswerState
    return {"ConversationStateAdvanced": ConversationStateAdvanced}
