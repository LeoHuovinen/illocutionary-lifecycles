"""``PersistentSaveLoadBase``, the interface every storage vendor implements, the registry of vendors by
``vendor_name``, and ``build_persistent_connection``, which builds the vendor a session names.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record, kept by the folder ``memory``, is stored beyond the
process by a vendor this module defines the shape of. Of the package's four folders, ``core`` calls
``build_persistent_connection`` from
``illocutionary_lifecycles.core.system_state.system_state.SystemState.InitializeMemoryClasses``, ``memory`` holds
every vendor and the ``Memory`` that calls them, and ``analyzers`` and ``server`` never reach a vendor.

A vendor does two things, it appends a batch of recorded events to one conversation's stored record, and it returns
that conversation's stored events. A vendor does not filter, order or interpret them, and ``Memory`` reads it once, at
session start, and then only writes to it. Two rules follow from the recorded event classes. ``dataclasses.asdict``
leaves out class attributes, so a vendor stores each event's ``CATEGORY`` with it under the key "CATEGORY". Several
events share one refresh index, so a stored event is named by its position in the stored record, counted at every
write, and not by its category and index.

The vendors in the package are "local" in ``illocutionary_lifecycles.memory.persistence.LocalConversationSaveLoad``,
"cosmos" in ``illocutionary_lifecycles.memory.persistence.CosmosSaveLoad``, and their reading-only subclasses
"local-readonly" and "cosmos-readonly" in ``illocutionary_lifecycles.memory.persistence.ReadOnlySaveLoad``, which raise
``ReadOnlyStoreError`` on the first save. A session serves the same way whichever vendor it has, since ``Memory`` never
asks which. A new vendor is one module in this folder with a subclass that sets ``vendor_name``, which registers it,
and implements both abstract methods, imported in this folder's ``__init__.py``, with a reading-only subclass beside
the two in ``ReadOnlySaveLoad``. A session then selects it by that name.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


# Every storage vendor class, by ``vendor_name``.
_VENDOR_REGISTRY: dict[str, type["PersistentSaveLoadBase"]] = {}


class PersistentSaveLoadBase(ABC):
    """The base class of every storage vendor, as the module docstring above explains.

    A subclass sets ``vendor_name``, the registered name a session selects it by, and implements
    ``save_persistent_batch`` and ``read_persistent_batch``, and a subclass that lacks either method cannot be
    instantiated. ``build_persistent_connection`` constructs a subclass with one argument, the session's
    ``vendor_session_address``.
    """

    vendor_name: str | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register every subclass that sets a non-empty ``vendor_name`` in ``_VENDOR_REGISTRY`` under that name, when
        the subclass is defined, so a vendor needs no list to be edited, and a later subclass with the same name
        replaces the earlier one. This is the registration the module docstring above explains."""
        super().__init_subclass__(**kwargs)
        if getattr(cls, "vendor_name", None):
            _VENDOR_REGISTRY[cls.vendor_name] = cls

    @abstractmethod
    def save_persistent_batch(
        self, SessionConversationId: str, RecordedEventBatch: list[Any],
    ) -> None:
        """Append the recorded event objects in ``RecordedEventBatch``, in order, to the stored record of the
        conversation ``SessionConversationId``, each with its fields and its ``CATEGORY``, and return ``None``. Called by
        ``Memory.drain`` and ``Memory.UpsertConversationInitEvent`` in ``illocutionary_lifecycles.memory.memory``."""
        raise NotImplementedError

    @abstractmethod
    def read_persistent_batch(
        self, SessionConversationId: str,
    ) -> list[dict[str, Any]]:
        """Return the stored events of the conversation ``SessionConversationId`` as dicts of their fields with the key
        "CATEGORY", in stored order, or an empty list when nothing is stored. Called by ``ReadCache.build`` in
        ``illocutionary_lifecycles.memory.memory`` at session start."""
        raise NotImplementedError


def build_persistent_connection(
    StorageVendorName: str | None,
    StorageVendorAddress: Any = None,
) -> PersistentSaveLoadBase | None:
    """Return an instance of the vendor registered as ``StorageVendorName``, built with ``StorageVendorAddress``, or
    ``None`` when ``StorageVendorName`` is ``None`` or empty, so the record is kept only in the running process.

    ``StorageVendorAddress`` is where the vendor stores, in the form that vendor takes, a directory path for the local
    vendors and a dict with the key ``prefix`` for the Cosmos DB ones. A name that is not registered raises
    ``KeyError`` with the text "unknown persistence vendor" followed by the name and the registered names, and a
    vendor's own constructor raises for a wrong address. Called only by ``SystemState.InitializeMemoryClasses`` at
    session start, as the module docstring above explains.
    """
    if not StorageVendorName:
        return None
    cls = _VENDOR_REGISTRY.get(StorageVendorName)
    if cls is None:
        raise KeyError(
            f"unknown persistence vendor {StorageVendorName!r}; "
            f"known: {sorted(_VENDOR_REGISTRY)}"
        )
    return cls(StorageVendorAddress)
