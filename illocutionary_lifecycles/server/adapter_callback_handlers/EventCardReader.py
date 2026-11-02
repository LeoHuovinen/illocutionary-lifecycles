"""The wording of the cards a person reads about a session, one card per recorded event and one per analyzer result,
with three hand-kept tables that name and explain the analyzers.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record, kept by the folder ``memory``, is what a flow's author
reads afterwards to see what happened and why. This module, in the folder ``server``, turns that
record into card text, with question wording from the flow, choices and remembered answers, and without field names or
indexes, while the units and their links come from
``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerHelpers``. The folders ``core`` and
``analyzers`` never call it, and it reads one thing from ``analyzers``, an analyzer module's prompt constant, through
``ImportAnalyzer``. The cards are for a person, so their texts are plain sentences.

The entry point is ``all_event_cards``, called by
``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader.event_cards``. The card functions are
reached through the tables ``_FORMS_BY_CATEGORY``, ``_ASSISTANT_FORMS`` and ``_USER_FORMS`` and not by import, so a
search finds no caller for them. Three tables are kept by hand and name or explain the analyzers by registered name,
``_ANALYZER_EXPLANATION``, ``_ANALYZER_READABLE_NAME`` and ``_STATE_DONE_SENTENCE``, and a fourth,
``_PRAGMATIC_FIELD_LABEL``, chooses which pragmatic fields a card shows. A new analyzer or a new pragmatic field shows
on the cards without a readable name or an explanation until its row is added here, and a new recorded event category
needs an entry in ``_FORMS_BY_CATEGORY`` and ``_CATEGORY_LABEL``.
"""
from __future__ import annotations

from typing import Any, Callable

from illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerHelpers import (
    FlowDesign,
    build_card_units,
    index_by_refresh,
    state_of,
)


def assistant_card_question(EventDict, by_idx, FlowDesign):
    """Return the ``transcription`` of the assistant ``UtteranceEvent`` dict ``EventDict``, the card text of a reply.
    ``by_idx`` and ``FlowDesign`` are accepted because ``_ASSISTANT_FORMS`` declares them and are not used. Reached
    through ``_ASSISTANT_FORMS`` in this module."""
    return EventDict.get("transcription", "")


def user_card_plain(EventDict):
    """Return the ``transcription`` of the user ``UtteranceEvent`` dict ``EventDict``, the card text of what the user
    said. Reached through ``_USER_FORMS`` in this module."""
    return EventDict.get("transcription", "")


# Shown on an analyzer's card, so a reader knows what the analyzer returns. Keyed by analyzer
# type. These strings are card text.
_ANALYZER_EXPLANATION: dict[str, str] = {
    "QuestionCompleteCriteria":
        "Checks whether the user has actually answered this state's question, and if so extracts "
        "their answer as a sentence.",
    "QuestionsAnsweredConversationStateTransitionCriteria":
        "Reports this state is finished once all of its questions have been answered. No LLM, it "
        "simply checks whether any questions remain.",
    "CategoricalAnswerConversationStateTransitionCriteria":
        "Reports this state can move on when the user's recorded category answer matches the option "
        "this entry declares. No LLM, a pure value check over the already-validated choice.",
    "TurnCountConversationStateTransitionCriteria":
        "Reports this state is finished after a set number of turns have passed. No LLM, it simply "
        "counts the turns spent in the state.",
    "PragmaticConversationStateTransitionCriteria":
        "Reports this state is finished by analyzing the conversation against a natural-language "
        "completion condition (for example, that the user has said goodbye).",
}


def _explanation_for(analyzer_name: str) -> str:
    """Return the explanation ``_ANALYZER_EXPLANATION`` holds for the registered name ``analyzer_name``, or an empty
    string when the table has no row for it. Called by ``analyzer_result_card`` in this module."""
    return _ANALYZER_EXPLANATION.get(analyzer_name, "")


