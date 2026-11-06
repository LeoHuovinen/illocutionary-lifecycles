"""Expose one dialogue definition as a remote text API over an RFC 6455 WebSocket.

That function reads the definition, stops with IL's own message when no model is configured in the environment,
prints the address, and listens on every network address of the machine.

    $ python -m illocutionary_lifecycles.server.WebSocketServer my-design.json --host 0.0.0.0 --port 8765 --route /ws

    <script>const socket = new WebSocket("ws://HOST:8765/ws");</script>

Any program that opens a WebSocket, a web page, an app, a game or a robot, can hold the dialogue with no Python
server written for it. Each connection is an independent session. The opening line is sent on connection, each
received message is one turn and is echoed as "TextHeardText", and the reply follows as "TextReplyText".
"""
import argparse
import json


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m illocutionary_lifecycles.server.WebSocketServer")
    parser.add_argument("DefinitionLocation")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--route", default="/ws")
    args = parser.parse_args(argv)
    import uvicorn
    from fastapi import FastAPI
    from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount import TextAdapterWebsocketMount
    try:
        Definition = json.load(open(args.DefinitionLocation, encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(f"{args.DefinitionLocation}: {error}")
    app = FastAPI()
    TextAdapterWebsocketMount(Definition).MountOnApp(app, args.route)
    from illocutionary_lifecycles.core.clients.llm import llm_client_from_env
    try:
        llm_client_from_env()
    except RuntimeError as error:
        parser.exit(1, f"{error}\n")
    url = f"ws://{args.host}:{args.port}{args.route}"
    print(url, flush=True)
    print(f'const socket = new WebSocket("{url}");', flush=True)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
