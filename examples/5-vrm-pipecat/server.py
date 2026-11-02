"""The VRM character example over Pipecat, where the microphone stays open and a pause ends the turn, run by Pipecat's
runner on port 7877.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount``, on Pipecat's own runner
app, which also serves Pipecat's page at /client/. The example ``examples/3-vrm-press-to-speak`` is the same example
over press-to-speak, with no Pipecat, and the two differ only in the mount, the Talk button and the port. The STT and
the voice come from ``STT_VENDOR`` and ``TTS_VOICE``, and this file loads the nearest ``.env``, looking in the folder it
starts from and then in each folder above it.
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


mount = PipecatVoiceAdapterWebRtcMount(conversation, STTVendor=os.environ["STT_VENDOR"], TTSVoice=os.environ["TTS_VOICE"])
mount.MountOnApp(app)
app.mount("/page", StaticFiles(directory="page", html=True))  # your VRM page, served at /page/; Pipecat's own page at /client/
mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=7877)
