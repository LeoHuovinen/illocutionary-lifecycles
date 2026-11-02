"""``AdapterBase``, the parent class of every adapter, made of ``SessionProviderSetters``, the session calls every
adapter passes on in the same way, and ``AdapterCallbackHandlers``, the list of handlers a server registers and the
session runs.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the adapters, in the folder ``server``, are the objects through
which typed or spoken turns reach the session in the folder ``core``, which checks them with ``analyzers`` and records
them in ``memory``. Every adapter passes each call to its
``illocutionary_lifecycles.core.session_provider.SessionProvider`` and changes nothing itself. The text adapter and
the voice adapter add only what their kind of turn needs, and everything they share is here.

``SessionProviderSetters`` holds ``open_session``, ``on_user_turn``, ``opening_reply``, ``SetQuestionAnswerHook`` and
``ApplyPromptChange``, which are session calls and not setters.
``AdapterCallbackHandlers`` is a mixin, a class added to ``AdapterBase`` to give it the handler list, and holds
``RegisterAdapterCallbackHandler`` and ``RunAdapterCallbackHandlers``. Creating an adapter registers it on its session
through ``AdapterBase.__post_init__``, so its handlers receive the session's adapter callbacks. The mounts in
``illocutionary_lifecycles.server.adapter_mounts`` create the adapters and register the handlers, and a new adapter
inherits ``AdapterBase`` and goes in a folder of its own under ``illocutionary_lifecycles/server/adapters``.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable


# ---- SessionProviderSetters ----


class SessionProviderSetters:
    """The session calls every adapter passes on unchanged, which expect the adapter to hold its session as
    ``self.SessionProvider``, as the module docstring above explains."""

    SessionProvider: Any

    def open_session(self) -> None:
        """Start the session through ``SessionProvider.start`` and return ``None``, raising whatever start-up raises
        for a wrong flow, a missing analyzer or a missing model key. The mounts call it once per connection. One of the
        session calls the module docstring above lists."""
        self.SessionProvider.start()

    async def on_user_turn(self, UserUtteranceText: str, static_reply: str | None = None) -> str:
        """Give the session one finished user utterance through ``SessionProvider.ResponseProcessing`` and return the
        reply text, an empty string when there is none.

        ``UserUtteranceText`` holds what the user said or typed. ``static_reply``, when given, is used as the reply
        while the utterance is still saved and analyzed, and no prompt is composed. The reply is not saved here, and the
        caller saves it with ``save_assistant`` once it has been delivered. Called by the text mount for a typed turn
        and by the assembler for a spoken one. One of the session calls the module docstring above lists.
        """
        turn = await self.SessionProvider.ResponseProcessing(UserUtteranceText, static_reply=static_reply)
        return (turn.get("reply", "") or "")

    async def opening_reply(self, static_reply: str | None = None) -> str:
        """Return the reply that opens the conversation before the user has said anything, composed by the first state
        from an empty utterance, or ``static_reply`` as it is when given. The caller saves it with ``save_assistant``
        once it has been delivered. The mounts call it once per connection after the session starts. One of the session
        calls the module docstring above lists."""
        result = await self.SessionProvider.ResponseProcessing("", static_reply=static_reply)
        return (result or {}).get("reply", "")

    def SetQuestionAnswerHook(self, Enabled: bool) -> bool:
        """Pass ``Enabled`` to ``SessionProvider.SetQuestionAnswerHook`` and return what it returns, true once the
        session has started. While the hook is on, every newly answered question is sent to the registered handlers as
        a ``QuestionAnsweredAdapterCallbackHandlerEvent``. One of the session calls the module docstring above lists."""
        return self.SessionProvider.SetQuestionAnswerHook(bool(Enabled))

    def ApplyPromptChange(self, block_key: str, value: Any, block_sub_key: str | None = None,
                          source: str = "server") -> int:
        """Pass a replacement of one authored prompt block to ``SessionProvider.ApplyPromptChange`` and return the
        refresh index of the ``ManualPromptChangeEvent`` it records, or ``-1`` when the session has not started. A server
        calls this from a handler after a state change to set what the entered state says, and every prompt composed
        from then on reads the new entry. One of the session calls the module docstring above lists."""
        return self.SessionProvider.ApplyPromptChange(block_key, value, block_sub_key=block_sub_key, source=source)


# ---- AdapterCallbackHandlers ----
class AdapterCallbackHandlers:
    """The handler list of an adapter, a mixin that ``AdapterBase`` inherits, through which the session's adapter
    callbacks reach whatever the server registered, as the module docstring above explains."""

    _AdapterCallbackHandlers: list[Callable[[dict], Awaitable[None]]]

    def RegisterAdapterCallbackHandler(self, AdapterCallbackHandler: Callable[[dict], Awaitable[None]]) -> None:
        """Add ``AdapterCallbackHandler``, an async function that takes one adapter callback as a dict, to the end of
        this adapter's handler list, and return ``None``. The WebSocket mounts register three per connection, one that relays
        the callbacks a page acts on, one that sends every callback as a log line, and one that passes to the server's
        ``OnAdapterCallback``, and the WebRTC mount registers its own RTVI senders and the last, as the module
        docstring above explains."""
        if not hasattr(self, "_AdapterCallbackHandlers") or self._AdapterCallbackHandlers is None:
            self._AdapterCallbackHandlers = []
        self._AdapterCallbackHandlers.append(AdapterCallbackHandler)

    async def RunAdapterCallbackHandlers(self, AdapterCallbackDict: dict) -> None:
        """Await every registered handler with ``AdapterCallbackDict``, one adapter callback as a dict with its
        ``type``, in registration order, and return ``None``. A handler that raises is logged as a warning and the others
        still run, so one handler cannot break a turn. Called by ``SessionProvider`` after every save and for every
        incremental pick, as the module docstring above explains."""
        for handler in list(getattr(self, "_AdapterCallbackHandlers", []) or []):
            try:
                await handler(AdapterCallbackDict)
            except Exception as e:
                logging.getLogger(__name__).warning(
                    "%s handler %s raised: %s", AdapterCallbackDict.get("type", ""),
                    getattr(handler, "__name__", handler), e)


# ---- AdapterBase ----


class AdapterBase(SessionProviderSetters, AdapterCallbackHandlers):
    """The parent class of ``TextAdapter`` and ``PipecatVoiceAdapter``, joining the session calls and the handler
    list, which expects a subclass to be a dataclass with the field ``SessionProvider``, as the module docstring above
    explains."""

    SessionProvider: Any

    def __post_init__(self) -> None:
        """Start an empty handler list and add this adapter to its session through
        ``SessionProvider.OverlaySessionAdapter``, so the session's adapter callbacks reach the handlers registered on
        it, which is the registration the module docstring above explains."""
        self._AdapterCallbackHandlers = []
        overlay = getattr(self.SessionProvider, "OverlaySessionAdapter", None)
        if overlay is not None:
            overlay(self)

