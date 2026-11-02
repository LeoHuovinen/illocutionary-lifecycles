"""The simplest text server, a FastAPI app of your own with the text mount on it, the page folder served beside it, and
uvicorn running it on port 8765.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server as anyone writes one, outside the package, using only its folder ``server``, the one of its four folders
beside ``core``, ``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount``, whose docstring gives the
socket's protocol. The page at /page/ speaks to the socket at /ws through the page scripts beside it. ``README.md`` is
enough to write this file.
"""
import json

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount import TextAdapterWebsocketMount

conversation = json.load(open("flow.json"))      # the conversation's flow, used as it is


app = FastAPI()
TextAdapterWebsocketMount(conversation).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
