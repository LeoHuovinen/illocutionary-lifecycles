"""``SystemState``, the only holder of a session's flow, its conversation states, the current state and its record, and
the one object that enters a state by reading that state's entry in the flow and writing the pragmatic fields from it.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this class is where the flow's states live while the conversation
runs. The class sits in the folder ``core``, one level below
``illocutionary_lifecycles.core.session_provider.SessionProvider``, which creates it in ``start`` and passes every
adapter's call to it, and it holds the record of the folder ``memory`` and the model client of
``illocutionary_lifecycles.core.clients``. The checks of the folder ``analyzers`` run in the states it enters, and the
folder ``server`` reaches it only through the provider. "System" in the name means the dialogue system's own side of
the conversation, as opposed to the user's, and not the machine or the process.

The flow is the dict a server hands to a mount, with ``PromptBlocks`` and
``ConversationStates``, and ``load_conversation_states_from_init`` and ``EstablishConversationState`` are where the
keys of a state are read and checked, so the error a malformed flow raises comes from here, at session start or when
the state is entered. A state is an entry of ``ConversationStates`` keyed by its index as a string, and may hold
``name``, ``questions``, ``ConversationStateTransitionCriteria``, ``Analyzers``, ``permissive_after_turns``,
``ignore_memories``, ``global_history_window``, ``global_history_turns``, ``session_first_reply_flag`` and
``incremental_phrase_instances``. A state without ``ConversationStateTransitionCriteria`` is an ending that the
conversation never leaves.

Two things write the pragmatic fields, this class, when a state is entered and when ``set_ignore_memories`` switches
the remembered answers off or on, and ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` after
analyzers have run, and everything else only reads them. The refresher moves the conversation by calling
``set_current_conversation_state``, and ``SessionProvider.ResponseProcessing`` then has the new state reply by calling
``EstablishConversationStateAndFirstReply``. The two methods ``ResponseProcessing`` and ``ComposeCurrentPrompt`` hold
no logic here and call the functions of the same names in
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing``.

A session reopened from a stored record gets the record and not its position, because nothing replays the recorded
state changes into this class, so ``conversation_state`` is the first state again while the record may end in another.
Reading a finished session is unaffected; resuming one with a writing vendor is not supported.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SystemState:
    """The flow, the conversation states, the current state, the record, the model client and the session's settings of
    one session, built by ``SessionProvider.start`` and set up by
    ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``, as the module docstring above explains.

    ``chat_id`` holds the session's id, which the record and the storage vendor use. ``conversation_state`` holds the index of the current
    state as an int, starting at 0, the same index the flow keys as a string, and ``ConversationStateName`` holds that state's ``name`` from the flow or an empty
    string, for adapters to show, and nothing acts on it. ``StorageVendorName`` and ``StorageVendorAddress`` hold the
    vendor's registered name and address the provider passed as ``memory_vendor`` and ``vendor_session_address``, and
    ``None`` keeps the record in memory only. ``ConversationStateInitBundle`` holds the flow, and
    ``ConversationStates`` the flow's states keyed by index as a string. ``Record`` holds the session's
    ``illocutionary_lifecycles.memory.memory.Memory``, the whole record, and ``memory_writer`` its
    ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter``. ``llm_config`` holds an ``LLMConfig``, an
    ``OpenAIConfig`` or a ``LocalLLMConfig`` to build the model client from in code, and ``None`` builds it from the
    environment. ``llm_client`` holds the client that writes the replies. ``PragmaticState`` holds the session's
    ``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.PragmaticState``. ``QuestionAnswerHook`` holds
    whether answered questions are sent to the adapters' handlers, and must stay a declared field because
    ``ConversationInit`` applies a setting only to an attribute that exists. ``global_history_window`` holds whether the
    prompt shows the last utterances of the whole conversation instead of the current state's, and
    ``global_history_turns`` how many it then shows, 10 by default. A reader takes ``Record`` from this object each time
    it reads and does not keep it.
    """

    chat_id: str = ""

    conversation_state: int = 0
    ConversationStateName: str = ""

    StorageVendorName: str | None = None
    StorageVendorAddress: Any = None

    ConversationStateInitBundle: Any = None

    ConversationStates: Any = None

    Record: Any = None
    memory_writer: Any = None

    llm_config: Any = None
    llm_client: Any = None

    PragmaticState: Any = field(default=None)

    # This must be a declared field. ``ConversationInit`` applies a setting only when
    # SystemState already has an attribute of that name.
    QuestionAnswerHook: bool = False

    global_history_window: bool = False
    global_history_turns: int = 10

    def InitializeMemoryClasses(self) -> None:
        """Create the session's record, ``Record``, and its writer, ``memory_writer``, and return ``None``.

        The storage vendor is built by ``illocutionary_lifecycles.memory.persistence.build_persistent_connection`` from
        ``StorageVendorName`` and ``StorageVendorAddress``, and with no vendor name the record is kept in memory only. A
        vendor's own errors, such as a missing directory for "local", are raised from there. Called first by
        ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``, as the module docstring above explains.
        """
        from illocutionary_lifecycles.memory.persistence import build_persistent_connection
        from illocutionary_lifecycles.memory.memory import Memory
        from illocutionary_lifecycles.memory.MemoryWriter import MemoryWriter
        connection = build_persistent_connection(self.StorageVendorName, self.StorageVendorAddress)
        self.Record = Memory(
            SessionConversationId=self.chat_id,
            SessionVendorConnection=connection,
        )
        self.memory_writer = MemoryWriter(self.Record)

    def InitializePragmaticState(self) -> None:
        """Create the session's ``PragmaticState`` with the refresher
        ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` and the cycle
        ``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` in its two function fields, and return
        ``None``. Called second by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``."""
        from illocutionary_lifecycles.core.pragmatic_state import PragmaticState
        from illocutionary_lifecycles.core.pragmatic_state.refresher import refresh
        from illocutionary_lifecycles.core.turn_taking.sync_cycle import SyncCycle

        self.PragmaticState = PragmaticState(
            Refresher=refresh,
            SyncCycle=SyncCycle,
        )

    def BuildLLMConnection(self) -> None:
        """Set ``llm_client`` to the language-model client that writes the replies, and return ``None``.

        With an ``LLMConfig``, ``OpenAIConfig`` or ``LocalLLMConfig`` in ``llm_config`` the matching client from
        ``illocutionary_lifecycles.core.clients`` is built, and ``configure_clients`` makes the analyzers in this process
        use the same client. With any other ``llm_config`` or none,
        ``illocutionary_lifecycles.core.clients.llm.llm_client_from_env`` builds the client from the environment and
        raises ``RuntimeError`` beginning "no model is configured" when no model key is set, so a session without a
        model does not start. Called third by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``.
        """
        from illocutionary_lifecycles.core.clients.llm import (
            configure_clients, llm_client_from_env,
        )
        if self.llm_config is not None:
            from illocutionary_lifecycles.core.clients.llm import (
                LLMClient, LLMConfig, OpenAIClient, OpenAIConfig,
            )
            from illocutionary_lifecycles.core.clients.LocalLLMClient import (
                LocalLLMClient, LocalLLMConfig,
            )
            if isinstance(self.llm_config, LLMConfig):
                self.llm_client = LLMClient(self.llm_config)
            elif isinstance(self.llm_config, OpenAIConfig):
                self.llm_client = OpenAIClient(self.llm_config)
            elif isinstance(self.llm_config, LocalLLMConfig):
                self.llm_client = LocalLLMClient(self.llm_config)
            else:
                self.llm_client = llm_client_from_env()
            configure_clients(self.llm_client)
        else:
            self.llm_client = llm_client_from_env()

    async def ResponseProcessing(self, UserUtteranceText: str, skip_TransitionCriteria: bool = False,
                                 static_reply: str | None = None,
                                 ReuseUserUtteranceIdx: int | None = None) -> dict:
        """Return what ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing`` returns for
        ``UserUtteranceText`` with this object as the session, passing the other three arguments unchanged. The method
        holds no logic of its own, and the processing of a user utterance is explained in that module's docstring.
        Called by ``SessionProvider.ResponseProcessing`` and by ``EstablishConversationStateAndFirstReply`` in this
        module."""
        from illocutionary_lifecycles.core.turn_taking.ResponseProcessing import ResponseProcessing
        return await ResponseProcessing(self, UserUtteranceText, skip_TransitionCriteria=skip_TransitionCriteria,
                                        static_reply=static_reply, ReuseUserUtteranceIdx=ReuseUserUtteranceIdx)

    async def ComposeCurrentPrompt(self) -> str:
        """Return the prompt ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt``
        composes for the current state, saving nothing and calling no model. The method holds no logic of its own.
        Called by ``ResponseProcessing`` in that module before the model call and by ``SessionProvider`` for the
        ``prompt`` field of the save-time adapter callbacks."""
        from illocutionary_lifecycles.core.turn_taking.ResponseProcessing import ComposeCurrentPrompt
        return await ComposeCurrentPrompt(self)

    def SaveRefreshResult(self, *, analyzer_results: dict[str, Any] | None = None) -> None:
        """Save the remembered answers and the pragmatic state's values of one refresh through ``memory_writer``, and
        return ``None``, doing nothing before the record and the pragmatic state exist.

        ``analyzer_results`` is the dict of this refresh's analyzer results by result key, passed on unchanged, and
        ``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter.save_refresh_result`` chooses which of them become
        ``MemoryEvent`` entries. The values are read from ``PragmaticState`` as the refresher left them, through
        ``illocutionary_lifecycles.core.pragmatic_state.pragmatic_state.pragmatic_values``. Called after every refresh by
        ``SyncCycle`` in ``illocutionary_lifecycles.core.turn_taking.sync_cycle`` and once by
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing`` for an empty utterance, and
        never by the refresher, which saves nothing.
        """
        if self.memory_writer is None or self.PragmaticState is None:
            return
        from illocutionary_lifecycles.core.pragmatic_state.pragmatic_state import (
            pragmatic_values as _pragmatic_values,
        )
        self.memory_writer.save_refresh_result(
            analyzer_results=analyzer_results or {},
            pragmatic_values=_pragmatic_values(self.PragmaticState),
        )

    def RecoverInit(self) -> bool:
        """Replace ``ConversationStateInitBundle`` with the flow stored in the newest ``ConversationInit`` category of
        the record, and return true when one was stored, or false when none was or there is no record.

        A stored flow therefore wins over the one handed to the provider, so a resumed or reopened session runs the
        flow it was started with. The record's in-memory copy must already be loaded by
        ``illocutionary_lifecycles.memory.memory.Memory.reinit_log_from_disk``. Called by
        ``illocutionary_lifecycles.core.ConversationInit.ConversationInit``, which stores the handed-in flow only when this
        returns false.
        """
        if self.Record is None:
            return False
        events = self.Record.read_cache.streams().get("ConversationInit") or []
        if not events:
            return False
        self.ConversationStateInitBundle = dict(events[-1].get("values", {}) or {})
        return True

    def PromptBlocks(self) -> dict[str, Any]:
        """Return the flow's ``PromptBlocks`` dict itself, not a copy, or an empty dict when the flow has none. Called
        by ``_CheckStatePrompt`` in this module and by
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt``, which hands it to the
        composer."""
        bundle = self.ConversationStateInitBundle
        if not isinstance(bundle, dict):
            return {}
        blocks = bundle.get("PromptBlocks")
        return blocks if isinstance(blocks, dict) else {}

    def ApplyPromptChange(self, block_key: str, value: Any, block_sub_key: str | None = None,
                          source: str = "") -> int:
        """Replace one entry of the flow's ``PromptBlocks`` while the conversation runs, record the replacement as a
        ``ManualPromptChangeEvent`` in the same step, and return that event's refresh index, or ``-1`` when the session has
        no flow or no record. Every prompt composed after this call reads the new entry, because
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` reads the blocks through
        ``PromptBlocks`` at every compose.

        ``block_key`` names the top-level entry, for example ``ConversationFramePrompt`` or ``memory_callback``.
        ``value`` is the new entry. ``block_sub_key`` is the key inside a nested entry, a state index under
        ``IllocutionaryPrompt`` or a condition name under ``memory_callback``, and ``None`` replaces the whole entry.
        ``source`` is the label the caller gives the record. Called by
        ``illocutionary_lifecycles.core.session_provider.SessionProvider.ApplyPromptChange``, through which a server
        changes what a state says between prompts, and the change is recorded by
        ``illocutionary_lifecycles.memory.memory.Memory.UpsertManualPromptChangeEvent``.
        """
        bundle = self.ConversationStateInitBundle
        if not isinstance(bundle, dict) or self.Record is None:
            return -1
        blocks = bundle.get("PromptBlocks")
        if not isinstance(blocks, dict):
            blocks = {}
            bundle["PromptBlocks"] = blocks
        if block_sub_key is None:
            previous_value = blocks.get(block_key)
            blocks[block_key] = value
        else:
            sub_lookup = blocks.get(block_key)
            if not isinstance(sub_lookup, dict):
                previous_value = None
                blocks[block_key] = {block_sub_key: value}
            else:
                previous_value = sub_lookup.get(block_sub_key)
                sub_lookup[block_sub_key] = value
        return self.Record.UpsertManualPromptChangeEvent(
            str(block_key), block_sub_key, previous_value, value, source=str(source or ""),
        )

    def load_conversation_states_from_init(self) -> None:
        """Check the flow's shape, copy its ``ConversationStates`` into ``ConversationStates``, set
        ``ConversationStateName`` for the first state, and return ``None``.

        The checks raise ``ValueError`` at session start with one of these texts, each followed by an explanation. The
        first begins "a flow is a dict with 'ConversationStates' (a dict of states keyed by index as a string) and
        'PromptBlocks'" when the flow is not such a dict. The second begins "ConversationStates keys must be state
        indexes as strings" when a key is not a string of digits. The third begins "conversation state" followed by the
        key and "must be a dict". The fourth begins "state" followed by the key and "'questions' must be a list" when
        ``questions`` is not a list. The fifth begins "ConversationStates has no entry for the first state '0'". The
        sixth begins "a flow needs 'PromptBlocks' with 'ConversationFramePrompt' (one text for the whole conversation)
        and 'IllocutionaryPrompt'". Called by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit`` after the
        stored flow, if any, has been recovered.
        """
        bundle = self.ConversationStateInitBundle
        # The flow's shape is checked here, once, so a mistake in a flow is one clear error at session
        # start and not a conversation that runs on an empty state.
        if not isinstance(bundle, dict) or not isinstance(bundle.get("ConversationStates"), dict):
            raise ValueError(
                "a flow is a dict with 'ConversationStates' (a dict of states keyed by index as a string) and 'PromptBlocks'; "
                f"got {type(bundle).__name__}" + (f" with keys {sorted(bundle)}" if isinstance(bundle, dict) else "") + ". "
                "The flow is a JSON file (flow.json in the examples), and a "
                "SessionProvider or a mount takes it as it is: json.load(open('flow.json')). The keys a state may hold "
                "are read in SystemState.EstablishConversationState.")
        states = bundle["ConversationStates"]
        for key, StateEntry in states.items():
            if not isinstance(key, str) or not key.isdigit():
                raise ValueError(
                    f"ConversationStates keys must be state indexes as strings ('0', '1', ...); got {key!r}. The flow is "
                    "JSON, where keys are always strings, and every reference to a state (a criterion's 'TargetConversationState', the "
                    "record's state changes, the PromptBlocks.IllocutionaryPrompt entries) is that string; a flow built in "
                    "Python with int keys would never be left by any criterion.")
            if not isinstance(StateEntry, dict):
                raise ValueError(
                    f"conversation state {key!r} must be a dict; got {type(StateEntry).__name__}. A state is written as "
                    "{'name': ..., 'questions': [...], 'ConversationStateTransitionCriteria': [...]}; an ending state has "
                    "no criteria list. The keys are read in SystemState.EstablishConversationState.")
            if "questions" in StateEntry and not isinstance(StateEntry["questions"], list):
                raise ValueError(
                    f"state {key!r}: 'questions' must be a list of question strings or {{'question', 'options'}} dicts; got "
                    f"{type(StateEntry['questions']).__name__}. Each item is one question the question checker "
                    "(QuestionCompleteCriteria) tries to get answered in this state, for example "
                    "['What do you want?', {'question': 'Fries?', 'options': ['yes', 'no']}]; a single question is a list of one.")
        if str(self.conversation_state) not in states:
            raise ValueError(
                f"ConversationStates has no entry for the first state {str(self.conversation_state)!r}; keys are {sorted(states)}. "
                "A conversation starts in state '0' (SystemState.conversation_state), so the flow needs that key; "
                "states are numbered from 0.")
        if not isinstance(bundle.get("PromptBlocks"), dict):
            raise ValueError(
                "a flow needs 'PromptBlocks' with 'ConversationFramePrompt' (one text for the whole conversation) and "
                "'IllocutionaryPrompt' (a dict from state index to that state's prompt, what the system does in that state); "
                "optional entries are 'memory_callback' and 'question_prompt'. The composer "
                "(PragmaticState.Composer) builds every prompt from these blocks and nothing else, so without them the model "
                "would get only the conversation so far. They are matched in memory/MemoryReadTools/StaticPromptBlocks.py.")
        self.ConversationStates = dict(states)
        _entry = self.ConversationStates.get(str(self.conversation_state))
        self.ConversationStateName = str(_entry.get("name", "") or "") if isinstance(_entry, dict) else ""

    def current_conversation_state(self) -> Any:
        """Return the flow's entry for the current conversation state, the dict under ``ConversationStates`` keyed by
        ``conversation_state`` as a string, or an empty dict when there is none. Called by ``EstablishConversationState``
        and ``EstablishConversationStateAndFirstReply`` in this module and by
        ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh``, which reads the entry's criteria list to
        find the ``TargetConversationState``."""
        return self.ConversationStates.get(str(self.conversation_state), {}) if self.ConversationStates else {}

    def set_current_conversation_state(self, ConversationStateIndex: Any) -> bool:
        """Set ``conversation_state`` to ``ConversationStateIndex``, copy it to the pragmatic field
        ``pConversationState``, set ``ConversationStateName``, save the move as a ``ConversationStateEvent``, and return
        true, or return false without moving when the index names no state of the flow or cannot be read as an int.

        ``ConversationStateIndex`` is the index of the state to enter, as an int or as the string a criteria entry's
        ``TargetConversationState`` holds. An index equal to the current state raises ``ValueError`` with the text "conversation state
        may not transition to itself", because a state that led to itself would be entered again on every turn with its
        turn count reset. The method does not set up the new state. The only caller,
        ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh``, moves the conversation from a criterion's
        result, and ``SessionProvider.ResponseProcessing`` then calls ``EstablishConversationStateAndFirstReply``, which
        sets the state up and has it process the same user utterance, as the module docstring above explains.
        """
        key = str(ConversationStateIndex)
        if self.ConversationStates and key not in self.ConversationStates:
            return False
        # A state that led to itself would be entered again on every user turn, with its turn
        # count reset each time.
        try:
            _TargetIndex = int(ConversationStateIndex)
        except (TypeError, ValueError):
            _TargetIndex = None
        if _TargetIndex is not None and _TargetIndex == self.conversation_state:
            raise ValueError(
                f"conversation state may not transition to itself (index {ConversationStateIndex!r}). "
                "A transition must name a different state")
        previous_state = self.conversation_state
        try:
            self.conversation_state = int(ConversationStateIndex)
        except (TypeError, ValueError):
            return False
        self._inherit_to_pragmatic("pConversationState", self.conversation_state)
        _entry = self.ConversationStates.get(str(self.conversation_state)) if self.ConversationStates else None
        self.ConversationStateName = str(_entry.get("name", "") or "") if isinstance(_entry, dict) else ""
        if self.Record is not None and hasattr(self.Record, "UpsertConversationStateEvent"):
            self.Record.UpsertConversationStateEvent(self.conversation_state, previous_state)
        return True

    def EstablishConversationState(self) -> None:
        """Read the current state's entry in the flow, check it, write the pragmatic fields for that state, and return
        ``None``.

        This method is where the keys of a flow state are read, so the flow written by an author and the running
        conversation meet here, as the module docstring above explains. The criteria list
        ``ConversationStateTransitionCriteria`` is checked entry by entry, each entry a dict with only the keys
        ``Analyzer``, ``Prompt`` and ``TargetConversationState``, and copied to ``pConversationStateTransitionCriteriaListState``. A
        state without the list is an ending, and the field is deleted. The turn count
        ``pConversationStateTurnCountState`` is set to zero. The field ``pConversationStatePermissiveThresholdState`` is
        set from ``permissive_after_turns``, or to the number of ``questions`` plus one when that key is missing or not
        an integer, and is the number of turns after which the question checker stops waiting. The keys
        ``ignore_memories``, ``global_history_window`` and ``global_history_turns`` are applied when they hold a bool,
        a bool and an int, and are left as they were otherwise.

        When the criteria list names ``QuestionsAnsweredConversationStateTransitionCriteria`` or
        ``CategoricalAnswerConversationStateTransitionCriteria``, the state's ``questions`` become
        ``pConversationStateRemainingQuestions`` and ``QuestionCompleteCriteria`` is added to the analyzers that run, and
        otherwise the remaining-questions field is deleted, so a state with questions and neither criterion never asks
        the question checker. ``pActiveAnalyzersState`` is set to those names, the criteria named in the list and the
        names in the state's ``Analyzers`` list. The state's prompt is checked by ``_CheckStatePrompt``. The list
        ``incremental_phrase_instances``, when present, is checked and copied to ``pIncrementalPhraseInstancesState``.

        A malformed entry raises ``ValueError`` here, when the state is entered, and not later as a conversation that
        silently stops moving. The texts begin "ConversationStateTransitionCriteria must be a non-empty list of
        entries", "each ConversationStateTransitionCriteria entry must be a mapping", "ConversationStateTransitionCriteria
        entry has unknown key(s)", "each ConversationStateTransitionCriteria entry requires an 'Analyzer' name string",
        "ConversationStateTransitionCriteria entry names" followed by a name that does not end in
        ``ConversationStateTransitionCriteria``, "a ConversationStateTransitionCriteria 'Prompt' must be a string",
        "ConversationStateTransitionCriteria 'TargetConversationState'" followed by a value that names no state or names this state,
        "a state's 'Analyzers' must be a list of analyzer name strings", "each 'Analyzers' entry must be a non-empty
        string", "a state's 'incremental_phrase_instances' must be a list of mappings, each with an 'identifier'" and
        "incremental phrase instance" followed by an identifier and "needs a non-empty 'IncrementalAnalyzerChoicesPrompt'
        list". Called by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit`` for the first state and by
        ``EstablishConversationStateAndFirstReply`` in this module for every state entered after it.
        """
        ps = self.PragmaticState
        if ps is None:
            return
        StateEntry = self.current_conversation_state()
        # A state declares its transition criteria in the ordered list
        # ``ConversationStateTransitionCriteria``: entries with ``Analyzer``, an optional ``Prompt``
        # and ``TargetConversationState``, their order being their priority. A state without the list is an
        # ending: nothing moves the conversation out of it.
        _TransitionArray = StateEntry.get("ConversationStateTransitionCriteria") if isinstance(StateEntry, dict) else None
        if _TransitionArray is not None:
            if not isinstance(_TransitionArray, list) or not _TransitionArray:
                raise ValueError(
                    "ConversationStateTransitionCriteria must be a non-empty list of entries, each "
                    "{'Analyzer': <registered name>, 'TargetConversationState': <state index as a string>, 'Prompt': <optional>}, in priority "
                    "order; the first entry whose criterion reports done moves the conversation to its TargetConversationState. A state that "
                    "the conversation never leaves (an ending) has no list at all rather than an empty one.")
            for _TransitionEntry in _TransitionArray:
                if not isinstance(_TransitionEntry, dict):
                    raise ValueError("each ConversationStateTransitionCriteria entry must be a mapping")
                _UnknownKeys = set(_TransitionEntry) - {"Analyzer", "Prompt", "TargetConversationState"}
                if _UnknownKeys:
                    raise ValueError(
                        f"ConversationStateTransitionCriteria entry has unknown key(s) {sorted(_UnknownKeys)}")
                _EntryAnalyzer = _TransitionEntry.get("Analyzer")
                if not (isinstance(_EntryAnalyzer, str) and _EntryAnalyzer.strip()):
                    raise ValueError(
                        "each ConversationStateTransitionCriteria entry requires an 'Analyzer' name string")
                if not _EntryAnalyzer.endswith("ConversationStateTransitionCriteria"):
                    # The cycle runs a criterion by the ending of its registered name; any other name in this list
                    # would be registered, pass the start-up check, and never run as a criterion.
                    raise ValueError(
                        f"ConversationStateTransitionCriteria entry names {_EntryAnalyzer!r}, which is not a transition criterion: "
                        "a criterion's registered name ends in 'ConversationStateTransitionCriteria' because the cycle "
                        "(core/turn_taking/sync_cycle.py) runs a state's criteria by that ending, in pass 2, once per entry. The "
                        "four shipped criteria are QuestionsAnswered-, CategoricalAnswer-, TurnCount- and "
                        "PragmaticConversationStateTransitionCriteria (analyzers/transition_analyzers/). The question checker, "
                        "QuestionCompleteCriteria, is not one of them: it runs by itself whenever a state has questions.")
                _EntryPrompt = _TransitionEntry.get("Prompt")
                if _EntryPrompt is not None and not isinstance(_EntryPrompt, str):
                    raise ValueError("a ConversationStateTransitionCriteria 'Prompt' must be a string")
                _EntryTarget = _TransitionEntry.get("TargetConversationState")
                if not (isinstance(_EntryTarget, str) and _EntryTarget in (self.ConversationStates or {})):
                    raise ValueError(
                        f"ConversationStateTransitionCriteria 'TargetConversationState' {_EntryTarget!r} does not name a state; the states are "
                        f"{sorted(self.ConversationStates or {})}. TargetConversationState is the index of the state to enter, as a string, the "
                        "same key the state has under ConversationStates.")
                if _EntryTarget == str(self.conversation_state):
                    raise ValueError(
                        f"ConversationStateTransitionCriteria 'TargetConversationState' {_EntryTarget!r} is the state "
                        "itself; a transition must name a different state")
            ps.pConversationStateTransitionCriteriaListState = [
                dict(_TransitionEntry) for _TransitionEntry in _TransitionArray]
            _TransitionNames = []
            for _TransitionEntry in _TransitionArray:
                if _TransitionEntry["Analyzer"] not in _TransitionNames:
                    _TransitionNames.append(_TransitionEntry["Analyzer"])
        else:
            if hasattr(ps, "pConversationStateTransitionCriteriaListState"):
                del ps.pConversationStateTransitionCriteriaListState
            _TransitionNames = []
        if hasattr(ps, "pConversationStateTurnCountState"):
            ps.pConversationStateTurnCountState = 0
        # The number of user turns after which the question checker stops waiting. Every state
        # gets one. The default gives each question one turn. A state whose question must never
        # be answered for the user sets a high ``permissive_after_turns``.
        _perm = StateEntry.get("permissive_after_turns") if isinstance(StateEntry, dict) else None
        _DefaultPermissive = (len(StateEntry.get("questions") or []) + 1) \
            if isinstance(StateEntry, dict) else 1
        try:
            ps.pConversationStatePermissiveThresholdState = int(_perm) if _perm is not None else \
                _DefaultPermissive
        except (TypeError, ValueError):
            ps.pConversationStatePermissiveThresholdState = _DefaultPermissive
        # These three settings stay as they were when the state does not give them.
        _IgnoreMemories = StateEntry.get("ignore_memories") if isinstance(StateEntry, dict) else None
        if isinstance(_IgnoreMemories, bool):
            self.set_ignore_memories(_IgnoreMemories)
        _GlobalWindow = StateEntry.get("global_history_window") if isinstance(StateEntry, dict) else None
        if isinstance(_GlobalWindow, bool):
            self.global_history_window = _GlobalWindow
        _GlobalTurns = StateEntry.get("global_history_turns") if isinstance(StateEntry, dict) else None
        if isinstance(_GlobalTurns, int) and not isinstance(_GlobalTurns, bool):
            self.global_history_turns = _GlobalTurns
        # The state's own ``Analyzers`` list: further analyzers that run in it, by name.
        _ExtraAnalyzerNames: list = []
        _ExtraAnalyzersArray = StateEntry.get("Analyzers") if isinstance(StateEntry, dict) else None
        if _ExtraAnalyzersArray is not None:
            if not isinstance(_ExtraAnalyzersArray, list):
                raise ValueError("a state's 'Analyzers' must be a list of analyzer name strings")
            for _ExtraName in _ExtraAnalyzersArray:
                if not (isinstance(_ExtraName, str) and _ExtraName.strip()):
                    raise ValueError("each 'Analyzers' entry must be a non-empty string")
                if _ExtraName not in _ExtraAnalyzerNames:
                    _ExtraAnalyzerNames.append(_ExtraName)
        # A state tracks questions when one of its criteria depends on their answers.
        is_question_state = (
            "QuestionsAnsweredConversationStateTransitionCriteria" in _TransitionNames
            or "CategoricalAnswerConversationStateTransitionCriteria" in _TransitionNames
        )
        if is_question_state:
            from illocutionary_lifecycles.core.pragmatic_state.pragmatic_state import (
                pConversationStateRemainingQuestions as _Questions,
            )
            questions = StateEntry.get("questions", []) if isinstance(StateEntry, dict) else []
            ps.pConversationStateRemainingQuestions = _Questions(questions)
            _FreshActiveSet = ["QuestionCompleteCriteria", *_TransitionNames]
        else:
            if hasattr(ps, "pConversationStateRemainingQuestions"):
                del ps.pConversationStateRemainingQuestions
            _FreshActiveSet = [*_TransitionNames]
        for _AddedName in _ExtraAnalyzerNames:
            if _AddedName not in _FreshActiveSet:
                _FreshActiveSet.append(_AddedName)
        ps.pActiveAnalyzersState = _FreshActiveSet
        self._CheckStatePrompt(StateEntry)
        # The state's incremental phrase instances, declared as data beside its questions: the incremental phrase settle runs the
        # analyzer that runs per incremental phrase instance once per entry on every interim transcription of the speech so far.
        _Instances = StateEntry.get("incremental_phrase_instances") if isinstance(StateEntry, dict) else None
        if _Instances is not None:
            if not isinstance(_Instances, list) or not all(
                    isinstance(_Entry, dict) and str(_Entry.get("identifier") or "").strip() for _Entry in _Instances):
                raise ValueError("a state's 'incremental_phrase_instances' must be a list of mappings, each with an 'identifier'")
            for _Entry in _Instances:
                _Options = _Entry.get("IncrementalAnalyzerChoicesPrompt")
                if not isinstance(_Options, list) or not _Options:
                    # Without options the incremental analyzer picks nothing on every tick and nothing says why.
                    raise ValueError(
                        f"incremental phrase instance {_Entry['identifier']!r} needs a non-empty 'IncrementalAnalyzerChoicesPrompt' list: the words the "
                        "model may answer on every tick of the speech so far, validated verbatim, with 'none' first when ordinary "
                        "speech should pick nothing, for example ['none', 'nod', 'shake_head']. Without options the analyzer "
                        "(analyzers/incremental_phrase_analyzers/IncrementalPhraseCategoryAnalyzer.py) picks nothing on every tick "
                        "and the page is never told. The other keys are 'IncrementalPromptSubjectKeywords' (what the options are about), 'IncrementalPromptRequestKeywords', "
                        "'RequiresGate' and 'Idempotent'.")
            ps.pIncrementalPhraseInstancesState = [dict(_Entry) for _Entry in _Instances]
        elif hasattr(ps, "pIncrementalPhraseInstancesState"):
            del ps.pIncrementalPhraseInstancesState

    # The blanks a prompt block may hold: every pragmatic field, and the composer's own two.
    _KnownBlanks = frozenset({
        "pConversationState", "pActiveAnalyzersState", "pConversationStateTurnCountState",
        "pConversationStateRemainingQuestions", "pConversationStateTransitionCriteriaListState",
        "pConversationStatePermissiveThresholdState", "pCategoricalAnswerState", "pIgnoreMemoriesState",
        "pIncrementalPhraseInstancesState", "pUserMemories",
    })

    def _CheckStatePrompt(self, StateEntry: Any) -> None:
        """Raise ``ValueError`` when the current state has no prompt in ``PromptBlocks.IllocutionaryPrompt``, or when
        the frame prompt, the state's prompt, ``memory_callback`` or ``question_prompt`` holds a blank in braces
        that is neither in ``_KnownBlanks`` nor a field name of the form p, then letters and digits, then State, and
        return ``None`` otherwise.

        The composer would fill an unknown blank with an empty string, and a state without a prompt would be composed
        from the frame prompt alone, and both would show only as an assistant that ignores the state's instruction. The
        texts begin "PromptBlocks.IllocutionaryPrompt has no prompt for state" and "the prompt for state" followed by
        "has a blank" and the blank's name. ``StateEntry`` is accepted and not read. Called only by
        ``EstablishConversationState`` in this module.
        """
        import re
        blocks = self.PromptBlocks()
        per_state = blocks.get("IllocutionaryPrompt")
        index = str(self.conversation_state)
        if not isinstance(per_state, dict) or index not in per_state:
            raise ValueError(
                f"PromptBlocks.IllocutionaryPrompt has no prompt for state {index!r}; it has "
                f"{sorted(per_state) if isinstance(per_state, dict) else 'no entries'}. Every state needs its illocutionary "
                "prompt, the text that says what the system does in that state; without it the composer would build this "
                "state's prompt from the frame prompt and the conversation alone, and the assistant would not ask this state's "
                "questions. A flow holds one per state.")
        texts = [blocks.get("ConversationFramePrompt"), per_state.get(index), blocks.get("memory_callback"),
                 blocks.get("question_prompt"), blocks.get("ConversationHistoryWindowHeading"), blocks.get("ConversationHistoryWindowEmptyNote")]
        for text in texts:
            for value in (text.values() if isinstance(text, dict) else [text]):
                if not isinstance(value, str):
                    continue
                for blank in re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", value):
                    if blank not in self._KnownBlanks and not re.fullmatch(r"p[A-Za-z0-9]+State", blank):
                        raise ValueError(
                            f"the prompt for state {index!r} has a blank {{{blank}}} that nothing fills. A blank in a prompt block "
                            "is replaced by a pragmatic state field of the same name when the prompt is composed "
                            "(PragmaticState.Composer); an unknown blank would be replaced by nothing, silently. The blanks are "
                            f"{sorted(self._KnownBlanks)} and the p<AnalyzerType>State fields; the one most prompts want is "
                            "{pConversationStateRemainingQuestions}, which becomes one 'QUESTION TO ASK: ...' line per open question.")

    async def EstablishConversationStateAndFirstReply(self, UserUtteranceText: str,
                                            ReuseUserUtteranceIdx: int | None = None,
                                            static_reply: str | None = None) -> dict:
        """Set up the state just entered with ``EstablishConversationState``, have it process the user utterance that
        led to it, and return what ``ResponseProcessing`` returns for that.

        This is the second half of a move between states, called by ``SessionProvider.ResponseProcessing`` after the
        refresher has moved the conversation, so the reply to the user's turn comes from the new state, as the module
        docstring above explains. ``UserUtteranceText`` is that utterance, ``ReuseUserUtteranceIdx`` is the refresh index
        it is already saved under, so it is analyzed again without being saved twice, and ``static_reply`` is a finished
        reply passed on so that a reply given for the turn survives the move. The new state's key
        ``session_first_reply_flag`` changes the processing. The value "skip_TransitionCriteria" runs no transition
        criterion for this reply, so the new state cannot be left at once. The value "ignore_EntryUtterance" analyzes
        nothing and composes the reply as if nothing had been said. Any other value or none processes the utterance as
        a normal turn of the new state.
        """
        self.EstablishConversationState()

        StateEntry = self.current_conversation_state()
        flag = None
        if isinstance(StateEntry, dict):
            flag = StateEntry.get("session_first_reply_flag")
        if flag == "skip_TransitionCriteria":
            return await self.ResponseProcessing(UserUtteranceText, skip_TransitionCriteria=True,
                                                 static_reply=static_reply,
                                                 ReuseUserUtteranceIdx=ReuseUserUtteranceIdx)
        if flag == "ignore_EntryUtterance":
            return await self.ResponseProcessing("", static_reply=static_reply)
        return await self.ResponseProcessing(UserUtteranceText, static_reply=static_reply,
                                             ReuseUserUtteranceIdx=ReuseUserUtteranceIdx)

    def _inherit_to_pragmatic(self, field_name: str, value: Any) -> None:
        """Set the field ``field_name`` on ``PragmaticState`` to ``value`` when that field exists, and return ``None``.
        Called only by ``set_current_conversation_state`` in this module, to copy the new state's index to
        ``pConversationState``, which the composer and the prompt blocks read."""
        if self.PragmaticState is not None and hasattr(self.PragmaticState, field_name):
            setattr(self.PragmaticState, field_name, value)

    def set_ignore_memories(self, Enabled: bool) -> bool:
        """Set the pragmatic field ``pIgnoreMemoriesState`` to true when ``Enabled`` is true, delete it when ``Enabled``
        is false, and return true, or return false for an ``Enabled`` that is not a bool or before the pragmatic state
        exists.

        While the field is set the composer leaves the remembered answers out of the prompt, and they are still
        recorded. Called by ``SessionProvider.set_ignore_memories`` and by ``EstablishConversationState`` in this module
        for a state's ``ignore_memories`` key."""
        if not isinstance(Enabled, bool):
            return False
        if self.PragmaticState is None:
            return False
        if Enabled:
            self.PragmaticState.pIgnoreMemoriesState = True
        elif hasattr(self.PragmaticState, "pIgnoreMemoriesState"):
            del self.PragmaticState.pIgnoreMemoriesState
        return True
