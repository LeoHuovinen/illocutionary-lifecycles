# Pipecat's Plasma visualizer on the assistant's voice

Pipecat's Plasma visualizer (from `@pipecat-ai/voice-ui-kit`, as built into `page/pipecat_plasma.js`) fills the page and
moves with the assistant's audio. Under it are the turn-state word (listening, thinking, speaking) from
`page/turn_label.js` and the karaoke from `page/karaoke.js`. The page runs on the voice server of `../README-VOICE.md`. Plasma
draws the assistant's audio track through its `track()` method, which the press-to-speak mount also gives, and the label
follows the RTVI events through its `rtvi()` method, which only the voice mount gives, and on press-to-speak it follows
`phase()` instead. Read the main `README.md` at the top of the repository and `../README-VOICE.md` first; this file adds the view. The simplest working case is
this folder.

The one file you replace is `flow.json`, the JSON object whose top-level fields are `PromptBlocks` and `ConversationStates`, which `json.load` reads into the dict the mount class takes as its first argument. `server.py` is the voice server
of `../README-VOICE.md` on port 7873, and `page/index.html` is the voice page with the modules as its views. Its comment at
the top lists every setting of `mountPlasma` with its range, voice-ui-kit's default and its value on this page.

```js
import { mountPlasma } from "./pipecat_plasma.js";
import { TurnLabel } from "./turn_label.js";
const plasma = mountPlasma(element, { effectScale: 0.94 });   // a view with track(mediaStreamTrack), the assistant's audio
const label = TurnLabel(element2, { hue: 187 });              // a view with rtvi(name, data), every RTVI event by name
ConnectConversation({ way: "voice", phase: "#phase", views: [karaoke, plasma, label] });
```

`python server.py`, then open `http://127.0.0.1:7873/page/`, press Start, speak. Pipecat's own page is at `/client/`.
