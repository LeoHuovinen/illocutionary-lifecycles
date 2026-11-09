"""Expose one dialogue flow, a ``flow.json`` file, as an OpenAI-compatible API over HTTP.

That function reads the dialogue flow, the JSON object whose top-level fields are ``PromptBlocks`` and
``ConversationStates``, stops with IL's own message when no model is configured in the environment,
prints the address and one curl row, and listens on every network address of the machine. ``--idle-seconds`` is the
time without a turn after which a conversation ends, 180 by default, ``--model-name`` the one name the endpoint lists
and echoes, ``--help-text-file`` a text file whose content answers the command ``HELP`` in place of the mount's README,
and ``--ended-text`` the reply to ``END`` and ``STOP``.

    $ python -m illocutionary_lifecycles.server.OpenAIServer flow.json --host 0.0.0.0 --port 8765 --route /v1

    $ curl http://HOST:8765/v1/chat/completions -H "Authorization: Bearer any-key" \\
        -H "Content-Type: application/json" -d '{"model": "any", "messages": [{"role": "user", "content": "Hello"}]}'

Any program or tool that can call OpenAI's API, a script with the ``openai`` library, a web page, a game, an
automation tool, holds the dialogue with only the address and the key changed. The conversation lives on the server
under the key the caller sends, one key is one conversation at a time, every call is the next turn, and only the newest
user message is read. This server checks no keys, any string works, and two callers sending different strings hold two
independent conversations. The commands ``HELP``, ``END`` and ``STOP``, the idle ending and the reply fields are in
``README-HTTPEndpointMount.md`` beside the mount, which is also the default reply to ``HELP``.
"""
import argparse
import json


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m illocutionary_lifecycles.server.OpenAIServer")
    parser.add_argument("DialogueFlowLocation")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--route", default="/v1")
    parser.add_argument("--idle-seconds", type=int, default=180,
                        help="seconds without a turn after which a conversation ends, 180 by default")
    parser.add_argument("--model-name", default="IL HTTP OpenAI endpoint",
                        help="the one model name the endpoint lists and echoes")
    parser.add_argument("--help-text-file", default=None,
                        help="a text file whose content answers the command HELP, the mount's README by default")
    parser.add_argument("--ended-text", default=None,
                        help="the reply to the commands END and STOP")
    args = parser.parse_args(argv)
    import uvicorn
    from fastapi import FastAPI
    from illocutionary_lifecycles.server.adapter_mounts.http_mounts.HTTPEndpointMount import HTTPEndpointMount
    try:
        with open(args.DialogueFlowLocation, encoding="utf-8") as flow_file:
            DialogueFlow = json.load(flow_file)
    except (OSError, ValueError) as error:
        parser.error(f"{args.DialogueFlowLocation}: {error}")
    HelpText = None
    if args.help_text_file is not None:
        try:
            with open(args.help_text_file, encoding="utf-8") as text:
                HelpText = text.read().strip()
        except OSError as error:
            parser.error(f"{args.help_text_file}: {error}")
    app = FastAPI()
    HTTPEndpointMount(DialogueFlow, IdleSeconds=args.idle_seconds, ModelName=args.model_name,
                      HelpText=HelpText, EndedText=args.ended_text).MountOnApp(app, args.route)
    from illocutionary_lifecycles.core.clients.llm import llm_client_from_env
    try:
        llm_client_from_env()
    except RuntimeError as error:
        parser.exit(1, f"{error}\n")
    url = f"http://{args.host}:{args.port}{args.route}"
    print(url, flush=True)
    print(f'curl {url}/chat/completions -H "Authorization: Bearer any-key" -H "Content-Type: application/json" '
          '-d \'{"model": "any", "messages": [{"role": "user", "content": "Hello"}]}\'', flush=True)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
