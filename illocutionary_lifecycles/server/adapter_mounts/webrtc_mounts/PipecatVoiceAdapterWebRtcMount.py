"""The voice way, ``PipecatVoiceAdapterWebRtcMount``, which speaks a session over WebRTC through Pipecat's runner with
``PipecatVoiceAdapter``, for an open microphone where a pause ends the turn, one of the three mounts that replace each
other by way, together with its default speech pipeline, ``PipecatVoiceConnectionLifecycle``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this mount, in the folder ``server``, lets the user simply talk to
it. Per connection it builds a session of the folder ``core``, whose checks run in ``analyzers``, also on the speech
so far, and whose record is kept in ``memory``. The pipeline holds no language model service, and every reply is the
session's, written by the folder ``core`` and spoken by TTS here, so a language model service must not be added to it.
The connecting side may be a browser page with ``PipecatVoiceAdapterWebRtcMount.js`` beside it in the page's folder,
an Android app with the Pipecat client, or any WebRTC program that speaks RTVI, Pipecat's message protocol over the
WebRTC connection.

Pipecat's runner owns the app and takes the WebRTC offer at "/api/offer", and ``MountOnApp`` only prepares that app,
renaming the offer body's key with ``WebRtcOfferBodyKeyRename`` and taking the ICE servers from the environment with
``ApplyWebRtcIceServersFromEnvironment``. ``StartWebRtcServerProcess`` then runs the runner with ``Attend`` as the
per-connection coroutine. The offer's request data is the connection's request data. Audio goes both ways over WebRTC.
Every adapter callback except the save callback reaches the connecting side as an RTVI server message with its ``type``
and without ``turns`` and ``prompt``, every callback also as a server message marked ``log``, every state change also as
a server message whose ``type`` is "conversation-state" with ``state``, ``name`` and ``previous_state``, and every
change of the assembler's detected conditions as a server message whose ``type`` is
"interim-threshold-or-playback-overlap". Typed text arrives as an RTVI client message of type "user" with ``text``,
comes back as a server message whose ``type`` is "PipecatVoiceHeardText" with ``text``, and joins the spoken turn
through the assembler's ``segment``, never a turn of its own. Other RTVI client messages are ignored, and
``OnClientMessage`` is never called on this way, while ``OnSessionOpened`` receives ``None`` as the send function.

The default pipeline runs, in order, the transport's input, Silero voice activity detection, Pipecat's
``UserTurnProcessor``, the STT ``STTVendor`` names, ``STTToAssemblerFrameProcessor``, Azure Speech TTS with ``TTSVoice``,
``SpokenReplySaveFrameProcessor`` and the transport's output, with Pipecat's RTVI processor placed first by Pipecat's
worker. Of the two turn mechanisms in it, the assembler sets when the session receives a turn, after ``debounce_s``,
2.5 seconds by default, and nothing in the pipeline acts on the turns Pipecat's ``UserTurnProcessor`` marks. A server
with another TTS or its own turn machinery passes its own ``Pipeline``, an async function called with the transport, the
runner's arguments, the voice adapter and the keywords ``TTSVoice``, ``STTVendor`` and ``debounce_s``. With the default
pipeline the server needs the ``pipecat`` extra, the model's variables, ``AZURE_SPEECH_KEY`` and
``AZURE_SPEECH_REGION`` for TTS, the key of the chosen STT vendor as ``PipecatSTTService`` lists, and, across networks,
``STUN_URL`` and ``TURN_URL`` as ``WebRtcIceServersFromEnvironment`` explains, all in the environment. The server loads
any ``.env`` file itself before it builds the mount, because Pipecat's runner looks for one upward from Pipecat's own
install folder and not from the working directory. ``examples/5-vrm-pipecat/server.py`` is one server built on it.
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase import AdapterMountBase
from illocutionary_lifecycles.server.adapters.voice_adapters.PipecatVoiceAdapter import PipecatVoiceAdapter
from illocutionary_lifecycles.server.adapters.voice_adapters.voice_adapter_helpers.PipecatVoiceAdapterHelpers import (
    UserSpeechTurnAggregationAssembler,
)

# ---- the WebRTC side ----


def WebRtcIceServersFromEnvironment() -> list:
    """Return the list of Pipecat ``IceServer`` objects built from the two optional environment variables ``STUN_URL``
    and ``TURN_URL``, an empty list when neither is set, which is logged.

    WebRTC carries the microphone audio directly between the connecting program and this server, so each side needs an
    address the other can reach. On one machine or one network they have it, and neither variable is needed. When a
    router stands between them, which WebRTC calls NAT, two standard kinds of server help, both optional here. A STUN
    server tells a side what its address looks like from outside and carries no audio. A TURN server relays the audio
    when no direct path exists, and needs a username and a credential, because relaying costs bandwidth.

    ``STUN_URL`` is written in the server's ``.env`` as STUN_URL= followed by the scheme stun, a colon, the
    host, a colon and the port, for example with the host stun.example.org and the port 3478 as one example.
    ``TURN_URL`` is written as TURN_URL= followed by the scheme turn, or turns over TLS, then a colon and two
    slashes, the username, a colon, the credential, an at sign, the host, a colon and the port, for
    example with the username alice, the credential s3cret, the host turn.example.org and the port 3478 as one example.
    The address and the credentials come from the deployment, a TURN server it runs or a hosted relay service, of which
    Cloudflare's is one example among several. No address appears in the code, and neither variable has a default. With
    neither set, audio flows where the two sides reach each other directly, and where they cannot, the call connects and
    no audio arrives. Called by ``ApplyWebRtcIceServersFromEnvironment`` in this module for every offer.
    """
    from urllib.parse import unquote, urlparse

    from pipecat.transports.smallwebrtc.connection import IceServer

    servers = []
    stun = os.environ.get("STUN_URL", "").strip()
    if stun:
        servers.append(IceServer(urls=stun))
    turn = os.environ.get("TURN_URL", "").strip()
    if turn:
        parsed = urlparse(turn)
        address = f"{parsed.scheme}:{parsed.hostname}" + (f":{parsed.port}" if parsed.port else "")
        servers.append(IceServer(urls=address, username=unquote(parsed.username or ""),
                                 credential=unquote(parsed.password or "")))
    if not servers:
        logger.info("no STUN_URL or TURN_URL in the environment: WebRTC audio flows only where the browser and this server "
                    "reach each other directly; see WebRtcIceServersFromEnvironment")
    return servers


def ApplyWebRtcIceServersFromEnvironment() -> None:
    """Replace two methods of Pipecat's ``SmallWebRTCRequestHandler`` so it takes its ICE servers from
    ``WebRtcIceServersFromEnvironment`` when it is built and again for every offer, and return ``None``. The change
    applies to the whole process. Called by ``PipecatVoiceAdapterWebRtcMount.MountOnApp`` in this module."""
    from pipecat.transports.smallwebrtc import request_handler

    original_init = request_handler.SmallWebRTCRequestHandler.__init__
    original_handle = request_handler.SmallWebRTCRequestHandler.handle_web_request

    def init_with_environment(self, *args, ice_servers=None, **kwargs):
        """Build the handler with the given ICE servers, or else those of the environment, for the enclosing function."""
        original_init(self, *args, ice_servers=ice_servers or WebRtcIceServersFromEnvironment(), **kwargs)

    async def handle_with_environment(self, *args, **kwargs):
        """Read the ICE servers of the environment again, then handle the offer as Pipecat does, for the enclosing
        function."""
        servers = WebRtcIceServersFromEnvironment()
        if servers:
            self.update_ice_servers(servers)
        return await original_handle(self, *args, **kwargs)

    request_handler.SmallWebRTCRequestHandler.__init__ = init_with_environment
    request_handler.SmallWebRTCRequestHandler.handle_web_request = handle_with_environment


class WebRtcOfferBodyKeyRename:
    """An ASGI wrapper around Pipecat's runner app that renames the key "requestData" to "request_data" in the body of
    every POST to "/api/offer" when the body has the first and not the second, and passes every other request unchanged.

    Pipecat's browser client posts the page's offer data under "requestData", while the runner's offer model reads only
    "request_data" and drops the rest, so without the rename the request data that ``ConnectConversation.js`` sends
    would never reach ``NewConversationSession`` or ``choose``. ``PipecatVoiceAdapterWebRtcMount.MountOnApp`` in this
    module adds it to the app as middleware.
    """

    def __init__(self, app: Any) -> None:
        """Keep ``app``, the ASGI app the requests go on to, as the class above describes."""
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Read the whole body of a POST to "/api/offer", rename the key when it applies, fix the content length, and
        pass the request on with the new body, or pass any other request on as it came,
        which is the rename the class above describes."""
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/api/offer":
            return await self.app(scope, receive, send)
        import json
        chunks, more = [], True
        while more:
            message = await receive()
            chunks.append(message.get("body", b""))
            more = message.get("more_body", False)
        raw = b"".join(chunks)
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "requestData" in data and "request_data" not in data:
                data["request_data"] = data.pop("requestData")
                raw = json.dumps(data).encode()
                scope["headers"] = [(k, v) for k, v in scope["headers"] if k != b"content-length"]
                scope["headers"].append((b"content-length", str(len(raw)).encode()))
        except ValueError:
            pass

        async def replay() -> dict:
            """Return the read body as one ASGI request message, for the enclosing ``__call__``."""
            return {"type": "http.request", "body": raw, "more_body": False}

        return await self.app(scope, replay, send)



