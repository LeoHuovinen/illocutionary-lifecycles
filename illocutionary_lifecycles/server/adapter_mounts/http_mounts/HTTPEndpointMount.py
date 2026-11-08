"""``HTTPEndpointMount`` serves a flow as an HTTP API in the request and reply formats of OpenAI's API, so a program or
a tool written for that API holds the conversation with only the address and the key changed. It is the fourth mount,
beside the three that serve a page.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this mount, in the folder ``server``, is how a program reaches it over
HTTP, an automation tool, a no-code app, a game or a script with the ``openai`` library. Per conversation it builds a
session of the folder ``core``, whose checks run in ``analyzers`` and whose record is kept in ``memory``, and keeps it
in memory between requests, since a request has no connection to live in. ``README-HTTPEndpointMount.md`` beside this
file says the same for the person who connects a program, and is the default reply to the command ``HELP``.

The conversation lives on the server under the API key. The key in ``Authorization: Bearer <key>`` names the live
conversation, one key is one conversation at a time, and several people or devices at once need one key each. Every call
is the next turn. Only the newest message whose role is "user" is read, and every earlier message the tool sends along,
its own memory of the conversation, and every system message, is ignored, since the flow defines the system.
``previous_response_id``, ``conversation``, ``user``, ``store``, ``stream``, ``tools``, ``temperature`` and
``instructions`` are read and ignored as well, and ``model`` is information only, echoed back as ``ModelName``.

The flow speaks first, so the first call opens the conversation. A first call with no user message returns the opening
line alone. A first call that already carries a user message, which most tools send, returns the opening line and the
reply to that message together, separated by a blank line, so the person still gets the greeting.

The conversation ends in four ways, and the next call with the same key then opens a new one and gets the opening line
again. It ends when the flow reaches an ending state, one without ``ConversationStateTransitionCriteria``. It ends after
``IdleSeconds`` without a turn, 180 by default, three minutes. It ends when the server restarts, since the sessions live
in the memory of the one server process, so a server must run as one process, not as several workers. And it ends on the
command ``END`` or ``STOP``, sent as the whole user message in capitals, which answers ``EndedText``. The third command,
``HELP``, answers ``HelpText``, the text of ``README-HTTPEndpointMount.md`` unless the server passes its own. The
commands match only the whole message in capitals, so ordinary text never triggers them. ``END`` and ``STOP`` drop the
session, ``HELP`` leaves it as it is. A call whose ``metadata`` holds ``{"conversation": "new"}`` also ends the live
conversation before answering, which is the format's own channel for such a request, but not every tool lets the person
set ``metadata``, which is why ``END`` exists.

Every reply carries ``metadata`` with two keys. ``conversation`` is "new", "continued" or "ended". ``history`` is "none"
when the call carried only the newest message, "consistent" when the earlier messages it carried are what this
conversation actually said, truncated or not, and "stale" when they describe a conversation this server does not have,
which happens when the tool kept its memory across an ending, a timeout, a restart or an ``END``, or when two devices
share one key, so the first call after a server restart can already report it. The reply is still the live
conversation's answer to the newest message.

The routes, under ``Path`` given to ``MountOnApp``, "/v1" by default, with cross-origin headers for every origin added
when the app has no ``CORSMiddleware``, since the connecting side is usually on another origin.

- ``POST <Path>/chat/completions``, the Chat Completions format, what most tools and most code send. The newest user
  message in ``messages`` is the turn. The reply is ``{"id", "object": "chat.completion", "created", "model",
  "metadata", "choices": [{"index": 0, "message": {"role": "assistant", "content"}, "finish_reason": "stop"}],
  "usage"}``.
- ``POST <Path>/responses``, the Responses format, what the ``openai`` library's ``responses.create`` sends. ``input``
  as a string is the turn, as a list its newest user item is. The reply is ``{"id", "object": "response", "created_at",
  "model", "status", "output_text", "metadata", "output": [{"type": "message", "role": "assistant", "content": [{"type":
  "output_text", "text"}]}], "usage"}``.
- ``GET <Path>/models``, which many tools call first, ``{"object": "list", "data": [{"id", "object": "model"}]}`` with
  the one name ``ModelName``.

``model`` in a request is information only, the key decides the flow, and the reply echoes ``ModelName``. Errors are
``{"error": {"message", "type", "code"}}``, 400 ``invalid_request_error`` for a body the mount cannot read or a
``ValueError`` from ``NewConversationSession``, and whatever a server raises as ``HTTPEndpointRefusal``, which carries
its own status, for its key check or its limit, 401 ``invalid_api_key`` and 429 ``rate_limit_exceeded`` by convention.

What a server overrides. ``Authenticate(RequestData)`` checks the key and raises ``HTTPEndpointRefusal`` to refuse, and
does nothing by default, so a bare mount accepts every key and even no key. ``SessionKey(RequestData)`` names the
conversation, the bearer string by default, so callers with no key share one conversation. ``NewConversationSession``
builds the session as on every mount, choosing the flow and the storage from ``RequestData``. ``RequestData`` is a dict
with ``authorization``, the header's value after "Bearer ", ``model``, ``body``, the whole JSON body, and ``metadata``,
the body's ``metadata`` dict. The extra ``text`` installs what the mount needs, FastAPI and uvicorn, and the server file
needs the model's variables in its environment, as ``illocutionary_lifecycles.core.clients.llm`` explains."""
from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase import AdapterMountBase

