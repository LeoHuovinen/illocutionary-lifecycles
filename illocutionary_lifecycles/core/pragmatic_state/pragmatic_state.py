"""``PragmaticState``, the values the next prompt is composed from, and its method ``Composer``, the one place in the
package where a prompt for the language model is built.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the model gets for every turn one prompt composed from the flow's
authored texts, the conversation so far, the remembered answers and these values, so this module, in the folder
``core``, is where what the conversation holds becomes what the model is told. Of the package's four folders, ``core``
holds this module, ``analyzers`` read the values without changing them, ``memory`` saves them after every refresh, and
``server`` never reads them. The values describe the current state only, such as its index, its open questions, its
analyzers, its turn count and the incremental picks. Which states exist and how they follow each other is held by
``illocutionary_lifecycles.core.system_state.system_state.SystemState``.

A field's name has the form p, then what it holds, then State, and the field exists only while it applies, so a state
without questions has no remaining-questions field. ``pConversationState`` and ``pConversationStateRemainingQuestions``
are the two names without the State ending. Three things write the fields. ``SystemState.EstablishConversationState``
writes a state's fields when the state is entered,
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` updates them after analyzers have run, and
``SystemState.set_ignore_memories`` sets or deletes ``pIgnoreMemoriesState`` when the remembered answers are switched
off or on. Every other
module only reads them, and nothing in the code prevents another write, so a new write elsewhere is a defect. The
fields that start with p are saved as a ``PragmaticStatesEvent`` after every refresh, and a prompt block may hold any
of them as a blank in braces.

The composer sends no instruction of its own. Every instruction in a prompt is text the flow's author wrote, and the
composer adds only short labels and the divider lines, and the whole prompt goes to the model as one user message
through ``illocutionary_lifecycles.core.clients.PostComposerLLMCallHelper.PostComposerLLMCallHelper``.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


def _readable(value: Any) -> str:
    """Return ``value`` as text for a prompt, a mapping as the text of its values one per line without its keys, a
    list, tuple or set as its items one per line, an empty value as an empty string, and anything else as its string.
    Called by ``PragmaticState.Composer`` in this module to fill blanks and to list the remembered answers."""
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if isinstance(value, Mapping):
        return "\n".join(_readable(item) for item in value.values() if _readable(item))
    if isinstance(value, (list, tuple, set)):
        return "\n".join(_readable(item) for item in value if _readable(item))
    return str(value)


def _as_int(value: Any, default: int = 0) -> int:
    """Return ``value`` as an int, or ``default`` when it cannot be read as one. Called by ``PragmaticState.Composer``
    in this module to read the turn count."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class _BlankFill(dict):
    """A dict of the values for the blanks of a prompt block, which returns an empty string for a blank it holds no
    value for, so ``str.format_map`` never raises on an unknown blank. Built by ``PragmaticState.Composer`` in this
    module, and ``SystemState._CheckStatePrompt`` raises at state entry for a blank nothing would fill."""

    def __missing__(self, key: str) -> str:
        """Return an empty string for the blank ``key`` that this dict holds no value for, as the class above says."""
        return ""


# An authored text is one string, or a mapping from condition names to strings. These are the
# condition names, in the order they are tried. ``Base`` always applies. The same names are
# used for every authored entry: the blocks, ``question_prompt`` and
# ``memory_callback``.
#   FirstTurn / LaterTurns: the state's first turn, or a later one.
#   NoMemories: used by the memory entry only, when there are no remembered answers to show.
_CONDITION_TOKEN_PRECEDENCE = ("FirstTurn", "LaterTurns", "Base")


def _ConditionResolvedText(value: Any, ActiveConditionTokens: set) -> Any:
    """Return the text that applies from the authored ``value``, which is ``value`` itself when it is not a mapping,
    and for a mapping from condition names to texts the text of the first name in ``_CONDITION_TOKEN_PRECEDENCE`` that
    the mapping holds and that is in ``ActiveConditionTokens`` or is "Base", or an empty string when none is.

    The condition names a flow's author may use as keys are "FirstTurn", for the state's first turn, "LaterTurns",
    for every later turn, and "Base", which always applies, tried in that order, and, for
    ``memory_callback`` only, "NoMemories", shown when there is no remembered answer. Called by
    ``PragmaticState.Composer`` in this module for every authored text.
    """
    if not isinstance(value, Mapping):
        return value
    for token in _CONDITION_TOKEN_PRECEDENCE:
        if token in value and (token == "Base" or token in ActiveConditionTokens):
            return value[token]
    return ""


