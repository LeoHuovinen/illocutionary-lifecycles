"""The one analyzer in ``illocutionary_lifecycles/analyzers/incremental_phrase_analyzers``, registered as
``IncrementalPhraseCategoryAnalyzer``, which picks one of an instance's declared option words from the words the user
has said since the last pick, while the user is still speaking.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and besides checking each finished turn it lets a flow state declare
words to listen for during speech, so that a connected page, app or robot can act before the turn ends, for example
turning when the user says "go left". This analyzer is that listening step, in the folder ``analyzers``, called by the
folder ``core``, with every pick recorded by the folder ``memory`` and sent by the folder ``server`` to the connected
program as an
``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerEvents.IncrementalPhraseAdapterCallbackHandlerEvent``.

``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` calls the function on every new
interim transcription, once for each entry of the current state's ``incremental_phrase_instances`` list, because the
function carries ``RunsPerIncrementalPhraseInstance`` set to true. The call passes three arguments, the pragmatic
state, an ``illocutionary_lifecycles.analyzers.AnalyzerBase.IncrementalPhrase`` with the speech so far and the
instance's identifier, and an ``illocutionary_lifecycles.analyzers.AnalyzerBase.IncrementalPhraseInstanceDeclaration``
with the instance's option words, subject keywords, request keywords, ``RequiresGate`` and ``Idempotent``. A command
word, a reaction to what the user says and a check for whether the user named one of several things are all this one
analyzer with different declared values.

The analyzer sends the model a prompt made of the option words, the subject keywords, the request keywords, the fixed
question in the module constant ``IncrementalPromptPickQuestion`` and only the words not analyzed before, through
``incremental_phrase_llm`` from ``illocutionary_lifecycles.core.clients.llm``, with temperature 0, at most
``MAX_REPLY_TOKENS`` tokens, which is 3, and a time limit of ``LLM_TIMEOUT_SECONDS``, which is 2.0 seconds. A reply that
is not exactly one of the option words, compared without case, picks nothing. When ``RequiresGate`` is true, the
analyzer first asks with ``IncrementalPromptGateQuestion`` whether the new words ask for a change, and asks for an
option only once the answer has been yes, which then holds for the rest of the utterance. Both question constants are
model text, and
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader._static_prompt_for`` shows the first on a
card.

What the analyzer has recorded for an instance in the current utterance, the words already analyzed under
``AnalyzedText``, the last picked option under ``category`` and an opened gate under ``gate``, is kept on the pragmatic
state in the field ``pIncrementalPhraseCategoryAnalyzerState``, under the instance's identifier, and nothing is kept on
the function, so nothing passes from one session to another. ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh``
writes that field from each result, and the analyzer only reads it. The already analyzed words are compared to the
start of the speech so far without case and without punctuation, so an STT's final transcription that only changes
capital letters or punctuation continues the same utterance. Speech that does not begin with the already analyzed
words is a new utterance, and everything recorded for the instance is dropped.
"""
from __future__ import annotations

import asyncio
from typing import Any

from illocutionary_lifecycles.analyzers.AnalyzerBase import (
    AnalysisResult,
    IncrementalPhraseInstanceDeclaration,
    IncrementalPhrase,
    register,
)
from illocutionary_lifecycles.core.clients.llm import incremental_phrase_llm

AnalyzerType = "IncrementalPhraseCategoryAnalyzer"

LLM_TIMEOUT_SECONDS = 2.0
MAX_REPLY_TOKENS = 3

IncrementalPromptPickQuestion = (
    "Which option does this speech fragment select? Answer none unless the fragment is asking "
    "for a change to the subject above. Judge meaning, not wording; the newest words win. "
    "Reply with one option word, or none."
)
IncrementalPromptGateQuestion = "Is this speech fragment asking for something to be changed? Reply yes or no."


_PUNCTUATION = str.maketrans("", "", ".,;:!?\"'“”‘’()[]-")


