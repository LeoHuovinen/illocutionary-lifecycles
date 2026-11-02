"""The folder of the adapters, one object per kind of caller writing into a session, of which the text adapter and the
voice adapter replace each other towards the session.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every user turn enters the folder ``core`` through an adapter
defined here, in the folder ``server``, while the checks run in ``analyzers`` and the record is kept in ``memory``. An
adapter passes every call to its ``illocutionary_lifecycles.core.session_provider.SessionProvider`` and changes
nothing itself, and creating one attaches it to its session so its handlers receive the session's adapter callbacks.

The module ``AdapterBase`` holds the calls every adapter shares and the handler list. The module
``text_adapters.TextAdapter`` holds ``TextAdapter`` for typed turns, used by the text mount. The module
``voice_adapters.PipecatVoiceAdapter`` holds ``PipecatVoiceAdapter`` for spoken turns from any speech source, used by
both speech mounts, and its folder ``voice_adapter_helpers`` holds the assembler
``UserSpeechTurnAggregationAssembler``, which sets when a spoken turn ends. The module
``flow_adapters.SaveLoadFlowAdapter`` holds ``SaveLoadFlowAdapter``, which saves a flow to a file before any session
exists and is an adapter by folder only. Nothing is re-exported here.
"""