class pConversationStateRemainingQuestions(list):
    """The list of the current state's questions not yet answered, held on the pragmatic state under the field of the
    same name.

    Each item is a question string, or a dict with ``question`` and ``options`` for a question with options.
    ``SystemState.EstablishConversationState`` creates the list from the state's ``questions``, the refresher removes
    each answered question by its position, and the list is empty once every question is answered. The cycle runs the
    question checker once per item, and the composer fills the blank ``{pConversationStateRemainingQuestions}`` with one
    line per item, as the module docstring above explains.
    """


@dataclass
class PragmaticState:
    """The values of one session that the next prompt is composed from, created by
    ``SystemState.InitializePragmaticState`` and written only by ``SystemState`` and the refresher, as the module
    docstring above explains.

    Three fields always exist. ``pConversationState`` holds the index of the current state. ``pActiveAnalyzersState`` holds the registered names
    of the analyzers that run in the current state. ``pConversationStateTurnCountState`` holds the number of user turns
    taken in the current state. Two further fields hold functions and are not saved, ``Refresher``, the refresher
    ``refresh``, and ``SyncCycle``, the cycle ``SyncCycle``.

    Other fields exist only while they apply, all set by ``SystemState.EstablishConversationState`` except where said.
    ``pConversationStateRemainingQuestions`` holds the open questions in a state whose criteria need them.
    ``pConversationStateTransitionCriteriaListState`` holds the state's criteria entries in order.
    ``pConversationStatePermissiveThresholdState`` holds the number of turns after which the question checker stops
    waiting. ``pIncrementalPhraseInstancesState`` holds the state's declared incremental instances.
    ``pCategoricalAnswerState`` holds the options chosen in the current state, set by the refresher.
    ``pIgnoreMemoriesState`` is set while remembered answers are kept out of the prompt, by
    ``SystemState.set_ignore_memories``. A field named p, then an analyzer's registered name, then State holds what
    that incremental analyzer last returned, by instance identifier, set by the refresher.
    """

    pConversationState: int = 0

    pActiveAnalyzersState: list = field(default_factory=list)

    pConversationStateTurnCountState: int = 0

    Refresher: Any = field(default=None, repr=False)
    SyncCycle: Any = field(default=None, repr=False)

    async def Composer(self, *, window: Any = None, memories: Any = None, blocks: Any = None) -> str:
        """Return the prompt for the next reply, built from this object's fields and the three inputs, with its parts
        joined by a line of three hyphens and empty parts left out.

        This is the one place a prompt is built, as the module docstring above explains, and
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` is its only caller. The
        parts come in a fixed order. First come the matched prompt blocks, the frame prompt and
        the state's illocutionary prompt, with their blanks filled from the fields. The blank
        ``{pConversationStateRemainingQuestions}`` becomes one line per open question, the words QUESTION TO ASK, a
        colon and the question in double quotes, followed by the authored ``question_prompt``, and a
        question's options are not shown. Then come the utterances, under the label
        the flow's ``ConversationHistoryWindowHeading`` or else a default heading, one line per utterance with its speaker, and a note in square brackets when the user has not spoken
        in this state yet. Last comes the authored ``memory_callback`` with the remembered answers, joined by
        semicolons, in its ``{pUserMemories}`` blank, or only its text under "NoMemories" when there is none, and
        nothing at all while ``pIgnoreMemoriesState`` is set. Every authored text may be one string or a mapping from
        the condition names "FirstTurn", "LaterTurns" and "Base" to strings, chosen by ``_ConditionResolvedText``.

        ``window`` holds the utterances to show as ``TurnView`` objects, or a callable that returns them, and ``None``
        shows none. ``memories`` holds the remembered answers. ``blocks`` holds a callable that takes the fields as a
        dict and returns the authored texts, as ``StaticPromptLibrary`` does, or a plain list of block texts.
        """
        PragmaticStates: dict[str, Any] = {}
        for _name, _value in vars(self).items():
            if not _name.startswith("p"):
                continue
            PragmaticStates[_name] = (
                dataclasses.asdict(_value) if dataclasses.is_dataclass(_value) else _value
            )

        _static = blocks(PragmaticStates) if callable(blocks) else (blocks or [])
        if isinstance(_static, Mapping):
            memory_callback = _static.get("memory_callback") or ""
            question_prompt = _static.get("question_prompt") or ""
            window_heading = _static.get("ConversationHistoryWindowHeading") or ""
            window_empty_note = _static.get("ConversationHistoryWindowEmptyNote") or ""
            matched = _static.get("blocks") or []
        else:
            memory_callback = ""
            question_prompt = ""
            window_heading = ""
            window_empty_note = ""
            matched = _static

        fill = _BlankFill({key: _readable(value) for key, value in PragmaticStates.items()})
        _remaining = PragmaticStates.get("pConversationStateRemainingQuestions") or []
        _q_lines = []
        for _q in _remaining:
            _text = _q.get("question", "") if isinstance(_q, Mapping) else _q
            _text = str(_text).strip()
            if _text:
                _q_lines.append(f'QUESTION TO ASK: "{_text}"')
        fill["pConversationStateRemainingQuestions"] = "\n".join(_q_lines)

        # The conditions that hold now. A turn count of 0 is the state's first turn. An
        # unreadable turn count is taken as 1, so that it never counts as a first turn.
        _sec_turn = _as_int(PragmaticStates.get("pConversationStateTurnCountState"), 1)
        Tokens = {"FirstTurn" if _sec_turn == 0 else "LaterTurns"}

        # 1. The blocks. The authored ``question_prompt`` text follows the question lines.
        if _q_lines:
            _QuestionPrompt = _ConditionResolvedText(question_prompt, Tokens)
            if _QuestionPrompt:
                fill["pConversationStateRemainingQuestions"] += "\n" + str(_QuestionPrompt)
        filled = [str(_ConditionResolvedText(block, Tokens)).format_map(fill)
                  for block in matched]

        # 2. The utterances handed in, one line each.
        if window is not None:
            _views = window() if callable(window) else window
            _lines = []
            _has_user = False
            for _view in _views or []:
                _role = getattr(_view, "role", "") or ""
                _text = (getattr(_view, "transcription", "") or "").strip()
                if _role == "user":
                    _has_user = True
                if _text:
                    _who = "User" if _role == "user" else "Assistant"
                    _lines.append(f'{_who}: "{_text}"')
            # The heading of the window and the note shown when the user has not spoken in this
            # state yet are the flow's ``ConversationHistoryWindowHeading`` and ``ConversationHistoryWindowEmptyNote`` when it authors
            # them, chosen by condition like every other authored text, and these two texts otherwise.
            _heading = str(_ConditionResolvedText(window_heading, Tokens) or "").strip() or "The conversation so far this section:"
            _empty_note = str(_ConditionResolvedText(window_empty_note, Tokens) or "").strip() or "[user hasn't replied anything yet]"
            if _has_user:
                filled.append(_heading + "\n" + "\n".join(_lines))
            else:
                filled.append(_heading + "\n"
                              + ("\n".join(_lines) + "\n" if _lines else "")
                              + _empty_note)

        # 3. The memory text. With ``pIgnoreMemoriesState`` set, none is shown. Memories are
        # still recorded.
        if not PragmaticStates.get("pIgnoreMemoriesState"):
            _mem_lines = [line for line in (_readable(memories) or "").splitlines() if line.strip()]
            if _mem_lines:
                fill["pUserMemories"] = "; ".join(_mem_lines)
                _memory_text = _ConditionResolvedText(memory_callback, Tokens)
            else:
                _memory_text = (memory_callback.get("NoMemories", "")
                                if isinstance(memory_callback, Mapping) else "")
            if _memory_text:
                filled.append(str(_memory_text).format_map(fill))

        return "\n\n---\n".join(part for part in filled if part.strip())


def pragmatic_values(PragmaticStateValues: PragmaticState) -> dict[str, Any]:
    """Return a dict of every field of ``PragmaticStateValues`` whose name starts with p and that exists at this moment,
    with dataclass values turned into dicts, leaving out ``Refresher`` and ``SyncCycle``. Called by
    ``SystemState.SaveRefreshResult``, which saves the dict as a ``PragmaticStatesEvent`` after every refresh, as the
    module docstring above explains."""
    out: dict[str, Any] = {}
    for Name, Value in vars(PragmaticStateValues).items():
        if not Name.startswith("p"):
            continue
        out[Name] = dataclasses.asdict(Value) if dataclasses.is_dataclass(Value) else Value
    return out