def _static_prompt_for(analyzer_name: str) -> str:
    """Return the ``PROMPT`` constant, or else the ``IncrementalPromptPickQuestion`` constant, of the analyzer module
    that registers ``analyzer_name``, found through
    ``illocutionary_lifecycles.analyzers.AnalyzerBase.ImportAnalyzer``, or an empty string when the name is empty, no
    module registers it or the module has neither constant. Called by ``analyzer_result_card`` in this module when a
    result recorded no prompt, as the incremental results do."""
    if not analyzer_name:
        return ""
    try:
        from illocutionary_lifecycles.analyzers.AnalyzerBase import ImportAnalyzer
        mod = ImportAnalyzer(analyzer_name)
    except Exception:
        return ""
    return str(getattr(mod, "PROMPT", "") or getattr(mod, "IncrementalPromptPickQuestion", "") or "").strip()

def _capitalized(text: str) -> str:
    """Return ``text`` as a string with surrounding spaces removed and its first letter capitalized, or an empty string.
    Called by the card functions of this module."""
    s = str(text or "").strip()
    return (s[0].upper() + s[1:]) if s else ""


# Card sentences for a transition criterion's result, by criterion type.
_STATE_DONE_SENTENCE: dict[str, str] = {
    "QuestionsAnsweredConversationStateTransitionCriteria": "All questions complete in the state",
    "TurnCountConversationStateTransitionCriteria": "Enough turns taken in this state",
    "CategoricalAnswerConversationStateTransitionCriteria": "The chosen option moves the state on",
    "PragmaticConversationStateTransitionCriteria": "State found complete",
}
_STATE_NOT_DONE_SENTENCE = "State not complete yet"


def analyzer_result_card(result_value, QuestionText, result_prompt="", result_name="", AnalyzedUtteranceText=""):
    """Return the card text of one analyzer result, its parts separated by blank lines.

    The parts come in a fixed order, the user utterance analyzed, ``AnalyzedUtteranceText``, after the word Heard, the
    question checked, ``QuestionText``, for a question checker only, the answer and choice of ``result_value`` as
    sentences, the done sentence of ``_STATE_DONE_SENTENCE`` for a transition criterion, one line for each other key of
    the value holding a bool, a string or a number, the registered name ``result_name`` after the word Analyzer, the
    explanation from ``_ANALYZER_EXPLANATION``, and the prompt, ``result_prompt``, or else the module's constant from
    ``_static_prompt_for``. A value that is not a dict is shown as one capitalized line. Called by ``_forms_for_unit`` in
    this module for every analyzer unit.
    """
    v = result_value or {}
    name = str(result_name or "").strip()
    name_line = f"Analyzer: {name}" if name else ""
    explanation = _explanation_for(name)
    is_transition_criterion = name.endswith("ConversationStateTransitionCriteria")
    show_question = name.endswith("QuestionCompleteCriteria")
    q_text = str(QuestionText or "").strip()
    question_line = f'Question: {q_text}' if (q_text and show_question) else ""
    heard_line = f'Heard: "{str(AnalyzedUtteranceText or "").strip()}"' if str(AnalyzedUtteranceText or "").strip() else ""

    if not isinstance(v, dict):
        s = _capitalized(v)
        return "\n".join([p for p in (heard_line, question_line, s, name_line, explanation) if p])

    answer = _capitalized(v.get("answer"))
    choice = _capitalized(v.get("choice"))

    # Keys worded as sentences below, and so not listed again as ``key: value`` lines.
    _TRANSLATED_KEYS = {"answer", "choice", "answered", "done", "AnalyzedText"}

    parts: list[str] = []
    if heard_line:
        parts.append(heard_line)
    if question_line:
        parts.append(question_line)
    if choice and answer:
        parts.append(f"Choice: {choice}, {answer}")
    elif choice or answer:
        parts.append(f"Answer: {choice or answer}")
    if is_transition_criterion and "done" in v:
        parts.append(
            _STATE_DONE_SENTENCE.get(name, "State found complete")
            if v.get("done") else _STATE_NOT_DONE_SENTENCE
        )
    extras = []
    for k, val in v.items():
        if k in _TRANSLATED_KEYS:
            continue
        if isinstance(val, bool):
            rendered = "yes" if val else "no"
        elif isinstance(val, (str, int, float)):
            rendered = _capitalized(val)
        else:
            continue
        if rendered:
            extras.append(f"{_capitalized(k.replace('_', ' '))}: {rendered}")
    if extras:
        parts.append("\n".join(extras))
    if name_line:
        parts.append(name_line)
    if explanation:
        parts.append(explanation)

    rp = str(result_prompt or "").strip() or _static_prompt_for(name)
    if rp:
        parts.append(f"Prompt sent to the analyzer:\n{rp}")

    return "\n\n".join(parts)


