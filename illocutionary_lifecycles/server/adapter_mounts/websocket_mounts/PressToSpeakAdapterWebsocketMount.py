"""The press-to-speak way, ``PressToSpeakAdapterWebsocketMount``, which puts ``PipecatVoiceAdapter`` on a WebSocket and
transcribes the user's speech while a button is held, with the same voice adapter, the same assembler and the same
incremental picks as the voice way and no Pipecat, one of the three mounts that replace each other by way.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this mount, in the folder ``server``, lets the user speak to it with
the turn's start and end set by a button, with no WebRTC and no voice activity detection. Per connection it builds a
session of the folder ``core``, whose checks run in ``analyzers``, including on the speech so far during the hold, and
whose record is kept in ``memory``. The connecting side may be a browser page with
``PressToSpeakAdapterWebsocketMount.js`` beside it in the page's folder, an Android app, a robot or any WebSocket
client. Nothing is heard while the button is not held, and the assistant is never spoken over unless the page lets a
new press stop the playback.

The socket's URL path is the ``SocketPath`` given to ``MountOnApp``, "/ws" by default, and its query string is the
connection's request data. The assistant's opening is spoken at connection. The connecting side sends a JSON object
whose ``type`` is "PressToSpeakHoldStart" when the button goes down, then the speech as binary frames of 16 kHz 16-bit
mono PCM, then a JSON object whose ``type`` is "PressToSpeakHoldEnd" when it goes up. A binary frame outside a hold is
dropped. During the hold every interim and final transcription comes back as a JSON object whose ``type`` is
"PressToSpeakHeardText" with ``text`` and ``final``, false for an interim and true for a final, and the turn goes to
the session after release once the pause ``debounce_s``, 0.3 seconds by default, has passed. Each reply comes back as a
JSON object whose ``type`` is "PressToSpeakReplyText" with ``text``, ``audio``, true when audio follows, and ``words``,
a list of dicts with ``text``, ``offset_ms`` and ``duration_ms`` for showing the words as they are spoken, followed by
one binary frame of WAV audio, and the reply is saved once its audio has been sent. A text frame, or a JSON object whose
``type`` is "user" with ``text``, is a typed line, which comes back as "PressToSpeakHeardText" with ``final`` true and
joins the spoken turn through the assembler's ``segment``, never a turn of its own. Any other JSON object reaches
``OnClientMessage``. The adapter callbacks come back as on the text way, as
``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase`` explains.

The STT and the TTS are two arguments of the mount, ``STTStreaming`` and ``TTSWithWordBoundaries``, whose defaults in
this module use Azure Speech's SDK, and the mount itself names no vendor. With the defaults the server needs the
``press`` extra, FastAPI, uvicorn, websockets and Azure's Speech SDK ``azure-cognitiveservices-speech``, the model's variables, and two speech variables in its environment, ``AZURE_SPEECH_KEY``, the key of an Azure
Speech resource, and ``AZURE_SPEECH_REGION``, the Azure region that resource is in, written as lines of the server's
``.env`` such as AZURE_SPEECH_REGION=westeurope as one example. The server file reads the ``.env`` itself or exports the
variables in its shell, since this way runs under no runner that loads one. A missing key raises ``RuntimeError``
beginning "AZURE_SPEECH_KEY is not set" from ``MountOnApp``, when the server starts and not at the first press.
``examples/2-press-to-speak/server.py`` is one server built on it.
"""
from __future__ import annotations

import json
import os
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase import AdapterMountBase


def _speech_key_and_region() -> tuple[str, str]:
    """Return the pair of ``AZURE_SPEECH_KEY`` and ``AZURE_SPEECH_REGION`` from the environment, raising
    ``RuntimeError`` beginning "AZURE_SPEECH_KEY is not set" when the key is missing and the ``RuntimeError`` of
    ``illocutionary_lifecycles.core.environment.Required`` when the region is. Called by the two Azure defaults of this
    module and by ``PressToSpeakAdapterWebsocketMount.MountOnApp``."""
    key = os.environ.get("AZURE_SPEECH_KEY", "")
    if not key:
        raise RuntimeError("AZURE_SPEECH_KEY is not set; the press-to-speak server needs Azure Speech for STT and TTS")
    from illocutionary_lifecycles.core.environment import Required
    return key, Required("AZURE_SPEECH_REGION", "the Azure Speech region of that key, for STT and TTS")


