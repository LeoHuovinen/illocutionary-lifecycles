"""``PostComposerLLMCallHelper``, the one call in the package that turns a composed prompt into the assistant's words.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the model writes every reply from one prompt the composer built for
that turn, so this module, in ``illocutionary_lifecycles/core/clients``, is the single point where the assistant's
words are asked for. Of the package's four folders, ``core`` holds this call, ``analyzers`` reach the model only for their checks,
``memory`` records the prompt before the call and the reply after it is delivered, and no mount, adapter or voice
pipeline in ``server`` holds a language model of its own. There are two callers.
``illocutionary_lifecycles.core.turn_taking.ResponseProcessing.ResponseProcessing`` asks for every reply, which is
recorded. ``illocutionary_lifecycles.core.session_provider.SessionProvider.Backchannel`` asks for a short reaction
that is not a turn, which is not recorded.
"""
from __future__ import annotations

from typing import Any


async def PostComposerLLMCallHelper(ModelClient: Any, prompt: str) -> str:
    """Return the reply ``ModelClient.complete`` gives for ``prompt``, or ``prompt`` unchanged when ``ModelClient`` is
    ``None``. ``ModelClient`` is the session's ``SystemState.llm_client``, which a started session always has, because
    ``SystemState.BuildLLMConnection`` raises when no model is configured, so the second case is reached only by code
    that calls this function without a session, as the module docstring above explains. Called by
    ``ResponseProcessing`` and by ``SessionProvider.Backchannel``.
    """
    if ModelClient is None:
        return prompt
    return await ModelClient.complete(prompt)
