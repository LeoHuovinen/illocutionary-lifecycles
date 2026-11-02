"""``MemoryWriter``, which records the remembered answers and the state values of one refresh under one shared refresh
index, and is the one place that chooses which analyzer results become remembered answers.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and an answer the question checker accepts is kept as a remembered
answer so later prompts can mention it. This module, in the folder ``memory``, makes that choice. Of the package's
four folders, ``core`` calls it through
``illocutionary_lifecycles.core.system_state.system_state.SystemState.SaveRefreshResult`` after every refresh, never
through the refresher, which saves nothing, ``analyzers`` produce the results it reads, and ``server`` learns of each
save from the adapter callback the session sends afterwards. The writer imports nothing from ``core`` or ``server``.
After each save it schedules a callable the session set on it, so the callback reaches the session's adapters without
this folder knowing them.
"""
from __future__ import annotations

from typing import Any

from illocutionary_lifecycles.memory.memory import (
    MemoryEvent,
    PragmaticStatesEvent,
)


class MemoryWriter:
    """The writer of one session's refreshes into that session's record, built by
    ``SystemState.InitializeMemoryClasses`` beside the ``Memory`` it writes to, as the module docstring above explains.

    ``RunAdapterCallbackHandlerEventsForRefreshSave`` holds an async callable with no arguments, which
    ``SessionProvider.start`` sets to its own method of that name, and which is scheduled without waiting after every
    save. ``None``, the value before the session starts, schedules nothing.
    """

    def __init__(self, memory: Any) -> None:
        """Keep ``memory``, the session's whole record, a ``Memory``, as the record every save goes to, as the class above describes."""
        self._memory = memory
        self.RunAdapterCallbackHandlerEventsForRefreshSave: Any = None

    def save_refresh_result(
        self,
        *,
        analyzer_results: dict[str, Any] | None = None,
        pragmatic_values: dict[str, Any] | None = None,
    ) -> None:
        """Record the remembered answers and the state values of one refresh under one shared refresh index, write them
        to the vendor, schedule the save callback, and return ``None``, doing nothing when there is nothing to record.

        ``analyzer_results`` is the dict of this refresh's analyzer results by result key. A result becomes a
        ``MemoryEvent`` when its ``success`` is true, its value's ``answered`` is true and its value's ``answer`` is a
        non-empty string, and the event holds the answer sentence, the registered name and the run's ``AnalyzerId``.
        ``pragmatic_values`` is the dict of the state values after the refresh, recorded as one ``PragmaticStatesEvent``,
        and ``None`` records none. The ``AnalyzerEvent`` entries themselves are recorded by the cycle, one per run. Called
        only by ``SystemState.SaveRefreshResult``, as the module docstring above explains.
        """
        events: list[Any] = []
        # A state that ignores remembered answers records none of its own either, so a later
        # state that reads them sees only the answers of the states that kept them.
        _ignoring = bool((pragmatic_values or {}).get("pIgnoreMemoriesState"))
        for entry in ([] if _ignoring else (analyzer_results or {}).values()):
            if not isinstance(entry, dict) or not entry.get("success"):
                continue
            value = entry.get("value")
            if not isinstance(value, dict) or not value.get("answered"):
                continue
            answer = value.get("answer")
            if not (isinstance(answer, str) and answer.strip()):
                continue
            events.append(MemoryEvent(
                memory={"answer": answer},
                PragmaticAnalyzerType=entry.get("AnalyzerType"),
                PragmaticAnalyzerInstance=entry.get("AnalyzerId") or "",
            ))
        if pragmatic_values is not None:
            events.append(PragmaticStatesEvent(values=pragmatic_values))
        if events:
            self._memory.UpsertRefreshEvents(events)
            self._memory.drain()
            # The adapter callback runs after the save, so handlers read events that include it.
            handlers_run = self.RunAdapterCallbackHandlerEventsForRefreshSave
            if handlers_run is not None:
                self._ScheduleAdapterCallbackHandlers(handlers_run)

    @staticmethod
    def _ScheduleAdapterCallbackHandlers(handlers_run: Any) -> None:
        """Schedule the async callable ``handlers_run`` on the running event loop, asyncio's scheduler, without waiting
        for it, and return ``None``, scheduling nothing when no event loop is running. Called only by
        ``save_refresh_result`` in this class."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(handlers_run())