# ---- the default pipeline ----

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    InterimTranscriptionFrame,
    TranscriptionFrame,
    TTSSpeakFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.services.azure.tts import AzureTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.turns.user_start.vad_user_turn_start_strategy import VADUserTurnStartStrategy
from pipecat.turns.user_stop.speech_timeout_user_turn_stop_strategy import (
    SpeechTimeoutUserTurnStopStrategy,
)
from pipecat.turns.user_turn_processor import UserTurnProcessor
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.workers.runner import WorkerRunner


ASSEMBLER_CONDITION_MARKERS = (
    "AggregateInterimCountExceededConfiguredThreshold",
    "TranscriptOrVadActiveAtReplyPlaybackStart",
    "InterimThresholdOrPlaybackOverlapResolved",
)


def PipecatSTTService(STTVendorName: str):
    """Return the Pipecat STT service that ``STTVendorName`` names, one of "azure", "elevenlabs", "openai"
    and "whisper", compared without case, built with that vendor's own key from the environment.

    The default pipeline needs two things from an STT, interim transcriptions while the user is still speaking, which
    feed the incremental analyzer, and final transcriptions, which the assembler joins into turns, and Pipecat delivers
    both as ``InterimTranscriptionFrame`` and ``TranscriptionFrame`` whatever the vendor. A vendor with no interim
    transcriptions, such as whisper through ``OpenAISTTService``, still works, and the incremental analyzer then receives
    nothing. A vendor that sends several final transcriptions for one utterance has them joined into one turn by the
    assembler's pause.

    Each vendor reads its key from the environment, azure ``AZURE_SPEECH_KEY`` and ``AZURE_SPEECH_REGION``,
    elevenlabs ``ELEVENLABS_API_KEY``, the secret that starts with sk and not the key id, and openai
    and whisper ``OPENAI_API_KEY``. A missing key raises ``KeyError`` with its name, except the Azure region, which
    raises the ``RuntimeError`` of ``Required``. Any other name raises ``ValueError`` beginning "STTVendor=". A new STT
    vendor is one more branch in this function, which is a branch and not a plugin. Called by
    ``PipecatVoiceConnectionLifecycle`` in this module.
    """
    STTVendorName = str(STTVendorName or "").strip().lower()
    if STTVendorName == "azure":
        from pipecat.services.azure.stt import AzureSTTService
        from illocutionary_lifecycles.core.environment import Required
        return AzureSTTService(api_key=os.environ["AZURE_SPEECH_KEY"],
                               region=Required("AZURE_SPEECH_REGION", "the Azure Speech region of that key"))
    if STTVendorName == "elevenlabs":
        from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
        return ElevenLabsRealtimeSTTService(api_key=os.environ["ELEVENLABS_API_KEY"])
    if STTVendorName == "openai":
        from pipecat.services.openai.stt import OpenAIRealtimeSTTService
        return OpenAIRealtimeSTTService(api_key=os.environ["OPENAI_API_KEY"])
    if STTVendorName == "whisper":
        from pipecat.services.openai.stt import OpenAISTTService
        return OpenAISTTService(api_key=os.environ["OPENAI_API_KEY"])
    raise ValueError(f"STTVendor={STTVendorName!r}: the STT is one of azure, elevenlabs, openai or whisper, "
                     "passed to the mount as STTVendor; each needs its vendor's key in the environment")


