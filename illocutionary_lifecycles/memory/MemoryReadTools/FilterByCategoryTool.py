"""``filter_by_category``, one of the three stateless reads in ``illocutionary_lifecycles/memory/MemoryReadTools``,
which returns one category's event dicts from the record's streams.

The record of a conversation run from a written flow is kept by the folder ``memory`` as event dicts grouped by
category, and this function, the plainest read over them, serves ``illocutionary_lifecycles.memory.memory.ReadCache``
in the folder ``memory`` and ``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader`` in the
folder ``server``, while ``core`` and ``analyzers`` read the record through ``Memory``, as the folder's
``__init__.py`` explains.
"""
from __future__ import annotations

from typing import Any


def filter_by_category(streams: dict[str, list[dict[str, Any]]],
                       EventCategory: str) -> list[dict[str, Any]]:
    """Return a new list of the event dicts under ``EventCategory`` in ``streams``, the dict from category to list of
    event dicts, or an empty list when the category has none, as the module docstring above explains."""
    return list(streams.get(EventCategory, []))
