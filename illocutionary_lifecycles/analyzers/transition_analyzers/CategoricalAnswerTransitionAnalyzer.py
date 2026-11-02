"""One of the four transition criteria in ``illocutionary_lifecycles/analyzers/transition_analyzers``, registered as
``CategoricalAnswerConversationStateTransitionCriteria``, which reports that the conversation may leave its state
through one entry of the state's ``ConversationStateTransitionCriteria`` list when the user's recorded choice equals
that entry's ``Prompt``.

The package leads a conversation between a user and a language model through the states of a flow written in advance,
with the questions of each state checked outside the model and the move to the next state chosen by small functions
rather than by the model. This module holds one of those functions, in the folder ``analyzers``, called by the
folder ``core`` after each user turn, with its result recorded by the folder ``memory`` and a move it allows sent by the
folder ``server`` to a connected page or app.

The four criteria replace each other by registered name. A flow picks one for each entry of a state's criteria list,
and ``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs this one in the second pass once for every
entry that names it, passing the entry's position. With this criterion an answer to a question with options sets which
state comes next, because each entry names one option as its ``Prompt`` and its own ``TargetConversationState``.

The criterion reads only the pragmatic state. The option of the entry comes from ``pConversationStateTransitionCriteriaListState``
at the entry's position, and the options chosen so far in this state come from ``pCategoricalAnswerState``. That field
is written by ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` from the ``choice`` the question
checker, ``illocutionary_lifecycles.analyzers.answer_analyzers.QuestionAnsweredAnalyzer``, returned in the first pass of
the same turn, and the refresher deletes it when the conversation leaves the state. This criterion reads no utterance,
calls no model and writes nothing.

``pCategoricalAnswerState`` is read here, written only by the refresher, and named as an allowed prompt blank in
``illocutionary_lifecycles.core.system_state.system_state.SystemState._KnownBlanks``. Nothing checks the name at
start-up, so a rename of the field in one of these modules breaks this criterion without an error. A state that uses this criterion is a
state with questions, because ``illocutionary_lifecycles.core.system_state.system_state.SystemState.EstablishConversationState``
sets up the open questions when a state's criteria list names it.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.analyzers.AnalyzerBase import AnalysisResult, register


AnalyzerType = "CategoricalAnswerConversationStateTransitionCriteria"   # the registered name: flows, records and the cycle's suffix checks use it; the file and function are CategoricalAnswerTransitionAnalyzer


@register(AnalyzerType)
async def CategoricalAnswerTransitionAnalyzer(
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int = -1,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` whose value is a dict with the one key ``done``, true when the ``Prompt`` of the
    criteria entry at ``WithinConversationStateOrdinal`` is non-empty and is among the options in
    ``pCategoricalAnswerState``, and false otherwise.

    This is the step at which a user's choice between options sends a conversation to one next state of the flow
    rather than another, as the module docstring above explains. The function sits in the folder ``analyzers``, the cycle in the folder ``core`` calls it
    in the second pass of a turn, and the refresher in the same folder moves the conversation when it returns true.

    ``PragmaticState`` is the session's pragmatic state, read for ``pConversationStateTransitionCriteriaListState`` and
    ``pCategoricalAnswerState``. ``WithinConversationStateOrdinal`` is the entry's position in the state's criteria
    list, passed by the cycle, and a position outside the list gives an empty option and so a false ``done``.
    ``UserMemoryFace`` and ``WindowFace`` are accepted because every criterion is called with them and are not used.
    The result carries the same position, which the refresher uses to pick the entry whose ``TargetConversationState`` is entered.
    """
    _SeededEntries = getattr(PragmaticState, "pConversationStateTransitionCriteriaListState", None)
    if _SeededEntries is not None and 0 <= WithinConversationStateOrdinal < len(_SeededEntries):
        option = str((_SeededEntries[WithinConversationStateOrdinal] or {}).get("Prompt") or "")
    else:
        option = ""
    chosen = list(getattr(PragmaticState, "pCategoricalAnswerState", None) or [])
    done = bool(option) and option in chosen
    return AnalysisResult(value={"done": done}, AnalyzerType=AnalyzerType,
                          WithinConversationStateOrdinal=WithinConversationStateOrdinal)