def _memory_text(m: dict[str, Any]) -> str:
    """Return the sentence of the remembered answer ``m``, its ``answer`` when that is a non-empty string, or else its
    first non-empty string value, or ``m`` itself when it is a string, or an empty string. Called by
    ``memory_card_fact`` and ``_card_summary`` in this module."""
    if not isinstance(m, dict):
        return str(m) if isinstance(m, str) else ""
    if isinstance(m.get("answer"), str) and m["answer"].strip():
        return m["answer"].strip()
    return next((x for x in m.values() if isinstance(x, str) and x.strip()), "")


def memory_card_fact(EventDict):
    """Return the card text of the ``MemoryEvent`` dict ``EventDict``, the words New memory, a colon and the
    remembered sentence. Reached through ``_FORMS_BY_CATEGORY`` in this module."""
    return f'New memory: {_memory_text(EventDict.get("memory", {}))}'


# The state fields shown on a state card, with their card labels. Other fields are left out.
_PRAGMATIC_FIELD_LABEL: dict[str, str] = {
    "pConversationState": "State",
    "pConversationStateRemainingQuestions": "Remaining questions",
    "pConversationStateTurnCountState": "Turns in this state",
    "pActiveAnalyzersState": "Active analyzers",
}


def _readable_pragmatic_value(field: str, value: Any, v: dict[str, Any], FlowDesign) -> str:
    """Return the value ``value`` of the pragmatic field ``field`` as card text, a state index as the text of that
    state's first question from ``FlowDesign`` or else the index, a list of remaining questions as their texts joined by
    semicolons, another list joined by commas, a bool as yes or no, a dict as an empty string, and anything else as its
    string. ``v``, the whole values dict, is accepted and not used. Called by ``pragmatic_card_values`` in this module."""
    if field == "pConversationState":
        return FlowDesign.question_text(value, 0) or str(value)
    if field == "pConversationStateRemainingQuestions" and isinstance(value, list):
        texts = [(x.get("question") if isinstance(x, dict) else str(x)) for x in value]
        return "; ".join(t for t in texts if t)
    if isinstance(value, dict):
        return ""
    if isinstance(value, list):
        return ", ".join(str(x) for x in value)
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


# Card names for analyzer types.
_ANALYZER_READABLE_NAME: dict[str, str] = {
    "QuestionCompleteCriteria": "question check",
    "QuestionsAnsweredConversationStateTransitionCriteria": "questions-answered completion",
    "TurnCountConversationStateTransitionCriteria": "turn-count completion",
    "PragmaticConversationStateTransitionCriteria": "pragmatic completion",
    "CategoricalAnswerConversationStateTransitionCriteria": "category-answer routing",
}


def _readable_analyzer_name(name: str) -> str:
    """Return the card name ``_ANALYZER_READABLE_NAME`` holds for the registered name ``name``, or, for a name without a
    row, ``name`` with the endings ConversationStateTransitionCriteria and Criteria removed. Called by
    ``pragmatic_card_values`` and ``transition_criteria_card`` in this module."""
    if name in _ANALYZER_READABLE_NAME:
        return _ANALYZER_READABLE_NAME[name]
    return name.replace("ConversationStateTransitionCriteria", "").replace("Criteria", "").strip() or name


def pragmatic_card_values(EventDict, FlowDesign):
    """Return the card text of the ``PragmaticStates`` dict ``EventDict``, one line per field listed in
    ``_PRAGMATIC_FIELD_LABEL``, the field's card label, a colon and its readable value, leaving out every
    other field and every field whose value reads as empty. ``FlowDesign`` turns indexes into question texts. Reached
    through ``_FORMS_BY_CATEGORY`` in this module."""
    v = EventDict.get("values", {}) or {}
    lines = []
    for field, value in v.items():
        if field not in _PRAGMATIC_FIELD_LABEL:
            continue
        label = _PRAGMATIC_FIELD_LABEL[field]
        if field == "pActiveAnalyzersState" and isinstance(value, list):
            readable = ", ".join(_readable_analyzer_name(str(x)) for x in value)
        else:
            readable = _readable_pragmatic_value(field, value, v, FlowDesign)
        if readable.strip():
            lines.append(f'{label}: {readable}')
    return "\n".join(lines)


