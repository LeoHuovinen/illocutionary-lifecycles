"""One of the four transition criteria in ``illocutionary_lifecycles/analyzers/transition_analyzers``, registered as
``QuestionsAnsweredConversationStateTransitionCriteria``, which reports that the conversation may leave its state
through one entry of the state's ``ConversationStateTransitionCriteria`` list when no question of the state is left
open.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and keeps the questions of each state outside the model, so the end of a
state's questions is noticed here rather than by the model. This criterion sits in the folder ``analyzers``, the
folder ``core`` calls it after each user turn, the folder ``memory`` records its result, and the folder ``server``
tells a connected page or app when the state changes.

The four criteria replace each other by registered name, one chosen for each entry of a state's criteria list.
``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs this one in the second pass, after the first
pass has run the question checker and the refresher has removed the questions it found answered, so a question
answered by the current utterance already counts.

The criterion reads only the pragmatic state's ``pConversationStateRemainingQuestions``, a list that
``illocutionary_lifecycles.core.system_state.system_state.SystemState.EstablishConversationState`` creates from the
state's ``questions`` when the state's criteria list names this criterion and that
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` shortens, and reads no utterance, calls no model
and writes nothing. A state whose ``questions`` list is empty is left on the first turn through an entry naming this
criterion.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.analyzers.AnalyzerBase import AnalysisResult, register


AnalyzerType = "QuestionsAnsweredConversationStateTransitionCriteria"   # the registered name: flows, records and the cycle's suffix checks use it; the file and function are QuestionsAnsweredTransitionAnalyzer


@register(AnalyzerType)
async def QuestionsAnsweredTransitionAnalyzer(
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int = -1,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` whose value is a dict with the one key ``done``, true when
    ``pConversationStateRemainingQuestions`` on ``PragmaticState`` is missing or empty, together with the entry's
    position ``WithinConversationStateOrdinal`` as the cycle passed it. ``UserMemoryFace`` and ``WindowFace`` are
    accepted because every criterion is called with them and are not used.

    This function is how a state of the flow is left once all its questions are answered, called by the cycle in the
    folder ``core``, as the module docstring above explains.
    """
    done = len(getattr(PragmaticState, "pConversationStateRemainingQuestions", []) or []) == 0
    answer = {"done": done}
    return AnalysisResult(value=answer, AnalyzerType=AnalyzerType,
                          WithinConversationStateOrdinal=WithinConversationStateOrdinal)
