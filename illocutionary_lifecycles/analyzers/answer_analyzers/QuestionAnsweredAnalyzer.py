"""The question checker, the one analyzer in ``illocutionary_lifecycles/analyzers/answer_analyzers``, registered as
``QuestionCompleteCriteria`` by the function ``QuestionAnsweredAnalyzer``, which reports whether one open question of
the current state was answered in the state's utterances and gives the answer as a sentence.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and keeps each state's questions outside the model, so this checker, not
the model that writes the replies, is what says a question is answered. The checker sits in the folder ``analyzers``
and is called by the folder ``core``, which runs the conversation, while the folder ``memory`` records its results and
the folder ``server`` sends each answered question to a connected page or app.

``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs it in the first pass of every turn, once for
each question in the pragmatic state's ``pConversationStateRemainingQuestions``, passing the question's position in
that list, because its registered name ends in ``QuestionCompleteCriteria``. The question checker is not one of the
transition criteria and has no replacement in the package. Each run sends one prompt through ``QuestionAnsweredAnalyzerLLMCall`` to the
client ``illocutionary_lifecycles.core.clients.llm.analyzer_llm`` returns, using that client's ``complete_json``, and
returns whether the question was answered, the answer sentence and, for a question with options, the chosen option.

The checker reads the pragmatic state and the current state's utterances, which the cycle passes as ``WindowFace``,
built from ``illocutionary_lifecycles.core.system_state.conversation_history_window.ConversationStateWindow``, the same
utterances the composer shows, and writes nothing. ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` removes an
answered question from ``pConversationStateRemainingQuestions`` and adds a chosen option to ``pCategoricalAnswerState``,
and ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter`` saves a non-empty answer sentence as a
``MemoryEvent``. ``illocutionary_lifecycles.memory.MemoryReadTools.AnsweredQuestionFactsTool.AnsweredQuestionFacts``
reads the answered results back for the question-answered adapter callback. These readers depend on the keys
``answered``, ``answer`` and ``choice`` of the value, so a change to those keys breaks them at run time.

The answer sentence states what the user said in response to which question, and never a preference or intention
inferred from it. The prompt text that asks for this is in the module constants ``PROMPT``, ``OPTIONS_PROMPT``,
``PERMISSIVE_PROMPT`` and ``PERMISSIVE_OPTIONS_PROMPT``, which are model text; the analyzer's results depend on their wording.
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader._static_prompt_for`` shows ``PROMPT`` on a
card when a result carries no prompt.

Once the state's turn count ``pConversationStateTurnCountState`` reaches ``pConversationStatePermissiveThresholdState``,
the checker stops waiting for a real answer. A question without options is then recorded as answered with whatever the
user said, including that the user avoided it, and a question with options is given the option that fits best.
``illocutionary_lifecycles.core.system_state.system_state.SystemState.EstablishConversationState`` sets the threshold
from the state's ``permissive_after_turns`` or, when that is missing, to the number of the state's questions plus one.
The module constant ``PERMISSIVE_AFTER_CONVERSATION_STATE_TURNS``, which is 4, is used only when the field is missing.
A model call that raises, or a reply that cannot be read, counts as not answered.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.analyzers.AnalyzerBase import AnalysisResult, register


# The name this analyzer is registered under.
AnalyzerType = "QuestionCompleteCriteria"   # the registered name: flows, records and the cycle's suffix checks use it; the file and function are QuestionAnsweredAnalyzer

# The analyzing prompt below the permissive threshold.
PROMPT = (
    "You are checking ONE question. Read the conversation of THIS section below and decide: "
    "DID THE USER PROVIDE AN ANSWER TO THIS QUESTION anywhere in this conversation? An answer means the "
    "user actually gave the information the question asks for — not a deflection ('I don't know'), not a "
    "vague filler ('it's nice', 'it's cool'), not silence.\n"
    "If the question asks WHAT KIND or WHAT TYPE of something, then a SINGLE ADJECTIVE or short noun "
    "phrase IS a complete answer. Do NOT require a full sentence or elaboration from the user; mark "
    "answered = true and record what they said.\n"
    "If they did, write the answer as a PRAGMATIC EVENT: a single complete sentence, AT LEAST 10 WORDS, "
    "that states WHAT THE USER RESPONDED TO WHICH QUESTION. Frame it as the act of responding — "
    "'The user responded ... when asked ...' / 'When asked ..., the user said ...' — NOT as an inferred "
    "trait or preference. Do NOT write 'the user likes X' or 'the person prefers X' (that is an "
    "inference); write 'the user responded that X when asked about Y'. No quotes, no transcripts, no raw words.\n"
    "Example: question 'Pizza or burger?', user says 'uh pizza I guess' → "
    "'When asked whether they want pizza or a burger, the user responded that they want pizza.'"
)

# The threshold, in user turns, used when the state carries none.
PERMISSIVE_AFTER_CONVERSATION_STATE_TURNS = 4
# The analyzing prompt for a question without options once the threshold is reached. It records
# whatever the user said, so a user who keeps avoiding the question does not hold the state open.
PERMISSIVE_PROMPT ="You are recording ONE question. The assistant ATTEMPTED to ask this question (possibly rephrased or woven into the conversation) and this section has already run for several turns, so we now RECORD an answer and MOVE ON regardless of how the user responded. Set answered = true. Read the conversation of THIS section below and write the answer as a PRAGMATIC EVENT: a single complete sentence, AT LEAST 10 WORDS, framed as the act of responding ('When asked ..., the user responded that ...'), NOT as an inferred trait. If the user actually gave a preference, summarise it. If the user STALLED, was EVASIVE, joked, deflected, or declined to give a real preference, then RECORD EXACTLY THAT — e.g. 'When asked whether they want pizza or a burger, the user joked instead of choosing one.' Either way answered = true. Do NOT invent a preference the user never stated; if they dodged, the recorded answer is that they dodged. No quotes, no raw fragments."
# Added for a question with options once the threshold is reached. The choice must still be one
# of the options.
PERMISSIVE_OPTIONS_PROMPT =" NOTE: this section has run for several turns and the user keeps stalling on this category question. You MUST now COMMIT to exactly ONE of the options — pick the option that best fits everything the user has said so far, inferring from their tone and any hints even if they never named it outright. You may NOT leave the choice empty; a category answer must always be one of the listed options."

# Added after ``PROMPT`` for a question with options. It asks for one of the options as ``choice``.
OPTIONS_PROMPT =" This question is a CATEGORY question: the user's answer selects exactly ONE of a fixed set of OPTIONS. In ADDITION to the judgement above, decide WHICH single option the user's answer selects. Choose the one option whose meaning best matches what the user actually said; judge by the real answer, not by word order or which option words appear. If the user did not answer, the choice is an empty string. THE OPTIONS ARE: {options_block}"

from illocutionary_lifecycles.core.clients.llm import analyzer_llm


def ConversationStateText(WindowFace: Callable[..., Any]) -> str:
    """Return the utterances ``WindowFace`` returns as one line each, the role, then a colon, then the
    text, skipping utterances without text, for the prompt ``QuestionAnsweredAnalyzerLLMCall`` builds. ``WindowFace``
    is the callable the cycle passes, which returns the current state's utterances, the same utterances the composer
    shows, so the checker reads what the model that wrote the replies was shown. Called only by
    ``QuestionAnsweredAnalyzerLLMCall`` in this module.
    """
    return "\n".join(
        f"{getattr(v, 'role', '')}: {getattr(v, 'transcription', '')}"
        for v in WindowFace() if getattr(v, "transcription", "")
    )


async def QuestionAnsweredAnalyzerLLMCall(
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int,
    *,
    WithIncrementalPhraseContext: bool = True,
) -> tuple[dict, str]:
    """Return a pair, the value dict and the prompt sent to the model, for the question at
    ``WithinConversationStateOrdinal`` in ``pConversationStateRemainingQuestions`` on ``PragmaticState``. This is the
    one model call per question, and only ``QuestionAnsweredAnalyzer`` in this module calls it.

    The value has ``answered``, a bool, and ``answer``, the sentence or an empty string, and for a question with options
    also ``choice``, one of the options or an empty string. A question is a string, or a dict with ``question`` and
    ``options``. When the position names no question, no model is called, the prompt is empty and nothing counts as
    answered. ``WindowFace`` is the callable that returns the current state's utterances. When
    ``WithIncrementalPhraseContext`` is true, which is the default, every pragmatic field whose name starts with p, ends
    with State, contains ``IncrementalPhrase`` and holds a dict is added to the prompt as context, with an instruction
    that the full utterance counts and the context does not. The prompt chosen depends on whether the state's turn
    count has reached ``pConversationStatePermissiveThresholdState`` and on whether the question has options. The
    model's ``choice`` is matched to an option after removing case, spaces and punctuation from both, and a choice that
    matches no option sets ``answered`` to false. Any error from the model call gives a not answered value and is not
    raised.
    """
    questions = list(getattr(PragmaticState, "pConversationStateRemainingQuestions", None) or [])
    answered = False
    answer_text = ""
    choice = ""
    options: list = []
    prompt = ""
    if 0 <= WithinConversationStateOrdinal < len(questions):
        entry = questions[WithinConversationStateOrdinal]
        # A question is a string, or ``{"question", "options"}`` when it has options.
        if isinstance(entry, dict):
            question = str(entry.get("question", ""))
            opts = entry.get("options")
            options = [str(o) for o in opts] if isinstance(opts, (list, tuple)) else []
        else:
            question = entry
        convo = ConversationStateText(WindowFace)
        # What the incremental phrase analyzers analyzed while the user was still speaking is added as
        # context. The result made here, on the whole utterance, is the one that counts.
        if WithIncrementalPhraseContext:
            IncrementalFields = {
                FieldName: FieldValue for FieldName, FieldValue in vars(PragmaticState).items()
                if FieldName.startswith("p") and FieldName.endswith("State")
                and "IncrementalPhrase" in FieldName and isinstance(FieldValue, dict)
            }
            if IncrementalFields:
                convo += (
                    "\n\nINCREMENTAL RESPONSE FROM THE PARTIAL UTTERANCE (a smaller, faster judge ran "
                    f"while the user was still speaking; it may be wrong): {IncrementalFields}"
                    "\nJudge from the FULL conversation above — the incremental phrase is context, "
                    "never authority."
                )
        # The state's own threshold is set when the state is entered.
        try:
            conversation_state_turns = int(getattr(PragmaticState, "pConversationStateTurnCountState", 0) or 0)
        except (TypeError, ValueError):
            conversation_state_turns = 0
        try:
            _threshold = int(getattr(PragmaticState, "pConversationStatePermissiveThresholdState",
                                     PERMISSIVE_AFTER_CONVERSATION_STATE_TURNS))
        except (TypeError, ValueError):
            _threshold = PERMISSIVE_AFTER_CONVERSATION_STATE_TURNS
        permissive = conversation_state_turns >= _threshold
        if options:
            options_block = "; ".join(str(o) for o in options)
            if permissive:
                extra_prompt = PROMPT + OPTIONS_PROMPT.format(options_block=options_block) + PERMISSIVE_OPTIONS_PROMPT
                json_instruction = 'Return ONLY JSON: {"answered": true, "answer": "<a pragmatic-event sentence of at least 10 words stating what the user responded to (or that they were evasive about) which question>", "choice": "<EXACTLY ONE of the options listed above, copied verbatim — you MUST pick the best-fit option, never an empty string>"}'
            else:
                extra_prompt = PROMPT + OPTIONS_PROMPT.format(options_block=options_block)
                json_instruction = 'Return ONLY JSON: {"answered": true or false, "answer": "<a pragmatic-event sentence of at least 10 words stating what the user responded to which question, or empty string if they did not answer>", "choice": "<EXACTLY ONE of the options listed above, copied verbatim, or empty string if they did not answer>"}'
            prompt = (
                f"{extra_prompt}\n\nTHE QUESTION: {question!r}\n\n"
                f"CONVERSATION (this section only):\n{convo}\n\n{json_instruction}"
            )
        else:
            base_prompt = PERMISSIVE_PROMPT if permissive else PROMPT
            prompt = (
                f"{base_prompt}\n\nTHE QUESTION: {question!r}\n\n"
                f"CONVERSATION (this section only):\n{convo}\n\n"
                'Return ONLY JSON: {"answered": true or false, "answer": "<a pragmatic-event sentence of at '
                'least 10 words stating what the user responded to (or that they were evasive about) which '
                'question, or empty string if not applicable>"}'
            )
        try:
            analyzed = await analyzer_llm().complete_json(prompt)
            answered = bool(analyzed.get("answered"))
            answer_text = str(analyzed.get("answer") or "")
            if options:
                # The model's choice is matched to an option ignoring case, spaces and
                # punctuation. A choice that matches no option leaves the question unanswered.
                def _norm(s: str) -> str:
                    """Return ``s`` in lower case with everything that is not a letter or digit removed, for
                    matching the model's choice in ``QuestionAnsweredAnalyzerLLMCall`` above."""
                    return "".join(c for c in str(s).lower() if c.isalnum())
                by_key = {_norm(o): o for o in options}
                picked = str(analyzed.get("choice") or "")
                canonical = by_key.get(_norm(picked))
                if canonical is not None:
                    choice = canonical
                else:
                    choice = ""
                    answered = False
        except Exception:
            answered, answer_text, choice = False, "", ""
    value: dict = {"answered": answered, "answer": answer_text}
    if options:
        value["choice"] = choice
    return value, prompt


