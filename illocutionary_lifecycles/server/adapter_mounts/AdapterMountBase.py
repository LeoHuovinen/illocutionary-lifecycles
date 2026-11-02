"""``AdapterMountBase``, the base class of the three mounts, holding what each shares, the per-connection session, the
hooks a server passes, and the rule of what crosses the wire to the connecting side.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a mount, in the folder ``server``, is how a program outside reaches
it, building per connection a session of the folder ``core``, whose checks run in ``analyzers`` and whose record is
kept in ``memory``. This module is the one place in the folder that imports
``illocutionary_lifecycles.core.session_provider.SessionProvider``, besides the WebRTC mount, which builds its own,
and it imports ``illocutionary_lifecycles.core.ConversationInit.FlowInCanonicalKeys`` to accept a flow's alias keys.

Per connection a mount builds a session through ``NewConversationSession``, creates its adapter, registers the
handlers that carry every adapter callback to the connecting side and to the server's ``OnAdapterCallback``, starts the
session, calls the server's ``OnSessionOpened``, sends the opening, and then carries turns from the wire in its
``Attend``. ``MountOnApp`` adds the one route of the way to the app, a WebSocket for the text and press-to-speak ways
and Pipecat's offer route for the voice way, and nothing over HTTP. The hooks, the overrides and the relay rule are the
surface a server uses, and a server needs nothing of its own besides them.

What crosses the wire is set here. ``RelayAdapterCallback`` drops the save callback and strips ``turns`` and
``prompt`` from every other adapter callback, so a page's views never receive the record or the composed prompt.
``LogRelay`` sends every adapter callback in full as a separate line marked with the key ``log``, the value "event" for
the save callback because it carries the recorded streams and "adapter callback" for the others, and ``log.js`` beside
the example pages prints the two kinds as two streams. The user's line and the assistant's reply never travel as
adapter callbacks, but as each way's own messages. The connecting side may be a browser page, a mobile app, a
robot or any program that speaks the wire as each mount's docstring states it.
"""
from __future__ import annotations

import inspect
from typing import Any