class AzureSpeechStreamingSTT:
    """The default STT of the press-to-speak mount for one hold, which takes the hold's 16 kHz 16-bit mono PCM as it is
    recorded and reports interim and final transcriptions back on the event loop, asyncio's scheduler on whose thread
    the assembler and the session must be touched, as Azure Speech produces them from its own thread, the same two
    kinds the voice way's STT gives, so the assembler and the incremental analyzer see the same input on both speech
    ways, as the module docstring above explains.

    The mount builds one at every "PressToSpeakHoldStart" and closes it at "PressToSpeakHoldEnd", and closing ends the
    audio, which makes Azure report the last final transcription and stop. A replacement passed as ``STTStreaming`` is
    called with the same four arguments and must offer ``push`` and an async ``close``. The SDK's own attributes
    ``recognizing`` and ``recognized`` on its ``SpeechRecognizer`` are the SDK's names for its interim and final
    results, and the handlers of this class are attached to them under those names.
    """

    def __init__(self, language: str, on_interim: Any, on_final: Any, loop: Any) -> None:
        """Start continuous Azure Speech recognition in ``language``, a BCP-47 tag such as en-US, on a push audio stream,
        calling ``on_interim`` with the text of each interim result and ``on_final`` with the text of each final result,
        both on the event loop ``loop``. Raises the errors of ``_speech_key_and_region`` when the speech variables are
        missing, as the class above describes."""
        import azure.cognitiveservices.speech as speechsdk
        key, region = _speech_key_and_region()
        config = speechsdk.SpeechConfig(subscription=key, region=region)
        config.speech_recognition_language = language
        audio_format = speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
        self._stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
        self._AzureSpeechSTT = speechsdk.SpeechRecognizer(speech_config=config,
                                                      audio_config=speechsdk.audio.AudioConfig(stream=self._stream))
        self._stopped = loop.create_future()

        def OnAzureInterimTranscription(evt: Any) -> None:
            """Pass the SDK's interim result text to ``on_interim`` on the event loop, for the enclosing ``__init__``."""
            loop.call_soon_threadsafe(on_interim, evt.result.text)

        def OnAzureFinalTranscription(evt: Any) -> None:
            """Pass the SDK's final result text to ``on_final`` on the event loop, when speech was recognized, for the
            enclosing ``__init__``."""
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                loop.call_soon_threadsafe(on_final, evt.result.text)

        def OnAzureSessionStopped(evt: Any) -> None:
            """Mark the recognition as stopped, on the event loop, when the SDK's session stops or is canceled, so the
            enclosing class's ``close`` can stop waiting."""
            loop.call_soon_threadsafe(lambda: None if self._stopped.done() else self._stopped.set_result(None))

        self._AzureSpeechSTT.recognizing.connect(OnAzureInterimTranscription)
        self._AzureSpeechSTT.recognized.connect(OnAzureFinalTranscription)
        self._AzureSpeechSTT.session_stopped.connect(OnAzureSessionStopped)
        self._AzureSpeechSTT.canceled.connect(OnAzureSessionStopped)
        self._AzureSpeechSTT.start_continuous_recognition_async()

    def push(self, PCMFrame: bytes) -> None:
        """Write ``PCMFrame``, one binary frame of 16 kHz 16-bit mono PCM from the hold, to the recognition's audio
        stream, and return ``None``. The mount calls it for every binary frame during a hold, as the class above
        describes."""
        self._stream.write(PCMFrame)

    async def close(self) -> None:
        """End the hold's audio, wait up to 8 seconds for the SDK to report its last final transcription and stop, then
        stop the recognition, and return ``None``. The mount calls it at "PressToSpeakHoldEnd", as the class above
        describes."""
        import asyncio
        self._stream.close()
        try:
            await asyncio.wait_for(self._stopped, 8)
        except asyncio.TimeoutError:
            pass
        self._AzureSpeechSTT.stop_continuous_recognition_async()


