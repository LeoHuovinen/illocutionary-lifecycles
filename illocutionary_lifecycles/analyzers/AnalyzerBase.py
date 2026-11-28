"""The registry of analyzers and the three types every analyzer works with, for the folder
``illocutionary_lifecycles/analyzers``, whose task is to return one result from one finished user utterance or from the
speech so far, and to change nothing.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), in which small functions registered here check after each user turn
which questions were answered and whether the state may be left, while the model only writes the replies. Of the
package's four folders, ``core`` runs the conversation and calls these functions, ``analyzers`` holds them together
with this module, ``memory`` records their results, and ``server`` holds the adapters and mounts through which a
browser page, an app or any other program sends the turns in.

An analyzer is an async function that a module under ``illocutionary_lifecycles/analyzers`` registers with
``register`` under a name. The registered name is what a flow writes, either as the ``Analyzer`` of an entry in a
state's ``ConversationStateTransitionCriteria`` list or as an entry of a state's ``Analyzers`` list. The record keeps
the same name as ``AnalyzerType``, and the cards keep their tables by it, so the name is a protocol and the module and
function that register it are named differently. The question checker, for example, is registered as
``QuestionCompleteCriteria`` by the function ``QuestionAnsweredAnalyzer`` in
``illocutionary_lifecycles.analyzers.answer_analyzers.QuestionAnsweredAnalyzer``.

The folder holds three subfolders, each for one kind of result. ``illocutionary_lifecycles.analyzers.answer_analyzers``
holds the question checker, which returns whether one open question was answered and the answer as a sentence.
``illocutionary_lifecycles.analyzers.transition_analyzers`` holds the four transition criteria, which return whether
the conversation may leave its state through one entry of the state's criteria list, registered as
``QuestionsAnsweredConversationStateTransitionCriteria``, ``CategoricalAnswerConversationStateTransitionCriteria``,
``TurnCountConversationStateTransitionCriteria`` and ``PragmaticConversationStateTransitionCriteria``.
``illocutionary_lifecycles.analyzers.incremental_phrase_analyzers`` holds the one analyzer that runs while the user is
still speaking, registered as ``IncrementalPhraseCategoryAnalyzer``, which returns one option word picked from the
speech so far. The subfolder chooses nothing at run time. Which way an analyzer is called is chosen from its registered
name and from one attribute on its function.

``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` calls the analyzers of the current state on every
finished user turn, looking each name up with ``GetAnalyzer``. An analyzer whose name ends in
``ConversationStateTransitionCriteria`` runs in the second pass, once for each entry of the state's
``ConversationStateTransitionCriteria`` list that names it, and receives the entry's position in the list as a fourth
argument. An analyzer whose name ends in ``QuestionCompleteCriteria`` runs in the first pass once for each open
question, and receives the question's position among the open questions as a fourth argument. Every other analyzer
runs in the first pass once, with three arguments. The three arguments are ``UserMemoryFace``, a callable that returns
the list of remembered answers, ``WindowFace``, a callable that returns the current state's recorded utterances, and
``PragmaticState``, the session's
``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.PragmaticState``, which the analyzer only reads. A
transition criterion whose registered name does not end in ``ConversationStateTransitionCriteria`` is never run as a
criterion, and ``illocutionary_lifecycles.core.system_state.system_state.SystemState.EstablishConversationState``
raises a ``ValueError`` when a criteria entry names one.

``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` calls, on every new interim
transcription of the speech so far, every registered function that carries the attribute
``RunsPerIncrementalPhraseInstance`` set to true, once for each instance the current state declares under
``incremental_phrase_instances``. Such a function receives three arguments, the ``PragmaticState``, an
``IncrementalPhrase`` and an ``IncrementalPhraseInstanceDeclaration``. The refresher
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` keeps its value on the pragmatic state only when
the registered name contains ``IncrementalPhrase``.

An analyzer returns one ``AnalysisResult`` and writes nothing. An analyzer saves nothing to the record, moves no conversation
and composes no prompt. The refresher updates the pragmatic state from the result and moves the conversation, and
``illocutionary_lifecycles.memory.memory.Memory`` records it. This module imports nothing from
``illocutionary_lifecycles.core``, ``illocutionary_lifecycles.memory`` or ``illocutionary_lifecycles.server``.

This module is imported by the six analyzer modules, by ``illocutionary_lifecycles.core.turn_taking.sync_cycle``, by
``illocutionary_lifecycles.core.ConversationInit`` and by
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``.

A new analyzer is one new module in the subfolder for its kind of result that calls ``register`` with a name of the
right ending. Nothing else in the package must change for it to run. Until a row for it is added to the tables
``_ANALYZER_EXPLANATION`` and ``_ANALYZER_READABLE_NAME`` in
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``, and for a transition criterion also to
``_STATE_DONE_SENTENCE``, its cards show without a readable name or an explanation.
"""
from __future__ import annotations

