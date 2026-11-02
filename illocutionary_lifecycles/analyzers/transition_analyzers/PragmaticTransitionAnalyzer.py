"""One of the four transition criteria in ``illocutionary_lifecycles/analyzers/transition_analyzers``, registered as
``PragmaticConversationStateTransitionCriteria``, and the only one of the four that calls a language model. This criterion reports
that the conversation may leave its state through one entry of the state's ``ConversationStateTransitionCriteria``
list when the condition written as that entry's ``Prompt`` holds for the current state's utterances.

The package moves a conversation between a user and a language model through the states of a flow written in advance,
and the move is chosen by small functions such as this one rather than by the model that writes the replies. This
criterion sits in the folder ``analyzers``, the folder ``core`` calls it after each user turn, the folder ``memory``
records its result, and the folder ``server`` tells a connected page or app when the state changes.

The four criteria replace each other by registered name, one chosen for each entry of a state's criteria list.
``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs this one in the second pass once for every
entry that names it, passing the entry's position. The condition is a sentence the flow's author wrote, for example
"the user has said goodbye".

The criterion reads the entry's ``Prompt`` from the pragmatic state's ``pConversationStateTransitionCriteriaListState``
and the current state's utterances through ``WindowFace``, which the cycle builds from
``illocutionary_lifecycles.core.system_state.conversation_history_window.ConversationStateWindow``, and sends one prompt
to the client ``illocutionary_lifecycles.core.clients.llm.analyzer_llm`` returns, through that client's
``complete_json``, and writes nothing. The prompt begins with the constant ``PROMPT`` of this module, which is model
text, also shown on the cards by
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader._static_prompt_for`` when a result carries
no prompt.

A model reply that cannot be read, or a model call that raises, gives a false ``done``, so the state is not left on
that turn and the next turn is analyzed again. A model call longer than the cycle's
``illocutionary_lifecycles.core.turn_taking.sync_cycle.AnalyzerLLMCallTimeout`` is dropped by the cycle and changes
nothing.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.analyzers.AnalyzerBase import AnalysisResult, register
from illocutionary_lifecycles.core.clients.llm import analyzer_llm


AnalyzerType = "PragmaticConversationStateTransitionCriteria"   # the registered name: flows, records and the cycle's suffix checks use it; the file and function are PragmaticTransitionAnalyzer
PROMPT = "Given the conversation, is this section complete? Return JSON."


@register(AnalyzerType)
async def PragmaticTransitionAnalyzer(
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int = -1,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` whose value is a dict with the one key ``done``, true when the model answered
    that the condition holds, together with the prompt that was sent and the entry's position.

    This function is the one criterion in the folder ``analyzers`` that asks a model, called by the cycle in the folder
    ``core`` in the second pass of a turn, as the module docstring above explains.

    ``WindowFace`` is the callable that returns the current state's utterances, and each utterance with text becomes
    one line of the prompt. When it returns no utterance with text, no model is called, the prompt is empty and
    ``done`` is false. ``PragmaticState`` is read for ``pConversationStateTransitionCriteriaListState``, and the
    ``Prompt`` of the entry at ``WithinConversationStateOrdinal`` is the condition, empty when the position is outside
    the list. ``UserMemoryFace`` is accepted because every criterion is called with it and is not used. Any error from
    the model call gives a false ``done`` and is not raised.
    """
    window = [view.transcription for view in WindowFace() if getattr(view, "transcription", "")]
    _SeededEntries = getattr(PragmaticState, "pConversationStateTransitionCriteriaListState", None)
    hint = ""
    if _SeededEntries is not None and 0 <= WithinConversationStateOrdinal < len(_SeededEntries):
        hint = str((_SeededEntries[WithinConversationStateOrdinal] or {}).get("Prompt") or "")
    done = False
    prompt = ""
    if window:
        prompt = (
            f"{PROMPT}\nCompletion condition for this section: {hint!r}\n"
            f"Recent conversation:\n" + "\n".join(window) +
            '\nReturn ONLY JSON: {"done": true or false}'
        )
        try:
            analyzed = await analyzer_llm().complete_json(prompt)
            done = bool(analyzed.get("done"))
        except Exception:
            done = False
    # The prompt is returned so that the recorded result can be explained afterwards.
    return AnalysisResult(value={"done": done}, AnalyzerType=AnalyzerType, prompt=prompt,
                          WithinConversationStateOrdinal=WithinConversationStateOrdinal)
