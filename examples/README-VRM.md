# A VRM character that speaks

The environment variables are listed in the main `README.md` at the top of the repository, and the page's surface is in the header of `ConnectConversation.js`. The press-to-speak server is in `README-PRESS.md` and the Pipecat voice server in `README-VOICE.md`. This file adds a VRM character whose mouth moves with the assistant's voice, on either mount. The working cases of exactly this are two folders: `examples/3-vrm-press-to-speak/` (hold a button to speak, no Pipecat, port 7871) and `examples/5-vrm-pipecat/` (the pause ends the turn, port 7877). The two differ only in the server's mount, the page's `way` and talk buttons, and the port. `examples/9-vrm-webxr-pipecat/` (port 7882) is a VRM character over Pipecat in a VR headset.

Needs: everything the press-to-speak page needs (`README-PRESS.md`) or everything the Pipecat voice page needs (`README-VOICE.md`), and at least one `.vrm` file in `page/vrm/`. Each example's own `README.md` gives the download of VRoid Project's three sample avatars; VRoid Studio (`https://vroid.com/en/studio`) exports your own, and VRoid Hub (`https://hub.vroid.com/en`) has ones other people made, each under the conditions on its page. No model is included here.

## The server

Exactly the press-to-speak server of `README-PRESS.md` or the Pipecat voice server of `README-VOICE.md`, with the voice you want. Nothing in the server is about VRM: the character lives entirely on the page. `examples/3-vrm-press-to-speak/server.py` and `examples/5-vrm-pipecat/server.py` are the two, reading the voice from `TTS_VOICE`.

## The page, from the examples

The quickest way is the examples' own view, `pipecat_vrm.js`: a character as one view, with a menu of the
models in `vrm/` beside the page and a warning when there is none. Copy into your `page/` folder, from
`examples/3-vrm-press-to-speak/page/` (press-to-speak) or `examples/5-vrm-pipecat/page/` (Pipecat voice):
`pipecat_vrm.js`, `vrm_motion.js`, `ConnectConversation.js`, `log.js`, and the mount's script
(`PressToSpeakAdapterWebsocketMount.js`, or `PipecatVoiceAdapterWebRtcMount.js` with `pipecat-client.js`). Then:

```html
<div id="stage" style="position:absolute;inset:0"></div>
<div style="position:absolute;top:8px;left:8px;z-index:5">   <!-- above the character, or its canvas takes the clicks -->
  <button id="start">Start</button> <button id="talk">Hold to speak</button> <span id="phase">not connected</span>
</div>
<script type="module">
  import "./log.js";
  import { ConnectConversation } from "./ConnectConversation.js";
  import { mountVrm } from "./pipecat_vrm.js";            // a view with level(), phase(), botMessage(): the character
  const vrm = mountVrm(document.getElementById("stage"));
  document.getElementById("start").onclick = () => ConnectConversation({ way: "press", talk: "#talk", phase: "#phase", views: [vrm] });
</script>
```

For the Pipecat voice mount, `way: "voice"` and no talk button. A model not among VRoid's three samples gets an entry in
`VRM_MODELS` in `pipecat_vrm.js`, with its file name in `vrm/`, its display name, its download address and its author.

## The page, from three-vrm's own

Or write `page/index.html` from three-vrm's own page, not copied here: from "How to Use, from HTML" in three-vrm's README,
`https://github.com/pixiv/three-vrm/blob/release/README.md`, and its example page
`https://github.com/pixiv/three-vrm/blob/release/packages/three-vrm/examples/basic.html`, filling the "..." the way
three.js's first page does, `https://github.com/mrdoob/three.js/blob/r180/manual/en/creating-a-scene.html`. Then make
these changes:

1. **The import.** Their import map and two imports (`three`, `@pixiv/three-vrm`) become the three import lines at the
   top of `pipecat_vrm.js`, which take three.js r180, its `GLTFLoader` and three-vrm 3.5.5 from esm.sh, with
   `?deps=three@0.180.0` so that three-vrm uses the same three.js. No import map on the page.
2. **The conversation.** Copy `ConnectConversation.js`, `log.js` and the mount's script beside the page as above, and add
   `import { ConnectConversation } from "./ConnectConversation.js";`, a `<button id="start">Start</button>`, for
   press-to-speak a `<button id="talk">Hold to speak</button>`, and a `<span id="phase">not connected</span>`. On the
   Start click, `ConnectConversation({ way: "press", talk: "#talk", phase: "#phase", views: [{ level: (l) => { level = l; } }] })`,
   or `way: "voice"` with no `talk` for the Pipecat voice mount. The script wires the button itself: "Loading…" until the
   assistant's opening has been spoken, recording only while it is held.
3. **The mouth.** Keep a `let level = 0;` and, in their render loop before `vrm.update(dt)`, add
   `vrm?.expressionManager?.setValue("aa", level);`. After their loader sets `vrm`, also call `VRMUtils.rotateVRM0(vrm)`
   so a VRM 0.x model faces the camera.

Point their loader at your model's file, for example `vrm/AvatarSample_A.vrm` after the download in an example's README.

`python server.py`, then open `http://127.0.0.1:7871/page/` (press-to-speak) or `http://127.0.0.1:7877/page/` (Pipecat
voice), press Start, and speak: on press-to-speak hold the button while you speak. The character's mouth opens with the
assistant's voice either way.

A page's `way` must match the server's mount; `expect: "press"` or `expect: "voice"` among the options makes the console
warn when the page names another way.

How it works. The mouth is driven by the assistant's audio level, which the `level` view method receives between 0 and 1 many times a second on both mounts, and three-vrm's `aa` expression takes exactly such a number; `vrm.update(dt)` every frame is what makes the expression show, and `VRMUtils.rotateVRM0` turns a VRM 0.x model to face the camera. Everything else on the page is three.js's and three-vrm's, so a later version of either is copied the same way: their page, the import lines, the conversation.

## Printing and logging what happens

The server runs without any of this. The log stream is the mount's own: every recorded event (the save of the cards,
with `turns`, `streams` and `prompt`, marked `"log": "event"`) and every adapter callback (a state change, an answered
question, an incremental phrase pick, marked `"log": "adapter callback"`), two different things, one
JSON line each. On the text and press mounts the lines arrive on the connection's own socket, each marked `log`; on the
voice mount they are sent over WebRTC as RTVI server messages marked `log`. Every example page carries
one row, which prints the stream in the browser console and puts nothing on the page:

```js
  import "./log.js";                               // the log stream, in the browser console: recorded events and adapter callbacks
```

On the server, a handler of your own for the adapter callbacks is still one argument of the mount, `OnAdapterCallback`,
a plain function or an `async` one of the callback dict.

## Offline use

The page needs esm.sh when it opens, because `pipecat_vrm.js` imports three.js and three-vrm from there; the model is a file beside the page. A page written from three-vrm's README with its jsDelivr import map needs jsDelivr in the same way; the only change for the conversation is then the `ConnectConversation` import, the `level` view and, for press-to-speak, the button.
