"""The text way, ``TextAdapterWebsocketMount``, which puts ``TextAdapter`` on a WebSocket, so typed lines are turns and
the replies and the adapter callbacks come back as JSON, one of the three mounts that replace each other by way.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this mount, in the folder ``server``, is the simplest way to hold
one, with typed turns only. Per connection it builds a session of the folder ``core``, whose checks run in
``analyzers`` and whose record is kept in ``memory``. The connecting side may be a browser page with
``TextAdapterWebsocketMount.js`` beside it in the page's folder, a mobile app, a robot or any WebSocket
client, and the protocol below is all such a program implements.

The socket's URL path is the ``SocketPath`` given to ``MountOnApp``, "/ws" by default, and the URL's query string, for
example session=abc, is the connection's request data, handed to ``NewConversationSession`` before the session opens.
At connection the assistant's opening comes back as a JSON object whose ``type`` is "TextReplyText" with ``text``,
without waiting for a first message. A text frame from the connecting side is one turn, and so is a JSON object whose
``type`` is "user" with ``text``. Each turn's line comes back first as a JSON object whose ``type`` is "TextHeardText"
with ``text``, when the session takes it, so the connecting side shows the lines in the conversation's order, and the
reply then comes back as "TextReplyText" and is saved once sent. Any other JSON object is a message for the server and
reaches ``OnClientMessage``. Every adapter callback except the save callback comes back as JSON with its ``type`` and
without ``turns`` and ``prompt``, and every callback comes back in full as a separate line with the key ``log``, as
``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase`` explains. The extra ``text`` installs what the mount
needs, FastAPI, uvicorn and websockets, and the server file needs the model's variables in its environment, as
``illocutionary_lifecycles.core.clients.llm`` explains. ``examples/0-text/server.py`` is one server built on it.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase import AdapterMountBase


class TextAdapterWebsocketMount(AdapterMountBase):
    """The text way's mount, ``TextAdapter`` on a WebSocket, whose ``Way`` is "text", built by a server file with the
    flow and the three optional hooks of ``AdapterMountBase``, as the module docstring above explains."""

    Way = "text"

    async def Attend(self, SendToConnectingSide: Any, ReceiveFromConnectingSide: Any, RequestData: Any = None) -> None:
        """Serve one connection until the connecting side closes it, following the protocol the module docstring above
        gives, and return ``None``.

        ``SendToConnectingSide`` is an async function that sends one JSON object, ``ReceiveFromConnectingSide`` an async
        function that returns the next text frame, and ``RequestData`` the connection's request data. The mount builds
        the session and the ``TextAdapter``, registers the relay, the log relay and the server's hook, starts the session,
        calls ``OnSessionOpened``, sends the opening and then handles each frame in order. Called by the socket route
        ``MountOnApp`` adds."""
        from illocutionary_lifecycles.server.adapters.text_adapters.TextAdapter import TextAdapter

        async def frames():
            """Yield each non-empty frame from the connecting side, as a dict when it is a JSON object and as its stripped
            text otherwise, for the enclosing ``Attend``."""
            while True:
                frame = str(await ReceiveFromConnectingSide() or "").strip()
                if not frame:
                    continue
                if frame[:1] == "{":
                    try:
                        data = json.loads(frame)
                    except ValueError:
                        data = None
                    if isinstance(data, dict):
                        yield data
                        continue
                yield frame

        provider = self.NewConversationSession(RequestData)
        adapter = TextAdapter(provider)
        adapter.RegisterAdapterCallbackHandler(self.RelayAdapterCallback(SendToConnectingSide))
        adapter.RegisterAdapterCallbackHandler(self.LogRelay(SendToConnectingSide))
        adapter.RegisterAdapterCallbackHandler(self.AdapterCallbackHandler(self.OnAdapterCallback))
        adapter.open_session()
        await self.Opened(provider, adapter, SendToConnectingSide)

        async def reply_with(reply: str) -> None:
            """Send ``reply`` as "TextReplyText" and save it through the adapter once sent, when it is not empty, for the
            enclosing ``Attend``."""
            await SendToConnectingSide({"type": "TextReplyText", "text": reply or ""})
            if reply:
                adapter.save_assistant(reply)

        await reply_with(await adapter.opening_reply())

        async def turn(text: str) -> None:
            """Send ``text`` back as "TextHeardText", give it to the session as one turn, and send the reply, for the
            enclosing ``Attend``."""
            await SendToConnectingSide({"type": "TextHeardText", "text": text})   # the line as the session takes it, in its order
            await reply_with(await adapter.on_user_turn(text))

        async for frame in frames():
            if isinstance(frame, dict):
                if frame.get("type") == "user":
                    text = str(frame.get("text") or "").strip()
                    if text:
                        await turn(text)
                else:
                    await self.ClientMessage(provider, frame)
                continue
            await turn(frame)

    def MountOnApp(self, app: Any, SocketPath: str = "/ws") -> None:
        """Add the one route of the text way to the FastAPI app ``app``, a WebSocket at ``SocketPath``, "/ws" by default,
        whose handler accepts each connection and runs ``Attend`` on it until the connecting side closes it, and return
        ``None``. The example servers call it with the path given positionally, as the module docstring above explains."""
        mount = self

        async def ws(sock: WebSocket) -> None:
            """Accept the socket ``sock`` and serve it with ``Attend``, ending quietly when the connecting side closes it,
            as the route the enclosing ``MountOnApp`` adds."""
            await sock.accept()
            try:
                await mount.Attend(sock.send_json, sock.receive_text, dict(sock.query_params))
            except WebSocketDisconnect:
                pass   # The connecting side closed its socket: the session ends with it.

        app.websocket(SocketPath)(ws)
