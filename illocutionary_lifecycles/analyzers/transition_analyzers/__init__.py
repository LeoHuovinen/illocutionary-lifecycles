"""The transition criteria, the analyzers that report whether the conversation may leave its current state through one
entry of the state's ``ConversationStateTransitionCriteria`` list.

The package carries a conversation with a language model through the states of a flow written in advance, and the
model never chooses when to go to the next state. That is answered after every user turn by the functions here, in the
folder ``analyzers``, and acted on by the folder ``core``, which runs the conversation, while the folder ``memory``
records each result and the folder ``server`` tells a connected page or app that the state changed.

The folder holds four criteria that replace each other by registered name. A flow chooses one for each entry of a
state's criteria list, and ``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs each in the second
pass of a turn, once per entry that names it, with the entry's position. The module
``QuestionsAnsweredTransitionAnalyzer``, registered as ``QuestionsAnsweredConversationStateTransitionCriteria``, reports
done when no question of the state is open. The module ``CategoricalAnswerTransitionAnalyzer``, registered as
``CategoricalAnswerConversationStateTransitionCriteria``, reports done when the user's recorded choice equals the
entry's ``Prompt``. The module ``TurnCountTransitionAnalyzer``, registered as
``TurnCountConversationStateTransitionCriteria``, reports done after the number of user turns in the entry's ``Prompt``.
The module ``PragmaticTransitionAnalyzer``, registered as ``PragmaticConversationStateTransitionCriteria``, reports done
when a language model answers that the condition written in the entry's ``Prompt`` holds for the state's utterances,
and is the only one of the four that calls a model.

Every criterion returns a value with the one key ``done`` and writes nothing.
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` moves the conversation to the ``TargetConversationState`` of the
lowest-positioned entry whose criterion reported done. A new criterion is a new module here whose registered name ends
in ``ConversationStateTransitionCriteria``, with rows added for it to the three tables in
``illocutionary_lifecycles.server.adapter_callback_handlers.EventCardReader``. The registry and the rules by which an
analyzer is called are explained in ``illocutionary_lifecycles.analyzers.AnalyzerBase``.
"""
