# The same conversation spoken while a button is held

The environment variables are listed in the main `README.md` at the top of the repository, and the page's surface (callbacks and adapter callbacks) is in the header of `ConnectConversation.js`. This guide covers the press-to-speak mount: a server file, a page, and the print and log statements in a section of their own. The simplest working case of exactly this is `examples/2-press-to-speak/`.

The user holds a button while speaking and lets go to send. Nothing is heard while the button is not held, and a press while the assistant speaks is ignored, so the user never talks over the assistant. There is no Pipecat and no WebRTC: the speech streams over the same kind of websocket the text mount uses while the button is held, Azure Speech transcribes it as it arrives, the session answers as on the text mount, and Azure Speech speaks the reply back. It also works where WebRTC is blocked.

Needs: the `press` extra (the `text` extra and Azure's Speech SDK, `azure-cognitiveservices-speech`), the language model's API key, `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` in the environment (export them in the shell; this server reads no `.env`), `flow.json` beside the server file, copied from any example and edited, the JSON object whose top-level fields are `PromptBlocks` and `ConversationStates`, which `json.load` reads into the dict the mount class takes as its first argument, a browser with a microphone.

## The server

`server.py`:

```python
"""The simplest press-to-speak server, a FastAPI app of your own with the press-to-speak mount on it, the page folder
served beside it, and uvicorn running it on port 7872.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
server outside the package that uses only its folder ``server``, through
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

conversation = json.load(open("flow.json"))      # the dict with PromptBlocks and ConversationStates, used as it is


def OnAdapterCallback(event):                      # [log] every adapter callback the session makes, with its type
    print(event["type"])                         # [log]


app = FastAPI()
PressToSpeakAdapterWebsocketMount(
    conversation,
    TTSVoice=os.environ["TTS_VOICE"],            # this server's choice, a voice your speech vendor lists, from its own environment
    language=os.environ["SPEECH_LANGUAGE"],      # the user's speech, a BCP-47 tag
    OnAdapterCallback=OnAdapterCallback,             # [log]
).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=7872, log_level="warning")
```

The parameter `language` (what the STT listens for, such as `en-US`) is required and has no default. The server stops at start when `AZURE_SPEECH_KEY` is not set.

## The page

`page/index.html`, with `ConnectConversation.js`, `PressToSpeakAdapterWebsocketMount.js` and `log.js` beside it in
`page/` (copy the three from `examples/2-press-to-speak/page/`):

```html
<!doctype html>
<meta charset="utf-8">
<title>press to speak</title>
<button id="start">Start</button> <button id="talk">Hold to speak</button> <button id="click-talk">Click to speak</button> <span id="phase">not connected</span>
<input id="box" placeholder="or type and press Enter">
<script type="module">
  import "./log.js";                             // the two log streams, in the browser console
  import { ConnectConversation } from "./ConnectConversation.js";
  document.getElementById("start").onclick = () => ConnectConversation({   // from a click: Safari and iOS want a gesture
    way: "press", talk: "#talk", clickTalk: "#click-talk", phase: "#phase", input: "#box",
    onUserMessage: (t) => console.log("YOU:", t), onBotMessage: (t) => console.log("BOT:", t),
  });
</script>
```

`python server.py`, then open `http://127.0.0.1:7872/page/`, press Start, then hold the button while you speak and let go,
or click once to start and once to finish. The browser asks for the microphone once, at Start. Both buttons read
"Loading…" until the assistant's opening has been spoken, and are greyed out while the assistant speaks. The phase runs through
connecting, thinking, speaking, listening.

`allowInterrupt: true` among the same options lets a new press stop the assistant's playback; without it, a press while the assistant
speaks is ignored. A typed line (`input`, or `conversation.sendText(text)` on what `ConnectConversation` returns) joins
the speech into one turn, and its reply is spoken too.

## Printing and logging what happens

The server runs without any of this. The log stream is the mount's own: every recorded event (the save of the cards,
with `turns`, `streams` and `prompt`, marked `"log": "event"`) and every adapter callback (a state change, an answered
question, an incremental phrase pick, marked `"log": "adapter callback"`), two different things, one
JSON line each. On the text and press mounts the lines arrive on the connection's own socket, each marked `log`; on the
voice mount they are sent over WebRTC as RTVI server messages marked `log`. Every example page carries
one row, which prints the stream in the browser console and puts nothing on the page:

```js
  import "./log.js";                               // the log stream, in the browser console: recorded events and adapter callbacks
```

On the server, a handler of your own for the adapter callbacks is still one argument of the mount, `OnAdapterCallback`,
a plain function or an `async` one of the callback dict.

## Building on another project's tutorial

A page does not need a recorder from another tutorial. The mount's browser script (`PressToSpeakAdapterWebsocketMount.js`, beside the page, loaded by `ConnectConversation.js` for way `press`) already records the microphone on the audio thread while the button is held, sends it as 16 kHz mono PCM, plays the reply and measures it, so views get `level`, `track` and `botWordSaid` and a VRM page or a visualizer works on press as on voice.

How it works. The socket is the mount's own `/ws`. A hold is `{"type": "PressToSpeakHoldStart"}`, then 16 kHz 16-bit mono PCM as binary frames while the button is held, then `{"type": "PressToSpeakHoldEnd"}`; the server recognises the speech as it arrives and answers `{"type": "PressToSpeakHeardText", "text": ..., "final": false}` on every interim transcription and with `"final": true` on every final one, so the incremental analyzers run on the speech so far during the hold exactly as on the voice way. A text frame is typed text; it joins the speech into one turn. The reply comes as `{"type": "PressToSpeakReplyText", "text": ..., "audio": true, "words": [{"text", "offset_ms", "duration_ms"}, ...]}` and then its audio as one binary WAV frame; the page's script hands each word to the views as it plays (`botWordSaid`). A binary frame outside a hold is dropped. An Android app or a robot speaks this protocol directly; no Pipecat is involved on either side.