logger = logging.getLogger(__name__)


class HTTPEndpointRefusal(Exception):
    """An error a server raises from ``Authenticate``, ``SessionKey`` or ``NewConversationSession`` to refuse a request
    in the API's own error shape, with ``Status``, the HTTP status, ``Message``, ``Type``, "invalid_request_error" by
    default, ``Code``, such as "invalid_api_key" or "rate_limit_exceeded", and ``RetryAfterSeconds``, sent as the
    ``Retry-After`` header when given, as the module docstring above explains."""

    def __init__(self, Status: int, Message: str, Type: str = "invalid_request_error", Code: str | None = None,
                 RetryAfterSeconds: int | None = None) -> None:
        super().__init__(Message)
        self.Status = Status
        self.Message = Message
        self.Type = Type
        self.Code = Code
        self.RetryAfterSeconds = RetryAfterSeconds


def ErrorResponse(Status: int, Message: str, Type: str = "invalid_request_error", Code: str | None = None,
                  RetryAfterSeconds: int | None = None) -> JSONResponse:
    """Return the API's error shape, ``{"error": {"message", "type", "code"}}``, with the HTTP status ``Status`` and
    the ``Retry-After`` header when ``RetryAfterSeconds`` is given. Called by the routes ``MountOnApp`` adds."""
    headers = {"Retry-After": str(RetryAfterSeconds)} if RetryAfterSeconds is not None else None
    return JSONResponse({"error": {"message": Message, "type": Type, "code": Code}}, status_code=Status,
                        headers=headers)


def _text_of(Content: Any) -> str:
    """Return the text of a message's ``content``, a string as it is and a list of parts joined by their ``text``,
    stripped, for the routes of ``HTTPEndpointMount``."""
    if isinstance(Content, str):
        return Content.strip()
    if isinstance(Content, list):
        return " ".join(str(part.get("text") or "") for part in Content if isinstance(part, dict)).strip()
    return ""


def _said(Items: Any) -> list[tuple[str, str]]:
    """Return the user and assistant messages of ``Items`` as ``(role, text)`` pairs in order, leaving out system
    messages and anything that is not a message, or an empty list for a string or nothing, for the routes of
    ``HTTPEndpointMount``."""
    if not isinstance(Items, list):
        return []
    return [(item["role"], _text_of(item.get("content"))) for item in Items
            if isinstance(item, dict) and item.get("role") in ("user", "assistant")]


