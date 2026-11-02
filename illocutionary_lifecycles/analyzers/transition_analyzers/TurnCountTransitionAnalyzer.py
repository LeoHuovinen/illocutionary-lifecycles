"""One of the four transition criteria in ``illocutionary_lifecycles/analyzers/transition_analyzers``, registered as
``TurnCountConversationStateTransitionCriteria``, which reports that the conversation may leave its state through one
entry of the state's ``ConversationStateTransitionCriteria`` list once the state has had the number of user turns
written as that entry's ``Prompt``.

The package moves a conversation between a user and a language model through the states of a flow written in advance,
and this criterion lets a flow's author leave a state after a set number of turns whatever was said. The criterion sits
in the folder ``analyzers``, the folder ``core`` calls it after each user turn, the folder ``memory`` records its
result, and the folder ``server`` tells a connected page or app when the state changes.

The four criteria replace each other by registered name, one chosen for each entry of a state's criteria list.
``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs this one in the second pass once for every
entry that names it, passing the entry's position.

The criterion reads only the pragmatic state, the entry's ``Prompt`` from ``pConversationStateTransitionCriteriaListState`` and
the count ``pConversationStateTurnCountState``. That count is set to zero by
``illocutionary_lifecycles.core.system_state.system_state.SystemState.EstablishConversationState`` when the state is
entered and raised by one by ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` after the first pass
of every turn. The criterion reads no utterance, calls no model and writes nothing. When the ``Prompt`` is missing, empty or not an
integer, the number is the module constant ``CONVERSATION_STATE_TURNS``, which is 2.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.analyzers.AnalyzerBase import AnalysisResult, register


AnalyzerType = "TurnCountConversationStateTransitionCriteria"   # the registered name: flows, records and the cycle's suffix checks use it; the file and function are TurnCountTransitionAnalyzer
# The number of turns used when the state gives none.
CONVERSATION_STATE_TURNS = 2


@register(AnalyzerType)
async def TurnCountTransitionAnalyzer(
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int = -1,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` whose value is a dict with the one key ``done``, true when
    ``pConversationStateTurnCountState`` on ``PragmaticState`` is at least the entry's number, together with the
    entry's position ``WithinConversationStateOrdinal`` as the cycle passed it.

    This function is called by the cycle in the folder ``core`` in the second pass of a turn, as the module docstring
    above explains.

    The number is the ``Prompt`` of the criteria entry at ``WithinConversationStateOrdinal``, written as an integer
    string such as "3". The criteria run in the second pass, after the refresh that counts the current user turn, so
    the count already includes this turn, and a number of 1 leaves the state on its first user utterance.
    ``UserMemoryFace`` and ``WindowFace`` are accepted because every criterion is called with them and are not used.
    """
    _Threshold = CONVERSATION_STATE_TURNS
    _SeededEntries = getattr(PragmaticState, "pConversationStateTransitionCriteriaListState", None)
    _Declared = None
    if _SeededEntries is not None and 0 <= WithinConversationStateOrdinal < len(_SeededEntries):
        _Declared = (_SeededEntries[WithinConversationStateOrdinal] or {}).get("Prompt")
    try:
        if _Declared is not None and str(_Declared).strip():
            _Threshold = int(str(_Declared).strip())
    except (TypeError, ValueError):
        _Threshold = CONVERSATION_STATE_TURNS
    done = getattr(PragmaticState, "pConversationStateTurnCountState", 0) >= _Threshold
    return AnalysisResult(value={"done": done}, AnalyzerType=AnalyzerType,
                          WithinConversationStateOrdinal=WithinConversationStateOrdinal)
