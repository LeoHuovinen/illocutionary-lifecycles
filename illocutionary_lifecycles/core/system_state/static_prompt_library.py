"""``StaticPromptLibrary``, the function that returns the authored prompt texts that apply to the current state, one of
the three read modules in ``illocutionary_lifecycles/core/system_state`` beside ``conversation_history_window`` and
``user_memory_state``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every prompt the model gets is built from texts the flow's author
wrote, the flow's ``PromptBlocks``, and from the conversation's values. Of the package's four folders, ``core`` holds
this module and its only caller, ``memory`` holds the function that matches the texts, and ``analyzers`` and
``server`` never read them. This module hands those texts to the composer
``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.PragmaticState.Composer``, which
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` calls with this function bound
to the flow's ``PromptBlocks``. Which blocks match the current state is chosen by
``illocutionary_lifecycles.memory.MemoryReadTools.StaticPromptBlocks.StaticPromptBlocks``, and "static" in both names
means the authored text, as opposed to the composed prompt.
"""
from __future__ import annotations

from typing import Any


def StaticPromptLibrary(blocks: Any, PragmaticStates: dict[str, Any]) -> dict[str, Any]:
    """Return a dict of the authored texts that apply now, with their blanks unfilled, or an empty list when
    ``blocks`` is ``None``.

    ``blocks`` is the flow's ``PromptBlocks`` dict, and ``PragmaticStates`` is the dict of the pragmatic fields
    the composer passes in. The dict returned holds, under ``blocks``, the list ``StaticPromptBlocks`` matches for
    the current state, under ``memory_callback`` the text that introduces the remembered answers, under
    ``question_prompt`` the text shown after the open questions, under ``ConversationHistoryWindowHeading`` the heading of the
    utterance window, and under ``ConversationHistoryWindowEmptyNote`` the note shown in that window while the user has not spoken in
    the state, each an empty string when the flow has none, in which case the composer uses its own heading and
    note. The composer chooses between condition-keyed texts and fills the blanks, as the module docstring above
    explains."""
    if blocks is None:
        return []
    from illocutionary_lifecycles.memory.MemoryReadTools.StaticPromptBlocks import (
        StaticPromptBlocks,
    )
    _lookup = dict(blocks)
    return {
        "blocks": StaticPromptBlocks(_lookup, PragmaticStates),
        "memory_callback": _lookup.get("memory_callback") or "",
        "question_prompt": _lookup.get("question_prompt") or "",
        "ConversationHistoryWindowHeading": _lookup.get("ConversationHistoryWindowHeading") or "",
        "ConversationHistoryWindowEmptyNote": _lookup.get("ConversationHistoryWindowEmptyNote") or "",
    }