@register(AnalyzerType)
async def QuestionAnsweredAnalyzer(
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    PragmaticState: Any,
    WithinConversationStateOrdinal: int = -1,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` for the question at ``WithinConversationStateOrdinal`` in
    ``pConversationStateRemainingQuestions``, whose value has ``answered`` and ``answer`` and, for a question with
    options, ``choice``, one of the options or an empty string, together with the prompt sent and the question's
    position.

    This is the function registered as ``QuestionCompleteCriteria``, which the cycle in the folder ``core`` calls once
    per open question on every turn, as the module docstring above explains. ``WindowFace`` is the callable that
    returns the current state's utterances, ``PragmaticState`` is the session's pragmatic state, read and not
    changed, and ``WithinConversationStateOrdinal`` is the question's position, passed by the cycle. ``UserMemoryFace``
    is accepted because the cycle passes it to every analyzer and is not used. The model call itself is
    ``QuestionAnsweredAnalyzerLLMCall`` in this module.
    """
    value, prompt = await QuestionAnsweredAnalyzerLLMCall(WindowFace, PragmaticState, WithinConversationStateOrdinal)
    return AnalysisResult(
        value=value,
        AnalyzerType=AnalyzerType,
        WithinConversationStateOrdinal=WithinConversationStateOrdinal,
        prompt=prompt,
    )