def _Words(text: str) -> list:
    """Return the words of ``text`` in lower case with the punctuation in ``_PUNCTUATION`` removed and empty words
    dropped, so that the analyzed words and the speech so far can be compared word by word. Called only by
    ``IncrementalPhraseCategoryAnalyzer`` in this module."""
    return [w for w in str(text or "").lower().translate(_PUNCTUATION).split() if w]


def IncrementalUtteranceStateOf(PragmaticState: Any, InstanceIdentifier: str) -> dict:
    """Return the dict this analyzer last recorded for the instance ``InstanceIdentifier``, read from the field
    ``pIncrementalPhraseCategoryAnalyzerState`` on ``PragmaticState``, or an empty dict when there is none or
    ``PragmaticState`` is ``None``. Called by ``IncrementalPhraseCategoryAnalyzer`` in this module to learn which words
    were already analyzed in the current utterance, as the module docstring above explains."""
    Field = getattr(PragmaticState, f"p{AnalyzerType}State", None) if PragmaticState is not None else None
    Placed = (Field or {}).get(InstanceIdentifier) if isinstance(Field, dict) else None
    return Placed if isinstance(Placed, dict) else {}


async def OneWord(OneWordPrompt: str) -> str:
    """Send ``OneWordPrompt`` to the client ``incremental_phrase_llm`` returns, with temperature 0 and at most
    ``MAX_REPLY_TOKENS`` tokens, and return the reply stripped of spaces and full stops and in lower case. Raises
    ``asyncio.TimeoutError`` when the model takes longer than ``LLM_TIMEOUT_SECONDS``, and the caller treats that as no
    pick. Called by ``IncrementalPhraseCategoryAnalyzer`` in this module for the gate question and the option question,
    as the module docstring above explains."""
    Reply = await asyncio.wait_for(
        incremental_phrase_llm().complete(OneWordPrompt, temperature=0.0, max_tokens=MAX_REPLY_TOKENS),
        timeout=LLM_TIMEOUT_SECONDS)
    return Reply.strip().strip(".").strip().lower()


