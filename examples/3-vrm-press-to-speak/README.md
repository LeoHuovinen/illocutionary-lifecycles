# A VRM character over press-to-speak

A VRM character, filling the page, over IL's press-to-speak mount: hold the button
to speak, no Pipecat. `examples/5-vrm-pipecat` is the same page over the Pipecat voice mount; the two differ only in the
mount, the Talk button and the port. Read the main `README.md` at the top of the repository and `../README-PRESS.md` first.

## Downloading models

The page's menu lists only the models whose file is in `page/vrm/`. Download all three, from this folder:

```bash
mkdir -p page/vrm && cd page/vrm
curl -fL https://raw.githubusercontent.com/semperai/amica/master/public/vrm/AvatarSample_B.vrm -o AvatarSample_A.vrm
curl -fL https://raw.githubusercontent.com/semperai/amica/master/public/vrm/AvatarSample_C.vrm -o AvatarSample_B.vrm
curl -fL https://raw.githubusercontent.com/semperai/amica/master/public/vrm/AvatarSample_D.vrm -o AvatarSample_C.vrm
```

They are VRoid Project's sample avatars AvatarSample_A, B and C (about 15 MB each); each model's own licence data lets
anyone use, change and pass it on, with no credit. Amica's file names are shifted by one, hence the renaming: Amica's
`AvatarSample_A.vrm` is another model whose licence forbids passing it on, so it is not listed. Any other `.vrm` works too:
add it to `VRM_MODELS` in `page/pipecat_vrm.js`. The repository's `.gitignore` keeps `page/vrm/` out of it; with nothing
downloaded, the page says "No model: download one, see README.md".

## The files

- `page/pipecat_vrm.js`: the character as a view, `mountVrm(element)` with `level()`, `phase()`, `botMessage()` and
  `adapterCallback()`. Its scene is a VRM panel: the camera on the head, lights, the
  mouth on the assistant's audio level. Added: the model menu over `vrm/` and the warning.
- `flow.json` is the Pizza-or-burger flow with a "motion" incremental phrase instance on every step. While the user is
  still speaking, the incremental analyzer picks one of its option words (`nod`, `shake_head`, `look_left`, `look_right`,
  `look_center`, `close_eyes` or `none`) from the speech so far, and `adapterCallback()` makes the character do it, so
  "nod at me" makes it nod before the turn ends. The instance is the `incremental_phrase_instances` entry of each step.
- `page/vrm_motion.js`: the movements: arms down, idle head drift, the head tilt while
  listening, bobs and glances on punctuation while speaking, blinks, eye contact, breathing, the mouth's shape, nods.
- `page/vrm.js`: three.js and @pixiv/three-vrm (both MIT) bundled as one module, so the page needs no CDN.
- `page/ConnectConversation.js`, `page/PressToSpeakAdapterWebsocketMount.js`, `page/log.js`: IL's browser scripts.
- `page/index.html`: the page, the character filling it.
- `server.py`: the press-to-speak server of `../README-PRESS.md` on port 7871.

```js
import { mountVrm } from "./pipecat_vrm.js";
const vrm = mountVrm(document.getElementById("stage"));
document.getElementById("start").onclick = () => ConnectConversation({ way: "press", talk: "#talk", clickTalk: "#click-talk", phase: "#phase", views: [karaoke, vrm, label] });
```

The page also shows the karaoke (`page/karaoke.js`) and the turn-state word (`page/turn_label.js`), as the other speech
examples do.

`python server.py`, open `http://127.0.0.1:7871/page/`, pick a model, press Start, hold Hold to speak while you speak (or
click Click to speak, speak, and click it again).
