"""The folder that processes one finished user utterance, from saving it to the reply, and holds the two cycles that
call the analyzers.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every user turn passes through this folder inside ``core``, where
the analyzers of the folder ``analyzers`` check it, the result is recorded in the folder ``memory``, and the reply is
written, before an adapter in the folder ``server`` delivers it. The module ``ResponseProcessing`` holds
``ResponseProcessing``, which saves the utterance, runs the cycle, composes the prompt and calls the model, and
``ComposeCurrentPrompt``. The module ``sync_cycle`` holds ``SyncCycle``, which runs a state's analyzers on a finished
turn in two passes, and ``DeferredIncrementalSettle``, which runs the incremental analyzer on the speech so far while
the user is still speaking.

Despite the folder's name, the end of a spoken turn is not set here. When the user speaks, the class
``illocutionary_lifecycles.server.adapters.voice_adapters.voice_adapter_helpers.PipecatVoiceAdapterHelpers.UserSpeechTurnAggregationAssembler``
joins the STT's final transcriptions into one turn and sets when it is finished, and this folder processes the
finished turn. ``ResponseProcessing`` is re-exported here.
"""
from illocutionary_lifecycles.core.turn_taking.ResponseProcessing import ResponseProcessing

__all__ = ["ResponseProcessing"]
