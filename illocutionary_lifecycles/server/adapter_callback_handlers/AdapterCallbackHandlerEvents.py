"""The four adapter callbacks a session sends to the handlers registered on its adapters, as dataclasses whose class
names are the ``type`` string every receiver matches. "Event" in these class names means adapter callback, never
recorded event.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a server, a page or an app connected to it needs to learn what
happened inside, that a save was made, that the state changed, that a question was answered or that the user's
unfinished words picked an option. These dataclasses, in the folder ``server``, are those messages.
``illocutionary_lifecycles.core.session_provider.SessionProvider`` builds and sends them, which is the one import from
the folder ``core`` into this folder, while ``analyzers`` and ``memory`` never see them. A handler receives each as
the dict ``wire`` returns, its fields and the key ``type`` holding the class name.

Three are sent after a save and carry ``turns``, every saved utterance as a dict, ``streams``, every recorded category of
the record, and ``prompt``, the prompt composed for the current state at that moment.
``RefreshCycleSavedAdapterCallbackHandlerEvent`` is sent after every save,
``ConversationStateChangedAdapterCallbackHandlerEvent`` once per state change, and
``QuestionAnsweredAdapterCallbackHandlerEvent`` once per answered question while the question-answer hook is on. The
fourth, ``IncrementalPhraseAdapterCallbackHandlerEvent``, is sent while the user is still speaking, once per incremental
pick, and carries none of those three fields.

What reaches a connecting program is set by the mount base
``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase.AdapterMountBase``. Its ``RelayAdapterCallback``
drops the save callback and strips ``turns`` and ``prompt`` from the others, and the result is what a page's views
receive through ``ConnectConversation.js``, while its ``LogRelay`` sends every callback in full as a log line marked
``log``. The server's own ``OnAdapterCallback`` receives every callback in full. The class names are matched by the
page scripts under ``examples/*/page`` and by the WebRTC mount, so renaming one breaks them at run time, and a new
adapter callback needs a dataclass here, a send in ``SessionProvider``, a relay rule in the mount base and a handler in
every page script that acts on it. All three uses this file serves read it, a server's ``OnAdapterCallback``, a browser
page, and a program that is not a browser reading the JSON from the wire.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class AdapterCallbackHandlerEvent:
    """The base class of the four adapter callbacks, whose class attribute ``CATEGORY`` holds the class name each
    subclass repeats, as the module docstring above explains."""

    CATEGORY: ClassVar[str] = "AdapterCallbackHandlerEvent"

    def wire(self) -> dict[str, Any]:
        """Return the callback as the dict a handler receives, its fields with the key ``type`` set to ``CATEGORY``.
        The name means "as it goes on the wire" and the method sends nothing. Called by ``SessionProvider`` for every
        callback it sends, as the module docstring above explains."""
        payload = dataclasses.asdict(self)
        payload["type"] = type(self).CATEGORY
        return payload


@dataclass
class RefreshCycleSavedAdapterCallbackHandlerEvent(AdapterCallbackHandlerEvent):
    """The adapter callback sent once after every save, carrying ``turns``, ``streams`` and ``prompt``, the whole state
    of the conversation for a server's ``OnAdapterCallback``. A mount never passes it to a page's views and sends it
    only as a log line marked "event", as the module docstring above explains."""

    CATEGORY: ClassVar[str] = "RefreshCycleSavedAdapterCallbackHandlerEvent"
    turns: list = field(default_factory=list)
    streams: dict = field(default_factory=dict)
    prompt: str = ""


@dataclass
class ConversationStateChangedAdapterCallbackHandlerEvent(AdapterCallbackHandlerEvent):
    """The adapter callback sent once for every recorded move to another state, after the save that follows it.

    ``conversation_state`` and ``previous_conversation_state`` hold the indexes of the state entered and the state left,
    from the recorded ``ConversationStateEvent``, and ``conversation_state_name`` and
    ``previous_conversation_state_name`` hold those states' ``name`` from the flow, or empty strings. ``turns``,
    ``streams`` and ``prompt`` are as on every save-time callback, as the module docstring above explains.
    """

    CATEGORY: ClassVar[str] = "ConversationStateChangedAdapterCallbackHandlerEvent"
    conversation_state: int = -1
    previous_conversation_state: int | None = None
    conversation_state_name: str = ""
    previous_conversation_state_name: str = ""
    turns: list = field(default_factory=list)
    streams: dict = field(default_factory=dict)
    prompt: str = ""


@dataclass
class QuestionAnsweredAdapterCallbackHandlerEvent(AdapterCallbackHandlerEvent):
    """The adapter callback sent once for every newly answered question while the question-answer hook is on, which
    the mounts turn on for every session.

    ``answer`` holds the answer sentence the question checker wrote, ``choice`` the chosen option for a question with
    options or an empty string, ``AnalyzerType`` the registered name of the analyzer, and ``AnalyzerInstance`` the run's
    ``AnalyzerId``, the registered name, two colons and the question's position, all found by
    ``illocutionary_lifecycles.memory.MemoryReadTools.AnsweredQuestionFactsTool.AnsweredQuestionFacts``. ``turns``,
    ``streams`` and ``prompt`` are as on every save-time callback, as the module docstring above explains.
    """

    CATEGORY: ClassVar[str] = "QuestionAnsweredAdapterCallbackHandlerEvent"
    answer: str = ""
    choice: str = ""
    AnalyzerType: str = ""
    AnalyzerInstance: str = ""
    turns: list = field(default_factory=list)
    streams: dict = field(default_factory=dict)
    prompt: str = ""


@dataclass
class IncrementalPhraseAdapterCallbackHandlerEvent(AdapterCallbackHandlerEvent):
    """The adapter callback sent while the user is still speaking, once for every pick of one incremental instance, the
    moment that instance's model call returns and after the pick has been recorded and placed on the pragmatic state.

    ``AnalyzerType`` holds the registered name of the incremental analyzer, ``InstanceIdentifier`` the instance's
    ``identifier`` from the flow, ``category`` the option word picked, ``gate`` the text "open" once a gated instance's
    gate has opened in this utterance or an empty string, and ``SpokenPhraseSoFar`` the speech so far it was picked from.
    The callback carries no ``turns``, ``streams`` or ``prompt``, because it may arrive several times a second, and a
    pick of "none" and an idempotent repeat are not sent. The page scripts under ``examples/*/page`` act on ``category``
    and ``InstanceIdentifier``, as the module docstring above explains.
    """

    CATEGORY: ClassVar[str] = "IncrementalPhraseAdapterCallbackHandlerEvent"
    AnalyzerType: str = ""
    InstanceIdentifier: str = ""
    category: str = ""
    gate: str = ""
    SpokenPhraseSoFar: str = ""
