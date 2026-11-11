"""The VRM character example over Pipecat, viewable in a VR headset, where the microphone stays open and a pause ends the
turn, run by Pipecat's runner on port 7882.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount``, on Pipecat's own runner
app, which also serves Pipecat's page at /client/. The STT and the voice come from ``STT_VENDOR`` and ``TTS_VOICE``, and
this file loads the nearest ``.env``, looking in the folder it starts from and then in each folder above it. Beside its
own page at /page/, it serves the pages of ``../7-plasma-visualizer-pipecat``, ``../6-rive-pipecat`` and
``../1-chatbot-visual-kiosk`` where they are, at /page/plasma/, /page/rive/ and /page/kiosk/, so the page imports their
modules, pictures and licences without copies.
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
for name, folder in (("plasma", "../7-plasma-visualizer-pipecat/page"), ("rive", "../6-rive-pipecat/page"), ("kiosk", "../1-chatbot-visual-kiosk/page")):
    app.mount(f"/page/{name}", StaticFiles(directory=folder))   # those examples' pages served where they are, before /page itself catches the path
app.mount("/page", StaticFiles(directory="page", html=True))  # your VRM page, served at /page/; Pipecat's own page at /client/
mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=7882)
