"""Two of the three language-model clients, ``LLMClient`` for Azure OpenAI and ``OpenAIClient`` for any
OpenAI-compatible API, the function that builds one from the environment, and the per-process choice of the client the
analyzers use.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and this module, in ``illocutionary_lifecycles/core/clients``, is how
the model is reached, both for the replies, through ``SystemState.llm_client``, and for the analyzers of the folder
``analyzers``, through ``analyzer_llm`` and ``incremental_phrase_llm``. Of the package's four folders, ``core`` holds
this module, ``analyzers`` import it for their client and nothing else of ``core``, and ``memory`` and ``server``
never reach a model. The two classes here and the third client,
``illocutionary_lifecycles.core.clients.LocalLLMClient.LocalLLMClient``, are interchangeable through their two async
methods, ``complete``, which sends the prompt as one user message and returns the reply text with its quote marks
removed, and
``complete_json``, which asks for a JSON object and returns it parsed, with a temperature of 0.3 by default. The class
``LLMClient`` serves Azure OpenAI only.

``llm_client_from_env`` is the only reader of the environment here. With ``AZURE_OPENAI_API_KEY`` set it builds an
``LLMClient`` and requires ``AZURE_OPENAI_ENDPOINT``, the address of the Azure OpenAI resource,
``AZURE_OPENAI_DEPLOYMENT``, the name under which the model is deployed in that resource, and
``AZURE_OPENAI_API_VERSION``, the API version the resource serves. Otherwise, with ``OPENAI_API_KEY`` set, it builds an
``OpenAIClient`` and requires ``OPENAI_MODEL`` and ``OPENAI_BASE_URL``, the address of the API. Written in the
server's ``.env`` file, a line has the form NAME=value, for example AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini as one possible
deployment name. With neither key set it raises ``RuntimeError`` beginning "no model is configured", so a session
without a model does not start, and there is no placeholder client. A local model is never chosen from the
environment.

The analyzers' client is chosen once per process. ``analyzer_llm`` builds it from the environment on first use, and
``configure_clients`` sets it in code, which ``SystemState.BuildLLMConnection`` does when a session is given an
``llm_config``. ``incremental_phrase_llm`` returns the incremental analyzer's client, the one ``configure_clients``
set for it, or else the analyzers' client.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from openai import AsyncAzureOpenAI, AsyncOpenAI


# Double quotes and backticks are removed from reply text. An apostrophe is removed only when
# it is not between two letters, so a quoted word loses its quotes while contractions and
# possessives ("don't", "we're", "o'clock", "it's") are kept.
_QUOTE_RE = re.compile(r'["“”`]')
_APOSTROPHE_RE = re.compile(r"(?<![A-Za-z])['’]|['’](?![A-Za-z])")


def _strip_quotes(text: str) -> str:
    """Return ``text`` with every double quote, curly double quote and backtick removed, and every apostrophe removed
    that is not between two letters, so a quoted word loses its quotes while "don't" and "it's" keep theirs. Called by
    ``complete`` of both clients in this module and of
    ``illocutionary_lifecycles.core.clients.LocalLLMClient.LocalLLMClient``, so no reply reaches a user with quotes."""
    return _APOSTROPHE_RE.sub("", _QUOTE_RE.sub("", text))


@dataclass
class LLMConfig:
    """The connection settings of an ``LLMClient``, the Azure OpenAI resource's ``endpoint``, its ``api_key``, the
    ``api_version`` it serves and the model's ``deployment`` name, built by ``llm_client_from_env`` in this module from
    the ``AZURE_OPENAI_*`` variables or passed in code as a session's ``llm_config``."""

    endpoint: str
    api_key: str
    api_version: str
    deployment: str


