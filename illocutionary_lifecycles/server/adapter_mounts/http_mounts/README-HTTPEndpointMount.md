# A conversation as an OpenAI-compatible API

`HTTPEndpointMount` serves a flow to programs in the request and reply formats of OpenAI's API, so a program or a tool
that can call that API calls the conversation instead, with only the address and the key changed. This page is for the
person who connects to the endpoint. The docstring of `HTTPEndpointMount.py`, beside this file, says the same for the
person who writes the server.

## How the conversation is kept

OpenAI's API is stateless, the client sends the whole conversation on every call and the server remembers nothing. Here
the conversation is a flow of states, so the server keeps it and the client carries nothing.

The conversation lives on the server under your API key. One key is one conversation at a time, and several people or
devices at once need one key each. Every call is the next turn. Only your newest message is read, and any earlier
messages your tool sends along, its own memory of the conversation, and any system message, are ignored, since the flow
defines the system.

The flow speaks first, so the first call opens the conversation. If your first call already carries a message, the reply
is the opening line and the answer to your message together, separated by a blank line.

The conversation ends when the flow reaches its end, after a time without a message, three minutes by default, when the
server restarts, or when you send `END` or `STOP` as the whole message, in capitals. Your next call then starts a new
conversation and gets the opening line again. Send `HELP` as the whole message to get the server's help text as the
reply. Ordinary text never triggers the three commands.

If a reply does not follow from what you sent, the conversation was restarted on the server and your tool's own memory
is out of date. The reply's `metadata` says so, `history` is `stale`, and it can say so on your first call after the
server restarted, since your tool still holds the old conversation. Send `END` and start again.

`model` is information only, the key decides the flow, and `GET /v1/models` returns one name, the server's `ModelName`.
`previous_response_id`, `conversation`, `user`, `store`, `stream`, `tools`, `temperature` and `instructions` are
accepted and ignored. A call whose `metadata` holds `{"conversation": "new"}` ends the live conversation before
answering, which is the format's own channel for such a request, but not every tool lets you set `metadata`, which is
why `END` exists.

## Calling it

`ADDRESS` is the server's `/v1` and `KEY` is the API key the server gave you. The call is the same on every turn, and
there is nothing to keep between calls.

```bash
curl ADDRESS/chat/completions -H "Authorization: Bearer KEY" -H "Content-Type: application/json" \
  -d '{"model":"any","messages":[{"role":"user","content":"Hello"}]}'
```

```python
from openai import OpenAI
client = OpenAI(base_url="ADDRESS", api_key="KEY")
reply = client.chat.completions.create(model="any", messages=[{"role": "user", "content": "Hello"}])
print(reply.choices[0].message.content)
```

The Responses format works the same way at `ADDRESS/responses`, with `input` as the message and the reply in
`output_text`. Any tool with an OpenAI setting takes `ADDRESS` as its base URL and `KEY` as its API key, and its model
list shows the one name the server returns.

## The server

```python
from illocutionary_lifecycles.server.adapter_mounts.http_mounts.HTTPEndpointMount import HTTPEndpointMount

HTTPEndpointMount(flow, IdleSeconds=180, ModelName="IL HTTP OpenAI endpoint",
                  HelpText=None, EndedText=None).MountOnApp(app, "/v1")
```

`flow` is the dict `json.load` returns for `flow.json`, as for every mount. `HelpText` and `EndedText` are the replies
to `HELP` and to `END` or `STOP`, this page and one sentence by default. A bare mount accepts every key and keeps one
conversation per key string. A server that issues keys passes its own two texts, written for the people who hold them,
overrides `Authenticate` to refuse unknown keys with `HTTPEndpointRefusal`, and overrides `SessionKey` or
`NewConversationSession` to choose the flow per key, as the docstring explains. The mount adds cross-origin headers for
every origin unless the app already has `CORSMiddleware`.

## Where the format is defined

- Chat Completions, https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
- Responses, https://developers.openai.com/api/reference/resources/responses/methods/create
- How the standard API keeps conversation state, which this mount replaces with the key,
  https://developers.openai.com/api/docs/guides/conversation-state
