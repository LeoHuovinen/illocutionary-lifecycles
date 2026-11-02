"""The analyzers that run on every new interim transcription of the speech so far, while the user is still speaking,
once for each instance the current state declares under ``incremental_phrase_instances``.

Most of the package waits for the user's turn to end, then checks the questions of the current state of a written flow
and has a language model write the reply. The functions here are the exception. They look at the user's words while
the user is still speaking, so that a page, an app or a robot connected through the folder ``server`` can react before
the turn ends. They sit in the folder ``analyzers``, are called by the folder ``core``, and their picks are saved in the
record in the folder ``memory``.

The folder holds one module, ``IncrementalPhraseCategoryAnalyzer``, whose function of the same name is registered under
the same name and picks one of an instance's declared option words from the words not yet analyzed.
``illocutionary_lifecycles.core.turn_taking.sync_cycle.DeferredIncrementalSettle`` selects it because its function
carries the attribute ``RunsPerIncrementalPhraseInstance`` set to true, and
``illocutionary_lifecycles.core.pragmatic_state.refresher.refresh`` keeps its value because its registered name contains
``IncrementalPhrase``. A new analyzer of this kind goes here and needs both, the attribute and the name. The registry
and the rules by which an analyzer is called are explained in ``illocutionary_lifecycles.analyzers.AnalyzerBase``.
"""
