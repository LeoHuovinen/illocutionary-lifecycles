"""The one way a setting is read from the environment, ``Required``, which returns an environment variable by name and
raises an error saying what the variable is for when it is missing.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and the model, the storage and the speech services it uses are reached
with addresses and keys that only the server knows. Of the package's four folders, ``core`` holds this module,
``analyzers`` never read the environment, and ``core``, ``memory`` and ``server`` call it, by
``illocutionary_lifecycles.core.clients.llm.llm_client_from_env`` for the model,
``illocutionary_lifecycles.memory.persistence.CosmosSaveLoad`` for the Cosmos DB store, and the two speech mounts
``illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount`` and
``illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount`` for the Azure Speech
region.

No URL, host, region, model, deployment, database, voice or vendor name appears as a default in the package's code. Each is a line
of the environment the server runs in, its ``.env`` file or its shell, under the vendor's own variable name where the
vendor has one, such as ``AZURE_OPENAI_API_KEY`` or ``AZURE_SPEECH_REGION``. Nothing in the package carries a default
for any of them, so a missing one raises at the moment it is first needed. A value that is not a vendor's variable is
an argument of the call instead, such as ``TTSVoice`` on a speech mount or ``llm_config`` on the session. A new setting
is read through ``Required`` and nowhere else.

The package itself reads only the process environment. A server loads a ``.env`` file itself before it builds the
mount, as the Pipecat voice example servers do with the nearest one above the folder they start from, or exports the
variables in its shell, as the text and press-to-speak example servers expect.
"""
from __future__ import annotations

import os


def Required(VariableName: str, purpose: str) -> str:
    """Return the value of the environment variable ``VariableName`` with surrounding spaces removed, or raise
    ``RuntimeError`` when the variable is unset or blank.

    ``purpose`` is a phrase saying what the value is for. The error text is the variable's name, then "is not set",
    then ``purpose``, then "Set it in the environment the server runs in (its .env or shell); the library carries no
    default for it." This is the one step through which the model clients, the Cosmos DB store and the speech mounts
    read their settings, as the module docstring above explains."""
    value = os.environ.get(VariableName, "").strip()
    if not value:
        raise RuntimeError(f"{VariableName} is not set; {purpose}. Set it in the environment the server runs in (its .env or shell); "
                           "the library carries no default for it.")
    return value
