# The text API

An example of the pure text API of IL's text mount (`../README-TEXT.md`), a WebSocket endpoint at `/ws` that any client can
connect to and use for anything you like. The page beside it is one such client, an input box with the user's lines and the
assistant's replies printed one under another. This example is text-only.

`python server.py`, open `http://127.0.0.1:8765/page/`, type.

| file | what it is |
|---|---|
| `server.py` | the text mount on a FastAPI app, with the page folder served at `/page/` |
| `flow.json` | the conversation the server runs |
| `page/index.html` | the page, an input box and the printed lines |
| `page/ConnectConversation.js`, `page/TextAdapterWebsocketMount.js`, `page/log.js` | IL's browser scripts, the same in every example |
