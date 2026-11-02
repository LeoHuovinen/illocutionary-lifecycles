"""The folder of what a session sends after a save and of the readers that turn its record into streams and cards.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this folder, inside ``server``, is how what happened inside the
folder ``core``, checked by ``analyzers`` and recorded in ``memory``, is told to a server, a page or an app, and shown
to a person afterwards. The module ``AdapterCallbackHandlerEvents`` holds the four adapter callback dataclasses the
session sends, whose class names every receiver matches, and is the one module of this folder the folder ``core``
imports. The module ``EventStreamReader`` holds ``event_streams`` and ``event_cards``, which read one session's record
through its provider. The module ``EventCardReader`` words the cards, and the module ``AdapterCallbackHandlerHelpers``
holds the flow lookup, the card units with their links and the turn clusters the cards are built from. Nothing is
imported or re-exported here.
"""
