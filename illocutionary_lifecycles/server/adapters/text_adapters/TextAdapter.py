"""``TextAdapter``, the adapter through which typed turns reach one session, which replaces ``PipecatVoiceAdapter``
towards the session because both pass the same calls.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a typed line enters the folder ``core`` through this adapter, in the
folder ``server``, to be checked by ``analyzers`` and recorded in ``memory``. What every adapter shares comes from
``illocutionary_lifecycles.server.adapters.AdapterBase.AdapterBase``, and what is added here is the save of a reply
once it has been shown. The adapter is created per connection by
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount``. The press-to-speak mount does not
use it, because typed text there joins the spoken turn through the voice adapter's assembler.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from illocutionary_lifecycles.server.adapters.AdapterBase import AdapterBase


@dataclass
class TextAdapter(AdapterBase):
    """The adapter of one typed conversation, holding its session as the field ``SessionProvider``, through which every
    call goes, as the module docstring above explains."""

    SessionProvider: Any

    def save_assistant(self, AssistantReplyText: str) -> int:
        """Save ``AssistantReplyText``, a reply once it has been shown, through ``SessionProvider.TTSUtteranceSave`` and
        return its refresh index, or ``-1`` before the session has started. The session then sends the save-time adapter
        callbacks to the handlers. Called by the text mount after it sends each reply, as the module docstring
        above explains."""
        return self.SessionProvider.TTSUtteranceSave(AssistantReplyText)