import importlib
import pkgutil

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class AnalysisResult:
    """The one result an analyzer returns, read by the cycle, the refresher and the record.

    This result carries one check's outcome from the folder ``analyzers`` to the folders ``core`` and ``memory``, as
    the module docstring above explains.

    ``value`` holds the analyzer's answer as a dict whose keys are a protocol read by
    ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh``,
    ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter`` and the cards. The question checker returns
    ``answered``, ``answer`` and, for a question with options, ``choice``. A transition criterion returns ``done``. The
    incremental analyzer returns ``category`` and, beside it, ``AnalyzedText``, ``repeat`` or ``gate``.
    ``AnalyzerType`` holds the registered name of the analyzer that returned the result. ``AnalyzerId`` is empty when
    an analyzer returns it. The cycle builds the run's identifier itself from ``AnalyzerType`` and the position.
    ``WithinConversationStateOrdinal`` holds the position of the question among the open questions for the question
    checker, the position of the entry in the state's criteria list for a listed transition criterion, and ``-1`` for
    every other analyzer. ``prompt`` holds the prompt the analyzer sent to its model, or an empty string when it called
    no model, and the record keeps it so the cards can show it.
    """

    value: Any
    AnalyzerType: str
    AnalyzerId: str = ""
    WithinConversationStateOrdinal: int = -1
    prompt: str = ""


@dataclass(frozen=True)
class IncrementalPhrase:
    """The speech so far and the instance a run is for, passed as the second argument to an analyzer that runs per
    incremental phrase instance.

    This object carries the user's unfinished words from the folder ``core`` to an analyzer while the user is still speaking,
    so a connected page or app can react before the turn ends, as the module docstring above explains.
    ``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` builds one for every declared
    instance on every new interim transcription. ``SpokenPhraseSoFar`` holds the text of the user's unfinished
    utterance as the STT has transcribed it up to this moment. ``InstanceIdentifier`` holds the ``identifier`` of the
    instance in the state's ``incremental_phrase_instances`` list, and is empty only when an analyzer is called by hand
    without an instance.
    """

    SpokenPhraseSoFar: str = ""
    InstanceIdentifier: str = ""


@dataclass(frozen=True)
class IncrementalPhraseInstanceDeclaration:
    """One entry of a flow state's ``incremental_phrase_instances`` list, passed as the third argument to an analyzer
    that runs per incremental phrase instance.

    This declaration is what a flow state lists to listen for while the user is still speaking, read by the folder ``core`` and
    handed to an analyzer, as the module docstring above explains.
    ``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` builds it from the entry's keys
    of the same names. The entry's ``identifier`` is not a field here, because it reaches the analyzer as
    ``IncrementalPhrase.InstanceIdentifier``. ``IncrementalAnalyzerChoicesPrompt`` holds the option words the model may
    answer, each compared to the reply without regard to case, with ``none`` first when ordinary speech should give a
    recorded pick that is not sent. ``IncrementalPromptSubjectKeywords`` holds the text placed in the prompt's
    "Subject keywords" row, saying what the options are about. ``IncrementalPromptRequestKeywords`` holds the text
    placed in the prompt's "Request keywords" row, and in the gate prompt when ``RequiresGate`` is true.
    ``RequiresGate``, when true, makes the analyzer first ask the model whether the new words ask for a change, and
    keeps the answer yes for the rest of the utterance before it asks for an option. ``Idempotent``, when true, makes
    a second pick of the option the instance already holds in this utterance a repeat that moves the word cursor and is
    not sent, so "left is good" is one pick, and when false makes every pick count, so "left left left" is three. A new
    utterance clears the instance's held option either way.
    """

    IncrementalAnalyzerChoicesPrompt: tuple = ()
    IncrementalPromptSubjectKeywords: str = ""
    IncrementalPromptRequestKeywords: str = ""
    RequiresGate: bool = False
    Idempotent: bool = True


