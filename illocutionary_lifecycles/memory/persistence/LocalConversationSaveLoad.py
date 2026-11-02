"""The storage vendor registered as "local", ``LocalConversationSaveLoad``, which keeps every recorded event of a
conversation as one JSON file on the local disk, and which replaces "cosmos" for any session.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record, kept by the folder ``memory``, is written here when a
session names "local", so the conversation can be read back after the process ends. Of the package's four folders,
``core`` selects this vendor by name at session start, ``memory`` holds it and writes to it through ``Memory.drain``,
and ``analyzers`` and ``server`` never reach it. The vendor needs no database or service.

Each event is the file named by its position followed by .json, in the folder events inside the folder named by the
session id inside the directory the session passes as ``vendor_session_address``. The position is the event's place in
the stored record, counted from 0 by counting the files already there at every write, which is correct while one
process writes one session. "local-readonly" in ``illocutionary_lifecycles.memory.persistence.ReadOnlySaveLoad`` reads
the same files and refuses every write. The interface is explained in
``illocutionary_lifecycles.memory.persistence.PersistentSaveLoadBase``.
"""
from __future__ import annotations

import dataclasses
import json
import os
from typing import Any

from illocutionary_lifecycles.memory.persistence.PersistentSaveLoadBase import (
    PersistentSaveLoadBase,
)


class LocalConversationSaveLoad(PersistentSaveLoadBase):
    """The "local" vendor, which stores each conversation's events as files under one directory, as the module
    docstring above explains."""

    vendor_name = "local"

    def __init__(self, directory: str) -> None:
        """Keep ``directory``, the directory that holds one folder per session, and raise ``ValueError`` beginning
        "memory_vendor 'local' needs vendor_session_address" when it is not a non-empty string. The directory is
        created on the first write, as the module docstring above explains."""
        if not isinstance(directory, str) or not directory:
            raise ValueError(
                f"memory_vendor 'local' needs vendor_session_address: the directory that holds one folder per session; got "
                f"{directory!r}. The record of each session is written as one JSON file per event under "
                "<directory>/<session_id>/events/, and read back from there when the session is reopened "
                "(memory_vendor 'local-readonly' reads the same files and refuses to write). For example "
                "SessionProvider(..., memory_vendor='local', vendor_session_address='./sessions').")
        self._dir = directory

    def _events_dir(self, SessionConversationId: str) -> str:
        """Return the path of the folder that holds the event files of the conversation ``SessionConversationId``, used by
        the two methods of this class."""
        return os.path.join(self._dir, SessionConversationId, "events")

    def _next_seq(self, events_dir: str) -> int:
        """Return the position the next event gets, the number of .json files already in ``events_dir``, or 0 when the
        folder does not exist. Called by ``save_persistent_batch`` in this class."""
        if not os.path.isdir(events_dir):
            return 0
        return sum(1 for n in os.listdir(events_dir) if n.endswith(".json"))

    def save_persistent_batch(
        self, SessionConversationId: str, RecordedEventBatch: list[Any],
    ) -> None:
        """Write each event of ``RecordedEventBatch``, in order, as the next numbered JSON file of the conversation
        ``SessionConversationId``, with its fields and its ``CATEGORY``, creating the folder when needed, and return
        ``None``. This is the write the module docstring above describes."""
        events_dir = self._events_dir(SessionConversationId)
        os.makedirs(events_dir, exist_ok=True)
        seq = self._next_seq(events_dir)
        for event in RecordedEventBatch:
            stored = dataclasses.asdict(event)
            stored["CATEGORY"] = type(event).CATEGORY
            with open(os.path.join(events_dir, f"{seq}.json"), "w", encoding="utf-8") as f:
                json.dump(stored, f)
            seq += 1

    def read_persistent_batch(
        self, SessionConversationId: str,
    ) -> list[dict[str, Any]]:
        """Return the stored events of the conversation ``SessionConversationId`` as dicts, ordered by the number in each
        file's name, or an empty list when the conversation has no folder, as the module docstring above explains."""
        events_dir = self._events_dir(SessionConversationId)
        if not os.path.isdir(events_dir):
            return []
        names = sorted(
            (n for n in os.listdir(events_dir) if n.endswith(".json")),
            key=lambda n: int(n[: -len(".json")]),
        )
        out: list[dict[str, Any]] = []
        for name in names:
            with open(os.path.join(events_dir, name), encoding="utf-8") as f:
                out.append(json.load(f))
        return out