class HTTPEndpointMount(AdapterMountBase):
    """The mount that serves a flow as an HTTP API in OpenAI's formats, with ``TextAdapter`` behind it, whose ``Way``
    is "text", built by a server file with the flow, ``IdleSeconds``, ``ModelName``, ``HelpText``, ``EndedText`` and the
    three optional hooks of ``AdapterMountBase``, as the module docstring above explains."""

    Way = "text"
    Commands = ("END", "STOP", "HELP")

    def __init__(self, ConversationStateInitBundle: dict, IdleSeconds: int = 180,
                 ModelName: str = "IL HTTP OpenAI endpoint", HelpText: str | None = None,
                 EndedText: str | None = None, **Hooks: Any) -> None:
        """Keep the flow and the hooks as ``AdapterMountBase`` does, ``IdleSeconds``, after which a conversation with no
        turn ends, 180 by default, ``ModelName``, the one name ``GET <Path>/models`` lists and every reply echoes,
        ``HelpText``, the reply to the command ``HELP``, the text of ``README-HTTPEndpointMount.md`` beside this file by
        default, and ``EndedText``, the reply to ``END`` and ``STOP``, and start the empty conversation store. A server
        that issues keys passes its own ``HelpText`` and ``EndedText``, written for the people who hold its keys."""
        super().__init__(ConversationStateInitBundle, **Hooks)
        self.IdleSeconds = IdleSeconds
        self.ModelName = ModelName
        if HelpText is None:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README-HTTPEndpointMount.md"),
                      encoding="utf-8") as readme:
                HelpText = readme.read().strip()
        self.HelpText = HelpText
        self.EndedText = EndedText if EndedText is not None else (
            "The conversation has ended. The next message to this address with this key starts a new one.")
        # Session key -> {"provider", "adapter", "lock", "last", "opening", "record"}, every live conversation, in this
        # process only, so the server runs as one process. "record" is what the connecting side received, user and
        # assistant texts in order, for the history check.
        self.Sessions: dict[str, dict[str, Any]] = {}

    # ---- what a server overrides ----
    def Authenticate(self, RequestData: Any) -> None:
        """Check the request's key and raise ``HTTPEndpointRefusal`` to refuse it, 401 for an unknown key or 429 for a
        key over its limit by convention, and return ``None`` to accept. Does nothing by default, so a bare mount
        accepts every key and no key at all. Called first on every route ``MountOnApp`` adds."""
        return None

    def SessionKey(self, RequestData: Any) -> str:
        """Return the key under which the conversation of ``RequestData`` is kept, the bearer string by default, so
        callers that send no key share one conversation. A server overrides this to key by its own notion of the key,
        such as a hash. Called by the two POST routes after ``Authenticate``."""
        return str(RequestData.get("authorization") or "")

    # ---- the conversation ----
    def _sweep(self) -> None:
        """End every conversation with no turn for ``IdleSeconds``, for ``Attend``."""
        now = time.time()
        for key in [k for k, row in self.Sessions.items() if now - row["last"] > self.IdleSeconds]:
            self.Sessions.pop(key, None)

    @staticmethod
    def _is_ending(provider: Any) -> bool:
        """Return whether ``provider``'s current state is an ending, one with no
        ``ConversationStateTransitionCriteria``, for ``Attend``."""
        state = getattr(provider, "SystemState", None)
        states = getattr(state, "ConversationStates", None) or {}
        entry = states.get(str(getattr(state, "conversation_state", 0)))
        return isinstance(entry, dict) and "ConversationStateTransitionCriteria" not in entry

    @staticmethod
    def _history(record: list[tuple[str, str]], said: list[tuple[str, str]]) -> str:
        """Return "none", "consistent" or "stale", the history check of the module docstring, comparing ``said``, the
        user and assistant messages the call carried before its newest user message, with ``record``, what this
        conversation's connecting side received. Consistent means ``said``, roles and texts, is a contiguous part of
        ``record``, so a tool that keeps only its last turns still passes."""
        earlier = said[:-1] if said and said[-1][0] == "user" else said
        if not earlier:
            return "none"
        fits = any(record[i:i + len(earlier)] == earlier for i in range(len(record) - len(earlier) + 1))
        return "consistent" if fits else "stale"

    async def _open(self, RequestData: Any) -> dict[str, Any]:
        """Build and start one conversation for ``RequestData`` and return its row, for ``Attend``. The sequence is the
        one the mount base lists, ``NewConversationSession``, the adapter, the server's handler, the start, ``Opened``
        with no send function since nothing is pushed over HTTP, and the opening, saved once composed."""
        from illocutionary_lifecycles.server.adapters.text_adapters.TextAdapter import TextAdapter

        provider = self.NewConversationSession(RequestData)
        adapter = TextAdapter(provider)
        adapter.RegisterAdapterCallbackHandler(self.AdapterCallbackHandler(self.OnAdapterCallback))
        adapter.open_session()
        await self.Opened(provider, adapter, None)
        opening = await adapter.opening_reply()
        if opening:
            adapter.save_assistant(opening)
        return {"provider": provider, "adapter": adapter, "lock": asyncio.Lock(), "last": time.time(),
                "opening": opening, "record": []}

    async def Attend(self, RequestData: Any, Said: list[tuple[str, str]]) -> tuple[str, str, dict[str, str]]:
        """Serve one call and return ``(reply, session id, metadata)``, following the module docstring above.
        ``Said`` holds the call's user and assistant messages in order, as ``_said`` gives them, and its last user
        message is the turn, "" when there is none. Called by the two POST routes ``MountOnApp`` adds."""
        self._sweep()
        key = self.SessionKey(RequestData)
        text = Said[-1][1] if Said and Said[-1][0] == "user" else ""
        if text in self.Commands:                                                    # the commands
            row = self.Sessions.get(key)
            sid = row["provider"].session_id if row else ""
            if text == "HELP":
                return self.HelpText, sid, {"conversation": "continued" if row else "none", "history": "none"}
            self.Sessions.pop(key, None)
            return self.EndedText, sid, {"conversation": "ended", "history": "none"}
        if (RequestData.get("metadata") or {}).get("conversation") == "new":            # the metadata way to start over
            self.Sessions.pop(key, None)
        row = self.Sessions.get(key)
        history = self._history(row["record"], Said) if row else ("none" if len(Said) <= 1 else "stale")
        started = row is None
        if started:
            row = self.Sessions[key] = await self._open(RequestData)
        async with row["lock"]:
            if not text:                                                             # the opening alone
                reply = row["opening"]
            else:
                reply = await row["adapter"].on_user_turn(text)
                if reply:
                    row["adapter"].save_assistant(reply)
                if started and row["opening"]:                                       # opening and reply together
                    reply = f"{row['opening']}\n\n{reply}"
                row["record"] += [("user", text), ("assistant", reply)]
            row["last"] = time.time()
            if self._is_ending(row["provider"]):                                     # the ending state
                self.Sessions.pop(key, None)
        return reply, row["provider"].session_id, {"conversation": "new" if started else "continued",
                                                   "history": history}

    # ---- the routes ----
    def MountOnApp(self, app: Any, Path: str = "/v1") -> None:
        """Add the three routes of the mount to the FastAPI app ``app`` under ``Path``, "/v1" by default, and
        cross-origin headers for every origin when the app has no ``CORSMiddleware`` yet, and return ``None``, as the
        module docstring above explains."""
        from fastapi.middleware.cors import CORSMiddleware

        if not any(m.cls is CORSMiddleware for m in getattr(app, "user_middleware", [])):
            app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        mount = self
        prefix = Path.rstrip("/")

        def request_data(request: Request, body: Any) -> dict[str, Any]:
            """Return the ``RequestData`` of ``request`` with ``body``, for the routes below."""
            auth = request.headers.get("authorization", "")
            metadata = body.get("metadata") if isinstance(body, dict) else None
            return {"authorization": auth[7:].strip() if auth.lower().startswith("bearer ") else auth.strip(),
                    "model": str(body.get("model") or "") if isinstance(body, dict) else "",
                    "body": body if isinstance(body, dict) else {},
                    "metadata": metadata if isinstance(metadata, dict) else {}}

        async def json_body(request: Request) -> dict[str, Any]:
            """Return the request's JSON object, raising ``HTTPEndpointRefusal`` 400 for anything else, for the routes
            below."""
            try:
                body = await request.json()
            except (ValueError, UnicodeDecodeError):
                body = None
            if not isinstance(body, dict):
                raise HTTPEndpointRefusal(400, "The body must be a JSON object.")
            return body

        def refused(error: Exception) -> JSONResponse:
            """Return the error response for ``error``, mapping the kinds the module docstring lists, for the routes
            below."""
            if isinstance(error, HTTPEndpointRefusal):
                return ErrorResponse(error.Status, error.Message, error.Type, error.Code, error.RetryAfterSeconds)
            if isinstance(error, ValueError):
                return ErrorResponse(400, str(error))
            logger.exception("HTTP endpoint request failed")
            return ErrorResponse(500, str(error), "server_error")

        async def chat_completions(request: Request) -> JSONResponse:
            """Serve ``POST <Path>/chat/completions``, as the route of the enclosing ``MountOnApp``."""
            try:
                body = await json_body(request)
                data = request_data(request, body)
                mount.Authenticate(data)
                reply, sid, metadata = await mount.Attend(data, _said(body.get("messages")))
            except Exception as error:
                return refused(error)
            return JSONResponse({"id": f"chatcmpl-{sid}", "object": "chat.completion", "created": int(time.time()),
                                 "model": mount.ModelName, "metadata": metadata,
                                 "choices": [{"index": 0, "message": {"role": "assistant", "content": reply},
                                              "finish_reason": "stop"}],
                                 "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})

        async def responses(request: Request) -> JSONResponse:
            """Serve ``POST <Path>/responses``, as the route of the enclosing ``MountOnApp``."""
            try:
                body = await json_body(request)
                data = request_data(request, body)
                mount.Authenticate(data)
                given = body.get("input")
                said = [("user", _text_of(given))] if isinstance(given, str) else _said(given)
                reply, sid, metadata = await mount.Attend(data, said)
            except Exception as error:
                return refused(error)
            return JSONResponse({"id": sid or uuid.uuid4().hex, "object": "response", "created_at": int(time.time()),
                                 "model": mount.ModelName, "status": "completed", "output_text": reply,
                                 "metadata": metadata,
                                 "output": [{"id": f"msg_{uuid.uuid4().hex[:12]}", "type": "message",
                                             "role": "assistant", "status": "completed",
                                             "content": [{"type": "output_text", "text": reply, "annotations": []}]}],
                                 "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}})

        async def models(request: Request) -> JSONResponse:
            """Serve ``GET <Path>/models``, as the route of the enclosing ``MountOnApp``."""
            try:
                mount.Authenticate(request_data(request, {}))
            except Exception as error:
                return refused(error)
            return JSONResponse({"object": "list", "data": [{"id": mount.ModelName, "object": "model", "created": 0,
                                                             "owned_by": "illocutionary-lifecycles"}]})

        app.post(f"{prefix}/chat/completions")(chat_completions)
        app.post(f"{prefix}/responses")(responses)
        app.get(f"{prefix}/models")(models)