@dataclass
class LLMClient:
    """The client for Azure OpenAI, with the two methods ``complete`` and ``complete_json`` every client has, built from
    an ``LLMConfig``, as the module docstring above explains. ``_client`` holds the vendor SDK's ``AsyncAzureOpenAI``
    object, opened on first use through the property ``client``."""

    config: LLMConfig
    _client: AsyncAzureOpenAI | None = None

    @property
    def client(self) -> AsyncAzureOpenAI:
        """Return the SDK's ``AsyncAzureOpenAI`` object for this client's resource, creating it on first use from
        ``config``. Read by the two methods of this class."""
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=self.config.endpoint,
                api_key=self.config.api_key,
                api_version=self.config.api_version,
            )
        return self._client

    async def complete(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        """Send ``prompt`` to the deployment as one user message and return the reply text, stripped of surrounding
        spaces and of quote marks by ``_strip_quotes``, or an empty string when the model returns no content.
        ``temperature`` is 0.3 by default, and ``max_tokens``, when given, caps the reply. The composed prompt reaches
        the model through ``PostComposerLLMCallHelper`` and this method, and the incremental analyzer calls it with
        temperature 0 and three tokens. Errors from the SDK are raised to the caller. The two methods every client has
        are explained in the module docstring above."""
        kwargs: dict[str, Any] = {
            "model": self.config.deployment,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            return ""
        return _strip_quotes(content.strip())

    async def complete_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Send ``prompt`` to the deployment as one user message with the JSON-object response format and return the
        parsed object, or an empty dict when the model returns no content. ``temperature`` is 0.3 by default. A reply
        that is not valid JSON raises ``json.JSONDecodeError``, which every analyzer catches and treats as no answer.
        Called by the question checker and the pragmatic transition criterion through ``analyzer_llm`` in this module."""
        response = await self.client.chat.completions.create(
            model=self.config.deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            return {}
        return json.loads(content)  # type: ignore[no-any-return]


@dataclass
class OpenAIConfig:
    """The connection settings of an ``OpenAIClient``, the ``api_key``, the ``model`` name and the API's ``base_url``,
    built by ``llm_client_from_env`` in this module from the ``OPENAI_*`` variables or passed in code as a session's
    ``llm_config``."""

    api_key: str
    model: str
    base_url: str


@dataclass
class OpenAIClient:
    """The client for any OpenAI-compatible API, with the two methods ``complete`` and ``complete_json`` every client
    has, built from an ``OpenAIConfig``, as the module docstring above explains. ``_client`` holds the vendor SDK's
    ``AsyncOpenAI`` object, opened on first use through the property ``client``."""

    config: OpenAIConfig
    _client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Return the SDK's ``AsyncOpenAI`` object for this client's API, creating it on first use from ``config``. Read
        by the two methods of this class."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
        return self._client

    async def complete(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        """Send ``prompt`` to the model as one user message and return the reply text, stripped of surrounding spaces
        and of quote marks by ``_strip_quotes``, or an empty string when the model returns no content, in the same
        way as ``LLMClient.complete`` in this module. Errors from the SDK are raised to the caller."""
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            return ""
        return _strip_quotes(content.strip())

    async def complete_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Send ``prompt`` to the model with the JSON-object response format and return the parsed object, or an empty
        dict when the model returns no content, in the same way as ``LLMClient.complete_json`` in this module."""
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            return {}
        return json.loads(content)  # type: ignore[no-any-return]


def llm_client_from_env() -> Any:
    """Return an ``LLMClient`` when ``AZURE_OPENAI_API_KEY`` is set, or else an ``OpenAIClient`` when ``OPENAI_API_KEY``
    is set, built from the environment as the module docstring above explains, and raise ``RuntimeError`` when neither
    key is set.

    The further variables of the chosen client are read through
    ``illocutionary_lifecycles.core.environment.Required``, which raises with the variable's name when one is missing.
    The error with no key begins "no model is configured" and names both sets of variables and ``LocalLLMConfig``, so
    no reply is written and no question is answered by a placeholder. Called by
    ``SystemState.BuildLLMConnection`` at session start and by ``analyzer_llm`` in this module on its first call.
    """
    import os
    from illocutionary_lifecycles.core.environment import Required

    if os.environ.get("AZURE_OPENAI_API_KEY"):
        return LLMClient(LLMConfig(
            endpoint=Required("AZURE_OPENAI_ENDPOINT", "the Azure OpenAI resource the replies and analyzers are sent to"),
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=Required("AZURE_OPENAI_API_VERSION", "the Azure OpenAI API version the resource serves"),
            deployment=Required("AZURE_OPENAI_DEPLOYMENT", "the deployment name of the model that writes the replies and runs the analyzers"),
        ))
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIClient(OpenAIConfig(
            api_key=os.environ["OPENAI_API_KEY"],
            model=Required("OPENAI_MODEL", "the model that writes the replies and runs the analyzers"),
            base_url=Required("OPENAI_BASE_URL", "the address of the OpenAI-compatible API"),
        ))
    raise RuntimeError(
        "no model is configured: set AZURE_OPENAI_API_KEY (with AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT and "
        "AZURE_OPENAI_API_VERSION) or OPENAI_API_KEY (with OPENAI_MODEL and OPENAI_BASE_URL) in the environment the server "
        "runs in, or pass a LocalLLMConfig as the session's llm_config. The same client writes every reply and runs every "
        "analyzer, so without one no question is ever answered and no state is ever left.")


_ANALYZER_LLM: Any = None
_INCREMENTAL_LLM: Any = None


def configure_clients(ModelClient: Any, IncrementalPhraseModelClient: Any = None) -> None:
    """Set, for the whole process, ``ModelClient`` as the client ``analyzer_llm`` returns and
    ``IncrementalPhraseModelClient`` as the client ``incremental_phrase_llm`` returns, using ``ModelClient`` for both
    when the second is ``None``, and return ``None``. Called by ``SystemState.BuildLLMConnection`` with the session's
    client when a session has an ``llm_config``. A smaller or faster model for
    the incremental analyzer is chosen only here, in code, as the module docstring above explains."""
    global _ANALYZER_LLM, _INCREMENTAL_LLM
    _ANALYZER_LLM = ModelClient
    _INCREMENTAL_LLM = IncrementalPhraseModelClient or ModelClient


def analyzer_llm() -> Any:
    """Return the client the analyzers use in this process, the one ``configure_clients`` set, or else one built by
    ``llm_client_from_env`` on the first call and reused afterwards. Called by the question checker and the pragmatic
    transition criterion in the folder ``analyzers``, and by ``incremental_phrase_llm`` in this module."""
    global _ANALYZER_LLM
    if _ANALYZER_LLM is None:
        _ANALYZER_LLM = llm_client_from_env()
    return _ANALYZER_LLM


def incremental_phrase_llm() -> Any:
    """Return the client the incremental analyzer uses in this process, the one ``configure_clients`` set for it, or
    else the client ``analyzer_llm`` returns. Called by ``OneWord`` in
    ``illocutionary_lifecycles.analyzers.incremental_phrase_analyzers.IncrementalPhraseCategoryAnalyzer``."""
    global _INCREMENTAL_LLM
    if _INCREMENTAL_LLM is None:
        _INCREMENTAL_LLM = analyzer_llm()
    return _INCREMENTAL_LLM
