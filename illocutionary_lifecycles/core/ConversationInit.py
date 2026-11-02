"""The start-up sequence of a session, ``ConversationInit``, run once on a new ``SystemState`` and called only by
``illocutionary_lifecycles.core.session_provider.SessionProvider.start``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and before the first turn every part the conversation needs must exist
and the flow must be checked. This module, in the folder ``core``, does that in a fixed order on
``illocutionary_lifecycles.core.system_state.system_state.SystemState``. First the record and its writer from the
folder ``memory`` are created, then the pragmatic state, then the model client. Then the stored record, if the storage
vendor has one for this session, is loaded into the record's in-memory copy, and a stored flow, if there is one,
replaces the flow handed in, while a new session stores the handed-in flow. Alias key names in the flow are mapped to
the canonical ones in memory by ``FlowInCanonicalKeys``. Then the flow's shape is checked, the
analyzers it names are imported and required from the folder ``analyzers``, the provider's settings are applied, and
the first state is entered. Of the package's four folders, this module is in ``core``, it uses ``memory`` and
``analyzers`` as described, and ``server`` reaches it only through the provider a mount builds per connection.

Every error a wrong flow, a missing analyzer, a missing model key or a missing vendor setting raises at session start
comes out of this sequence, from the module that checks it. No analyzer is defined here, and ``RegisterSessionAnalyzers``
only imports the analyzer modules so each registers itself, and checks the names. "Init" in this module's name, in
``InitSystemSetterSettings`` and in ``ConversationStateInitBundle`` refers to the session's start, and the flow is the
dict passed to the provider as ``ConversationStateInitBundle``.
"""
from __future__ import annotations

import copy
from typing import Any


def RegisterSessionAnalyzers(design_analyzers: Any) -> None:
    """Pass the registered names in ``design_analyzers`` to
    ``illocutionary_lifecycles.analyzers.AnalyzerBase.RequireAnalyzers``, which imports every analyzer module so each
    registers itself and raises ``LookupError`` beginning "the flow names analyzers that are not in the package" when a
    name is not registered, and return ``None``. A session whose flow names a missing analyzer therefore does not start,
    instead of running with a check that never happens. Called only by ``ConversationInit`` in this module, with the
    names ``ConversationInitAnalyzerCollection`` collects.
    """
    from illocutionary_lifecycles.analyzers.AnalyzerBase import RequireAnalyzers
    RequireAnalyzers(list(design_analyzers or ()))


# Alias to canonical name of a flow's top-level keys.
_FLOW_KEY_ALIASES = {"prompt_blocks": "PromptBlocks", "conversation_states": "ConversationStates"}
# Alias to canonical name of a flow's prompt blocks.
_PROMPT_BLOCK_KEY_ALIASES = {"character_memory_callback": "memory_callback"}
# Prompt blocks the package does not read, left out of the flow.
_IGNORED_PROMPT_BLOCK_KEYS = ("character", "character_return_greeting")
# Alias to canonical name of the keys of one entry of a state's ``ConversationStateTransitionCriteria``.
_CRITERION_KEY_ALIASES = {"NextNode": "TargetConversationState"}


def FlowInCanonicalKeys(Flow: Any) -> Any:
    """Return a deep copy of ``Flow`` with every alias key name replaced by its canonical name and the ignored prompt
    blocks left out, or ``Flow`` itself when it is not a dict, so the flow's own check can report it. A flow already
    in the canonical names comes back equal to itself, and a key that holds both names keeps the canonical one's value.
    Raises nothing. A file on disk is never written, so it stays as it was exported. Called by ``ConversationInit`` in
    this module and by ``illocutionary_lifecycles.server.adapter_mounts.AdapterMountBase.AdapterMountBase``. A key
    accepted under another name needs a row in the tables above."""
    if not isinstance(Flow, dict):
        return Flow
    Result = copy.deepcopy(Flow)
    for Alias, Canonical in _FLOW_KEY_ALIASES.items():
        if Alias in Result:
            AliasValue = Result.pop(Alias)
            Result.setdefault(Canonical, AliasValue)
    Blocks = Result.get("PromptBlocks")
    if isinstance(Blocks, dict):
        for Ignored in _IGNORED_PROMPT_BLOCK_KEYS:
            Blocks.pop(Ignored, None)
        for Alias, Canonical in _PROMPT_BLOCK_KEY_ALIASES.items():
            if Alias in Blocks:
                AliasValue = Blocks.pop(Alias)
                Blocks.setdefault(Canonical, AliasValue)
    States = Result.get("ConversationStates")
    if isinstance(States, dict):
        for State in States.values():
            Criteria = State.get("ConversationStateTransitionCriteria") if isinstance(State, dict) else None
            if not isinstance(Criteria, list):
                continue
            for Entry in Criteria:
                if not isinstance(Entry, dict):
                    continue
                for Alias, Canonical in _CRITERION_KEY_ALIASES.items():
                    if Alias in Entry:
                        AliasValue = Entry.pop(Alias)
                        Entry.setdefault(Canonical, AliasValue)
    return Result