class STTToAssemblerFrameProcessor(FrameProcessor):
    """The Pipecat frame processor of the default pipeline that relays four kinds of frame to the assembler and changes
    nothing, the start and stop of the user's speech from voice activity detection, and the STT's interim and final
    transcriptions with text.

    Whether those make a turn is set by the assembler, so no logic is added here. The processor must sit after the STT
    in the pipeline, and every frame passes on unchanged. Built by ``PipecatVoiceConnectionLifecycle`` in this module.
    """

    def __init__(self, assembler: UserSpeechTurnAggregationAssembler, **kwargs) -> None:
        """Keep ``assembler``, the connection's ``UserSpeechTurnAggregationAssembler``, and pass ``kwargs`` to Pipecat's
        ``FrameProcessor``, as the class above describes."""
        super().__init__(**kwargs)
        self._assembler = assembler

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Call the assembler's ``speech_started``, ``speech_stopped``, ``interim`` or ``segment`` for the four kinds of
        frame, and push every frame on unchanged, the relay the class above describes."""
        await super().process_frame(frame, direction)
        if isinstance(frame, VADUserStartedSpeakingFrame):
            self._assembler.speech_started()
        elif isinstance(frame, VADUserStoppedSpeakingFrame):
            self._assembler.speech_stopped()
        elif isinstance(frame, InterimTranscriptionFrame) and frame.text.strip():
            self._assembler.interim(frame.text.strip())
        elif isinstance(frame, TranscriptionFrame) and frame.text.strip():
            self._assembler.segment(frame.text.strip())
        await self.push_frame(frame, direction)


class SpokenReplySaveFrameProcessor(FrameProcessor):
    """The Pipecat frame processor of the default pipeline that tells the assembler when a reply starts playing and
    saves the reply through the voice adapter when it has finished playing, and changes nothing else.

    The start of playback is what lets the assembler send turns again, so speech heard before it is held for the next
    turn, and the save after playback means the record holds what was actually spoken. The processor must sit after the
    TTS in the pipeline. Pipecat's frame names ``BotStartedSpeakingFrame`` and ``BotStoppedSpeakingFrame`` mark the
    assistant's playback. Built by ``PipecatVoiceConnectionLifecycle`` in this module.
    """

    def __init__(self, voice: PipecatVoiceAdapter, assembler: UserSpeechTurnAggregationAssembler,
                 pending: dict, **kwargs) -> None:
        """Keep ``voice``, the connection's voice adapter, ``assembler``, its assembler, and ``pending``, the dict whose
        key ``text`` holds the reply queued for TTS, and pass ``kwargs`` to Pipecat's ``FrameProcessor``, as the class above
        describes."""
        super().__init__(**kwargs)
        self._voice = voice
        self._assembler = assembler
        self._pending = pending
        self._speaking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Call the assembler's ``TTSStarted`` when playback starts, save the pending reply through ``save_assistant``
        when it stops, and push every frame on unchanged, as the class above describes."""
        await super().process_frame(frame, direction)
        if isinstance(frame, BotStartedSpeakingFrame):
            self._speaking = True
            self._assembler.TTSStarted()
        elif isinstance(frame, BotStoppedSpeakingFrame) and self._speaking:
            self._speaking = False
            line = (self._pending.pop("text", "") or "").strip()
            if line:
                self._voice.save_assistant(line)
        await self.push_frame(frame, direction)