@register(AnalyzerType)
async def IncrementalPhraseCategoryAnalyzer(
    PragmaticState: Any,
    IncrementalPhrase: IncrementalPhrase | None = None,
    InstanceDeclaration: IncrementalPhraseInstanceDeclaration | None = None,
) -> AnalysisResult:
    """Return an ``AnalysisResult`` with the option the new words pick for one instance, or with no pick.

    This function is the listening step the module docstring above explains, called by the settle in the folder
    ``core`` once per declared instance on every new interim transcription. ``PragmaticState`` is read for what was
    already recorded for the instance, ``IncrementalPhrase`` carries the speech so far and the instance's identifier, and
    ``InstanceDeclaration`` carries the instance's declared values, and when either of the last two is missing the
    function uses empty values.

    On a pick the value holds ``category``, the option word, and ``AnalyzedText``, the speech so far. When an instance
    with ``Idempotent`` true picks the option it already holds in this utterance, the value also holds ``repeat`` set
    to true, and the settle records it and does not send it. When a gated instance's gate has opened in this
    utterance, the value holds ``gate`` set to "open" beside either. When there are no option words, no new words, a
    closed gate, a reply that is no option or a model that did not answer in time, the value holds only ``category``
    set to ``None``, and the settle neither records nor sends it.
    """
    Spoken = (IncrementalPhrase.SpokenPhraseSoFar if IncrementalPhrase else "") or ""
    Identifier = (IncrementalPhrase.InstanceIdentifier if IncrementalPhrase else "") or ""
    IncrementalAnalyzerChoicesPrompt = [str(Option) for Option in ((InstanceDeclaration.IncrementalAnalyzerChoicesPrompt if InstanceDeclaration else ()) or ())]
    IncrementalPromptSubjectKeywords = (InstanceDeclaration.IncrementalPromptSubjectKeywords if InstanceDeclaration else "") or ""
    IncrementalPromptRequestKeywords = (InstanceDeclaration.IncrementalPromptRequestKeywords if InstanceDeclaration else "") or ""
    RequiresGate = bool(InstanceDeclaration.RequiresGate) if InstanceDeclaration else False
    Idempotent = bool(InstanceDeclaration.Idempotent) if InstanceDeclaration else True

    Own = IncrementalUtteranceStateOf(PragmaticState, Identifier)
    AnalyzedPhrase = str(Own.get("AnalyzedText", "") or "")
    AnalyzedPhraseWords = _Words(AnalyzedPhrase)
    if _Words(Spoken)[:len(AnalyzedPhraseWords)] != AnalyzedPhraseWords:
        Own, AnalyzedPhrase, AnalyzedPhraseWords = {}, "", []   # A new utterance: every recorded fact for this instance expires.
    # The cursor is in words, compared without case or punctuation, so an STT's final that recapitalises and
    # punctuates the interim ("i have a dog" then "I have a dog, at home.") continues the same utterance.
    AnalyzedPhraseNotYetAnalyzedWords = " ".join(Spoken.split()[len(AnalyzedPhraseWords):]).strip()
    if not IncrementalAnalyzerChoicesPrompt or not AnalyzedPhraseNotYetAnalyzedWords:
        return AnalysisResult(value={"category": None}, AnalyzerType=AnalyzerType)

    AnalyzerResultValue: dict = {}
    if RequiresGate:
        if Own.get("gate") == "open":
            AnalyzerResultValue["gate"] = "open"                      # latched for the rest of this utterance
        else:
            GatePrompt = (f"Request keywords: {IncrementalPromptRequestKeywords}\n" if IncrementalPromptRequestKeywords else "") + f"{IncrementalPromptGateQuestion}\nFragment: {AnalyzedPhraseNotYetAnalyzedWords}"
            try:
                Opened = (await OneWord(GatePrompt)).startswith("yes")
            except Exception:
                Opened = False
            if not Opened:
                return AnalysisResult(value={"category": None}, AnalyzerType=AnalyzerType)
            AnalyzerResultValue["gate"] = "open"
            AnalyzerResultValue["AnalyzedText"] = Spoken                # the gate opening is a recorded fact of this utterance

    Prompt = (
        f"Options: {'; '.join(IncrementalAnalyzerChoicesPrompt)}\n"
        + (f"Subject keywords: {IncrementalPromptSubjectKeywords}\n" if IncrementalPromptSubjectKeywords else "")
        + (f"Request keywords: {IncrementalPromptRequestKeywords}\n" if IncrementalPromptRequestKeywords else "")
        + f"{IncrementalPromptPickQuestion}\nFragment: {AnalyzedPhraseNotYetAnalyzedWords}"
    )
    try:
        Reply = await OneWord(Prompt)
        Chosen = next((Option for Option in IncrementalAnalyzerChoicesPrompt if Option.lower() == Reply), None)
    except Exception:
        Chosen = None
    if Chosen and Idempotent and Own.get("category") == Chosen:
        AnalyzerResultValue["AnalyzedText"] = Spoken                    # the same pick again in this utterance: the cursor moves, nothing is sent
        AnalyzerResultValue["category"] = Chosen
        AnalyzerResultValue["repeat"] = True
    elif Chosen:
        AnalyzerResultValue["category"] = Chosen
        AnalyzerResultValue["AnalyzedText"] = Spoken                    # the speech counts as analyzed only when an option was picked
    elif "gate" not in AnalyzerResultValue:
        return AnalysisResult(value={"category": None}, AnalyzerType=AnalyzerType, prompt=Prompt)
    return AnalysisResult(value=AnalyzerResultValue, AnalyzerType=AnalyzerType, prompt=Prompt)


IncrementalPhraseCategoryAnalyzer.RunsPerIncrementalPhraseInstance = True   # the incremental phrase settle calls it once per entry of the state's incremental_phrase_instances
