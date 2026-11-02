"""The folder that holds the clients through which the conversation reaches a language model, and the one call that
turns a composed prompt into a reply.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the model is reached for two purposes only, writing each reply and
answering the analyzers' checks, both through the clients here, inside the folder ``core``, while the folders
``memory`` and ``server``, which keep the record and connect pages and apps, never call a model. Three clients replace
each other because each has the two async methods ``complete``, which returns text, and ``complete_json``, which
returns a parsed JSON object, and no base class enforces that. The module ``llm`` holds ``LLMClient`` for Azure OpenAI
and ``OpenAIClient`` for any OpenAI-compatible API, both chosen from the environment by ``llm_client_from_env``, and
the two per-process choices ``analyzer_llm`` and ``incremental_phrase_llm``. The module ``LocalLLMClient`` holds
``LocalLLMClient``, a model run on the same machine, chosen only in code by a ``LocalLLMConfig`` given as the
session's ``llm_config``. The module ``PostComposerLLMCallHelper`` holds the one call that sends a composed prompt to
the session's client.

The analyzers of the folder ``analyzers`` import ``illocutionary_lifecycles.core.clients.llm`` for their client and
nothing else of ``core``. A new client is a class with the two methods, built in
``illocutionary_lifecycles.core.system_state.system_state.SystemState.BuildLLMConnection`` from its own config class.
"""
