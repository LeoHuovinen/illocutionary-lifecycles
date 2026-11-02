"""The analyzers whose result is whether and how one question of the current state was answered.

A conversation in this package is run between a user and a language model from a written flow, and each state of the
flow lists questions the conversation must get answered. Instead of trusting the model to say when that has happened,
the package asks a separate check after every user turn, and that check lives here, inside the folder ``analyzers``.
The other folders are ``core``, which runs the conversation and calls the check, ``memory``, which records the answers,
and ``server``, which connects pages and apps that send the user's turns.

The folder holds one module, ``QuestionAnsweredAnalyzer``, whose function ``QuestionAnsweredAnalyzer`` is registered as
``QuestionCompleteCriteria`` and is called the question checker.
``illocutionary_lifecycles.core.turn_taking.sync_cycle.SyncCycle`` runs it in the first pass of every turn, once for
each open question, because its registered name ends in ``QuestionCompleteCriteria``. Its result is read by
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh``, which removes the answered question, and by
``illocutionary_lifecycles.memory.MemoryWriter.MemoryWriter``, which saves the answer sentence as a remembered answer.
The question checker is not one of the transition criteria, which are in ``illocutionary_lifecycles/analyzers/transition_analyzers``. A
new analyzer of this kind goes here, and runs once per open question only if its registered name also ends in
``QuestionCompleteCriteria``. The registry and the rules by which an analyzer is called are explained in
``illocutionary_lifecycles.analyzers.AnalyzerBase``.
"""