def init_card_overview(EventDict):
    """Return the card text of the stored flow ``EventDict``, a ``ConversationInit`` dict, saying that the session began
    and how many states the flow has. The stored flow is in the streams only
    when the session's record was loaded from a storage vendor, so a running session that was never reopened shows no
    such card. Reached through ``_FORMS_BY_CATEGORY`` in this module."""
    v = EventDict.get("values", {}) or {}
    states = v.get("ConversationStates", {}) or {}
    return f'The session began.\nThis conversation has {len(states)} states.'


def state_card_change(EventDict, FlowDesign):
    """Return the card text of the ``ConversationStateEvent`` dict ``EventDict``, saying the conversation moved on and
    naming the state left and the state entered by their first questions from ``FlowDesign``, or a general sentence
    when a state has no question. Reached through ``_FORMS_BY_CATEGORY`` in this module."""
    prev = FlowDesign.question_text(EventDict.get("previous_conversation_state"), 0)
    now = FlowDesign.question_text(EventDict.get("conversation_state"), 0)
    if prev and now:
        return f'The conversation moved on from "{prev}" to "{now}".'
    return f'The conversation moved on to "{now}".' if now else "The conversation moved to a new state."


def transition_criteria_card(EventDict):
    """Return the card text of the ``TransitionCriteriaEvent`` dict ``EventDict``, saying which criterion, by its card
    name, reported that this state can move on and, when the record holds it, the entry's place in the state's priority
    order counted from 1. The move itself, when one follows, has its own ``ConversationStateEvent`` card. Reached
    through ``_FORMS_BY_CATEGORY`` in this module."""
    name = _readable_analyzer_name(str(EventDict.get("AnalyzerType", "") or ""))
    ordinal = EventDict.get("WithinConversationStateOrdinal")
    place = ""
    if isinstance(ordinal, int) and ordinal >= 0:
        place = f" (transition {ordinal + 1} in this state's priority order)"
    return f"A transition condition fired: {name} signaled this state can move on.{place}"



def composed_prompt_card(EventDict):
    """Return the ``prompt`` of the ``ComposedPromptEvent`` dict ``EventDict``, the composed prompt as the model got it,
    or an empty string. Reached through ``_FORMS_BY_CATEGORY`` in this module."""
    return EventDict.get("prompt", "") or ""


def prompt_change_card(EventDict):
    """Return the card text of the ``ManualPromptChangeEvent`` dict ``EventDict``, which prompt block was replaced, what it
    reads now, what it read before and the ``source`` label of the change. Reached through ``_FORMS_BY_CATEGORY`` in
    this module."""
    def _shown(value):
        """Return ``value`` as one line of card text, a dict as its keys, a string as itself."""
        if isinstance(value, dict):
            return "{" + ", ".join(sorted(str(k) for k in value)) + "}"
        return str(value) if value is not None else "(nothing)"
    key = str(EventDict.get("block_key", "") or "")
    sub = EventDict.get("block_sub_key")
    where = f"{key}[{sub}]" if sub is not None else key
    return (f"Prompt block {where} changed by {EventDict.get('source', '') or 'unknown'}.\n"
            f"Now: {_shown(EventDict.get('value'))}\nBefore: {_shown(EventDict.get('previous_value'))}")


def interrupted_card_fields(EventDict):
    """Return the card text of the ``InterruptedUtteranceEvent`` dict ``EventDict``, two lines with what the user heard
    before interrupting and the whole generated reply. Reached
    through ``_FORMS_BY_CATEGORY`` in this module."""
    heard = EventDict.get("heard", "") or ""
    full = EventDict.get("transcription", "") or ""
    return f"What user heard: {heard}\nFull generated turn: {full}"


