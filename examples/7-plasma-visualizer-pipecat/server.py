"""The Plasma visualizer's server, Pipecat's runner app with the voice mount on it and the page folder served beside it,
run on port 7873.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount``. The page draws the
assistant's audio track and its turn label follows Pipecat's RTVI events, which only the voice mount delivers, as
``README-VOICE.md`` explains. The STT and the voice come from ``STT_VENDOR`` and ``TTS_VOICE``.
"""
import json
import os

from dotenv import find_dotenv, load_dotenv
from fastapi.staticfiles import StaticFiles
from pipecat.runner.run import app

from illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount import (
    PipecatVoiceAdapterWebRtcMount,
)

load_dotenv(find_dotenv(usecwd=True), override=True)      # the nearest .env: this folder, then each folder above it
conversation = json.load(open("flow.json"))      # the conversation's flow, used as it is


mount = PipecatVoiceAdapterWebRtcMount(
    conversation, STTVendor=os.environ["STT_VENDOR"],
    TTSVoice=os.environ["TTS_VOICE"],   # the voice is this server's choice, from its environment
)
mount.MountOnApp(app)
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/; Pipecat's own page at /client/
mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=7873)
