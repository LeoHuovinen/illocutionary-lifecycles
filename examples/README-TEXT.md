# A conversation served as text

The environment variables are listed in the main `README.md` at the top of the repository, and the page's surface (callbacks and adapter callbacks) is in the header of `ConnectConversation.js`. This guide covers the text mount: a server file of your own with the text mount on it, a page, and the print and log statements in a section of their own. The mount is `TextAdapterWebsocketMount`; your server owns the app, the page folder and the port. The simplest working case of exactly this is `examples/0-text/`.

Needs: the `text` extra, the language model's API key in the environment, and `flow.json` beside the server file, copied from any example and edited, the JSON object whose top-level fields are `PromptBlocks` and `ConversationStates`, which `json.load` reads into the dict the mount class takes as its first argument.

## The server

`server.py`:

```python
"""The simplest text server, a FastAPI app of your own with the text mount on it, the page folder served beside it, and
uvicorn running it on port 8765.

The package runs a conversation between a user and a language model from the flow in ``flow.json``, and this file is a
standalone server, outside the package, using only its folder ``server`` through
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount``, whose docstring gives the
socket's protocol. The page at /page/ speaks to the socket at /ws through the page scripts beside it. ``README-TEXT.md`` is
enough to write this file.
"""
import json

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount import TextAdapterWebsocketMount

conversation = json.load(open("flow.json"))      # the dict with PromptBlocks and ConversationStates, used as it is


def OnAdapterCallback(event):                      # [log] every adapter callback the session makes, with its type
    print(event["type"])                         # [log]


app = FastAPI()
TextAdapterWebsocketMount(conversation, OnAdapterCallback=OnAdapterCallback).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
```

## The page

`page/index.html` uses only a WebSocket: what is typed goes out as a text frame, the reply comes back as
`{"type": "TextReplyText", "text": ...}` and is printed.

```html
<!doctype html>
<meta charset="utf-8">
<title>text page</title>
<input id="box" placeholder="type and press Enter" autofocus><pre id="log"></pre>
<script>
  const show = (t) => { document.getElementById("log").textContent += t + "\n"; };
  const socket = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  socket.onmessage = (m) => { const r = JSON.parse(m.data); if (r.type === "TextReplyText") show(`BOT: ${r.text}`); };
  document.getElementById("box").onchange = (ev) => { socket.send(ev.target.value); show(`YOU: ${ev.target.value}`); ev.target.value = ""; };
</script>
```

`python server.py`, then open `http://127.0.0.1:8765/page/`. The opening arrives at connect; each typed line is printed as `YOU:` and its reply as `BOT:`.

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

`log.js` prints what the mount's browser script hands it, so a page that uses it also carries `ConnectConversation.js`
and `TextAdapterWebsocketMount.js` beside it in its own folder: copy all three from `examples/0-text/page/`.

On the server, a handler of your own for the adapter callbacks is still one argument of the mount, `OnAdapterCallback`,
a plain function or an `async` one of the callback dict.


## The same conversation as an OpenAI-compatible API

`HTTPEndpointMount` serves the same flow to programs instead of pages, in the request and reply formats of OpenAI's
API, with the conversation kept on the server under the caller's API key. It is the server above with one import and
one line changed and the page folder left out:

```python
from illocutionary_lifecycles.server.adapter_mounts.http_mounts.HTTPEndpointMount import HTTPEndpointMount

HTTPEndpointMount(conversation).MountOnApp(app, "/v1")
```

Without a server file of your own, `python -m illocutionary_lifecycles.server.OpenAIServer flow.json` serves one
dialogue flow the same way on port 8765, with `--port`, `--route`, `--idle-seconds`, `--model-name`, `--help-text-file`
and `--ended-text` as its options, and prints the curl row to try it. One key is one conversation at a time, and
[`README-HTTPEndpointMount.md`](../illocutionary_lifecycles/server/adapter_mounts/http_mounts/README-HTTPEndpointMount.md)
beside the mount explains it for the person who connects to it.
