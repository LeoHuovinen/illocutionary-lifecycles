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
``ignore_memories``, ``global_history_window``, ``global_history_turns``, ``session_first_reply_flag``,
``incremental_phrase_instances`` and ``nonconversational_socket_instances``, which names the server's
sockets the state shows, as ``SessionProvider.SetNonconversationalSocketReader`` explains. A state without ``ConversationStateTransitionCriteria`` is an ending that the
conversation never leaves. The flow stays as it started unless the server sets ``FlowChangeAllowed``, a later addition
after which ``ApplyStateChange`` may write states other than the current one while the conversation runs, as its
docstring explains.

Two things write the pragmatic fields, this class, when a state is entered, when ``set_ignore_memories`` switches
the remembered answers off or on and when ``SetNonconversationalContentSocket`` places or removes a server's content,
and ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` after analyzers have run, and everything else
only reads them. The refresher moves the conversation by calling
``set_current_conversation_state``, and ``SessionProvider.ResponseProcessing`` then has the new state reply by calling
``EstablishConversationStateAndFirstReply``. The two methods ``ResponseProcessing`` and ``ComposeCurrentPrompt`` hold
no logic here and call the functions of the same names in
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing``.

A session reopened from a stored record gets the record and not its position, because nothing replays the recorded
state changes into this class, so ``conversation_state`` is the first state again while the record may end in another.
Reading a finished session is unaffected; resuming one with a writing vendor is not supported.
"""
from __future__ import annotations

import copy
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

    # Whether ``ApplyStateChange`` may change the running flow, a declared field for the same reason. False when the
    # server does not set it, so a session that does not ask for flow changes runs as before.
    FlowChangeAllowed: bool = False

    global_history_window: bool = False
    global_history_turns: int = 10

    # The server's function that returns its sockets' texts by name, called each time a reply is composed. A function
    # and never a text, because IL stores no socket text, as ``SessionProvider.SetNonconversationalSocketReader`` says.
    NonconversationalSocketReader: Any = None
    # The custom analyzers instantiated for this session, by name, as ``SetAnalyzerInstance`` in this class explains,
    # each run only in a state (eg. during runtime, upcoming ConversationStates in the active flow in SystemState) that
    # lists it in its ``Analyzers``. Empty in a session that instantiates none, which then runs exactly as before.
    CustomAnalyzerInstances: dict = field(default_factory=dict, repr=False)
    # Every socket name the flow lists when the session starts, a frozenset set once at the first state entry and never
    # changed, the immutable side against which flow changes are checked, and ``None`` before that entry. The mutable side, the
    # names the current state shows, is the pragmatic field ``pNonconversationalSocketInstancesState``.
    NonconversationalSocketOptions: Any = None

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

        After the stored flow is recovered, every ``FlowChangeEvent`` in the record is applied to it in the order it
        was recorded, so a reopened session runs the flow as it last was and not as it started. This rebuilds the
        flow only. No turn is run again and the conversation's position is not restored. A record made without
        ``FlowChangeAllowed`` holds no such event, and the flow is recovered as before. The events are applied whatever
        the setting is now, because this runs before the settings are applied.
        """
        if self.Record is None:
            return False
        events = self.Record.read_cache.streams().get("ConversationInit") or []
        if not events:
            return False
        self.ConversationStateInitBundle = dict(events[-1].get("values", {}) or {})
        for change in self.Record.read_cache.streams().get("FlowChangeEvent") or []:
            if change.get("entry") is None:      # a removal, made only by ReplaceBranch
                self._RemoveStateFromFlow(str(change.get("state_key")), with_states=False)
            else:
                self._PutStateIntoFlow(str(change.get("state_key")), copy.deepcopy(change.get("entry")),
                                       change.get("prompt"), with_states=False)
        for RecordedInstantiationEvent in self.Record.read_cache.streams().get("CustomAnalyzerInstantiationEvent") or []:
            RecordedCustomAnalyzerName = str(RecordedInstantiationEvent.get("CustomAnalyzerName") or "")
            if RecordedInstantiationEvent.get("CustomAnalyzerRemoved"):
                self.CustomAnalyzerInstances.pop(RecordedCustomAnalyzerName, None)
                continue
            self._InstantiateCustomAnalyzer(
                RecordedCustomAnalyzerName,
                str(RecordedInstantiationEvent.get("CustomAnalyzerPrompt") or ""),
                RecordedInstantiationEvent.get("CustomAnalyzerOutputSchema") or {},
                bool(RecordedInstantiationEvent.get("CustomAnalyzerReadsNonconversationalSocketFeed")))
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

    def ApplyStateChange(self, key: str, entry: dict, prompt: str, source: str = "") -> tuple[bool, str]:
        """Write the conversation state ``key`` of the running flow, a new state or a replacement, with ``entry`` as
        its entry under ``ConversationStates`` and ``prompt`` as its entry under ``PromptBlocks["IllocutionaryPrompt"]``,
        and return whether it was applied together with the reason when it was not.

        NOTE: You will only need this during dynamic dialogue tree construction, during an ongoing conversation
        session. Only use this feature if you genuinely need a complicated, dynamic conversation, rather than a
        structured or planned one.

        This is a later addition to the package. A flow was first fixed for the whole session, and everything else in
        this class still works as if it were, because the class reads the flow only by key at the moment it needs it,
        when it moves to a state, when it enters one and when it composes a prompt. The method does nothing and
        returns false unless the setting ``FlowChangeAllowed`` is true, which a server sets through the provider's
        ``InitSystemSetterSettings`` and which is false when absent, so a session that does not ask for it runs
        exactly as before.

        The current state is never changed. The analyzers judge its exits on the copy ``EstablishConversationState``
        made when it was entered, and ``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` maps the
        winning exit's position back onto the live list, so a list changed in place could send the conversation to the
        wrong state. The method also refuses a key that is not a string of digits, an entry that is not a dict or whose
        ``questions`` is not a list, an exit whose ``TargetConversationState`` is the state itself or names no existing
        state, and an analyzer that is not registered. A change it accepts is recorded first, as a ``FlowChangeEvent``
        written to the storage vendor through ``illocutionary_lifecycles.memory.memory.Memory.UpsertFlowChangeEvent``,
        holding the new and the previous entry and prompt and ``source``, and only then put into
        ``ConversationStateInitBundle`` and ``ConversationStates`` together. The record therefore holds the starting
        flow and every change in order, and ``RecoverInit`` rebuilds the latest flow from them when the session is
        reopened. Called by ``illocutionary_lifecycles.core.session_provider.SessionProvider.ApplyStateChange``.
        """
        key = str(key)
        if not self.FlowChangeAllowed:
            return False, "flow changes are not allowed in this session, set FlowChangeAllowed to allow them"
        if self.Record is None or not isinstance(self.ConversationStateInitBundle, dict) or self.ConversationStates is None:
            return False, "the session has not started"
        if key == str(self.conversation_state):
            return False, "the current conversation state is never changed"
        if not key.isdigit():
            return False, f"a state key is a string of digits, not {key!r}"
        if not isinstance(entry, dict) or not isinstance(entry.get("questions", []), list):
            return False, "an entry is a dict, and its 'questions' a list"
        if self._SocketListRefusal(entry):
            return False, self._SocketListRefusal(entry)
        refusal = self._TurnCountRefusal(entry)
        if refusal:
            return False, refusal
        names = []
        for criterion in entry.get("ConversationStateTransitionCriteria") or []:
            target = criterion.get("TargetConversationState") if isinstance(criterion, dict) else None
            if not isinstance(target, str) or target == key or target not in self.ConversationStates:
                return False, f"the TargetConversationState {target!r} is not another existing state"
            names.append(criterion.get("Analyzer"))
        if entry.get("questions"):
            names.append("QuestionCompleteCriteria")
        names += [n for n in (entry.get("Analyzers") or []) if isinstance(n, str) and n.strip()]
        from illocutionary_lifecycles.analyzers.AnalyzerBase import RequireAnalyzers
        try:
            RequireAnalyzers([n for n in names if n and n not in self.CustomAnalyzerInstances])
        except LookupError as exc:
            return False, str(exc)
        previous_entry = self.ConversationStates.get(key)
        previous_prompt = (self.PromptBlocks().get("IllocutionaryPrompt") or {}).get(key)
        # Recorded and stored before the change takes effect, so no change of the flow goes unrecorded.
        self.Record.UpsertFlowChangeEvent(key, entry, prompt, previous_entry, previous_prompt, source=source)
        self._PutStateIntoFlow(key, copy.deepcopy(entry), prompt, with_states=True)
        return True, ""

    def _SocketListRefusal(self, entry: dict) -> str:
        """Return why ``entry``'s list ``nonconversational_socket_instances`` may not go into the running flow, or an
        empty string when it may or when the entry has no list. The list must hold socket names only, and every name
        must be in ``NonconversationalSocketOptions``, the names fixed when the session started, so a flow change never
        adds a socket. Checking here, before anything changes, matters, because a malformed list that got in would
        only raise at that state's entry, in the middle of a turn, and leave the conversation stuck there. Called by
        ``ApplyStateChange`` and ``ReplaceBranch`` in this class."""
        names = entry.get("nonconversational_socket_instances")
        if names is None:
            return ""
        if not (isinstance(names, list) and all(isinstance(n, str) and n.strip() for n in names)):
            return "'nonconversational_socket_instances' must be a list of socket names"
        allowed = self.NonconversationalSocketOptions or frozenset()
        unknown = [n for n in names if n not in allowed]
        return f"the sockets {unknown} were not in the flow at session start" if unknown else ""

    # The values of ``session_first_reply_flag`` that make an entered state wait for the user's next turn.
    _WaitingFirstReplyFlags = frozenset({"skip_TransitionCriteria", "ignore_EntryUtterance"})

    def _TurnCountRefusal(self, entry: Any) -> str:
        """Return why ``entry`` may not have a turn count criterion below 2, or an empty string when it may.

        The reason is how a move between states works. When a user utterance moves the conversation, the reply to that
        utterance is written by the state just entered, not by the state left, so the user hears the new state at
        once. To write it, ``EstablishConversationStateAndFirstReply`` has the new state process that same utterance
        as one of its own turns, and the refresher counts it, so the new state's turn count is already 1 before the
        user has said anything to it.

        A ``TurnCountConversationStateTransitionCriteria`` whose ``Prompt`` is below 2 is therefore met on that very
        utterance. The new state is left again within the same turn, before it has replied, and the user never hears
        it. When two such states lead to each other, the one utterance is passed back and forth until
        ``SessionProvider.ResponseProcessing`` stops at its cap on moves per turn, and the reply is empty, with no
        error.

        The two values of ``_WaitingFirstReplyFlags`` remove that cause. "skip_TransitionCriteria" still counts the
        utterance but runs no criterion for the first reply, and "ignore_EntryUtterance" does not process the
        utterance at all, so in both the new state replies first and is left only on a later turn of the user. A
        number below 2 is allowed with either of them and refused without. A missing or non-integer ``Prompt`` is read
        as 2 by the criterion and is allowed. Called by ``load_conversation_states_from_init``, ``ApplyStateChange``
        and ``ReplaceBranch`` in this class, so a flow is refused when the session starts or when a state is written,
        never in the middle of a turn."""
        if not isinstance(entry, dict):
            return ""
        if entry.get("session_first_reply_flag") in self._WaitingFirstReplyFlags:
            return ""
        for criterion in entry.get("ConversationStateTransitionCriteria") or []:
            if not (isinstance(criterion, dict)
                    and criterion.get("Analyzer") == "TurnCountConversationStateTransitionCriteria"):
                continue
            try:
                turns = int(str(criterion.get("Prompt") or "").strip())
            except ValueError:
                continue
            if turns < 2:
                return (f"a TurnCountConversationStateTransitionCriteria 'Prompt' of {turns} needs "
                        "'session_first_reply_flag' set to 'skip_TransitionCriteria' or 'ignore_EntryUtterance'")
        return ""

    def ReplaceBranch(self, old_keys: Any, new_states: dict, rewritten_states: dict,
                      source: str = "") -> tuple[bool, str]:
        """Replace a branch of the running flow with another in a single step, and return whether it was applied
        together with the reason when it was not. This is the only way a state ever leaves the flow.

        NOTE: You will only need this during dynamic dialogue tree construction, during an ongoing conversation
        session. Only use this feature if you genuinely need a complicated, dynamic conversation, rather than a
        structured or planned one.

        ``old_keys`` holds the keys of the states going out. ``new_states`` maps the key of every state coming in to
        its entry and prompt as a pair, under keys the flow does not hold yet. ``rewritten_states`` maps the key of
        every remaining state whose exits must change, usually because they led into the old branch, to its new entry
        and prompt as a pair. ``source`` is the label the caller gives the record.

        Any shape can be built this way, forks, merges, loops inside a branch, branches inside branches and branches
        leading into other branches, as deep and as wide as needed, and swapped in and out for as long as the session
        runs. A few rules hold at the moment of a swap, and none of them limits the shape a graph can take. No state
        exits to itself, as everywhere in the package, so a loop passes through another state. Every exit leads to a
        state that exists after the swap, so the whole new branch is passed together and a dangling exit is refused.
        The current state is never touched, so a swap that would remove or rewrite it, or remove any state of a
        branch the conversation is in, is refused and waits for a later call. The starting state always stays,
        because a reopened session begins there. A branch goes out only whole, so a swap is refused while any state
        that remains would still lead into it, and no part is ever left cut off.

        Everything is checked before anything changes, the rules above, the shape of every entry, as
        ``ApplyStateChange`` checks it, and that every analyzer named is registered, and a refused swap changes
        nothing at all. An accepted swap writes the new states, then the rewritten ones, then removes the old ones, each
        recorded first as a ``FlowChangeEvent`` through
        ``illocutionary_lifecycles.memory.memory.Memory.UpsertFlowChangeEvent`` and only then applied to
        ``ConversationStateInitBundle`` and ``ConversationStates`` together. A removal is recorded with ``None`` as its
        entry and prompt and with the removed entry and prompt as the previous ones, so the record keeps every state
        that ever existed and ``RecoverInit`` rebuilds the same flow when the session is reopened. The method has no
        await, so no part of a turn runs in the middle of it. Called by
        ``illocutionary_lifecycles.core.session_provider.SessionProvider.ReplaceBranch``.
        """
        if not self.FlowChangeAllowed:
            return False, "flow changes are not allowed in this session, set FlowChangeAllowed to allow them"
        if self.Record is None or not isinstance(self.ConversationStateInitBundle, dict) or self.ConversationStates is None:
            return False, "the session has not started"
        old = [str(k) for k in (old_keys or [])]
        try:
            new = {str(k): (v[0], v[1]) for k, v in (new_states or {}).items()}
            rewritten = {str(k): (v[0], v[1]) for k, v in (rewritten_states or {}).items()}
        except (TypeError, IndexError):
            return False, "new_states and rewritten_states map a key to an (entry, prompt) pair"
        current = str(self.conversation_state)
        if current in old or current in rewritten:
            return False, "the current conversation state is never changed"
        if "0" in old:
            return False, "the starting state '0' always stays, a reopened session begins there"
        for k in old:
            if k not in self.ConversationStates:
                return False, f"there is no state {k!r} to remove"
        for k in new:
            if k in self.ConversationStates:
                return False, f"the new state {k!r} is already in the flow"
        for k in rewritten:
            if k in old or k not in self.ConversationStates:
                return False, f"the rewritten state {k!r} is not a remaining state of the flow"
        after = (set(self.ConversationStates) - set(old)) | set(new)
        writes = {**new, **rewritten}
        names = []
        for k, (entry, _prompt) in writes.items():
            if not k.isdigit():
                return False, f"a state key is a string of digits, not {k!r}"
            if not isinstance(entry, dict) or not isinstance(entry.get("questions", []), list):
                return False, f"the entry of {k!r} is a dict, and its 'questions' a list"
            if self._SocketListRefusal(entry):
                return False, f"the entry of {k!r}: " + self._SocketListRefusal(entry)
            refusal = self._TurnCountRefusal(entry)
            if refusal:
                return False, f"the entry of {k!r}: " + refusal
            for criterion in entry.get("ConversationStateTransitionCriteria") or []:
                target = criterion.get("TargetConversationState") if isinstance(criterion, dict) else None
                if not isinstance(target, str) or target == k or target not in after:
                    return False, f"the TargetConversationState {target!r} of {k!r} is not another state of the flow after the swap"
                names.append(criterion.get("Analyzer"))
            if entry.get("questions"):
                names.append("QuestionCompleteCriteria")
            names += [n for n in (entry.get("Analyzers") or []) if isinstance(n, str) and n.strip()]
        for k in after - set(writes):
            for criterion in self.ConversationStates[k].get("ConversationStateTransitionCriteria") or []:
                target = criterion.get("TargetConversationState") if isinstance(criterion, dict) else None
                if target in old:
                    return False, f"the state {k!r} would still lead to {target!r}, rewrite it in the same swap"
        from illocutionary_lifecycles.analyzers.AnalyzerBase import RequireAnalyzers
        try:
            RequireAnalyzers([n for n in names if n and n not in self.CustomAnalyzerInstances])
        except LookupError as exc:
            return False, str(exc)
        prompts = self.PromptBlocks().get("IllocutionaryPrompt") or {}
        for k, (entry, prompt) in writes.items():
            self.Record.UpsertFlowChangeEvent(k, entry, prompt, self.ConversationStates.get(k), prompts.get(k),
                                              source=source)
            self._PutStateIntoFlow(k, copy.deepcopy(entry), prompt, with_states=True)
        for k in old:
            self.Record.UpsertFlowChangeEvent(k, None, None, self.ConversationStates.get(k), prompts.get(k),
                                              source=source)
            self._RemoveStateFromFlow(k, with_states=True)
        return True, ""

    def _RemoveStateFromFlow(self, key: str, with_states: bool) -> None:
        """Remove ``key`` from the flow's ``ConversationStates`` and from its ``IllocutionaryPrompt``, and from
        ``ConversationStates`` of this class too when ``with_states`` is true. Called only by ``ReplaceBranch`` and by
        ``RecoverInit`` when it replays a removal, never from outside this class."""
        bundle = self.ConversationStateInitBundle
        bundle.get("ConversationStates", {}).pop(key, None)
        (bundle.get("PromptBlocks", {}).get("IllocutionaryPrompt") or {}).pop(key, None)
        if with_states:
            self.ConversationStates.pop(key, None)

    def _PutStateIntoFlow(self, key: str, entry: Any, prompt: Any, with_states: bool) -> None:
        """Put ``entry`` under ``key`` in the flow's ``ConversationStates`` and ``prompt`` under ``key`` in its
        ``IllocutionaryPrompt``, and in ``ConversationStates`` of this class too when ``with_states`` is true. Called by
        ``ApplyStateChange`` and by ``RecoverInit``, which runs before ``ConversationStates`` is filled."""
        bundle = self.ConversationStateInitBundle
        bundle.setdefault("ConversationStates", {})[key] = entry
        bundle.setdefault("PromptBlocks", {}).setdefault("IllocutionaryPrompt", {})[key] = prompt
        if with_states:
            self.ConversationStates[key] = entry

    def load_conversation_states_from_init(self) -> None:
        """Check the flow's shape, copy its ``ConversationStates`` into ``ConversationStates``, set
        ``ConversationStateName`` for the first state, and return ``None``.

        The checks raise ``ValueError`` at session start with one of these texts, each followed by an explanation. The
        first begins "a flow is a dict with 'ConversationStates' (a dict of states keyed by index as a string) and
        'PromptBlocks'" when the flow is not such a dict. The second begins "ConversationStates keys must be state
        indexes as strings" when a key is not a string of digits. The third begins "conversation state" followed by the
        key and "must be a dict". The fourth begins "state" followed by the key and "'questions' must be a list" when
        ``questions`` is not a list. The fifth begins "state" followed by the key and the text of ``_TurnCountRefusal``.
        The sixth begins "ConversationStates has no entry for the first state '0'". The seventh begins "a flow needs
        'PromptBlocks' with 'ConversationFramePrompt' (one text for the whole conversation) and 'IllocutionaryPrompt'". Called by ``illocutionary_lifecycles.core.ConversationInit.ConversationInit`` after the
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
            refusal = self._TurnCountRefusal(StateEntry)
            if refusal:
                raise ValueError(f"state {key!r}: " + refusal)
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
        The list ``nonconversational_socket_instances`` is checked and copied to
        ``pNonconversationalSocketInstancesState``, as an empty list when the state has none, and at the first entry
        every name the flow lists is fixed in ``NonconversationalSocketOptions``.

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
        _SocketNames = StateEntry.get("nonconversational_socket_instances") if isinstance(StateEntry, dict) else None
        if _SocketNames is not None and not (isinstance(_SocketNames, list) and all(isinstance(n, str) and n.strip() for n in _SocketNames)):
            raise ValueError("a state's 'nonconversational_socket_instances' must be a list of socket names")
        ps.pNonconversationalSocketInstancesState = list(_SocketNames or [])
        if self.NonconversationalSocketOptions is None:   # the first entry, at session start
            self.NonconversationalSocketOptions = frozenset(n for e in self.ConversationStates.values() if isinstance(e, dict)
                                                            for n in (e.get("nonconversational_socket_instances") or []))

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

    def SetAnalyzerInstance(self, CustomAnalyzerName: str, CustomAnalyzerPrompt: str,
                            CustomAnalyzerOutputSchema: dict,
                            CustomAnalyzerReadsNonconversationalSocketFeed: bool = False) -> tuple[bool, str]:
        """Instantiate one custom analyzer for this session from its four arguments, and return a pair of true and an
        empty string when it was instantiated, or false and the reason when it was not.

        NOTE: This is an experimental feature. You will only need this for an analyzer that does not exist when the
        session starts, during an ongoing conversation session. Only use this feature if you are sure you need it. It
        goes against the basic idea of IL, a flow written in advance whose states (eg. during runtime, upcoming
        ConversationStates in the active flow in SystemState) name only registered analyzers.

        The arguments are the fields of ``illocutionary_lifecycles.analyzers.AnalyzerBase.CustomAnalyzerDeclaration``,
        whose docstring explains them. The analyzer is built by ``_InstantiateCustomAnalyzer`` in this class, kept in
        ``CustomAnalyzerInstances`` under ``CustomAnalyzerName``, and runs only while the conversation is in a state that
        lists that name in its ``Analyzers``, exactly like that state's other analyzers. Such a state can only be written
        after this call, through ``ApplyStateChange`` or ``ReplaceBranch``, because a flow given at session start may
        name only registered analyzers. The call is refused with the reason ``_CustomAnalyzerRefusal`` gives. An accepted
        call is recorded as a ``CustomAnalyzerInstantiationEvent`` before it takes effect, so a reopened session has the
        same custom analyzers, and a second call under the same name replaces the first. Called by
        ``illocutionary_lifecycles.core.session_provider.SessionProvider.SetAnalyzerInstance``."""
        CustomAnalyzerRefusalReason = self._CustomAnalyzerRefusal(
            CustomAnalyzerName, CustomAnalyzerPrompt, CustomAnalyzerOutputSchema,
            CustomAnalyzerReadsNonconversationalSocketFeed)
        if CustomAnalyzerRefusalReason:
            return False, CustomAnalyzerRefusalReason
        CheckedCustomAnalyzerName = str(CustomAnalyzerName).strip()
        if self.Record is not None:
            self.Record.UpsertCustomAnalyzerInstantiationEvent(
                CheckedCustomAnalyzerName, str(CustomAnalyzerPrompt), CustomAnalyzerOutputSchema,
                CustomAnalyzerReadsNonconversationalSocketFeed=CustomAnalyzerReadsNonconversationalSocketFeed)
        self._InstantiateCustomAnalyzer(CheckedCustomAnalyzerName, str(CustomAnalyzerPrompt), CustomAnalyzerOutputSchema,
                                        CustomAnalyzerReadsNonconversationalSocketFeed)
        return True, ""

    def RemoveAnalyzerInstance(self, CustomAnalyzerName: str) -> bool:
        """Remove the custom analyzer kept under ``CustomAnalyzerName`` to free its memory, and return true, or return
        false when there is none under that name, or while any state of the flow (eg. during runtime, upcoming
        ConversationStates in the active flow in SystemState) still lists it among its analyzers.

        NOTE: This is only a cleanup function. You will not need it in almost any session. It exists for a long
        session that instantiates custom analyzers without end, where the ones no state lists any more would otherwise
        stay in memory until the session ends. A custom analyzer is never removed to stop it from running, because it
        runs only in the states that list it.

        A removal is refused while any state lists the analyzer, and not only the current one, because a state that
        names a missing analyzer would make a reopened session refuse to start. The removal is recorded as a
        ``CustomAnalyzerInstantiationEvent``, so a reopened session does not instantiate it again. The note of
        ``SetAnalyzerInstance`` applies here too. Called by
        ``illocutionary_lifecycles.core.session_provider.SessionProvider.RemoveAnalyzerInstance``."""
        CheckedCustomAnalyzerName = str(CustomAnalyzerName or "")
        if CheckedCustomAnalyzerName not in self.CustomAnalyzerInstances:
            return False
        for FlowStateEntry in (self.ConversationStates or {}).values():
            FlowStateAnalyzerNames = list((FlowStateEntry or {}).get("Analyzers") or []) if isinstance(FlowStateEntry, dict) else []
            if CheckedCustomAnalyzerName in FlowStateAnalyzerNames:
                return False
        if self.Record is not None:
            self.Record.UpsertCustomAnalyzerInstantiationEvent(CheckedCustomAnalyzerName, CustomAnalyzerRemoved=True)
        del self.CustomAnalyzerInstances[CheckedCustomAnalyzerName]
        return True

    def _CustomAnalyzerRefusal(self, CustomAnalyzerName: Any, CustomAnalyzerPrompt: Any, CustomAnalyzerOutputSchema: Any,
                               CustomAnalyzerReadsNonconversationalSocketFeed: Any) -> str:
        """Return why these arguments may not instantiate a custom analyzer, or an empty string when they may. A name
        must end in ``CustomAnalyzer`` with a name of its own before it, and may not be the name of a registered analyzer.
        The prompt may not be empty. The output schema must be a dict that is not empty, whose every key is a string
        that is not empty and whose every value is "str", "int" or a list of strings that is not empty. Whether the
        analyzer reads the socket feeds must be true or false. Checking all of it before anything changes keeps a
        refused call from recording or replacing anything. Called only by ``SetAnalyzerInstance`` in this class."""
        from illocutionary_lifecycles.analyzers.AnalyzerBase import ImportAllAnalyzers
        CheckedCustomAnalyzerName = str(CustomAnalyzerName or "").strip()
        if not CheckedCustomAnalyzerName.endswith("CustomAnalyzer") or CheckedCustomAnalyzerName == "CustomAnalyzer":
            return "a custom analyzer's name ends in 'CustomAnalyzer', with a name of its own before it"
        if CheckedCustomAnalyzerName in ImportAllAnalyzers():
            return f"{CheckedCustomAnalyzerName!r} is already the name of a registered analyzer"
        if not str(CustomAnalyzerPrompt or "").strip():
            return "a custom analyzer needs a prompt"
        CustomAnalyzerOutputKindsValid = isinstance(CustomAnalyzerOutputSchema, dict) and bool(CustomAnalyzerOutputSchema) and all(
            isinstance(CustomAnalyzerOutputKey, str) and CustomAnalyzerOutputKey
            and (CustomAnalyzerOutputKind in ("str", "int")
                 or (isinstance(CustomAnalyzerOutputKind, list) and CustomAnalyzerOutputKind
                     and all(isinstance(CustomAnalyzerOutputChoice, str) for CustomAnalyzerOutputChoice in CustomAnalyzerOutputKind)))
            for CustomAnalyzerOutputKey, CustomAnalyzerOutputKind in CustomAnalyzerOutputSchema.items())
        if not CustomAnalyzerOutputKindsValid:
            return "a custom analyzer's output schema maps every key to a list of strings, 'str' or 'int'"
        if not isinstance(CustomAnalyzerReadsNonconversationalSocketFeed, bool):
            return "whether a custom analyzer reads the nonconversational socket feeds is true or false"
        return ""

    def _InstantiateCustomAnalyzer(self, CustomAnalyzerName: str, CustomAnalyzerPrompt: str, CustomAnalyzerOutputSchema: dict,
                                   CustomAnalyzerReadsNonconversationalSocketFeed: bool) -> None:
        """Build the custom analyzer these four fields declare and keep it in ``CustomAnalyzerInstances`` under
        ``CustomAnalyzerName``, and return ``None``. The declaration is
        ``illocutionary_lifecycles.analyzers.AnalyzerBase.CustomAnalyzerDeclaration`` with a deep copy of the output
        schema, the analyzer is built by ``illocutionary_lifecycles.analyzers.AnalyzerBase.InstantiateCustomAnalyzer``,
        and its nonconversational socket feed is ``_NonconversationalSocketFeeds`` of this class, bound to this session.
        This is the one place a custom analyzer is built, so one instantiated by ``SetAnalyzerInstance`` and one rebuilt
        by ``RecoverInit`` from the record are built the same way. Called only by those two methods of this class."""
        from illocutionary_lifecycles.analyzers.AnalyzerBase import CustomAnalyzerDeclaration, InstantiateCustomAnalyzer
        self.CustomAnalyzerInstances[CustomAnalyzerName] = InstantiateCustomAnalyzer(
            CustomAnalyzerDeclaration(
                CustomAnalyzerName=CustomAnalyzerName,
                CustomAnalyzerPrompt=CustomAnalyzerPrompt,
                CustomAnalyzerOutputSchema=copy.deepcopy(CustomAnalyzerOutputSchema),
                CustomAnalyzerReadsNonconversationalSocketFeed=bool(CustomAnalyzerReadsNonconversationalSocketFeed)),
            self._NonconversationalSocketFeeds)

    def _NonconversationalSocketFeeds(self) -> str:
        """Return the nonconversational socket feeds the current conversation state shows, as one text, and write
        nothing.

        A nonconversational feed is the text a server keeps in a socket, a pragmatically useful description of something
        neither the user nor the assistant said (for example what is on a screen, what the user just touched, captions or
        narration, recent events with their times, what has been built so far, how much time has passed, or the server's
        own summary of what happened earlier). It is always text the server has already written for the conversation,
        never the source it describes, and the server replaces it whenever the source changes. Its form is the server's
        choice, such as one sentence describing the present, a single line about what the user is focusing on, a short
        list of recent events, lines of names and values, or nothing when there is nothing to show.

        IL keeps no copy and no history of a feed. It reads whatever the feed says at the moment it is used, which is
        when a reply is composed and, for a custom analyzer that reads socket feeds, each time that analyzer runs, so
        anything earlier that should still count has to be written into the feed by the server. Without a socket reader,
        the feed is the one text placed through ``SetNonconversationalContentSocket``. With a socket reader set through
        ``illocutionary_lifecycles.core.session_provider.SessionProvider.SetNonconversationalSocketReader``, the reader is
        called with the socket names the current state shows, from the pragmatic field
        ``pNonconversationalSocketInstancesState``, and the texts it returns are joined one per line, empty ones left out,
        in the order the reader returns them. That is what
        ``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ComposeCurrentPrompt`` shows for a reply, so a custom
        analyzer that reads the feeds sees what the reply sees. An empty string comes back for a session without a
        pragmatic state and when nothing is shown, and an error the reader raises reaches the caller, as it does when a
        reply is composed.

        NOTE: This is an experimental feature, as ``SetAnalyzerInstance`` explains. The method is handed, bound to this
        session, to every custom analyzer that ``_InstantiateCustomAnalyzer`` in this class builds, and is called only by
        the custom analyzers that read socket feeds, each time they run."""
        if self.PragmaticState is None:
            return ""
        if self.NonconversationalSocketReader is None:
            return str(getattr(self.PragmaticState, "pNonconversationalContentSocketState", "") or "")
        ShownNonconversationalSocketNames = list(
            getattr(self.PragmaticState, "pNonconversationalSocketInstancesState", []) or [])
        ShownNonconversationalSocketFeeds = self.NonconversationalSocketReader(ShownNonconversationalSocketNames) or {}
        return "\n".join(str(ShownNonconversationalSocketFeed) for ShownNonconversationalSocketFeed
                         in ShownNonconversationalSocketFeeds.values() if str(ShownNonconversationalSocketFeed or "").strip())

    def SetNonconversationalContentSocket(self, Content: str) -> bool:
        """Set the pragmatic field ``pNonconversationalContentSocketState`` to ``Content`` with surrounding spaces
        removed, delete the field when ``Content`` is empty, and return true, or return false before the pragmatic
        state exists.

        The field holds one text the server places for the session, which neither the user nor the assistant said. A
        server uses it to send things like summaries of the closed captions of media the user and the assistant
        share, such as a video being watched, a screen being browsed or events in a VR scene. The content is shown
        to the model wherever the flow's authored text holds the field's name in braces, so a conversation state
        whose text does not hold the name does not show it, and it is handed with the pragmatic state to every
        analyzer, those that run on a finished turn and those that run on the speech so far. The analyzers shipped
        in the package do not read it. A new placement replaces the one before, the content stays through a move
        to another conversation state until the server replaces or removes it, and it is saved with the other
        pragmatic values after every refresh. The name is best given a line of its own in the authored text,
        because the words around it stay when the field is absent. Called by
        ``SessionProvider.SetNonconversationalContentSocket``."""
        if self.PragmaticState is None:
            return False
        Content = str(Content or "").strip()
        if Content:
            self.PragmaticState.pNonconversationalContentSocketState = Content
        elif hasattr(self.PragmaticState, "pNonconversationalContentSocketState"):
            del self.PragmaticState.pNonconversationalContentSocketState
        return True