def AzureSpeechSynthesisReplyWithWordBoundaries(ReplyTextToSpeak: str, TTSVoice: str) -> tuple[bytes, list[dict]]:
    """Return a pair, the WAV audio of ``ReplyTextToSpeak`` spoken by TTS with the voice ``TTSVoice`` through Azure
    Speech's SDK, 24 kHz 16-bit mono, and the list of its word boundaries, each a dict with ``text``, ``offset_ms`` and
    ``duration_ms``, which let a connecting side show the words as they are spoken.

    This is the default TTS of the press-to-speak mount, and a replacement passed as ``TTSWithWordBoundaries`` takes the
    same two arguments and returns the same pair, as the module docstring above explains. A voice the region refuses
    raises ``RuntimeError`` beginning "Azure Speech refused TTSVoice=" with the voice, the SDK's reason, and the advice
    to set ``TTSVoice`` in the server file to a voice the region offers. The function blocks, so the mount runs it in a
    worker thread.
    """
    import azure.cognitiveservices.speech as speechsdk
    key, region = _speech_key_and_region()
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_synthesis_voice_name = TTSVoice
    config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
    config.set_property(speechsdk.PropertyId.SpeechServiceResponse_RequestWordBoundary, "true")
    AzureSpeechSynthesis = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
    words: list[dict] = []
    AzureSpeechSynthesis.synthesis_word_boundary.connect(lambda e: words.append(
        {"text": e.text, "offset_ms": e.audio_offset / 10000, "duration_ms": e.duration.total_seconds() * 1000}))
    result = AzureSpeechSynthesis.speak_text_async(ReplyTextToSpeak).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = getattr(result, "cancellation_details", None)
        raise RuntimeError(f"Azure Speech refused TTSVoice={TTSVoice!r}: {getattr(details, 'reason', '')} "
                           f"{getattr(details, 'error_details', '')}; set TTSVoice in the server file where the mount is built to a voice the region offers")
    return result.audio_data, words