async def PipecatVoiceConnectionLifecycle(transport: BaseTransport, runner_args: RunnerArguments, VoiceAdapter: PipecatVoiceAdapter,
                  TTSVoice: str, STTVendor: str, debounce_s: float = 2.5) -> None:
    """Build and run the default speech pipeline the module docstring above lists on ``transport`` for the session
    already open behind ``VoiceAdapter``, until the connection ends, and return ``None``.

    The conversation is the caller's, the provider, the voice adapter and the handlers and hooks registered on it, and
    this function builds only the pipeline. ``transport`` is Pipecat's transport of the connection and ``runner_args``
    the runner's arguments, accepted for the shape every ``Pipeline`` has. ``TTSVoice`` is the Azure Speech voice name
    the replies are spoken with, ``STTVendor`` the name ``PipecatSTTService`` takes, and ``debounce_s`` the pause that
    ends a turn, 2.5 seconds by default. The function registers three handlers on the voice adapter, which send the
    adapter callbacks, the "conversation-state" messages and the log lines as RTVI server messages, builds the
    assembler with a marker that sends the detected conditions, takes typed text from RTVI client messages of type
    "user", and speaks the opening when the connecting side has connected. ``AZURE_SPEECH_KEY`` missing raises
    ``KeyError``, and a vendor that refuses ``TTSVoice`` reports it in Pipecat's log. Called by
    ``PipecatVoiceAdapterWebRtcMount.Attend`` as the default ``Pipeline``.
    """
    # The RTVI processor is handed to the worker, which places it at the very top of the
    # pipeline. There its decoded client audio and its start-streaming signal reach the input
    # transport, which is how Pipecat's eval harness feeds the user's speech in.
    rtvi = RTVIProcessor()

    key = os.environ["AZURE_SPEECH_KEY"]
    from illocutionary_lifecycles.core.environment import Required
    region = Required("AZURE_SPEECH_REGION", "the Azure Speech region of that key, for TTS")
    STTService = PipecatSTTService(STTVendor)
    logger.info(f"STT: {type(STTService).__name__}")
    TTSService = AzureTTSService(
        api_key=key, region=region,
        settings=AzureTTSService.Settings(voice=TTSVoice),
        sample_rate=16000,
    )
    vad = VADProcessor(vad_analyzer=SileroVADAnalyzer(params=VADParams(min_volume=0.2)))
    pipecat_user_turn_processor = UserTurnProcessor(user_turn_strategies=UserTurnStrategies(
        start=[VADUserTurnStartStrategy()],
        stop=[SpeechTimeoutUserTurnStopStrategy()],
    ))
    PendingReplyText: dict = {}

    async def QueueReplyForTTS(reply: str) -> None:
        """Keep ``reply`` for the save after playback and queue it to the pipeline's TTS, as the assembler's ``on_reply``
        in the enclosing ``PipecatVoiceConnectionLifecycle``."""
        PendingReplyText["text"] = reply
        await worker.queue_frames([TTSSpeakFrame(reply)])

    def SendAssemblerConditionRtviServerMessage(tap: str, mark: str, text: str = "") -> None:
        """Send a change of the assembler's detected conditions, one of ``ASSEMBLER_CONDITION_MARKERS``, as an RTVI
        server message of type "interim-threshold-or-playback-overlap" with ``state``, ``reason`` and ``interim_count``,
        ignoring every other mark, as the assembler's ``marker`` in the enclosing ``PipecatVoiceConnectionLifecycle``."""
        if mark not in ASSEMBLER_CONDITION_MARKERS:
            return
        payload: dict = {"type": "interim-threshold-or-playback-overlap",
                         "state": None if mark == ASSEMBLER_CONDITION_MARKERS[2] else mark,
                         "reason": "", "interim_count": None}
        for token in text.split():
            if token.startswith("reason="):
                payload["reason"] = token[len("reason="):]
            elif token.startswith("interim_count="):
                try:
                    payload["interim_count"] = int(token[len("interim_count="):])
                except ValueError:
                    pass
        asyncio.ensure_future(rtvi.send_server_message(payload))

    async def SendConversationStateRtviServerMessage(AdapterCallback: dict) -> None:
        """Send a state change callback also as the RTVI server message of type "conversation-state", with the
        state's index, name and the previous index, ignoring every other callback, as one of the three handlers the
        enclosing ``PipecatVoiceConnectionLifecycle`` registers."""
        if AdapterCallback.get("type") != "ConversationStateChangedAdapterCallbackHandlerEvent":
            return
        await rtvi.send_server_message({
            "type": "conversation-state",
            "state": AdapterCallback.get("conversation_state"),
            "name": AdapterCallback.get("conversation_state_name") or "",
            "previous_state": AdapterCallback.get("previous_conversation_state"),
        })

    VoiceAdapter.RegisterAdapterCallbackHandler(SendConversationStateRtviServerMessage)

    async def SendAdapterCallbackAsRtviServerMessage(AdapterCallback: dict) -> None:
        """Send ``AdapterCallback`` as an RTVI server message without ``turns`` and ``prompt``, unless it is the save
        callback, the same rule ``AdapterMountBase.RelayAdapterCallback`` applies on the WebSocket ways, so every
        connecting program gets the same adapter callbacks a text client gets. The words themselves travel as Pipecat's
        own transcripts. One of the three handlers the enclosing ``PipecatVoiceConnectionLifecycle`` registers."""
        if AdapterCallback.get("type") == "RefreshCycleSavedAdapterCallbackHandlerEvent":
            return
        await rtvi.send_server_message({k: v for k, v in AdapterCallback.items() if k not in ("turns", "prompt")})

    VoiceAdapter.RegisterAdapterCallbackHandler(SendAdapterCallbackAsRtviServerMessage)

    async def SendLogLineAsRtviServerMessage(AdapterCallback: dict) -> None:
        """Send ``AdapterCallback`` in full as an RTVI server message marked ``log`` by ``AdapterMountBase.LogLine``,
        which the browser script hands to ``log.js`` and never to the page's views. One of the three handlers the
        enclosing ``PipecatVoiceConnectionLifecycle`` registers."""
        await rtvi.send_server_message(AdapterMountBase.LogLine(AdapterCallback))

    VoiceAdapter.RegisterAdapterCallbackHandler(SendLogLineAsRtviServerMessage)

    assembler = UserSpeechTurnAggregationAssembler(
        VoiceAdapter, QueueReplyForTTS,
        debounce_s=debounce_s,
        marker=SendAssemblerConditionRtviServerMessage,
    )

    @rtvi.event_handler("on_client_message")
    async def TypedTurnFromRtviClientMessage(_rtvi, message) -> None:
        """Take an RTVI client message of type "user" with ``text``, send the line back as a server message of type
        "PipecatVoiceHeardText", and give it to the assembler's ``segment``, so it joins, in arrival order, the turn being
        spoken or the one waiting for its reply, never a turn of its own. Every other client message is ignored, as the module
        docstring above explains."""
        if message.type != "user":
            return
        line = str((message.data or {}).get("text") or "").strip()
        if not line:
            return
        await rtvi.send_server_message({"type": "PipecatVoiceHeardText", "text": line})
        assembler.segment(line)

    pipeline = Pipeline([
        transport.input(), vad, pipecat_user_turn_processor, STTService,
        STTToAssemblerFrameProcessor(assembler), TTSService,
        SpokenReplySaveFrameProcessor(VoiceAdapter, assembler, PendingReplyText),
        transport.output(),
    ])
    worker = PipelineWorker(pipeline, params=PipelineParams(enable_metrics=True),
                            rtvi_processor=rtvi)

    @transport.event_handler("on_client_connected")
    async def on_connected(_transport, _client):
        """Compose the opening reply when the connecting side has connected, and queue it to TTS when it is not empty, for
        the enclosing ``PipecatVoiceConnectionLifecycle``."""
        logger.info("client connected: composing the opening")
        greeting = (await VoiceAdapter.opening_reply() or "").strip()
        if greeting:
            PendingReplyText["text"] = greeting
            await worker.queue_frames([TTSSpeakFrame(greeting)])

    runner = WorkerRunner()
    await runner.add_workers(worker)
    await runner.run()


