"""The folder that holds everything between a session and whatever program connects to it, a browser page, an app, a
robot or any other client, and that reaches the conversation only through
``illocutionary_lifecycles.core.session_provider.SessionProvider``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), with the questions checked outside the model in ``core`` and
``analyzers`` and every event kept in ``memory``, and this folder is how a user's typed or spoken turns get in and how
the replies and the adapter callbacks get out. A connecting program speaks a wire, a mount owns that wire and builds a
session and an adapter per connection, the adapter talks to the provider, and nothing reaches further in. The only
imports of ``core`` in this folder are of ``SessionProvider``, in the mount base and the WebRTC mount, of
``illocutionary_lifecycles.core.ConversationInit.FlowInCanonicalKeys`` in the mount base, and of
``illocutionary_lifecycles.core.environment.Required``, and the one import the other way is the provider's import of
the adapter callback dataclasses from this folder.

The folder ``adapters`` holds one adapter class per kind of caller that writes into a session, typed or spoken, and
the assembler that joins spoken final transcriptions into turns. The folder ``adapter_callback_handlers`` holds the
adapter callbacks a session sends after a save and the readers that turn the record into streams and cards. The folder
``adapter_mounts`` holds the mounts, each of which puts one adapter on one wire of an app the server owns, text or
press-to-speak over a WebSocket, or voice over WebRTC through Pipecat.
"""
