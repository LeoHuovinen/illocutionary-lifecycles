"""The folder of what prepares the voice adapter's input, holding the one module ``PipecatVoiceAdapterHelpers``, whose
class ``UserSpeechTurnAggregationAssembler`` joins the STT's final transcriptions into turns and sets when each turn
goes to the session, which is the speech side of turn taking for both speech mounts. The rules are explained in that
module's docstring. Nothing is imported or re-exported here.
"""