AnalyzerFn = Callable[..., Awaitable[AnalysisResult]]

# Every registered analyzer, by registered name. Filled by ``register`` when an analyzer module is imported.
ANALYZER_REGISTRY: dict[str, AnalyzerFn] = {}


@dataclass(frozen=True)
class CustomAnalyzerDeclaration:
    """The arguments a custom analyzer is instantiated with, by ``InstantiateCustomAnalyzer`` in this module, while a
    session runs.

    NOTE: This is an experimental feature. You will only need this for an analyzer that does not exist when the
    session starts, during an ongoing conversation session. Only use this feature if you are sure you need it. It goes
    against the basic idea of IL, a flow written in advance whose states (eg. during runtime, upcoming
    ConversationStates in the active flow in SystemState) name only registered analyzers.

    ``CustomAnalyzerName`` is the name the instance is kept under and the name a state lists in its ``Analyzers`` to
    run it, and it ends in ``CustomAnalyzer``, so it is never taken for a transition criterion or a question checker.
    ``CustomAnalyzerPrompt`` is the text the model is given before the current state's utterances.
    ``CustomAnalyzerOutputSchema`` maps every key of the model's reply to what that key holds, a list of the only
    strings it may be, "str" for any string, or "int" for any whole number.
    ``CustomAnalyzerReadsNonconversationalSocketFeed`` says whether the analyzer is also given the nonconversational
    socket feeds the current state shows, read the same way the reply reads them, and is false unless set.

    A nonconversational feed is the text a server keeps in a socket, a pragmatically useful description of something
    neither the user nor the assistant said (for example what is on a screen, what the user just touched, captions or
    narration, recent events with their times, what has been built so far, how much time has passed, or the server's
    own summary of what happened earlier). It is always text the server has already written for the conversation, never
    the source it describes, and the server replaces it whenever the source changes. Its form is the server's choice,
    such as one sentence describing the present, a single line about what the user is focusing on, a short list of
    recent events, lines of names and values, or nothing when there is nothing to show. IL keeps no copy and no history
    of a feed, and reads whatever it says each time a custom analyzer that reads socket feeds runs, as
    ``illocutionary_lifecycles.core.system_state.system_state.SystemState._NonconversationalSocketFeeds`` explains.

    The declaration is created only by
    ``illocutionary_lifecycles.core.system_state.system_state.SystemState._InstantiateCustomAnalyzer``, for a custom
    analyzer instantiated through ``SystemState.SetAnalyzerInstance`` and again for one rebuilt by
    ``SystemState.RecoverInit`` from the recorded fields.
    """
    CustomAnalyzerName: str
    CustomAnalyzerPrompt: str
    CustomAnalyzerOutputSchema: dict
    CustomAnalyzerReadsNonconversationalSocketFeed: bool = False

    def _CustomAnalyzerOutputJsonSchema(self) -> dict:
        """Return ``CustomAnalyzerOutputSchema`` as the strict JSON Schema the analyzer client holds the model's reply
        to, an object with every key required and no other key, a string limited to the listed strings for a list, a
        string for "str", and an integer for "int". Called only by the analyzer that ``InstantiateCustomAnalyzer`` in
        this module builds, each time it runs."""
        CustomAnalyzerOutputProperties = {}
        for CustomAnalyzerOutputKey, CustomAnalyzerOutputKind in self.CustomAnalyzerOutputSchema.items():
            if isinstance(CustomAnalyzerOutputKind, list):
                CustomAnalyzerOutputProperties[CustomAnalyzerOutputKey] = {
                    "type": "string",
                    "enum": [str(CustomAnalyzerOutputChoice) for CustomAnalyzerOutputChoice in CustomAnalyzerOutputKind],
                }
            elif CustomAnalyzerOutputKind == "int":
                CustomAnalyzerOutputProperties[CustomAnalyzerOutputKey] = {"type": "integer"}
            else:
                CustomAnalyzerOutputProperties[CustomAnalyzerOutputKey] = {"type": "string"}
        return {"type": "object", "properties": CustomAnalyzerOutputProperties,
                "required": list(CustomAnalyzerOutputProperties), "additionalProperties": False}


