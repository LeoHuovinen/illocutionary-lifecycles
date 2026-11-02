"""``PipecatVoiceAdapter``, the adapter through which spoken turns and the speech so far reach one session, for every
speech source, with Pipecat or without it, and which replaces ``TextAdapter`` towards the session.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and speech enters the folder ``core`` through this adapter, in the
folder ``server``, to be checked by ``analyzers``, including while the user is still speaking, and recorded in
``memory``. The adapter imports nothing from Pipecat and changes nothing about the conversation, passing each call to
its ``SessionProvider``. Both speech mounts use it,
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount`` and
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount``, which runs no
Pipecat at all.

The end of a spoken turn is not set here. The assembler
``illocutionary_lifecycles.server.adapters.voice_adapters.voice_adapter_helpers.PipecatVoiceAdapterHelpers.UserSpeechTurnAggregationAssembler``
joins the STT's final transcriptions into one turn and calls this adapter's ``on_user_turn``, and passes every new
interim transcription to ``incremental_phrase_tick``. Voices are the server's choice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from illocutionary_lifecycles.server.adapters.AdapterBase import AdapterBase


@dataclass
class PipecatVoiceAdapter(AdapterBase):
    """The adapter of one spoken conversation, holding its session as the field ``SessionProvider``, through which
    every call goes, with the shared calls from ``AdapterBase`` and the two calls speech needs added here, as the module
    docstring above explains."""

    SessionProvider: Any

    def save_assistant(self, AssistantReplyText: str, truncated: bool = False) -> int:
        """Save ``AssistantReplyText``, a reply once TTS has spoken it, through ``SessionProvider.TTSUtteranceSave`` and
        return its refresh index, or ``-1`` before the session has started. ``truncated`` is true when an interruption
        cut the spoken reply short. Called by the press mount after it has sent the reply's audio and by the WebRTC
        mount's ``SpokenReplySaveFrameProcessor`` when the reply has finished playing, the two
        mounts the module docstring above names."""
        return self.SessionProvider.TTSUtteranceSave(AssistantReplyText, truncated=truncated)

    def incremental_phrase_tick(self, IncrementalPhraseTickInputs: dict) -> None:
        """Pass ``IncrementalPhraseTickInputs`` to ``SessionProvider.IncrementalPhraseTick`` and return ``None`` at once.
        The dict's key ``IncrementalPhrase`` holds the speech so far, and the assembler may add a record of a detected
        condition under its own key. Called by the assembler on every new interim and final transcription, while the
        user is still speaking, as the module docstring above explains."""
        self.SessionProvider.IncrementalPhraseTick(IncrementalPhraseTickInputs)
