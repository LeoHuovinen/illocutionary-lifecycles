"""The folder that runs one conversation, holding the session object, the session's state, the cycle that calls the
analyzers, the composer of each prompt and the language-model clients.

A conversation here goes between a user and a language model through the states of a flow written in advance, with
each state's questions checked outside the model, and this folder is where that happens turn by turn. The folder
``analyzers`` holds the checking functions this folder calls, the folder ``memory`` holds the record this folder
writes every event to, and the folder ``server`` holds the adapters and mounts through which a browser page, an app or
another program reaches this folder, always through
``illocutionary_lifecycles.core.session_provider.SessionProvider`` and never further in.

The module ``session_provider`` holds ``SessionProvider``, the one object through which every adapter speaks to a
session. The module ``ConversationInit`` holds the start-up sequence that ``SessionProvider.start`` runs on a new
session. The folder ``system_state`` holds ``SystemState``, which holds the flow's states, the current state and the
record, together with three read functions over the record. The folder ``pragmatic_state`` holds the values the next
prompt is composed from, the composer, and the refresher, which is the one function that updates those values from
analyzer results. The folder ``turn_taking`` holds the processing of one finished user utterance and the two cycles
that call the analyzers. The folder ``clients`` holds the three language-model clients and the one call that turns a
composed prompt into a reply. The module ``environment`` holds ``Required``, the one way a setting is read from the
environment.

Nothing in this folder knows an adapter, a mount, a wire, Pipecat, a browser or a storage vendor. The one import from
``server`` is in ``session_provider``, which imports the adapter callback dataclasses it sends from
``illocutionary_lifecycles.server.adapter_callback_handlers.AdapterCallbackHandlerEvents``. Nothing is imported or
re-exported here.
"""
