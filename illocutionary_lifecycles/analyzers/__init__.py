"""The analyzers, each an async function that returns one
``illocutionary_lifecycles.analyzers.AnalyzerBase.AnalysisResult`` from one finished user utterance or from the speech
so far, registered by name and changing nothing.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the point of the whole design is that the model only writes replies,
while whether a question was answered and whether the conversation moves to the next state is checked by the functions
in this folder. Beside this folder, ``core`` runs the conversation and calls these functions after every user turn and
while the user speaks, ``memory`` keeps the record in which each result is saved, and ``server`` holds the adapters
and mounts that bring a user's turns in from a browser page, an app or another program.

The module ``illocutionary_lifecycles.analyzers.AnalyzerBase`` holds the registry, the result type and the per-instance
declaration, and its docstring explains how the registered name and one attribute on the function choose how an
analyzer is called. The subfolder ``answer_analyzers`` holds the question checker, which returns whether one open
question was answered. The subfolder ``transition_analyzers`` holds the four transition criteria, which return whether
the conversation may leave its state through one criteria entry. The subfolder ``incremental_phrase_analyzers`` holds
the one analyzer that runs on every new interim transcription while the user is still speaking.

Nothing in this folder saves to the record, moves the conversation or composes a prompt. The analyzers are called by
``illocutionary_lifecycles.core.turn_taking.sync_cycle``, and they import only
``illocutionary_lifecycles.analyzers.AnalyzerBase`` and ``illocutionary_lifecycles.core.clients.llm`` for their model
client. Nothing is imported or re-exported here.
"""
