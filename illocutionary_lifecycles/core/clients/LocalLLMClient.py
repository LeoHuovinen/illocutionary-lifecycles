"""The third language-model client, ``LocalLLMClient``, which runs a model on the same machine through the
``transformers`` text-generation pipeline, and its settings, ``LocalLLMConfig``.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this module, in ``illocutionary_lifecycles/core/clients``, lets that
model be one on the server's own machine instead of a remote service. Of the package's four folders, ``core`` holds
this client and calls it for every reply, ``analyzers`` calls it for their checks, and neither ``memory``, which keeps
the record, nor ``server``, which connects pages and apps, ever reaches it. The client replaces ``LLMClient`` and
``OpenAIClient`` of ``illocutionary_lifecycles.core.clients.llm`` because it has the same two async methods,
``complete`` and ``complete_json``. A server chooses it only in code, by passing a ``LocalLLMConfig`` as the session's
``llm_config``, which ``SystemState.BuildLLMConnection`` turns into this client, and the environment never selects it.
``transformers`` and ``torch`` are installed by the package's ``local`` extra, and the model is loaded on first use.

A local model has no JSON response format to rely on, so ``complete_json`` finds the JSON object in the model's text
itself with ``extract_json_object``, and returns an empty dict when there is none. Generation blocks its thread, so it
runs in a worker thread and the event loop, asyncio's scheduler that runs every session's coroutines in one thread,
stays free for the other sessions.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from illocutionary_lifecycles.core.clients.llm import _strip_quotes


@dataclass
class LocalLLMConfig:
    """The settings of a ``LocalLLMClient``, passed as a session's ``llm_config``, as the module docstring above explains.

    ``model`` holds the name or path of the model as ``transformers`` resolves it. ``max_new_tokens`` holds the most
    tokens a call generates when it gives no limit, 160 by default. ``device`` holds "cpu", "cuda", a device index, or
    "auto" to let ``transformers`` place the model, and has no default value a model can load with, so a server sets
    it. ``local_files_only`` holds whether the model is loaded only from files already on the machine, true by default,
    so nothing is downloaded unless the server asks.
    """

    model: str = ""
    max_new_tokens: int = 160
    device: str = ""
    local_files_only: bool = True


def extract_json_object(ModelReplyText: str) -> dict[str, Any]:
    """Return the first JSON object found in ``ModelReplyText``, or an empty dict when there is none or the first
    valid JSON found there is not an object.

    The object is found by counting opening and closing braces from each opening brace, so text before and after it
    is ignored, and a balanced span that is not valid JSON is skipped and the search goes on from the next opening
    brace. Called only by ``LocalLLMClient.complete_json`` in this module.
    """
    ModelReplyText = str(ModelReplyText or "")
    start = ModelReplyText.find("{")
    while start >= 0:
        depth = 0
        for end in range(start, len(ModelReplyText)):
            if ModelReplyText[end] == "{":
                depth += 1
            elif ModelReplyText[end] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(ModelReplyText[start:end + 1])
                    except json.JSONDecodeError:
                        break
                    return parsed if isinstance(parsed, dict) else {}
        start = ModelReplyText.find("{", start + 1)
    return {}


@dataclass
class LocalLLMClient:
    """The client for a model run on the same machine, with the two methods ``complete`` and ``complete_json`` every
    client has, built from a ``LocalLLMConfig``, as the module docstring above explains. ``_pipeline`` holds the
    ``transformers`` text-generation pipeline, loaded on first use through the property ``pipeline``."""

    config: LocalLLMConfig = field(default_factory=LocalLLMConfig)
    _pipeline: Any = field(default=None, repr=False)

    @property
    def pipeline(self) -> Any:
        """Return the ``transformers`` text-generation pipeline for ``config.model``, loading the tokenizer and the model
        on first use, with the model placed by ``transformers`` when ``config.device`` is "auto" and on that device
        otherwise. Loading errors from ``transformers`` are raised to the caller. Read by ``_generate`` in this class."""
        if self._pipeline is None:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            tokenizer = AutoTokenizer.from_pretrained(
                self.config.model, local_files_only=self.config.local_files_only)
            placement = ({"device_map": "auto"} if self.config.device == "auto" else {})
            model = AutoModelForCausalLM.from_pretrained(
                self.config.model, local_files_only=self.config.local_files_only, **placement)
            device = {} if self.config.device == "auto" else {"device": self.config.device}
            self._pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, **device)
        return self._pipeline

    def _generate(self, prompt: str, temperature: float, max_tokens: int | None) -> str:
        """Return the model's text for ``prompt`` without the prompt itself, stripped of surrounding spaces, generating
        at most ``max_tokens`` tokens or ``config.max_new_tokens`` when that is ``None``, sampling when ``temperature``
        is above 0 and choosing the most likely tokens otherwise. A model with a chat template is given the prompt as one
        user message, so an instruction-tuned model answers instead of continuing the text. Runs in a worker thread,
        called by ``complete`` and ``complete_json`` in this class."""
        pipe = self.pipeline
        settings: dict[str, Any] = {
            "max_new_tokens": max_tokens if max_tokens is not None else self.config.max_new_tokens,
            "return_full_text": False,
        }
        if temperature > 0:
            settings.update(do_sample=True, temperature=temperature)
        else:
            settings.update(do_sample=False)
        # A model with a chat template is given the prompt as one user message, so that an
        # instruction-tuned model answers instead of continuing the text.
        tokenizer = getattr(pipe, "tokenizer", None)
        if getattr(tokenizer, "chat_template", None):
            out = pipe([{"role": "user", "content": prompt}], **settings)
            generated = out[0]["generated_text"]
            if isinstance(generated, list):
                generated = generated[-1].get("content", "") if generated else ""
        else:
            out = pipe(prompt, **settings)
            generated = out[0]["generated_text"]
        return str(generated or "").strip()

    async def complete(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        """Return the model's reply text to ``prompt`` with quote marks removed by ``_strip_quotes`` from
        ``illocutionary_lifecycles.core.clients.llm``, generated in a worker thread with ``temperature``, 0.3 by
        default, and ``max_tokens``, in the same way the other clients' ``complete`` behaves."""
        text = await asyncio.to_thread(self._generate, prompt, temperature, max_tokens)
        return _strip_quotes(text)

    async def complete_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Return the first JSON object in the model's reply to ``prompt``, found by ``extract_json_object``, or an empty
        dict when the reply holds none, generated in a worker thread with ``temperature``, 0.3 by default, as the module
        docstring above explains."""
        text = await asyncio.to_thread(self._generate, prompt, temperature, None)
        return extract_json_object(text)
