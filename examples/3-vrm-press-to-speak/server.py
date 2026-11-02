"""The VRM character example over press-to-speak, where the user holds a button to speak and no Pipecat runs, served by
uvicorn on port 7871.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount``. The example
``examples/5-vrm-pipecat`` is the same example over Pipecat, where a pause ends the turn, and the two differ only in the
mount, the Talk button and the port. The voice and the speech language come from ``TTS_VOICE`` and ``SPEECH_LANGUAGE``,
with ``AZURE_SPEECH_KEY`` and ``AZURE_SPEECH_REGION`` beside them.
"""
import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount import (
    PressToSpeakAdapterWebsocketMount,
)

conversation = json.load(open("flow.json"))      # the conversation's flow, used as it is


app = FastAPI()
PressToSpeakAdapterWebsocketMount(conversation, language=os.environ["SPEECH_LANGUAGE"], TTSVoice=os.environ["TTS_VOICE"]).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))  # your VRM page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=7871, log_level="warning")
