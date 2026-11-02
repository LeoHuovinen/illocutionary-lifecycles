"""``SaveLoadFlowAdapter``, which saves a flow to a JSON file before any session exists, and is an adapter by folder
only, since it holds no session and inherits nothing from ``AdapterBase``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed). A flow is the dict with ``PromptBlocks`` and ``ConversationStates`` that
a session takes as ``ConversationStateInitBundle``, and this module, in the folder ``server``, writes such a dict to a
file for a program that authors flows. The folders ``core``, ``analyzers`` and ``memory`` never call it.
Loading needs no adapter, since the saved file is read with ``json.load`` and
handed to ``SessionProvider`` as ``ConversationStateInitBundle``, as in the lines below.

    SaveLoadFlowAdapter().save_flow(flow, "pizza.json")

    provider = SessionProvider(ConversationStateInitBundle=json.load(open("pizza.json", encoding="utf-8")))
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class SaveLoadFlowAdapter:
    """The writer of flows to files, holding no state, as the module docstring above explains."""

    def save_flow(self, ConversationStateInitBundle: dict[str, Any], FlowFilePath: str) -> str:
        """Write a deep copy of the flow ``ConversationStateInitBundle`` to the file ``FlowFilePath`` as indented JSON,
        creating the file's directory when missing, and return ``FlowFilePath``. A value that is not a dict with a
        ``ConversationStates`` dict raises ``ValueError`` with the text "a flow is an init dict with
        'ConversationStates'". The module docstring above shows how a saved flow is loaded again."""
        if not isinstance(ConversationStateInitBundle, dict) \
                or not isinstance(ConversationStateInitBundle.get("ConversationStates"), dict):
            raise ValueError("a flow is an init dict with 'ConversationStates'")
        directory = os.path.dirname(os.path.abspath(FlowFilePath))
        os.makedirs(directory, exist_ok=True)
        with open(FlowFilePath, "w", encoding="utf-8") as fh:
            json.dump(copy.deepcopy(ConversationStateInitBundle), fh, ensure_ascii=False, indent=2)
        return FlowFilePath