# The card function of each event category. An entry is (form name, function, whether the
# function takes the refresh index, whether it takes the FlowDesign). Analyzer events are not listed
# because each analyzer result gets its own card from ``analyzer_result_card``. Utterances are
# listed by role below.
_FORMS_BY_CATEGORY: dict[str, list[tuple[str, Callable[..., str], bool, bool]]] = {
    "UtteranceEvent": [],
    "MemoryEvent": [("", memory_card_fact, False, False)],
    "PragmaticStates": [("", pragmatic_card_values, False, True)],
    "ConversationInit": [("", init_card_overview, False, False)],
    "ConversationStateEvent": [("", state_card_change, False, True)],
    "TransitionCriteriaEvent": [("", transition_criteria_card, False, False)],
    "InterruptedUtteranceEvent": [("", interrupted_card_fields, False, False)],
    "ComposedPromptEvent": [("", composed_prompt_card, False, False)],
    "ManualPromptChangeEvent": [("", prompt_change_card, False, False)],
}

_ASSISTANT_FORMS: list[tuple[str, Callable[..., str], bool, bool]] = [
    ("", assistant_card_question, True, True),
]
_USER_FORMS: list[tuple[str, Callable[..., str], bool, bool]] = [
    ("", user_card_plain, False, False),
]

def _call(entry, EventDict, by_idx, FlowDesign) -> str:
    """Return what the card function of ``entry`` returns for ``EventDict``, passing ``by_idx`` and ``FlowDesign`` when
    the entry's two flags ask for them, or the text "(detail unavailable)" when the function raises, so one malformed
    event does not lose the whole list of cards. ``entry`` is a tuple of the form name, the function and the two flags,
    from the tables of this module. Called by ``event_cards`` in this module."""
    _name, fn, needs_by_idx, needs_design = entry
    args: list[Any] = [EventDict]
    if needs_by_idx:
        args.append(by_idx)
    if needs_design:
        args.append(FlowDesign)
    try:
        return fn(*args)
    except Exception:
        return "(detail unavailable)"


def _select_forms_for_event(EventDict: dict[str, Any], card_forms: Any):
    """Return the table entries whose card functions word ``EventDict``, ``_ASSISTANT_FORMS`` or ``_USER_FORMS`` for
    an utterance by role and the entries of ``_FORMS_BY_CATEGORY`` otherwise, keeping only the form names
    ``card_forms`` lists for the event's category when ``card_forms`` is a dict that has the category. ``None`` or a
    missing category keeps every entry. Called by ``event_cards`` in this module."""
    EventCategory = EventDict.get("CATEGORY")
    if EventCategory == "UtteranceEvent":
        available = _ASSISTANT_FORMS if EventDict.get("role") == "assistant" else _USER_FORMS
    else:
        available = list(_FORMS_BY_CATEGORY.get(EventCategory, []))
    if not card_forms:
        return available
    wanted = card_forms.get(EventCategory)
    if wanted is None:
        return available
    by_name = {entry[0]: entry for entry in available}
    return [by_name[name] for name in wanted if name in by_name]


def _forms_for_unit(unit: dict[str, Any], by_idx, FlowDesign: FlowDesign, card_forms: Any) -> list[dict[str, str]]:
    """Return the list of card forms of ``unit``, one unit from ``build_card_units``, each a dict with ``form`` and
    ``text``. An analyzer unit gets one form from ``analyzer_result_card``, with the question found from the state of
    its refresh and the result's position, and every other unit the forms of ``event_cards``. Called by
    ``all_event_cards`` in this module."""
    EventDict = unit["event"]
    if "result_key" in unit:
        state = state_of(EventDict, by_idx)
        ordinal = (EventDict.get("results", {}) or {}).get(unit["result_key"], {}).get("WithinConversationStateOrdinal", 0)
        question = FlowDesign.question_text(state, ordinal)
        return [{"form": "", "text": analyzer_result_card(
            unit["result"], question, unit.get("result_prompt", ""), unit.get("result_name", ""),
            AnalyzedUtteranceText=unit.get("AnalyzedUtteranceText", ""))}]
    return event_cards(EventDict, by_idx, FlowDesign, card_forms)


def event_cards(EventDict: dict[str, Any], by_idx: dict[Any, dict[str, dict[str, Any]]],
                FlowDesign: FlowDesign, card_forms: Any = None) -> list[dict[str, str]]:
    """Return the card forms of ``EventDict``, an event that is not an analyzer event, as a list of dicts with
    ``form``, the form's name, and ``text``, the card text, one per entry ``_select_forms_for_event`` picks with
    ``card_forms``. ``by_idx`` is the index from ``index_by_refresh`` and ``FlowDesign`` the flow lookup. Called by
    ``_forms_for_unit`` in this module."""
    forms = _select_forms_for_event(EventDict, card_forms)
    return [{"form": entry[0], "text": _call(entry, EventDict, by_idx, FlowDesign)} for entry in forms]


