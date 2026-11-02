"""``StaticPromptBlocks``, one of the three stateless reads in ``illocutionary_lifecycles/memory/MemoryReadTools``,
which returns the flow's authored prompt blocks that apply to the current state, and is the one place that choice is
made.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and every prompt begins with texts the flow's author wrote, so this
function, kept in the folder ``memory`` though it reads the flow and not the record, picks them for the composer in
the folder ``core``, reached through
``illocutionary_lifecycles.core.system_state.static_prompt_library.StaticPromptLibrary``. The folders ``analyzers``
and ``server`` never call it. "Static" means the authored text, as opposed to the composed prompt.

Two entries of the flow's ``PromptBlocks`` are matched, in this order. ``ConversationFramePrompt`` is one text for
the whole conversation. ``IllocutionaryPrompt`` is a dict from state index, as a string, to the prompt of
that state, which says what the assistant does in it. A block is text with blanks in braces the composer fills, and may
be a dict from condition name to text, as ``PragmaticState.Composer`` explains.

Two pieces of advice for a flow's author follow from how the prompt is used. The composed prompt asks for one reply,
so the frame prompt should say the reply belongs to a conversation already under way and should
not ask for a greeting. A greeting or an introduction belongs in the illocutionary prompt of the first state, and the
prompt of every other state should say the conversation is already under way.
"""
from __future__ import annotations

from typing import Any


def StaticPromptBlocks(blocks: dict[str, Any],
                       PragmaticStates: dict[str, Any]) -> list[Any]:
    """Return the list of matched block values, the frame prompt, then the current state's
    illocutionary prompt, leaving out any that the flow does not have.

    ``blocks`` is the flow's ``PromptBlocks`` dict, and ``PragmaticStates`` is the dict of the pragmatic fields, of
    which ``pConversationState`` is read. The values are returned as authored, with their
    blanks unfilled, as the module docstring above explains.
    """
    matched: list[Any] = []

    frame_value = blocks.get("ConversationFramePrompt")
    if frame_value is not None:
        matched.append(frame_value)

    # The lookup is stored through JSON, so its keys are strings.
    illocutionary_lookup = blocks.get("IllocutionaryPrompt", {})
    illocutionary_value = illocutionary_lookup.get(
        str(PragmaticStates.get("pConversationState")))
    if illocutionary_value is not None:
        matched.append(illocutionary_value)

    return matched