def InstantiateCustomAnalyzer(InstantiatedCustomAnalyzerDeclaration: CustomAnalyzerDeclaration,
                              NonconversationalSocketFeed: Callable[[], str] | None = None) -> AnalyzerFn:
    """Return a new analyzer built from ``InstantiatedCustomAnalyzerDeclaration`` alone, called like every other analyzer with
    ``UserMemoryFace``, ``WindowFace`` and ``PragmaticState``, and keep nothing.

    The analyzer sends the declaration's prompt followed by the current state's utterances to the analyzer model client
    through its ``complete_json``. When the declaration's ``CustomAnalyzerReadsNonconversationalSocketFeed`` is true, it
    also calls ``NonconversationalSocketFeed`` each time it runs, a callable bound to the session that returns the
    nonconversational socket feeds the current state shows, and adds them after the utterances when there are any.
    That callable is ``SystemState._NonconversationalSocketFeeds`` of the session, handed over only by
    ``SystemState._InstantiateCustomAnalyzer``, so the analyzer itself is still called with the normal arguments only. The call to the
    model uses the declaration's ``_CustomAnalyzerOutputJsonSchema`` as the strict schema, and
    returns an ``AnalysisResult`` whose ``value`` is the reply, whose ``AnalyzerType`` is the declaration's
    ``CustomAnalyzerName`` and whose ``prompt`` is the text sent. A model call that raises gives an empty ``value`` and is
    not raised. Two declarations with the same fields give analyzers that send the same request to the model,
    which is what lets a reopened session rebuild its custom analyzers from the record. The note of ``CustomAnalyzerDeclaration`` applies here too.
    """
    async def CustomAnalyzerInstanceCall(UserMemoryFace: Any, WindowFace: Any, PragmaticState: Any) -> AnalysisResult:
        """Return this custom analyzer's ``AnalysisResult`` for the current state's utterances, as
        ``InstantiateCustomAnalyzer`` above explains."""
        from illocutionary_lifecycles.core.clients.llm import analyzer_llm
        CustomAnalyzerUtteranceLines = [CustomAnalyzerUtteranceView.transcription for CustomAnalyzerUtteranceView in WindowFace()
                                        if getattr(CustomAnalyzerUtteranceView, "transcription", "")]
        CustomAnalyzerSentPrompt = (InstantiatedCustomAnalyzerDeclaration.CustomAnalyzerPrompt + "\nRecent conversation:\n"
                                    + "\n".join(CustomAnalyzerUtteranceLines))
        if InstantiatedCustomAnalyzerDeclaration.CustomAnalyzerReadsNonconversationalSocketFeed and NonconversationalSocketFeed:
            CustomAnalyzerShownSocketFeed = str(NonconversationalSocketFeed() or "").strip()
            if CustomAnalyzerShownSocketFeed:
                CustomAnalyzerSentPrompt += "\nNonconversational socket feed shown now:\n" + CustomAnalyzerShownSocketFeed
        try:
            CustomAnalyzerReplyValue = await analyzer_llm().complete_json(
                CustomAnalyzerSentPrompt, schema=InstantiatedCustomAnalyzerDeclaration._CustomAnalyzerOutputJsonSchema(),
                schema_name=InstantiatedCustomAnalyzerDeclaration.CustomAnalyzerName)
        except Exception:
            CustomAnalyzerReplyValue = {}
        return AnalysisResult(value=CustomAnalyzerReplyValue, AnalyzerType=InstantiatedCustomAnalyzerDeclaration.CustomAnalyzerName,
                              prompt=CustomAnalyzerSentPrompt)
    return CustomAnalyzerInstanceCall


def register(RegisteredName: str) -> Callable[[AnalyzerFn], AnalyzerFn]:
    """Return a decorator that stores the decorated analyzer function in ``ANALYZER_REGISTRY`` under
    ``RegisteredName`` and returns the function unchanged. Every analyzer module calls it once, when the module is
    imported. A second registration under the same name replaces the first. This is the registration the module
    docstring above explains.

    The decorator ties the name a flow writes to the checking function, so the folder ``core`` can find it, as the module
    docstring above explains."""
    def _decorate(fn: AnalyzerFn) -> AnalyzerFn:
        """Store ``fn`` under ``RegisteredName`` and return it. This is the decorator ``register`` above returns."""
        ANALYZER_REGISTRY[RegisteredName] = fn
        return fn
    return _decorate


