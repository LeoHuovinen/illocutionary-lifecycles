"""The folder that holds the values the next prompt is composed from, the composer that builds the prompt, and the one
function that updates those values after analyzers have run.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every prompt the model gets is composed afresh for one turn from
these values and the flow's authored texts, so this folder, inside ``core``, is where what the conversation currently
holds turns into what the model is told, while the folder ``memory`` saves these values after every refresh and the
folder ``server`` never reads them. The module ``pragmatic_state`` holds ``PragmaticState``, whose ``p``-prefixed
fields are the values, and its method ``Composer``, the one place a prompt is built. The module ``refresher`` holds
``refresh``, which updates the fields from the results of the folder ``analyzers`` and moves the conversation when a
transition criterion reports done. ``PragmaticState`` and ``refresh`` are re-exported here.
"""
from illocutionary_lifecycles.core.pragmatic_state.pragmatic_state import PragmaticState
from illocutionary_lifecycles.core.pragmatic_state.refresher import refresh

__all__ = [
    "PragmaticState",
    "refresh",
]
