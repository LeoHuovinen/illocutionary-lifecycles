"""The folder of the mounts, each of which puts one adapter on one wire of an app the server owns, in three ways that
replace each other, text, press-to-speak and voice, with one page contract, each giving a page everything the one
before gives.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and a mount is how a program outside reaches it. Per connection a mount
builds a session in the folder ``core``, whose checks run in ``analyzers`` and whose record is kept in ``memory``, and
an adapter from this folder's sibling ``adapters``, and then carries the turns in and the replies and the adapter
callbacks out. The module ``AdapterMountBase`` holds what every mount shares, the per-connection session, the hooks a
server passes and the rule of what crosses the wire. Nothing in this folder is served over HTTP for a browser, and a
browser page carries its own scripts in its own folder, as the examples' pages do.

The folder ``websocket_mounts`` holds ``TextAdapterWebsocketMount``, the text way, with ``TextAdapter`` for typed turns
over a WebSocket, and ``PressToSpeakAdapterWebsocketMount``, the press-to-speak way, with ``PipecatVoiceAdapter`` for
speech recorded while a button is held, over a WebSocket, with no WebRTC, no voice activity detection and no Pipecat.
The folder ``webrtc_mounts`` holds ``PipecatVoiceAdapterWebRtcMount``, the voice way, with ``PipecatVoiceAdapter``
over WebRTC through Pipecat's runner, for an open microphone where a pause ends the turn. Each mount's protocol is the
other half of the page script of the same name, ``TextAdapterWebsocketMount.js``,
``PressToSpeakAdapterWebsocketMount.js`` or ``PipecatVoiceAdapterWebRtcMount.js``, copied beside every example page
under ``examples/*/page`` with ``ConnectConversation.js``, which gives a page one interface on every way. The
connecting side may be a browser page with those scripts, a mobile app, a robot or any program that speaks
the wire. A server is a file that owns an app, builds a mount with the exported flow and the settings outside it, such as
the voice, calls ``MountOnApp`` and runs, and ``examples`` holds one such server per way. A new wire is a new mount in a
new subfolder here, inheriting ``AdapterMountBase``, setting ``Way`` and defining ``MountOnApp`` and ``Attend``, with its
page script beside the examples' pages. Nothing is imported or re-exported here.
"""
