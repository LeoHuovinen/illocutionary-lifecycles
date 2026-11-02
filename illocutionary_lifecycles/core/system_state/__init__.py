"""The folder that holds ``SystemState``, the dialogue system's own side of one conversation, and three read functions
over the record it holds.

A conversation in this package runs between a user and a language model through the states of a flow written in
advance, and this folder, inside the folder ``core``, holds the flow's states, the current state and the record while
the conversation runs, beside ``analyzers``, ``memory`` and ``server``. The module ``system_state`` holds
``SystemState``, which enters each state and holds the record. The module ``conversation_history_window`` holds three
functions that return recorded utterances as ``TurnView`` objects, read by the analyzers through the cycle and by the
composer. The module ``user_memory_state`` holds ``UserMemoryState``, which returns the remembered answers for the
composer and the analyzers. The module ``static_prompt_library`` holds ``StaticPromptLibrary``, which returns the
authored prompt texts that apply to the current state for the composer.

The three read functions sit here because they read the record ``SystemState`` holds, and each takes what it reads as
an argument and returns data, never a callable. ``SystemState``, ``UserMemoryState``, ``ConversationHistoryWindow``
and ``TurnView`` are re-exported here, and
``illocutionary_lifecycles.core.session_provider`` imports ``SystemState`` from this folder.
"""
from illocutionary_lifecycles.core.system_state.system_state import SystemState
from illocutionary_lifecycles.core.system_state.user_memory_state import UserMemoryState
from illocutionary_lifecycles.core.system_state.conversation_history_window import (
    ConversationHistoryWindow,
    TurnView,
)

__all__ = [
    "SystemState",
    "UserMemoryState",
    "ConversationHistoryWindow",
    "TurnView",
]