def GetAnalyzer(RegisteredName: str) -> AnalyzerFn | None:
    """Return the analyzer function registered under ``RegisteredName``, or ``None`` when no imported module has
    registered it. ``GetAnalyzer`` imports nothing. ``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` calls it for
    every name in the pragmatic state's ``pActiveAnalyzersState`` and skips a name it returns ``None`` for.

    When a user turn arrives, the code in the folder ``core`` that runs the conversation must find, for the current
    state of the written flow, the checking functions in the folder ``analyzers`` that change nothing themselves and
    only return whether questions were answered and whether the state may be left. This lookup is the one step between the
    name the flow wrote and that function."""
    return ANALYZER_REGISTRY.get(RegisteredName)


def ImportAnalyzer(RegisteredName: str):
    """Import every analyzer module through ``ImportAllAnalyzers`` and return the module whose function is registered
    under ``RegisteredName``. ``ImportAnalyzer`` raises ``ModuleNotFoundError`` with the text "no analyzer module registers" followed
    by the name when no module registers it.
    ``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader._static_prompt_for`` calls it to read
    the module's ``PROMPT`` or ``IncrementalPromptPickQuestion`` constant for a card.

    The folder ``server`` turns the record of a finished or running conversation into cards a person can read, and a
    card about a check sometimes needs the prompt that check sends to the language model. This function lets that
    folder reach from a registered name in the record to the module in the folder ``analyzers`` that holds the prompt,
    without the folder ``server`` knowing any analyzer's file."""
    import sys
    fn = ImportAllAnalyzers().get(RegisteredName)
    if fn is None:
        raise ModuleNotFoundError(f"no analyzer module registers {RegisteredName!r}")
    return sys.modules[fn.__module__]


def ImportAllAnalyzers() -> dict[str, "AnalyzerFn"]:
    """Import every module under ``illocutionary_lifecycles/analyzers`` and its subfolders, skipping modules whose name
    starts with an underscore, so that each analyzer module registers itself, and return ``ANALYZER_REGISTRY``. Called
    by ``ImportAnalyzer`` and ``RequireAnalyzers`` in this module. A module placed under the folder is imported by it
    without any list being edited, but it runs as a transition criterion or as a question checker only when its
    registered name has the ending this module's docstring names.

    Before a conversation with a language model can start from its written flow, every checking function the flow
    names must have registered itself, and a function registers itself only when its module is imported. This function
    is how the folder ``analyzers`` imports all of its own modules at once, so neither the folder ``core`` nor the flow
    has to list them."""
    import illocutionary_lifecycles.analyzers as pkg
    for info in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if info.name.rsplit(".", 1)[-1].startswith("_"):
            continue
        importlib.import_module(info.name)
    return ANALYZER_REGISTRY


def RequireAnalyzers(RegisteredNames) -> None:
    """Import every analyzer module through ``ImportAllAnalyzers`` and raise ``LookupError`` when a non-empty name in
    ``RegisteredNames`` is not registered, returning ``None`` when every name is registered. The error text begins
    "the flow names analyzers that are not in the package", lists the missing names and the registered names, and says
    that a flow names an analyzer by its registered name and that a transition criterion's name must end in
    ``ConversationStateTransitionCriteria``.
    ``illocutionary_lifecycles.core.ConversationInit.RegisterSessionAnalyzers`` calls it at session start with the
    names ``illocutionary_lifecycles.core.ConversationInit.ConversationInitAnalyzerCollection`` collects from the
    flow, so a session whose flow names a missing analyzer does not start.

    A session is one conversation between a user and a language model, run by the folder ``core`` from a flow whose
    questions and state changes are checked by functions in the folder ``analyzers``. A flow that named a function
    nobody registered would run with a check that never happens and a state that is never left, so this function stops
    the session at its start, before the folder ``server`` has sent any turn in, with an error that names what is
    missing."""
    registry = ImportAllAnalyzers()
    missing = [n for n in RegisteredNames if n and n not in registry]
    if missing:
        raise LookupError(
            f"the flow names analyzers that are not in the package: {missing}; registered: {sorted(registry)}. A flow names "
            "an analyzer by its registered name (the 'Analyzer' of a criteria entry, or an entry of a state's 'Analyzers' "
            "list), not by its file: for example QuestionsAnsweredConversationStateTransitionCriteria lives in "
            "analyzers/transition_analyzers/QuestionsAnsweredTransitionAnalyzer.py. To add one, put a file under "
            "illocutionary_lifecycles/analyzers/ that calls register(<name>); a transition criterion's name must end in "
            "'ConversationStateTransitionCriteria' to run as one.")