class PressToSpeakAdapterWebsocketMount(AdapterMountBase):
    """The press-to-speak way's mount, ``PipecatVoiceAdapter`` on a WebSocket with the speech transcribed while a button
    is held, whose ``Way`` is "press", speaking the protocol the module docstring above gives."""

    Way = "press"

    def __init__(self, ConversationStateInitBundle: dict, TTSVoice: str, language: str,
                 debounce_s: float = 0.3, OnAdapterCallback: Any = None, OnSessionOpened: Any = None,
                 OnClientMessage: Any = None, STTStreaming: Any = None,
                 TTSWithWordBoundaries: Any = None) -> None:
        """Keep the flow, the hooks, the voice, the language, the pause and the two speech functions, and raise
        ``ValueError`` beginning "the press-to-speak mount takes TTSVoice" when ``TTSVoice`` or ``language`` is missing,
        because the package carries no default voice and no default language.

        ``ConversationStateInitBundle`` and the three hooks are as ``AdapterMountBase`` takes them. ``TTSVoice`` is the
        name of the TTS voice the replies are spoken with, a value the TTS vendor lists, chosen in the server file.
        ``language`` is the language of the user's speech for the STT, a BCP-47 tag such as en-US. ``debounce_s`` is the
        pause in seconds after release before the turn goes to the session, 0.3 by default, short because the release
        already ends the turn. ``STTStreaming`` is the function that builds one hold's STT from the language, the interim
        and final callbacks and the event loop, ``AzureSpeechStreamingSTT`` when ``None``. ``TTSWithWordBoundaries`` is
        the function that returns the WAV audio and the word boundaries of a reply for a voice,
        ``AzureSpeechSynthesisReplyWithWordBoundaries`` when ``None``, both defined in this module.
        """
        super().__init__(ConversationStateInitBundle, OnAdapterCallback, OnSessionOpened, OnClientMessage)
        if not TTSVoice or not language:
            raise ValueError("the press-to-speak mount takes TTSVoice (the TTS voice the replies are spoken with) and "
                             "language (the STT language of the user's speech, a BCP-47 tag) from the server file; the "
                             "library carries no default voice and no default language")
        self.TTSVoice = TTSVoice
        self.language = language
        self.debounce_s = debounce_s  # the pause after release before the turn goes; release is the boundary, so short
        self.STTStreaming = STTStreaming or AzureSpeechStreamingSTT     # (language, on_interim, on_final, loop) -> object with push(bytes), close()
        self.TTSWithWordBoundaries = TTSWithWordBoundaries or AzureSpeechSynthesisReplyWithWordBoundaries   # (text, voice) -> (wav bytes, words)

    def MountVoiceName(self, RequestData: Any = None) -> str:
        """Return the TTS voice name for one connection, the mount's ``TTSVoice``, unless a server overrides this method to
        pick a voice from ``RequestData``, the connection's request data. Called by ``Attend`` in this class once per
        connection."""
        return str(self.TTSVoice)

    async def Attend(self, SendJsonToConnectingSide: Any, SendBytesToConnectingSide: Any, ReceiveFromConnectingSide: Any, RequestData: Any = None) -> None:
        """Serve one connection until the connecting side closes it, following the protocol the module docstring above
        gives, and return ``None``.

        ``SendJsonToConnectingSide`` is an async function that sends one JSON object, ``SendBytesToConnectingSide`` one
        that sends one binary frame, ``ReceiveFromConnectingSide`` one that returns the next frame as bytes or text, and
        ``RequestData`` the connection's request data. The mount builds the session, the ``PipecatVoiceAdapter`` and one
        ``UserSpeechTurnAggregationAssembler`` with ``debounce_s``, registers the relay, the log relay and the server's
        hook, starts the session, calls ``OnSessionOpened``, speaks the opening, and then handles each frame in order.
        Called by the socket route ``MountOnApp`` adds.
        """
        import asyncio

        from illocutionary_lifecycles.server.adapters.voice_adapters.PipecatVoiceAdapter import PipecatVoiceAdapter
        from illocutionary_lifecycles.server.adapters.voice_adapters.voice_adapter_helpers.PipecatVoiceAdapterHelpers import (
            UserSpeechTurnAggregationAssembler,
        )

        loop = asyncio.get_running_loop()
        provider = self.NewConversationSession(RequestData)
        VoiceAdapter = PipecatVoiceAdapter(SessionProvider=provider)
        VoiceAdapter.RegisterAdapterCallbackHandler(self.RelayAdapterCallback(SendJsonToConnectingSide))
        VoiceAdapter.RegisterAdapterCallbackHandler(self.LogRelay(SendJsonToConnectingSide))
        VoiceAdapter.RegisterAdapterCallbackHandler(self.AdapterCallbackHandler(self.OnAdapterCallback))
        TTSVoice = self.MountVoiceName(RequestData)

        async def speak(reply: str) -> None:
            """Send ``reply`` as "PressToSpeakReplyText" with its words and then its audio, save it, and tell the
            assembler its playback started, or send an empty "PressToSpeakReplyText" with ``audio`` false for no reply. The
            assembler's ``on_reply`` in the enclosing ``Attend``."""
            if not reply:
                await SendJsonToConnectingSide({"type": "PressToSpeakReplyText", "text": "", "audio": False, "words": []})
                return
            audio, words = await asyncio.to_thread(self.TTSWithWordBoundaries, reply, TTSVoice)
            # The words first, with their timing, so the connecting side can show them as they play; then the audio.
            await SendJsonToConnectingSide({"type": "PressToSpeakReplyText", "text": reply, "audio": True, "words": words})
            await SendBytesToConnectingSide(audio)
            VoiceAdapter.save_assistant(reply)
            assembler.TTSStarted()

        assembler = UserSpeechTurnAggregationAssembler(VoiceAdapter, speak, debounce_s=self.debounce_s)
        VoiceAdapter.open_session()
        await self.Opened(provider, VoiceAdapter, SendJsonToConnectingSide)
        opening = await VoiceAdapter.opening_reply()
        await speak(opening or "")

        async def heard(text: str, final: bool) -> None:
            """Send ``text`` back as "PressToSpeakHeardText" with ``final``, for the enclosing ``Attend``."""
            await SendJsonToConnectingSide({"type": "PressToSpeakHeardText", "text": text, "final": final})

        def on_interim(text: str) -> None:
            """Give the STT's interim ``text`` to the assembler and send it back as heard with ``final`` false, for the
            enclosing ``Attend``."""
            assembler.interim(text)
            asyncio.ensure_future(heard(text, False))

        def on_final(text: str) -> None:
            """Give the STT's final ``text`` to the assembler and send it back as heard with ``final`` true, for the
            enclosing ``Attend``."""
            assembler.segment(text)
            asyncio.ensure_future(heard(text, True))

        def typed(text: str) -> None:
            """Give the typed line ``text`` to the assembler's ``segment``, so it joins the spoken turn, as the module
            docstring above explains."""
            # Typed text is never a turn of its own: it joins the speech in arrival order, into the
            # turn being spoken or the one waiting for the assistant to finish, and goes to the session with it as one turn.
            assembler.segment(text)

        STTStream = None
        while True:
            frame = await ReceiveFromConnectingSide()
            if isinstance(frame, bytes):
                if STTStream is not None:      # PCM of the hold in progress; a frame outside a hold is dropped
                    STTStream.push(frame)
                continue
            text = str(frame or "").strip()
            if not text:
                continue
            data = None
            if text[:1] == "{":
                try:
                    data = json.loads(text)
                except ValueError:
                    data = None
            if isinstance(data, dict):
                kind = data.get("type")
                if kind == "PressToSpeakHoldStart":
                    assembler.speech_started()
                    STTStream = self.STTStreaming(self.language, on_interim, on_final, loop)
                elif kind == "PressToSpeakHoldEnd":
                    if STTStream is not None:
                        await STTStream.close()
                        STTStream = None
                    assembler.speech_stopped()
                elif kind == "user":
                    line = str(data.get("text") or "").strip()
                    if line:
                        await heard(line, True)   # a typed turn comes back as heard, as on the text mount
                        typed(line)
                else:
                    await self.ClientMessage(provider, data)
                continue
            await heard(text, True)   # a typed turn comes back as heard, as on the text mount
            typed(text)

    def MountOnApp(self, app: Any, SocketPath: str = "/ws") -> None:
        """Add the one route of the press-to-speak way to the FastAPI app ``app``, a WebSocket at ``SocketPath``, "/ws" by
        default, whose handler accepts each connection and runs ``Attend`` on it until the connecting side closes it, and
        return ``None``. The speech variables are checked first through ``_speech_key_and_region``, so a missing key
        fails when the server starts and not at the first press, even when the mount was given its own speech
        functions, as the module docstring above explains."""
        _speech_key_and_region()
        mount = self

        async def ws(sock: WebSocket) -> None:
            """Accept the socket ``sock`` and serve it with ``Attend``, ending quietly when the connecting side closes it,
            as the route the enclosing ``MountOnApp`` adds."""
            await sock.accept()

            async def receive() -> Any:
                """Return the next frame of ``sock`` as bytes or text, raising ``WebSocketDisconnect`` when it closes, as
                the receive function the enclosing route passes to ``Attend``."""
                message = await sock.receive()
                if message["type"] == "websocket.disconnect":
                    raise WebSocketDisconnect(message.get("code", 1000))
                return message["bytes"] if message.get("bytes") is not None else message.get("text")

            try:
                await mount.Attend(sock.send_json, sock.send_bytes, receive, dict(sock.query_params))
            except WebSocketDisconnect:
                pass   # The connecting side closed its socket: the session ends with it.

        app.websocket(SocketPath)(ws)