# The header label of each event category's card.
_CATEGORY_LABEL: dict[str, str] = {
    "ConversationInit": "Conversation Init",
    "PragmaticStates": "Pragmatic State",
    "AnalyzerEvent": "Analyzer Event",
    "MemoryEvent": "Remembered Answer",
    "ConversationStateEvent": "State Event",
    "TransitionCriteriaEvent": "Transition Trigger",
    "InterruptedUtteranceEvent": "Assistant Utterance (Interrupted)",
    "ComposedPromptEvent": "Composed Prompt",
    "ManualPromptChangeEvent": "Prompt Change",
}


def _card_label(EventDict: dict[str, Any]) -> str:
    """Return the header label of the card of ``EventDict``, "Assistant Utterance" or "User Utterance" for an
    utterance by role, the label ``_CATEGORY_LABEL`` holds for every other category, or "Event". Called by
    ``all_event_cards`` in this module when the unit has no label of its own."""
    EventCategory = EventDict.get("CATEGORY")
    if EventCategory == "UtteranceEvent":
        return "Assistant Utterance" if EventDict.get("role") == "assistant" else "User Utterance"
    return _CATEGORY_LABEL.get(EventCategory, "Event")


def _card_summary(unit: dict[str, Any], FlowDesign: FlowDesign) -> str:
    """Return the one-line summary shown on the collapsed card of ``unit``, the utterance, the
    heard part, the remembered sentence or the word Fired by category, or an empty string when that text is longer than
    15 letters, since a summary is never cut short. An analyzer's choice or answer is returned whole, and a
    criterion's result as "State done" or "Not done". ``FlowDesign`` is accepted and not used. Called by
    ``all_event_cards`` in this module."""
    EventDict = unit["event"]
    EventCategory = EventDict.get("CATEGORY")
    s = ""
    if EventCategory == "UtteranceEvent":
        s = EventDict.get("transcription", "") or ""
    elif EventCategory == "InterruptedUtteranceEvent":
        s = EventDict.get("heard", "") or ""
    elif EventCategory == "MemoryEvent":
        s = _memory_text(EventDict.get("memory", {}))
    elif EventCategory == "TransitionCriteriaEvent":
        s = "Fired"
    elif EventCategory == "AnalyzerEvent":
        v = unit.get("result", {}) or {}
        answer = str(v.get("choice") or v.get("answer") or "").strip()
        if answer:
            return answer.replace("\n", " ")
        if str(unit.get("result_name", "")).endswith("ConversationStateTransitionCriteria") and "done" in v:
            return "State done" if v.get("done") else "Not done"
        s = ""
    s = s.strip().replace("\n", " ")
    return s if len(s) <= 15 else ""


def all_event_cards(streams: dict[str, list[dict[str, Any]]],
                    FlowDesign: FlowDesign, card_forms: Any = None) -> list[dict[str, Any]]:
    """Return one card for every unit ``build_card_units`` makes from ``streams``, in recorded order, each a dict with
    ``key``, an identifier for lists and links that is not for display, ``label``, the header, ``summary``, the
    one-line summary or an empty string, ``links``, the keys of the cards it came from, and ``forms``, a list of dicts
    with ``form`` and ``text``.

    ``streams`` is the dict from category to event dicts that
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader.event_streams`` returns,
    ``FlowDesign`` is a ``FlowDesign`` built from the session's flow, and ``card_forms`` is a dict from category to the
    form names wanted, or ``None`` for every form. This is the module's entry point, called by ``event_cards`` in that
    module, as the module docstring above explains.
    """
    by_idx = index_by_refresh(streams)
    units = build_card_units(streams)
    out: list[dict[str, Any]] = []
    for u in units:
        EventDict = u["event"]
        card: dict[str, Any] = {
            "key": u["key"],
            "label": u.get("label_override") or _card_label(EventDict),
            "summary": _card_summary(u, FlowDesign),
            "links": list(u.get("links", [])),
            "forms": _forms_for_unit(u, by_idx, FlowDesign, card_forms),
        }
        out.append(card)
    return out
