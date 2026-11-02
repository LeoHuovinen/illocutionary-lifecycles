"""The simplest press-to-speak server, a FastAPI app of your own with the press-to-speak mount on it, the page folder
served beside it, and uvicorn running it on port 7872.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount``, whose docstring
gives the socket's protocol. The voice and the speech language come from the environment variables ``TTS_VOICE`` and
``SPEECH_LANGUAGE``, and the mount needs ``AZURE_SPEECH_KEY`` and ``AZURE_SPEECH_REGION`` too. ``README-PRESS.md`` is
enough to write this file.
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
PressToSpeakAdapterWebsocketMount(
    conversation, language=os.environ["SPEECH_LANGUAGE"],
    TTSVoice=os.environ["TTS_VOICE"],   # the voice is this server's choice, from its environment
).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=7872, log_level="warning")
