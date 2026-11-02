"""The two reading-only storage vendors, registered as "local-readonly" and "cosmos-readonly", which are the "local"
and "cosmos" vendors with every write refused, so a stored conversation can be opened to be read and never appended to.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a finished one is often opened again only to be read, for review
or for the cards. This module, in ``illocutionary_lifecycles/memory/persistence``, makes that safe. Of the
package's four folders, ``core`` selects one of these vendors by name when a session is started with it, ``memory``
holds them, and ``analyzers`` and ``server`` never reach them. A ``SessionProvider`` started with ``memory_vendor``
set to "local-readonly" or "cosmos-readonly" loads the stored record and serves every read as usual, and its first
save raises ``ReadOnlyStoreError``, before anything is written, with the text that begins "read-only store", a colon
and "refusing to write", followed by the number of events and the session id.

Each class subclasses the writing vendor it reads like and replaces only ``save_persistent_batch``, so a new storage
vendor gets its reading-only subclass here, beside these two, in the same few lines.
"""
from __future__ import annotations

from illocutionary_lifecycles.memory.persistence.CosmosSaveLoad import CosmosSaveLoad
from illocutionary_lifecycles.memory.persistence.LocalConversationSaveLoad import LocalConversationSaveLoad


class ReadOnlyStoreError(RuntimeError):
    """The error a reading-only vendor raises on any write, a ``RuntimeError``, raised through ``Memory.drain`` to the
    code that made the save, as the module docstring above explains."""


def _refuse(SessionConversationId: str, RecordedEventBatch: list) -> None:
    """Raise ``ReadOnlyStoreError`` naming the number of events in ``RecordedEventBatch`` and the session
    ``SessionConversationId``. Called by ``save_persistent_batch`` of both classes in this module."""
    raise ReadOnlyStoreError(
        f"read-only store: refusing to write {len(RecordedEventBatch)} event(s) into {SessionConversationId!r}")


class LocalConversationSaveLoadReadOnly(LocalConversationSaveLoad):
    """The vendor registered as "local-readonly", which reads the files of ``LocalConversationSaveLoad`` exactly as
    that vendor does and refuses every write, as the module docstring above explains. The class is named for the vendor
    it reads like, and the registered name differs."""

    vendor_name = "local-readonly"

    def save_persistent_batch(self, SessionConversationId: str, RecordedEventBatch: list) -> None:
        """Raise ``ReadOnlyStoreError`` through ``_refuse`` in this module and write nothing."""
        _refuse(SessionConversationId, RecordedEventBatch)


class CosmosSaveLoadReadOnly(CosmosSaveLoad):
    """The vendor registered as "cosmos-readonly", which reads the documents of ``CosmosSaveLoad`` exactly as that
    vendor does and refuses every write, as the module docstring above explains. The class is named for the vendor it
    reads like, and the registered name differs."""

    vendor_name = "cosmos-readonly"

    def save_persistent_batch(self, SessionConversationId: str, RecordedEventBatch: list) -> None:
        """Raise ``ReadOnlyStoreError`` through ``_refuse`` in this module and write nothing."""
        _refuse(SessionConversationId, RecordedEventBatch)
