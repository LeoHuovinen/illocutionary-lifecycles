"""The storage vendor registered as "cosmos", ``CosmosSaveLoad``, which keeps every recorded event of a conversation as
one document in an Azure Cosmos DB container, and which replaces "local" for any session.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record, kept by the folder ``memory``, is written here when a
session names "cosmos", so many conversations on several servers can be kept in one database. Of the package's four
folders, ``core`` selects this vendor by name at session start and supplies ``Required`` for its settings, ``memory``
holds it and writes to it through ``Memory.drain``, and ``analyzers`` and ``server`` never reach it.

Each event is one document in the container named by the address's ``prefix`` followed by _state, partitioned by the
field ``chat_id``, which holds the session id. A document's id is the session id, two colons and the event's position,
and the position is counted at every write by asking the container how many documents the session has. The documents
are read back ordered by that position, because Cosmos DB's own timestamp ``_ts`` has a resolution of one second and
cannot order events written in the same second. "cosmos-readonly" in
``illocutionary_lifecycles.memory.persistence.ReadOnlySaveLoad`` reads the same documents and refuses every write.

The connection is read on first use from three required variables, ``COSMOS_ENDPOINT``, the address of the Cosmos DB
account, ``COSMOS_KEY``, that account's key, and ``COSMOS_DATABASE``, the database that holds the container, written in
the server's ``.env`` as NAME=value lines, for example COSMOS_DATABASE=conversations. A missing one raises the
``RuntimeError`` of ``illocutionary_lifecycles.core.environment.Required``. The ``azure-cosmos`` package, installed by
the package's ``cosmos`` extra, is imported on first use, and the container is created when it is missing.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from illocutionary_lifecycles.memory.persistence.PersistentSaveLoadBase import (
    PersistentSaveLoadBase,
)


class CosmosSaveLoad(PersistentSaveLoadBase):
    """The "cosmos" vendor, which stores each conversation's events as documents in one Cosmos DB container, as the
    module docstring above explains."""

    vendor_name = "cosmos"

    def __init__(self, address: Any) -> None:
        """Keep ``address``, a dict whose key ``prefix`` names the container, and connect nothing yet. A wrong address
        raises only on the first read or write, from ``_get_container`` in this class."""
        self._address = address or {}
        self._container = None

    def _get_container(self) -> Any:
        """Return the container, connecting and creating it when it is missing on the first call and reusing it after.
        Raises ``ValueError`` beginning "memory_vendor 'cosmos' needs vendor_session_address" when the address has no
        non-empty ``prefix``, and the ``RuntimeError`` of ``Required`` when ``COSMOS_ENDPOINT``, ``COSMOS_KEY`` or
        ``COSMOS_DATABASE`` is missing, as the module docstring above explains."""
        if self._container is not None:
            return self._container
        from illocutionary_lifecycles.core.environment import Required
        prefix = (self._address or {}).get("prefix") if isinstance(self._address, dict) else None
        if not isinstance(prefix, str) or not prefix.strip():
            raise ValueError(
                "memory_vendor 'cosmos' needs vendor_session_address={'prefix': <name>}: each session's events become documents "
                "in the container <prefix>_state of the database COSMOS_DATABASE, partitioned by the session id; the container "
                f"is created on first use. Got {self._address!r}.")
        endpoint = Required("COSMOS_ENDPOINT", "the Cosmos DB account the record is stored in")
        key = Required("COSMOS_KEY", "the key of that Cosmos DB account")
        database = Required("COSMOS_DATABASE", f"the database that holds the container {prefix}_state")
        from azure.cosmos import CosmosClient, PartitionKey
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database)
        self._container = db.create_container_if_not_exists(
            id=f"{prefix}_state",
            partition_key=PartitionKey(path="/chat_id"),
        )
        return self._container

    def _next_seq(self, container: Any, SessionConversationId: str) -> int:
        """Return the position the next event of ``SessionConversationId`` gets, the number of its documents already in
        ``container``, which costs one count query per write. Called by ``save_persistent_batch`` in this class."""
        rows = list(container.query_items(
            query="SELECT VALUE COUNT(1) FROM c WHERE c.chat_id=@cid",
            parameters=[{"name": "@cid", "value": SessionConversationId}],
            partition_key=SessionConversationId,
        ))
        return int(rows[0]) if rows else 0

    def save_persistent_batch(
        self, SessionConversationId: str, RecordedEventBatch: list[Any],
    ) -> None:
        """Write each event of ``RecordedEventBatch``, in order, as the next document of the conversation
        ``SessionConversationId``, with its fields, its ``CATEGORY``, the id made of the session id, two colons and the
        position, and ``chat_id``, and return ``None``. This is the write the module docstring above describes."""
        container = self._get_container()
        seq = self._next_seq(container, SessionConversationId)
        for event in RecordedEventBatch:
            stored = dataclasses.asdict(event)
            stored["CATEGORY"] = type(event).CATEGORY
            stored["id"] = f"{SessionConversationId}::{seq}"
            stored["chat_id"] = SessionConversationId
            container.upsert_item(stored)
            seq += 1

    def read_persistent_batch(
        self, SessionConversationId: str,
    ) -> list[dict[str, Any]]:
        """Return the stored events of the conversation ``SessionConversationId`` as dicts, ordered by the position in
        each document's id, with the fields whose names start with an underscore, Cosmos DB's own, left out. The order is
        not taken from ``_ts``, as the module docstring above explains."""
        container = self._get_container()
        rows = list(container.query_items(
            query="SELECT * FROM c WHERE c.chat_id=@cid",
            parameters=[{"name": "@cid", "value": SessionConversationId}],
            partition_key=SessionConversationId,
        ))

        def _position(row: dict[str, Any]) -> int:
            """Return the position written after the last two colons of the document's id, or ``-1`` when unreadable,
            as the sort key of the enclosing ``read_persistent_batch``."""
            try:
                return int(str(row.get("id", "")).rsplit("::", 1)[-1])
            except ValueError:
                return -1

        rows.sort(key=_position)
        out: list[dict[str, Any]] = []
        for r in rows:
            out.append({k: v for k, v in r.items() if not k.startswith("_")})
        return out