def ConversationInitAnalyzerCollection(Flow: Any) -> list:
    """Return the list of registered analyzer names the flow ``Flow`` uses, in the order found, with repeats.

    The list holds the ``Analyzer`` of every entry of every state's ``ConversationStateTransitionCriteria`` list, then
    ``QuestionCompleteCriteria`` when any state has a non-empty ``questions`` list, then every non-empty string in
    every state's ``Analyzers`` list. States that are not dicts are skipped. Called only by ``ConversationInit`` in this
    module, as the module docstring above explains.
    """
    states = (Flow or {}).get("ConversationStates") or {}
    names: list = []
    # A criterion that is not registered never runs, and its state is then never left.
    for state in states.values():
        if not isinstance(state, dict):
            continue
        for entry in (state.get("ConversationStateTransitionCriteria") or []):
            if isinstance(entry, dict) and entry.get("Analyzer"):
                names.append(entry["Analyzer"])
    if any(isinstance(state, dict) and state.get("questions") for state in states.values()):
        names.append("QuestionCompleteCriteria")
    for state in states.values():
        if not isinstance(state, dict):
            continue
        for extra in (state.get("Analyzers") or []):
            if isinstance(extra, str) and extra.strip():
                names.append(extra)
    return names


def ConversationInit(
    SystemState: Any,
    InitSystemSetterSettings: Any = None,
) -> None:
    """Run the start-up sequence the module docstring above lays out on the new ``SystemState`` and return ``None``,
    after which the session can take its first turn.

    ``InitSystemSetterSettings`` is the dict the provider received, from ``SystemState`` attribute names to values,
    applied after the analyzers are required and before the first state is entered, because entering a state reads
    them, and a key that is not an attribute of ``SystemState`` is ignored. The handed-in flow is deep-copied before it
    is stored, so nothing the session does alters the caller's own dict. Every error a step raises reaches the caller,
    ``SessionProvider.start``, unchanged.
    """
    SystemState.InitializeMemoryClasses()
    SystemState.InitializePragmaticState()
    SystemState.BuildLLMConnection()
    # The stored record is loaded into the in-memory copy first; everything below reads that copy.
    SystemState.Record.reinit_log_from_disk()
    # A stored init dict takes precedence. The handed-in dict is used, and stored, only when
    # none was stored. It is deep-copied so that a later prompt change, which writes into
    # the nested prompt blocks, does not alter the application's own dict.
    recovered = SystemState.RecoverInit()
    # Alias key names are mapped in memory only; the file stays as exported.
    SystemState.ConversationStateInitBundle = FlowInCanonicalKeys(SystemState.ConversationStateInitBundle)
    if not recovered and SystemState.ConversationStateInitBundle is not None:
        SystemState.ConversationStateInitBundle = copy.deepcopy(
            SystemState.ConversationStateInitBundle)
        SystemState.Record.UpsertConversationInitEvent(SystemState.ConversationStateInitBundle)
    SystemState.load_conversation_states_from_init()      # checks the flow's shape first; one clear error for a wrong flow
    design_analyzers = ConversationInitAnalyzerCollection(SystemState.ConversationStateInitBundle)
    RegisterSessionAnalyzers(design_analyzers)
    # The settings are applied before the first state is entered, because entering a state
    # reads them.
    for Key, Value in (InitSystemSetterSettings or {}).items():
        if hasattr(SystemState, Key):
            setattr(SystemState, Key, Value)
    # The first state is entered here, so that the opening reply is composed in it and the
    # first user utterance is analyzed by its analyzers.
    SystemState.EstablishConversationState()
