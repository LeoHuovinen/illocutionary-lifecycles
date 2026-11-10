# The examples, in order

Numbered by the mount they run on, each giving a page everything the one before it gives and more (the header of any
page's `ConnectConversation.js` lists what): the text WebSocket mount, then the press-to-speak WebSocket mount, then the
Pipecat WebRTC voice mount. The order is also the order of what a page can do. Each folder from `0-text` to `7-plasma-visualizer-pipecat` is a
server (`server.py`), a page folder (`page/`) with IL's browser scripts beside the page, and the conversation
(`flow.json`). `8-side-by-side` reuses the pages and flow of the others. `9-vrm-webxr-pipecat` has the same three parts.

| | example | mount | open after `python server.py` |
|---|---|---|---|
| 0 | `0-text`: an example of the pure text API, a WebSocket endpoint any client can connect to and use for anything you like | text WebSocket | `http://127.0.0.1:8765/page/` |
| 1 | `1-chatbot-visual-kiosk`: the current step's choices as picture cards, the words as chat bubbles | press-to-speak WebSocket | `http://127.0.0.1:7874/page/` |
| 2 | `2-press-to-speak`: hold a button to speak; on one page, the assistant's voice as two bar visualizers, and the step, the answers and the turns as tables | press-to-speak WebSocket | `http://127.0.0.1:7872/page/` |
| 3 | `3-vrm-press-to-speak`: a VRM character | press-to-speak WebSocket | `http://127.0.0.1:7871/page/` |
| 4 | `4-rive-press-to-speak`: a Rive character, its mouth on the assistant's voice | press-to-speak WebSocket | `http://127.0.0.1:7876/page/` |
| 5 | `5-vrm-pipecat`: example 3 over Pipecat | Pipecat WebRTC voice | `http://127.0.0.1:7877/page/` |
| 6 | `6-rive-pipecat`: example 4 over Pipecat | Pipecat WebRTC voice | `http://127.0.0.1:7881/page/` |
| 7 | `7-plasma-visualizer-pipecat`: Pipecat's Plasma visualizer on the assistant's audio | Pipecat WebRTC voice | `http://127.0.0.1:7873/page/` |
| 8 | `8-side-by-side`: any of the pages above next to each other, over one conversation | Pipecat if any page uses it, else press-to-speak, else text | `http://127.0.0.1:7880/page/` |
| 9 | `9-vrm-webxr-pipecat`: a VRM character in a VR headset | Pipecat WebRTC voice | `http://127.0.0.1:7882/page/` |

Four guides beside this file show how to write such a server and page yourself, `README-TEXT.md`, `README-PRESS.md`,
`README-VOICE.md` and `README-VRM.md`. Each example's own `README.md` covers only what that example adds.

Every speech page carries a karaoke (the assistant's words as they are said, the person's as they are heard) with
its look in named rows, and the listening / thinking / speaking word with a row to show or hide it. Every page imports
`./log.js`, which prints the two log streams (recorded events and adapter callbacks, each on its own) in the browser console
and puts nothing on the page.

To run one: set the environment variables (the main `README.md` at the top of the repository, under Environment variables), `python server.py` in its folder, open its
address. The servers read the voice and the STT from the environment as well, `TTS_VOICE` (for example
`en-US-JennyNeural`) for every speech example, `SPEECH_LANGUAGE` (for example `en-US`) for the press-to-speak ones and
`STT_VENDOR` (for example `azure`) for the Pipecat ones, and stop with a `KeyError` naming the one that is missing.
Characters and models are not shipped: the VRM and Rive examples (`3-vrm-press-to-speak`, `4-rive-press-to-speak`, `5-vrm-pipecat`, `6-rive-pipecat`, `9-vrm-webxr-pipecat`) give the download in their README, and their page says so when none is there. The pictures in `1-chatbot-visual-kiosk/page/img/` are credited in
the comment at the top of its `page/index.html`.