# Pipecat's TransportParams per transport name, what its runner builds the transport from.
PipecatTransportParamsByName = {
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
}


class PipecatVoiceAdapterWebRtcMount(AdapterMountBase):
    """The voice way's mount, ``PipecatVoiceAdapter`` on WebRTC through Pipecat's runner, whose ``Way`` is "voice",
    speaking the protocol the module docstring above gives.

    The mount names no speech vendor and holds the offer, the per-connection session and the hooks, while the vendors
    are in the pipeline function. With the default, ``PipecatVoiceConnectionLifecycle``, ``TTSVoice`` is an Azure Speech
    voice name and the STT is the vendor ``STTVendor`` names, and with a server's own ``Pipeline``, ``TTSVoice`` means
    whatever that pipeline makes of it.
    """

    Way = "voice"

    def __init__(self, ConversationStateInitBundle: dict, TTSVoice: str, STTVendor: str,
                 debounce_s: float = 2.5, OnAdapterCallback: Any = None, choose: Any = None, Pipeline: Any = None,
                 OnSessionOpened: Any = None, OnClientMessage: Any = None) -> None:
        """Keep the flow, the hooks, the voice, the STT, the pause, ``choose`` and the pipeline, and raise ``ValueError``
        beginning "the voice mount takes TTSVoice" when ``TTSVoice`` or ``STTVendor`` is missing, because the package
        carries no default voice and no default STT.

        ``ConversationStateInitBundle`` and the three hooks are as ``AdapterMountBase`` takes them, and
        ``OnClientMessage`` is kept but never called on this way. ``TTSVoice`` is the voice the replies are spoken with,
        chosen in the server file. ``STTVendor`` is "azure", "elevenlabs", "openai" or "whisper".
        ``debounce_s`` is the pause that ends a turn, 2.5 seconds by default. ``choose`` is an optional plain function of
        the request data that returns a dict with the optional keys ``conversation`` and ``TTSVoice``, picking the flow
        and the voice for one connection without a subclass. ``Pipeline`` is the async function run per connection,
        ``PipecatVoiceConnectionLifecycle`` when ``None``, with the signature the module docstring above gives.
        """
        super().__init__(ConversationStateInitBundle, OnAdapterCallback, OnSessionOpened, OnClientMessage)
        if not TTSVoice or not STTVendor:
            raise ValueError("the voice mount takes TTSVoice (the TTS voice the replies are spoken with) and STTVendor (the "
                             "STT: azure, elevenlabs, openai or whisper) from the server file; the "
                             "library carries no default voice and no default STT")
        self.TTSVoice = TTSVoice
        self.STTVendor = STTVendor
        self.debounce_s = debounce_s
        self.choose = choose          # the function form of MountConversationStateInitBundle and MountVoiceName, see there
        self.Pipeline = Pipeline or PipecatVoiceConnectionLifecycle   # (transport, runner_args, VoiceAdapter, TTSVoice=, STTVendor=, debounce_s=) -> awaitable

    def MountConversationStateInitBundle(self, RequestData: Any = None) -> dict:
        """Return the flow for one connection, the ``conversation`` that ``choose`` returns for ``RequestData`` when it
        gives one, or else the mount's own flow. Called by ``NewConversationSession`` in this class."""
        picked = (self.choose(RequestData or {}) or {}) if self.choose else {}
        return picked.get("conversation") or self.ConversationStateInitBundle

    def MountVoiceName(self, RequestData: Any = None) -> str:
        """Return the TTS voice name for one connection, a voice the TTS vendor lists, the ``TTSVoice`` that ``choose``
        returns for ``RequestData`` when it gives one, or else the mount's ``TTSVoice``. A server overrides this method,
        or gives ``choose`` when it does not subclass. Called by ``Attend`` in this class."""
        picked = (self.choose(RequestData or {}) or {}) if self.choose else {}
        return str(picked.get("TTSVoice") or self.TTSVoice)

    def NewConversationSession(self, RequestData: Any = None) -> Any:
        """Return a new, started ``SessionProvider`` for one offer, on a deep copy of the flow
        ``MountConversationStateInitBundle`` returns for ``RequestData``, with the question-answer hook on and no
        storage vendor, raising whatever session start-up raises. Called by ``Attend`` in this class."""
        import copy
        from illocutionary_lifecycles.core.session_provider import SessionProvider
        provider = SessionProvider(ConversationStateInitBundle=copy.deepcopy(self.MountConversationStateInitBundle(RequestData)),
                                   InitSystemSetterSettings={"QuestionAnswerHook": True})
        provider.start()
        return provider

    async def Attend(self, runner_args: Any) -> None:
        """Serve one WebRTC connection until it ends and return ``None``, building the session from the offer's request
        data in ``runner_args.body``, the ``PipecatVoiceAdapter`` with the server's ``OnAdapterCallback`` registered,
        Pipecat's transport, calling ``OnSessionOpened`` with ``None`` as the send function, and then running
        ``Pipeline`` with the connection's voice. ``runner_args`` is what Pipecat's runner passes for one connection.
        ``StartWebRtcServerProcess`` in this class gives this method to the runner as the per-connection coroutine."""
        from pipecat.runner.utils import create_transport
        body = getattr(runner_args, "body", None) or {}
        provider = self.NewConversationSession(body)
        VoiceAdapter = PipecatVoiceAdapter(SessionProvider=provider)
        VoiceAdapter.RegisterAdapterCallbackHandler(self.AdapterCallbackHandler(self.OnAdapterCallback))
        transport = await create_transport(runner_args, PipecatTransportParamsByName)
        await self.Opened(provider, VoiceAdapter, None)
        TTSVoice = self.MountVoiceName(body)
        await self.Pipeline(transport, runner_args, VoiceAdapter, TTSVoice=TTSVoice, STTVendor=self.STTVendor, debounce_s=self.debounce_s)

    def MountOnApp(self, app: Any, path: str = "/api/offer") -> None:
        """Prepare Pipecat's runner app ``app`` for this mount by adding ``WebRtcOfferBodyKeyRename`` as middleware and
        making the offers take their ICE servers from the environment, and return ``None``. The offer route,
        "/api/offer", is Pipecat's own, and ``path`` is accepted for the shape every mount's ``MountOnApp`` has and is
        not used, as the module docstring above explains."""
        app.add_middleware(WebRtcOfferBodyKeyRename)   # the connecting side's requestData reaches choose(body)
        ApplyWebRtcIceServersFromEnvironment()

    @staticmethod
    def StartWebRtcServerProcess(PerConnectionEntry: Any, host: str, port: int) -> None:
        """Run Pipecat's runner on ``host`` and ``port`` with the WebRTC transport and ``PerConnectionEntry``, usually
        the mount's ``Attend``, as the per-connection coroutine, and return only when the runner stops. Pipecat's runner
        looks for a function named ``bot`` on the file that was run, so this sets it there, and it replaces
        ``sys.argv`` with the runner's arguments, as the module docstring above explains."""
        from pipecat.runner.run import main
        sys.modules["__main__"].bot = PerConnectionEntry   # Pipecat's runner looks for ``bot`` on the file that was run
        sys.argv = [sys.argv[0], "--host", host, "--port", str(port), "-t", "webrtc"]
        main()
