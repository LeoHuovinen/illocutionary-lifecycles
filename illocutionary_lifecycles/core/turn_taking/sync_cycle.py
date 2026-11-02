"""The two cycles that call the analyzers, ``SyncCycle``, which runs the current state's analyzers on a finished user
turn in two passes, and ``DeferredIncrementalSettle``, which runs the incremental analyzer on the speech so far while
the user is still speaking.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the model never says whether a question was answered or whether the
state may be left, so these cycles, in the folder ``core``, are where the checking functions of the folder
``analyzers`` are called and their results handed to the refresher
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` and recorded in the folder ``memory``, while the
folder ``server`` receives the incremental picks as adapter callbacks. Neither cycle writes the pragmatic state
itself, and the refresher is the only writer they call. "Sync" in ``SyncCycle`` names the cycle that runs in step with
a finished turn, as opposed to the deferred one that nothing waits for.

``SyncCycle`` is called through ``PragmaticState.SyncCycle`` by
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing``. The first pass runs the question
checker once for every open question and every other analyzer of the state that is not a transition criterion, saves
each result as its own ``AnalyzerEvent``, has the refresher remove the answered questions and count the turn, and saves
the remembered answers and the state values. The second pass runs the transition criteria, which therefore see a
question answered by this utterance as answered and see the turn count including this turn, records every criterion
that reports done as a ``TransitionCriteriaEvent``, and has the refresher move the conversation by the lowest-positioned
entry that reported done. Which analyzer goes into which pass, and with which extra argument, is read from the ending
of its registered name, as ``illocutionary_lifecycles.analyzers.AnalyzerBase`` explains, and the result key is the
registered name followed by two colons and the position for a question checker or a listed criterion, and the
registered name alone otherwise. One turn therefore gives two refreshes, and more when the new state processes the
same utterance again, so a refresh index does not count turns.

An analyzer whose call takes longer than ``AnalyzerLLMCallTimeout``, 4.0 seconds, is dropped for the pass, changes
nothing, and the next utterance is analyzed afresh, and the constant is changed in this module's code, not by an
environment variable.

``DeferredIncrementalSettle`` is scheduled by
``illocutionary_lifecycles.core.session_provider.SessionProvider.IncrementalPhraseTick`` on every new interim
transcription, and nothing waits for it, so it never delays a reply. For every instance the current state declares
under ``incremental_phrase_instances``, every registered analyzer that carries ``RunsPerIncrementalPhraseInstance`` is
called once. Each result is recorded with the key made of the registered name, two colons and the instance's
identifier, so two analyzers of one instance never overwrite each other, handed to the refresher, and sent to the
adapters' handlers as an ``IncrementalPhraseAdapterCallbackHandlerEvent``, in that order and the moment its own model
call returns, so the next interim transcription reads this pick and a slow instance never delays a fast one. A pick of
"none" and an idempotent repeat are recorded and not sent. The tick's records are written to the storage vendor once,
after all its calls have returned.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable

# The longest one analyzer's model call may take in a pass, in seconds.
AnalyzerLLMCallTimeout = 4.0


async def DeferredIncrementalSettle(
    SystemState: Any,
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    IncrementalPhraseTickInputs: dict,
    RunAdapterCallbackHandlersForIncrementalPhraseResult: Any = None,
) -> None:
    """Run every analyzer that carries ``RunsPerIncrementalPhraseInstance`` once for every instance the current state
    declares, on the speech so far, and return ``None``, raising nothing.

    This is the settle the module docstring above explains, run while the user is still speaking. ``SystemState`` is
    the session's state, whose ``Record`` and ``PragmaticState`` are used, and nothing runs when either is missing.
    ``IncrementalPhraseTickInputs`` is the dict whose key ``IncrementalPhrase`` holds the speech so far, and nothing runs
    when that is empty or when the pragmatic field ``pIncrementalPhraseInstancesState``, copied from the state's
    ``incremental_phrase_instances``, is empty, so a session whose state declares no instance runs nothing and sessions
    never run each other's instances. An instance without an ``identifier`` is skipped. ``UserMemoryFace`` and
    ``WindowFace`` are accepted for the same shape as ``SyncCycle`` and are not passed to the analyzers, which receive
    the pragmatic state, an ``IncrementalPhrase`` and an ``IncrementalPhraseInstanceDeclaration``.

    Each result whose value is not empty is saved as its own ``AnalyzerEvent`` with ``analyzed_utterance_idx`` set to
    ``-1``, because the utterance is not finished, without writing to the storage vendor yet. The refresher then keeps
    it, when the registered name contains ``IncrementalPhrase``, on ``p<AnalyzerType>State`` under the instance's
    identifier, counting no turn. Then ``RunAdapterCallbackHandlersForIncrementalPhraseResult``, which
    ``SessionProvider.IncrementalPhraseTick`` passes as the provider's method of that name, is awaited with the
    registered name, the identifier, the value and the speech so far, unless the pick is "none" with no open gate or
    is a repeat. After every call has returned, the record is written to the storage vendor once. An error in an
    analyzer or in a handler ends that part without raising.
    """
    Record = getattr(SystemState, "Record", None)
    PragmaticState = getattr(SystemState, "PragmaticState", None)
    if Record is None or PragmaticState is None:
        return
    SpokenPhraseSoFar = IncrementalPhraseTickInputs.get("IncrementalPhrase")   # the phrase so far on this tick
    Calls: list = []

    # An incremental phrase instance is one entry of the current flow state's ``incremental_phrase_instances`` list
    # (identifier, IncrementalAnalyzerChoicesPrompt, IncrementalPromptSubjectKeywords, IncrementalPromptRequestKeywords,
    # RequiresGate, Idempotent), kept on the pragmatic state as ``pIncrementalPhraseInstancesState``. Every registered
    # analyzer marked ``RunsPerIncrementalPhraseInstance`` is called once per such entry. The entries are this
    # session's flow state's own, so a session whose state has no entries runs nothing here.
    async def RunIncrementalPhraseInstanceAdapterCallbackHandlers(Call, IncrementalPhraseInstanceIdentifier):
        """Await ``Call``, one analyzer's call for the instance ``IncrementalPhraseInstanceIdentifier``, then record its
        result, hand it to the refresher and send it to the handlers, and return the ``AnalysisResult``. Doing this per
        call and not after the whole settle is what lets a fast instance's pick be sent and read before a slow one
        returns, as ``DeferredIncrementalSettle`` above explains."""
        # 1. The instance's own model call returns its AnalysisResult.
        Result = await Call
        AnalyzerResultValue = getattr(Result, "value", None)
        # 2. An empty value (nothing picked, gate closed, model late) runs no callback handler.
        Empty = not isinstance(AnalyzerResultValue, dict) or all(v in (None, "", []) for v in AnalyzerResultValue.values())
        if Empty:
            return Result
        # 3. The result is recorded and the refresher places it on the pragmatic state now, per result, so the next
        #    tick's call for this instance reads this pick (and not the previous settle's). The refresher, called just
        #    below, is the only writer of the pragmatic state; nothing here writes it directly.
        Keyed = {
            f"{Result.AnalyzerType}::{IncrementalPhraseInstanceIdentifier}": {
                "success": True, "value": AnalyzerResultValue, "AnalyzerType": Result.AnalyzerType,
                "AnalyzerId": IncrementalPhraseInstanceIdentifier, "prompt": "",
            }
        }
        if hasattr(Record, "UpsertAnalyzerEvent"):
            Record.UpsertAnalyzerEvent(results=Keyed, analyzed_utterance_idx=-1,
                                       PragmaticAnalyzerType=Result.AnalyzerType,
                                       PragmaticAnalyzerInstance=IncrementalPhraseInstanceIdentifier,
                                       drain=False)          # one vendor write per tick, below
        if "IncrementalPhrase" in Result.AnalyzerType:
            PragmaticState.Refresher(SystemState, analyzer_results=Keyed, TurnCounter=False)
        # 4. The adapters' callback handlers run with the result, unless it is a repeat of an idempotent instance's
        #    pick or a pick of none: nothing listens for those.
        IsRepeat = bool(AnalyzerResultValue.get("repeat"))
        IsQuiet = AnalyzerResultValue.get("category") in (None, "", "none") and not AnalyzerResultValue.get("gate")
        if RunAdapterCallbackHandlersForIncrementalPhraseResult is not None and not IsRepeat and not IsQuiet:
            try:
                await RunAdapterCallbackHandlersForIncrementalPhraseResult(Result.AnalyzerType, IncrementalPhraseInstanceIdentifier, AnalyzerResultValue,
                                                      str(SpokenPhraseSoFar or ""))
            except Exception:
                pass
        return Result

    IncrementalPhraseInstanceDeclarations = list(getattr(PragmaticState, "pIncrementalPhraseInstancesState", None) or [])
    if SpokenPhraseSoFar and IncrementalPhraseInstanceDeclarations:
        from illocutionary_lifecycles.analyzers.AnalyzerBase import (
            ANALYZER_REGISTRY,
            IncrementalPhraseInstanceDeclaration,
            IncrementalPhrase,
        )
        for IncrementalPhraseInstanceAnalyzerName, IncrementalPhraseInstanceAnalyzer in list(ANALYZER_REGISTRY.items()):
            if not getattr(IncrementalPhraseInstanceAnalyzer, "RunsPerIncrementalPhraseInstance", False):
                continue
            for IncrementalPhraseInstanceEntry in IncrementalPhraseInstanceDeclarations:
                IncrementalPhraseInstanceIdentifier = str(IncrementalPhraseInstanceEntry.get("identifier") or "").strip()
                if not IncrementalPhraseInstanceIdentifier:
                    continue
                Calls.append(RunIncrementalPhraseInstanceAdapterCallbackHandlers(
                    IncrementalPhraseInstanceAnalyzer(
                        PragmaticState,
                        IncrementalPhrase(SpokenPhraseSoFar=SpokenPhraseSoFar,
                                          InstanceIdentifier=IncrementalPhraseInstanceIdentifier),
                        IncrementalPhraseInstanceDeclaration(
                            IncrementalAnalyzerChoicesPrompt=tuple(str(Option) for Option in (IncrementalPhraseInstanceEntry.get("IncrementalAnalyzerChoicesPrompt") or ())),
                            IncrementalPromptSubjectKeywords=str(IncrementalPhraseInstanceEntry.get("IncrementalPromptSubjectKeywords") or ""),
                            IncrementalPromptRequestKeywords=str(IncrementalPhraseInstanceEntry.get("IncrementalPromptRequestKeywords") or ""),
                            RequiresGate=bool(IncrementalPhraseInstanceEntry.get("RequiresGate")),
                            Idempotent=bool(IncrementalPhraseInstanceEntry.get("Idempotent", True)))),
                    IncrementalPhraseInstanceIdentifier))

    if not Calls:
        return
    try:
        # The caller that scheduled this call continues before any analyzer runs. Each result is recorded, placed on
        # the pragmatic state and handed to the handlers by its own wrapper above, the moment its call returns.
        await asyncio.sleep(0)
        await asyncio.gather(*Calls)
    except Exception:
        return
    if hasattr(Record, "drain"):
        Record.drain()                                   # the tick's recorded results, in one vendor write


async def SyncCycle(
    SystemState: Any,
    UserMemoryFace: Callable[..., Any],
    WindowFace: Callable[..., Any],
    skip_TransitionCriteria: bool = False,
    UserUtteranceIdx: int = -1,
) -> dict[str, Any]:
    """Run the current state's analyzers on the latest user utterance in the two passes the module docstring above
    explains, and return a dict of every result of both passes by result key, plus the key ``ConversationStateAdvanced``
    holding whether either pass moved the conversation to another state.

    ``SystemState`` is the session's state, and a missing ``PragmaticState`` returns only that key set to false. The
    analyzer names are read from ``pActiveAnalyzersState`` when the call starts, so a call made after a move runs the
    new state's analyzers, and a name nothing registered is skipped. ``UserMemoryFace`` and ``WindowFace`` are the two
    callables passed to every analyzer, which return the remembered answers and the current state's utterances.
    ``skip_TransitionCriteria``, when true, runs no transition criterion, so the conversation cannot leave its state in
    this call. ``UserUtteranceIdx`` is the refresh index of the user utterance analyzed, saved with every
    ``AnalyzerEvent``, and ``-1`` when there is none. Called by
    ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing`` through the pragmatic state's
    ``SyncCycle`` field.
    """
    from illocutionary_lifecycles.analyzers.AnalyzerBase import GetAnalyzer

    PragmaticState = getattr(SystemState, "PragmaticState", None)
    if PragmaticState is None:
        return {"ConversationStateAdvanced": False}

    ActiveIds = getattr(PragmaticState, "pActiveAnalyzersState", None) or []
    Resolved = [(AnalyzerId, GetAnalyzer(AnalyzerId)) for AnalyzerId in ActiveIds]
    Resolved = [(AnalyzerId, Analyzer) for AnalyzerId, Analyzer in Resolved if Analyzer is not None]

    # An analyzer whose name ends in ``QuestionCompleteCriteria`` is a question checker and runs
    # once for every open question. The refresher reads its results by the same rule.

    # Pass 1: everything except the transition criteria. Pass 2: the transition criteria.
    PragmaticUtteranceAnalyzers = [
        (active_id, analyzer) for active_id, analyzer in Resolved
        if not active_id.endswith("ConversationStateTransitionCriteria")
    ]
    ConversationStateTransitionAnalyzers = [] if skip_TransitionCriteria else [
        (active_id, analyzer) for active_id, analyzer in Resolved
        if active_id.endswith("ConversationStateTransitionCriteria")
    ]

    async def RunActiveAnalyzersAndRefresh(
        ActiveAnalyzers: list, TurnCounter: bool,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Run one pass and return a pair, the pass's results by result key and the dict the refresher returned.

        ``ActiveAnalyzers`` is the list of pairs of registered name and function for this pass, and ``TurnCounter``
        is whether this pass's refresh counts the user turn, true for the first pass only, so one utterance is counted
        once. The pass calls the analyzers at the same time, each capped at ``AnalyzerLLMCallTimeout``, saves each
        result as its own ``AnalyzerEvent``, saves a ``TransitionCriteriaEvent`` for every listed criterion that
        reported done, calls the refresher, and saves the remembered answers and the state values through
        ``SystemState.SaveRefreshResult``. The refresher is called even when no analyzer ran, because it also counts
        the turn. Each pass of the enclosing ``SyncCycle`` is one call of this function.
        """
        Calls = []
        RemainingNow = len(list(getattr(PragmaticState, "pConversationStateRemainingQuestions", None) or []))
        TransitionEntries = getattr(PragmaticState, "pConversationStateTransitionCriteriaListState", None)
        for ActiveId, Analyzer in ActiveAnalyzers:
            if ActiveId.endswith("QuestionCompleteCriteria"):
                for Ordinal in range(RemainingNow):
                    Calls.append(Analyzer(UserMemoryFace, WindowFace, PragmaticState, Ordinal))
            elif (TransitionEntries is not None
                  and ActiveId.endswith("ConversationStateTransitionCriteria")):
                continue
            else:
                Calls.append(Analyzer(UserMemoryFace, WindowFace, PragmaticState))

        # A state's ordered list of transition criteria: each entry gets one run of the
        # criterion it names, with the entry's position. Two entries that name the same
        # criterion are two runs.
        if TransitionEntries is not None:
            ResolvedByName = dict(ActiveAnalyzers)
            for TransitionOrdinal, TransitionEntry in enumerate(TransitionEntries):
                EntryAnalyzer = ResolvedByName.get(str((TransitionEntry or {}).get("Analyzer", "")))
                if EntryAnalyzer is not None:
                    Calls.append(EntryAnalyzer(
                        UserMemoryFace, WindowFace, PragmaticState, TransitionOrdinal))

        async def CappedAnalyzerLLMCall(AnalyzerCall: Any) -> Any:
            """Return the result of ``AnalyzerCall``, or ``None`` when it takes longer than ``AnalyzerLLMCallTimeout``
            seconds, in which case the pass leaves that analyzer out and nothing changes because of it, as the
            module docstring above explains."""
            try:
                return await asyncio.wait_for(AnalyzerCall, timeout=AnalyzerLLMCallTimeout)
            except asyncio.TimeoutError:
                return None

        Results = await asyncio.gather(*(CappedAnalyzerLLMCall(Call) for Call in Calls)) if Calls else []

        ActiveAnalyzerResults: dict[str, Any] = {}
        for Result in Results:
            if Result is None:
                continue
            if Result.AnalyzerType.endswith("QuestionCompleteCriteria"):
                # The run's id names the question it analyzed, so the memory written from it
                # and the answered-question adapter callback can be traced back to this run.
                ActiveAnalyzerResults[f"{Result.AnalyzerType}::{Result.WithinConversationStateOrdinal}"] = {
                    "success": True,
                    "value": Result.value,
                    "AnalyzerType": Result.AnalyzerType,
                    "AnalyzerId": getattr(Result, "AnalyzerId", "")
                    or f"{Result.AnalyzerType}::{Result.WithinConversationStateOrdinal}",
                    "WithinConversationStateOrdinal": Result.WithinConversationStateOrdinal,
                    "prompt": getattr(Result, "prompt", "") or "",
                }
                continue
            if (Result.AnalyzerType.endswith("ConversationStateTransitionCriteria")
                    and Result.WithinConversationStateOrdinal >= 0):
                ActiveAnalyzerResults[f"{Result.AnalyzerType}::{Result.WithinConversationStateOrdinal}"] = {
                    "success": True,
                    "value": Result.value,
                    "AnalyzerType": Result.AnalyzerType,
                    "AnalyzerId": getattr(Result, "AnalyzerId", "") or Result.AnalyzerType,
                    "WithinConversationStateOrdinal": Result.WithinConversationStateOrdinal,
                    "prompt": getattr(Result, "prompt", "") or "",
                }
                continue
            ActiveAnalyzerResults[Result.AnalyzerType] = {
                "success": True,
                "value": Result.value,
                "AnalyzerType": Result.AnalyzerType,
                "AnalyzerId": getattr(Result, "AnalyzerId", "") or Result.AnalyzerType,
                "prompt": getattr(Result, "prompt", "") or "",
            }

        # Each result is saved as its own analyzer event, before the refresh.
        Record = getattr(SystemState, "Record", None)
        if Record is not None and hasattr(Record, "UpsertAnalyzerEvent"):
            StampedAnalyzerEventIdx: dict[str, int] = {}
            for ResultKey, ResultEntry in ActiveAnalyzerResults.items():
                StampedAnalyzerEventIdx[ResultKey] = Record.UpsertAnalyzerEvent(
                    results={ResultKey: ResultEntry},
                    analyzed_utterance_idx=UserUtteranceIdx if UserUtteranceIdx is not None else -1,
                    PragmaticAnalyzerType=ResultEntry.get("AnalyzerType"),
                    PragmaticAnalyzerInstance=ResultEntry.get("AnalyzerId") or ResultKey,
                )
            # Every criterion from a state's ordered list that reports done is recorded, before
            # the refresher takes the first that moves the conversation.
            if hasattr(Record, "UpsertTransitionCriteriaEvent"):
                for ResultKey, ResultEntry in ActiveAnalyzerResults.items():
                    TriggerOrdinal = ResultEntry.get("WithinConversationStateOrdinal")
                    if (isinstance(TriggerOrdinal, int) and TriggerOrdinal >= 0
                            and str(ResultEntry.get("AnalyzerType", "")).endswith(
                                "ConversationStateTransitionCriteria")
                            and (ResultEntry.get("value") or {}).get("done")):
                        Record.UpsertTransitionCriteriaEvent(
                            AnalyzerType=str(ResultEntry.get("AnalyzerType", "")),
                            WithinConversationStateOrdinal=TriggerOrdinal,
                            analyzer_event_idx=StampedAnalyzerEventIdx.get(ResultKey, -1),
                        )

        RefreshOutcome = PragmaticState.Refresher(
            SystemState, analyzer_results=ActiveAnalyzerResults, TurnCounter=TurnCounter,
        ) or {}

        # The refreshed state values and the new memories are saved after every refresh.
        if hasattr(SystemState, "SaveRefreshResult"):
            SystemState.SaveRefreshResult(analyzer_results=ActiveAnalyzerResults)
        return ActiveAnalyzerResults, RefreshOutcome

    # Only pass 1 counts the user turn, so one utterance is counted once.
    analyzer_results: dict[str, Any] = {}
    PassOneResults, PassOneOutcome = await RunActiveAnalyzersAndRefresh(PragmaticUtteranceAnalyzers, True)
    analyzer_results.update(PassOneResults)
    PassTwoResults, PassTwoOutcome = await RunActiveAnalyzersAndRefresh(ConversationStateTransitionAnalyzers, False)
    analyzer_results.update(PassTwoResults)
    analyzer_results["ConversationStateAdvanced"] = bool(
        PassOneOutcome.get("ConversationStateAdvanced") or PassTwoOutcome.get("ConversationStateAdvanced")
    )
    return analyzer_results
