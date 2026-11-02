"""``UserMemoryState``, the function that returns the remembered answers of a conversation, one of the three read
modules in ``illocutionary_lifecycles/core/system_state`` beside ``conversation_history_window`` and
``static_prompt_library``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every answer the question checker accepts is kept as a remembered
answer, a ``MemoryEvent`` in the record of the folder ``memory``, so that later prompts can mention it. This module,
in the folder ``core``, is how the composer and the analyzers of the folder ``analyzers`` read those answers, and the
folder ``server`` sees them only in the callbacks the session sends.
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` passes the result to the
composer as data, and the cycle passes the function, bound to the record, to every analyzer as ``UserMemoryFace``. The
answers are written by ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter``.
"""
from __future__ import annotations

from typing import Any

from illocutionary_lifecycles.memory.memory import MemoryEvent


def UserMemoryState(Record: Any) -> Any:
    """Return the ``memory`` dict of every recorded ``MemoryEvent`` in ``Record``, in order, each holding the answer
    sentence under ``answer``, or an empty list for a ``Record`` of ``None``. The function reads the record's in-memory
    copy through ``illocutionary_lifecycles.memory.memory.Memory.RelevantMemoryOfKind`` and writes nothing, as the
    module docstring above explains.
    """
    if Record is None:
        return []
    return Record.RelevantMemoryOfKind(MemoryEvent.CATEGORY)
