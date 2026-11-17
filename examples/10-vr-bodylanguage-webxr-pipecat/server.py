"""The head nod and head shake example over Pipecat, viewable in a VR headset, where the microphone stays open and a
pause ends the turn, run by Pipecat's runner on port 7883.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, the one of its four folders beside ``core``,
``analyzers`` and ``memory`` that a program outside it speaks to, through
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount``, on Pipecat's own runner
app, which also serves Pipecat's page at /client/. The STT and the voice come from ``STT_VENDOR`` and ``TTS_VOICE``, and
this file loads the nearest ``.env``, looking in the folder it starts from and then in each folder above it. Beside its
own page at /page/, it serves the page of ``../9-vrm-webxr-pipecat`` where it is, at /page/vr/, so the page imports its
karaoke and its panels in VR without copies.

A head nod or a head shake reaches the session as a typed line that joins the person's spoken turn. Beside that, the
page may post a client message to /OnClientMessage, which makes one of two session calls by the message's type, and
neither joins the turn.
"""
import json
import os

from dotenv import find_dotenv, load_dotenv
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from pipecat.runner.run import app

from illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount import (
    PipecatVoiceAdapterWebRtcMount,
)

load_dotenv(find_dotenv(usecwd=True), override=True)      # the nearest .env: this folder, then each folder above it
conversation = json.load(open("flow.json"))      # the conversation's flow, used as it is
OpenedSessionProvider = {"SessionProvider": None}


def OnSessionOpened(provider, adapter, send):
    """Keep the session of the connection that just opened, so OnClientMessage can reach it. One page connects at a
    time, and a later connection replaces the earlier one."""
    OpenedSessionProvider["SessionProvider"] = provider


# The two session calls a client message may ask for, by the message's type. Each is a call of the same name on the
# session, and neither joins the person's turn.
#   IncrementalPhraseTick              the text goes to the incremental analyzers of the current state
#   SetNonconversationalContentSocket  the text is placed where the flow holds {pNonconversationalContentSocketState},
#                                      replacing the text before it, and an empty text removes it
SessionProviderCalls = {
    "IncrementalPhraseTick": lambda provider, text: provider.IncrementalPhraseTick({"IncrementalPhrase": text}),
    "SetNonconversationalContentSocket": lambda provider, text: provider.SetNonconversationalContentSocket(text),
}


@app.post("/OnClientMessage")
async def OnClientMessage(request: Request):
    """Take one client message from the page, a JSON object with type and text, and make the session call its type
    names. The voice mount does not call its own OnClientMessage hook, so the page posts here. A line that joins the
    person's spoken turn does not come here, because the page sends it as a typed line. A further kind of message is
    one more entry in SessionProviderCalls."""
    body = await request.json()
    provider, call = OpenedSessionProvider["SessionProvider"], SessionProviderCalls.get(body.get("type"))
    if provider is None or call is None:
        return {"ok": False}
    call(provider, str(body.get("text") or "").strip())
    return {"ok": True}


mount = PipecatVoiceAdapterWebRtcMount(conversation, STTVendor=os.environ["STT_VENDOR"], TTSVoice=os.environ["TTS_VOICE"],
                                       OnSessionOpened=OnSessionOpened)
mount.MountOnApp(app)
app.mount("/page/vr", StaticFiles(directory="../9-vrm-webxr-pipecat/page"))   # example 9's page served where it is, before /page itself catches the path
app.mount("/page", StaticFiles(directory="page", html=True))  # this example's page, served at /page/; Pipecat's own page at /client/
mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=7883)