class AdapterMountBase:
    """The base class of every mount, whose subclass sets ``Way`` to "text", "press" or "voice" and defines
    ``MountOnApp`` and ``Attend``, as the module docstring above explains."""

    Way: str = ""

    def __init__(self, ConversationStateInitBundle: dict, OnAdapterCallback: Any = None,
                 OnSessionOpened: Any = None, OnClientMessage: Any = None) -> None:
        """Keep the flow and the three hooks a server passes, and raise ``ValueError`` beginning "a mount takes the
        flow" when ``ConversationStateInitBundle`` is not a dict with a ``ConversationStates`` dict, so a wrong
        flow fails where the server file builds the mount and not at the first connection.

        ``ConversationStateInitBundle`` is the flow every connection's session starts from, unless
        ``MountConversationStateInitBundle`` is overridden. ``OnAdapterCallback`` is a function of one adapter callback
        dict, plain or async, which receives every callback in full. ``OnSessionOpened`` is a function, plain or async,
        called once per connection with the provider, the adapter and the function that sends a JSON message to the
        connecting side, which is ``None`` on the voice way, so the server can keep its own per-connection objects.
        ``OnClientMessage`` is a function, plain or async, of the provider and one JSON message from the connecting side
        that is not a turn, called on the two WebSocket ways. None of the three is required. The hooks are the surface the
        module docstring above describes.
        """
        # Alias key names are mapped in memory only; the file stays as exported.
        from illocutionary_lifecycles.core.ConversationInit import FlowInCanonicalKeys
        ConversationStateInitBundle = FlowInCanonicalKeys(ConversationStateInitBundle)
        if not isinstance(ConversationStateInitBundle, dict) or not isinstance(ConversationStateInitBundle.get("ConversationStates"), dict):
            # Fail where the server file builds the mount, not at the first connection.
            raise ValueError(
                "a mount takes the flow: a dict with 'ConversationStates' and 'PromptBlocks'; "
                f"got {type(ConversationStateInitBundle).__name__}. In a server file: "
                "conversation = json.load(open('flow.json')); TextAdapterWebsocketMount(conversation).MountOnApp(app, '/ws'). "
                "The mount builds one session from this flow per connection (NewConversationSession); a server that chooses "
                "the flow per connection overrides MountConversationStateInitBundle instead.")
        self.ConversationStateInitBundle = ConversationStateInitBundle
        self.OnAdapterCallback = OnAdapterCallback
        self.OnSessionOpened = OnSessionOpened        # (provider, adapter, send) once the session is open; the server keeps what it needs
        self.OnClientMessage = OnClientMessage        # (provider, ClientMessageDict) for every JSON message from the connecting side that is not a turn

    # ---- per connection ----
    def NewConversationSession(self, RequestData: Any = None) -> Any:
        """Return a new ``SessionProvider`` for one connection, on a deep copy of the flow
        ``MountConversationStateInitBundle`` returns, with the question-answer hook on, and without a storage vendor, so
        the record lives in memory only.

        ``RequestData`` is what the connecting side sent with its connection, the query string of the socket URL as a
        dict on the WebSocket ways and the request data of the WebRTC offer on the voice way. A server overrides this
        method to choose the session id, the storage vendor and the flow from it, or overrides
        ``MountConversationStateInitBundle`` to choose the flow alone. The WebRTC mount overrides it to start the session
        at once. Called by every mount's ``Attend`` once per connection, the first step of the sequence the module
        docstring above lists.
        """
        import copy

        from illocutionary_lifecycles.core.session_provider import SessionProvider
        return SessionProvider(ConversationStateInitBundle=copy.deepcopy(self.MountConversationStateInitBundle(RequestData)),
                               InitSystemSetterSettings={"QuestionAnswerHook": True})


    # ---- the plain-function handler ----
    @staticmethod
    def AdapterCallbackHandler(OnAdapterCallback: Any) -> Any:
        """Return an async handler that calls ``OnAdapterCallback`` with each adapter callback dict, awaiting the result
        when the function is async, and does nothing when ``OnAdapterCallback`` is ``None``. Every mount registers it on
        its adapter so the server's hook receives every callback in full, as the module docstring above explains."""

        async def handle(event: dict) -> None:
            """Pass ``event``, one adapter callback dict, to the server's hook, for the enclosing method."""
            if OnAdapterCallback is None:
                return
            result = OnAdapterCallback(event)
            if inspect.isawaitable(result):
                await result

        return handle


    @staticmethod
    def LogLine(AdapterCallbackDict: dict) -> dict:
        """Return a copy of ``AdapterCallbackDict`` with the key ``log`` added, holding "event" for the save callback,
        ``RefreshCycleSavedAdapterCallbackHandlerEvent``, because it carries the recorded streams, and "adapter callback"
        for every other callback. The browser scripts send lines with ``log`` to ``log.js`` and never to a page's views.
        Called by ``LogRelay`` in this class and by the WebRTC mount's pipeline."""
        kind = "event" if AdapterCallbackDict.get("type") == "RefreshCycleSavedAdapterCallbackHandlerEvent" else "adapter callback"
        return dict(log=kind, **AdapterCallbackDict)

    def LogRelay(self, SendToConnectingSide: Any) -> Any:
        """Return an async handler that sends the ``LogLine`` of every adapter callback, in full, through
        ``SendToConnectingSide``, beside the way's own messages. Both WebSocket mounts register it, and the voice mount
        sends the same lines as RTVI server messages, as the module docstring above explains."""
        async def relay(event: dict) -> None:
            """Send ``event``, one adapter callback dict, in full as a log line, for the enclosing ``LogRelay``."""
            await SendToConnectingSide(self.LogLine(event))

        return relay

    @staticmethod
    def RelayAdapterCallback(SendToConnectingSide: Any) -> Any:
        """Return an async handler that sends every adapter callback except the save callback,
        ``RefreshCycleSavedAdapterCallbackHandlerEvent``, through ``SendToConnectingSide``, with ``turns`` and ``prompt``
        left out, which is what a page's views receive. The user's line and the assistant's reply never travel this way,
        but as each way's own messages, the text and press replies and the voice transcripts. Both WebSocket mounts
        register it, and the voice mount applies the same rule in its pipeline. This is the rule of what crosses the wire
        that the module docstring above describes."""
        async def relay(event: dict) -> None:
            """Send ``event``, one adapter callback dict, without ``turns`` and ``prompt``, unless it is the save callback,
            for the enclosing ``RelayAdapterCallback``."""
            if event.get("type") == "RefreshCycleSavedAdapterCallbackHandlerEvent":
                return
            await SendToConnectingSide({k: v for k, v in event.items() if k not in ("turns", "prompt")})

        return relay

    async def Opened(self, provider: Any, adapter: Any, SendToConnectingSide: Any) -> None:
        """Call the server's ``OnSessionOpened`` with ``provider``, ``adapter`` and ``SendToConnectingSide``, awaiting it
        when it is async, and do nothing when the server gave none. Called by every mount's ``Attend`` once the session
        has started, as the module docstring above lists."""
        if self.OnSessionOpened is None:
            return
        result = self.OnSessionOpened(provider, adapter, SendToConnectingSide)
        if inspect.isawaitable(result):
            await result

    async def ClientMessage(self, provider: Any, ClientMessageDict: Any) -> None:
        """Call the server's ``OnClientMessage`` with ``provider`` and ``ClientMessageDict``, one JSON object from the
        connecting side that is not a turn, awaiting it when it is async, and do nothing when the server gave none. Called
        by the two WebSocket mounts' ``Attend``, as the module docstring above explains."""
        if self.OnClientMessage is None:
            return
        result = self.OnClientMessage(provider, ClientMessageDict)
        if inspect.isawaitable(result):
            await result

    def MountConversationStateInitBundle(self, RequestData: Any = None) -> dict:
        """Return the flow the session of one connection is built from, the mount's own unless a server overrides this to
        pick another from ``RequestData``, the connecting side's request data, such as a browser page's option or an
        Android app's or a robot's own fields. ``NewConversationSession`` passes a deep copy of it to ``SessionProvider``
        as ``ConversationStateInitBundle``, in this class."""
        return self.ConversationStateInitBundle

    def MountOnApp(self, app: Any, SocketPath: str = "/ws") -> None:
        """Add this mount's one route to ``app`` at ``SocketPath``, "/ws" by default, which each subclass defines, and
        raise ``NotImplementedError`` in this class."""
        raise NotImplementedError

    async def Attend(self, *wire: Any) -> None:
        """Serve one connection of the wire until it closes, which each subclass defines with the arguments its wire
        needs, and raise ``NotImplementedError`` in this class."""
        raise NotImplementedError

