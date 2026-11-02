"""The folder of three stateless functions that read recorded event dicts and the flow's prompt blocks they are given,
plain functions and not tools a language model calls, despite the folder's name.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and its record and its authored texts are read in a few small ways by
more than one module, so those reads sit here, inside the folder ``memory``, knowing no session. Of the package's four
folders, ``core`` and ``server`` call them and ``analyzers`` never do. The module ``FilterByCategoryTool`` holds
``filter_by_category``, which returns one category's event dicts and serves ``Memory`` and
``illocutionary_lifecycles.server.adapter_callback_handlers.EventStreamReader``. The module ``StaticPromptBlocks``
holds the function of the same name, which returns the authored prompt blocks that apply to the current state and
serves ``illocutionary_lifecycles.core.system_state.static_prompt_library``. The module ``AnsweredQuestionFactsTool``
holds ``AnsweredQuestionFacts``, which returns the answered questions found in recorded analyzer results and serves
``illocutionary_lifecycles.core.session_provider.SessionProvider`` for the question-answered callbacks. The three
functions are re-exported here.
"""
from illocutionary_lifecycles.memory.MemoryReadTools.FilterByCategoryTool import (
    filter_by_category,
)
from illocutionary_lifecycles.memory.MemoryReadTools.StaticPromptBlocks import (
    StaticPromptBlocks,
)
from illocutionary_lifecycles.memory.MemoryReadTools.AnsweredQuestionFactsTool import (
    AnsweredQuestionFacts,
)

__all__ = [
    "filter_by_category", "StaticPromptBlocks", "AnsweredQuestionFacts",
]
