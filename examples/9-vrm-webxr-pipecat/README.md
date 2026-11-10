# A VRM character over Pipecat, in a VR headset

A VRM character, filling the page, over IL's Pipecat voice mount: the microphone
stays open and the pause ends the turn. In a VR headset's browser, such as the Meta Quest's, the Enter VR button places
the character 1.2 m in front of the viewer. Read the main `README.md` at the top of the repository and `../README-VOICE.md` first.

## Opening it in a VR headset

The headset's browser allows the microphone and VR only for pages on HTTPS or on `127.0.0.1`. Connect the headset to the
computer by USB with developer mode on, and run `adb reverse tcp:7882 tcp:7882` on the computer. The headset's browser
then reaches the server at `http://127.0.0.1:7882/page/`. Press Start, then Enter VR. In VR only the character is shown,
because the karaoke and the turn-state word are HTML on the page, and a VR session does not show HTML.

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
  mouth on the assistant's audio level. Added: the model menu over `vrm/` and the warning. For VR it has
  three.js's `VRButton`, turns on `renderer.xr`, places the character in front of the viewer in VR, and draws through
  `renderer.setAnimationLoop`, since in VR the headset times the frames and `requestAnimationFrame` cannot.
- `flow.json` is the Pizza-or-burger flow with a "motion" incremental phrase instance on every step. While the user is
  still speaking, the incremental analyzer picks one of its option words (`nod`, `shake_head`, `look_left`, `look_right`,
  `look_center`, `close_eyes` or `none`) from the speech so far, and `adapterCallback()` makes the character do it, so
  "nod at me" makes it nod before the turn ends. The instance is the `incremental_phrase_instances` entry of each step.
- `page/vrm_motion.js`: the movements: arms down, idle head drift, the head tilt while
  listening, bobs and glances on punctuation while speaking, blinks, eye contact, breathing, the mouth's shape, nods.
- three.js r180 and @pixiv/three-vrm 3.5.5 (both MIT), which `page/pipecat_vrm.js` imports from esm.sh, so there is no bundle to rebuild.
- `page/ConnectConversation.js`, `page/PipecatVoiceAdapterWebRtcMount.js`, `page/pipecat-client.js`, `page/log.js`: IL's
  browser scripts.
- `page/index.html`: the page, the character filling it.
- `server.py`: the Pipecat voice server of `../README-VOICE.md` on port 7882.

```js
import { mountVrm } from "./pipecat_vrm.js";
const vrm = mountVrm(document.getElementById("stage"));
document.getElementById("start").onclick = () => ConnectConversation({ way: "voice", phase: "#phase", views: [karaoke, vrm, label] });
```

The page also shows the karaoke (`page/karaoke.js`) and the turn-state word (`page/turn_label.js`), as the other speech
examples do.

`python server.py`, open `http://127.0.0.1:7882/page/`, pick a model, press Start, press Enter VR, speak.
