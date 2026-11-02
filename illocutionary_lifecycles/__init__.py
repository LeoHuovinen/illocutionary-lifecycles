"""The package runs one conversation at a time between a user and a language model for a flow someone wrote in
advance, in which the model writes every reply from a prompt composed for that one turn and never settles what counts
as answered.

A flow, the dict a server hands to a mount, gives every conversation state a prompt that
says what the assistant does in it and the questions it must get answered. The questions are kept outside the model.
After every user turn small functions called analyzers return whether each open question was answered and whether the
conversation state may be left, the conversation moves between conversation states from those results, and every event is recorded. The
package's name, Illocutionary Lifecycles, abbreviated IL in the READMEs and folder names, refers to what each
utterance does in the conversation, its illocutionary force, followed from the question being asked to its being
answered.

The package has four folders, each with one task. ``core`` runs one conversation, with the session, its state, the
cycle that calls the analyzers, the composer of each prompt and the model clients, and knows no adapter, wire, Pipecat,
browser or storage vendor. ``analyzers`` holds the analyzer functions, each returning one result from one utterance or
from the speech so far and changing nothing. ``memory`` holds the record of a conversation, every event added and never
changed, and the storage vendors that keep it. ``server`` holds everything between a session and whatever connects to
it, the adapters, the adapter callbacks a session sends after a save, and the mounts that put an adapter on a wire.

A connecting program, a browser page, a native app, a robot or any other client, reaches a conversation in one order and no
further. The program speaks a wire, a mount owns that wire and builds a session and an adapter per connection, and the adapter
talks to ``illocutionary_lifecycles.core.session_provider.SessionProvider``, the one object exported here. Three mounts
replace each other by way. ``TextAdapterWebsocketMount`` serves typed turns over a WebSocket.
``PressToSpeakAdapterWebsocketMount`` serves speech recorded while a button is held, over a WebSocket, with no WebRTC
and no voice activity detection. ``PipecatVoiceAdapterWebRtcMount`` serves an open microphone over WebRTC through
Pipecat, where a pause ends the turn. Each page script of the same name beside the examples' pages gives a browser page
one interface on every way, and a program that is not a browser speaks the wire as the mount's docstring states it.

A few words have one meaning throughout. The flow is also called the bundle, ``ConversationStateInitBundle``, and the
init dict. "Event" is always said with which of
three it means, a recorded event in ``memory``, an adapter callback sent by the session, or an RTVI event of Pipecat.
A turn is a finished user utterance the session processes, and a tick is one new interim transcription of the speech
so far while the user is still speaking. The assembler is the class in
``illocutionary_lifecycles.server.adapters.voice_adapters.voice_adapter_helpers`` that joins final transcriptions into
one spoken turn. The cards are the readable account of a record for a person, worded by
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``. ``TargetConversationState`` in a transition criteria
entry is the index of the next conversation state. ``memory_callback`` is the key of ``ConversationStateInitBundle["PromptBlocks"]`` whose value
introduces the remembered answers, either one string or a mapping from condition names to strings.
``ConversationHistoryWindowHeading`` and ``ConversationHistoryWindowEmptyNote`` are two optional keys of
``ConversationStateInitBundle["PromptBlocks"]``, the heading ``PragmaticState.Composer`` prints above the current
conversation state's utterances and the note it prints while the user has not yet spoken in that conversation state,
and ``PragmaticState.Composer`` prints its own heading and note when the keys are absent.
``SessionProvider.ApplyPromptChange`` replaces the value of one key of ``ConversationStateInitBundle["PromptBlocks"]``
while the conversation runs, and adds one ``ManualPromptChangeEvent`` to ``SystemState.Record``, holding ``block_key``,
``block_sub_key``, ``previous_value``, ``value`` and ``source``.
"""
from illocutionary_lifecycles.core.session_provider import SessionProvider

__all__ = [
    "SessionProvider",
]
