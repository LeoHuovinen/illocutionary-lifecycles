# The same conversation served as voice

The environment variables are listed in the main `README.md` at the top of the repository, and the page's surface (callbacks and adapter callbacks) is in the header of `ConnectConversation.js`. This guide covers the voice mount: a server file, a page, and the print and log statements in a section of their own. Working cases of exactly this are `examples/7-plasma-visualizer-pipecat/` (Pipecat's Plasma visualizer on the assistant's audio), `examples/5-vrm-pipecat/` (a VRM character) and `examples/6-rive-pipecat/` (a Rive character).

Needs: the `pipecat` extra, the language model's API key, `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` in the environment (the server below loads the nearest `.env`, looking in the folder it starts from and then in each folder above it), `flow.json` beside the server file, copied from any example and edited, the JSON object whose top-level fields are `PromptBlocks` and `ConversationStates`, which `json.load` reads into the dict the mount class takes as its first argument, a browser with a microphone.

## The server

`server.py`:

```python
# The simplest voice server: Pipecat's runner app, the voice mount on it, your page folder, the runner. Read README-VOICE.md
# first; it is enough to write this file.
import json
import os

from dotenv import find_dotenv, load_dotenv
from fastapi.staticfiles import StaticFiles
from pipecat.runner.run import app

from illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount import (
    PipecatVoiceAdapterWebRtcMount,
)

load_dotenv(find_dotenv(usecwd=True), override=True)      # the nearest .env: this folder, then each folder above it
conversation = json.load(open("flow.json"))      # the dict with PromptBlocks and ConversationStates, used as it is


def OnAdapterCallback(event):                      # [log] every adapter callback the session makes, with its type
    print(event["type"])                         # [log]


mount = PipecatVoiceAdapterWebRtcMount(
    conversation,
    TTSVoice=os.environ["TTS_VOICE"],            # this server's choice, a voice your speech vendor lists, from its own environment
    STTVendor=os.environ["STT_VENDOR"],          # azure, elevenlabs, openai or whisper
    OnAdapterCallback=OnAdapterCallback,             # [log]
)
mount.MountOnApp(app)
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/; Pipecat's own page at /client/
mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=7873)
```

The parameter `STTVendor` (the STT, such as `azure`) is required and has no default. The other parameter is `debounce_s` (the pause that ends a user turn, default 2.5). `StartWebRtcServerProcess` hands Pipecat's runner its own command-line arguments, so the server file cannot read arguments of its own after that call.

## The page

`page/index.html`, with `ConnectConversation.js`, `PipecatVoiceAdapterWebRtcMount.js`, `pipecat-client.js` and `log.js`
beside it in `page/` (copy the four from `examples/7-plasma-visualizer-pipecat/page/`):

```html
<!doctype html>
<meta charset="utf-8">
<title>voice page</title>
<button id="start">Start</button> <span id="phase">not connected</span> <input id="box" placeholder="or type and press Enter">
<script type="module">
  import "./log.js";                             // the two log streams, in the browser console
  import { ConnectConversation } from "./ConnectConversation.js";
  document.getElementById("start").onclick = () => ConnectConversation({   // from a click: Safari and iOS want a gesture
    way: "voice", phase: "#phase", input: "#box",
    onUserMessage: (t) => console.log("YOU:", t), onBotMessage: (t) => console.log("BOT:", t),
  });
</script>
```

`python server.py`, then open `http://127.0.0.1:7873/page/`, press Start, speak. Pipecat's own page is at `/client/`. The phase runs through connecting, listening, thinking, speaking.

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

A page does not need any code from Pipecat. The mount's browser script (`PipecatVoiceAdapterWebRtcMount.js`, beside the page, loaded by `ConnectConversation.js` for way `voice`) already wraps the Pipecat client: it posts the offer to `/api/offer`, opens the microphone, plays the assistant's track and turns the SDK's events into the callbacks listed in the header of `ConnectConversation.js`. A page imports that one script and calls `ConnectConversation` from a click.

How it works. The SDK's own README (`https://github.com/pipecat-ai/pipecat-client-web/blob/main/README.md`) and the SmallWebRTC transport README (`https://github.com/pipecat-ai/pipecat-client-web-transports/blob/main/transports/small-webrtc-transport/README.md`) describe a client built with npm and an import map; a page served by this library has neither, so the client is bundled as `pipecat-client.js`, copied beside the page, and wrapped once, and every page gets the same callbacks whether the server runs text or voice. Only a page that needs something the callbacks do not carry, such as the SDK's raw events or its own transport settings, imports `./pipecat-client.js` directly and follows those two READMEs; its server still mounts `PipecatVoiceAdapterWebRtcMount`, and the offer endpoint is still `/api/offer`.
