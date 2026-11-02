"""``AnsweredQuestionFacts``, one of the three stateless reads in ``illocutionary_lifecycles/memory/MemoryReadTools``,
which returns the answered questions found in recorded analyzer results.

A conversation run from a written flow keeps its questions outside the language model, and a server or a page may want
to know the moment one is answered. This function, in the folder ``memory``, finds those answers in the record, and
``illocutionary_lifecycles.core.session_provider.SessionProvider.RunAdapterCallbackHandlerEventsForRefreshSave`` in the
folder ``core`` sends one ``QuestionAnsweredAdapterCallbackHandlerEvent`` from each new one to the adapters of the
folder ``server``, while the results themselves come from the question checker in the folder ``analyzers``. The function
reads the result keys ``answered``, ``answer`` and ``choice``, so a change to those keys breaks it.
"""
from __future__ import annotations

from typing import Any


def AnsweredQuestionFacts(AnalyzerEventStream: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return one dict per result whose value has ``answered`` true, across the recorded ``AnalyzerEvent`` dicts in
    ``AnalyzerEventStream``, in recorded order, with ``answer`` holding the answer sentence, ``choice`` the chosen option
    or an empty string, ``AnalyzerType`` the registered name and ``AnalyzerInstance`` the run's ``AnalyzerId``.

    Any analyzer whose value reports ``answered`` true is included, not only the question checker. Entries that are
    not dicts are skipped. The caller keeps count of how many it has sent and sends only the newer ones, as the module
    docstring above explains.
    """
    Facts: list[dict[str, str]] = []
    for AnalyzerEntry in AnalyzerEventStream or []:
        if not isinstance(AnalyzerEntry, dict):
            continue
        for ResultValue in (AnalyzerEntry.get("results") or {}).values():
            value = (ResultValue or {}).get("value") or {}
            if not (isinstance(value, dict) and value.get("answered")):
                continue
            Facts.append({
                "answer": str(value.get("answer", "") or ""),
                "choice": str(value.get("choice", "") or ""),
                "AnalyzerType": str(ResultValue.get("AnalyzerType", "") or ""),
                "AnalyzerInstance": str(ResultValue.get("AnalyzerId", "") or ""),
            })
    return Facts
