# A Rive character that speaks

A character drawn by the Rive web runtime, its mouth following the assistant's voice, filling the page. The conversation runs on
the press-to-speak mount of `../README-PRESS.md` (hold a button to speak, no Pipecat), because the character needs only the
assistant's audio level. Read the main `README.md` at the top of the repository and `../README-PRESS.md` first; this file adds the character.

Needs: everything the press-to-speak page needs, the files under `page/` (`pipecat_rive.js`, `vendor/rive-2.44.2.wasm`,
IL's browser scripts), and one or more characters downloaded into `page/rive/`. No character is shipped here.

## Downloading characters

The page's menu lists only the characters whose file is in `page/rive/`. Download all of them, from this folder:

```bash
mkdir -p page/rive && cd page/rive
for f in 28789-54540-lion-lip-sync-system.riv 21097-39950-custom-talking-avatar-real-time-lip-sync-for-your-app.riv \
         28687-54254-lip-syncvisemes.riv 25582-47749-gargoyle-avatar.riv \
         24791-46343-lip-syncing-bald-female-character.riv 26373-49354-talk-for-video-call.riv 27757-52432-character-talking.riv \
         20725-39009-bone-based-lipsync-character-animation.riv 28218-53312-dim-sum-talking.riv 24941-46557-expression-grid.riv \
         28375-53657-old-man-character-animation-or-rive-interactive-v02.riv 28761-54484-sobo.riv 19679-37036-cursor-following-head.riv \
         13204-24955-voice-activation-maybe.riv 5628-11215-wave-hear-and-talk.riv \
         18971-35688-female-wave-hear-and-talk.riv 23033-43063-talking-bear.riv 9940-18945-speaking-bear.riv 6408-12409-speaking.riv \
         4532-9211-character-face-animation.riv 8078-15527-face-speakmute.riv \
         25311-47232-expressive-floating-character-rig-old-work-share.riv \
         5023-10162-mouth-movement.riv 12148-23106-wufwuf.riv; do
  curl -fLO "https://public.rive.app/community/runtime-files/$f"
done
```

Or only the ones you want: each is `curl -fLO <address>` inside `page/rive/`. The
whole list, with each character's mouth binding, is `source/riveModels.js`; the repository's `.gitignore` keeps what you
download out of it. With nothing downloaded, the page says so: "No character: download one, see README.md".

The page looks for the files when it runs, so a download shows up on the next reload; nothing is rebuilt. It looks only for
the file names in `source/riveModels.js`, exactly as written there (the commands above keep them). For each listed name
not downloaded, the browser console shows one "404 (Not Found)" line: that is the page checking which ones are there.

A character of your own, or one saved under another name, needs its own entry in `source/riveModels.js` (its `file` name
in `page/rive/` and its mouth binding, as the entries there show) and then the rebuild described under "The runtime, and
the wrapper"; without an entry it is not in the menu, and the page has no way to move its mouth.

| Character | By | File |
|---|---|---|
| Lion | stvfunm | `28789-54540-lion-lip-sync-system.riv` |
| Custom Talking Avatar | stvfunm | `21097-39950-custom-talking-avatar-real-time-lip-sync-for-your-app.riv` |
| Lip Sync/Visemes (monster) | ElmerVergara | `28687-54254-lip-syncvisemes.riv` |
| Gargoyle | malchemist | `25582-47749-gargoyle-avatar.riv` |
| Bald woman | stvfunm | `24791-46343-lip-syncing-bald-female-character.riv` |
| Talk for video call | saurs_ | `26373-49354-talk-for-video-call.riv` |
| Character Talking | interactiver | `27757-52432-character-talking.riv` |
| Bone-based coach | HaiDo | `20725-39009-bone-based-lipsync-character-animation.riv` |
| Dim Sum (face) | Julia.fer.surrealm | `28218-53312-dim-sum-talking.riv` |
| Expression Grid (mouth) | erdemediz | `24941-46557-expression-grid.riv` |
| Old man | ar.akash | `28375-53657-old-man-character-animation-or-rive-interactive-v02.riv` |
| Sobo | Patgrivet | `28761-54484-sobo.riv` |
| Cursor-following head | info-WP6YK | `19679-37036-cursor-following-head.riv` |
| Voice activation girl | zentrie101 | `13204-24955-voice-activation-maybe.riv` |
| Wave, hear and talk (bear) | japarj | `5628-11215-wave-hear-and-talk.riv` |
| Female bear | nelsons | `18971-35688-female-wave-hear-and-talk.riv` |
| Talking bear | majid.entysquare | `23033-43063-talking-bear.riv` |
| Speaking bear | xiaoshayu1001 | `9940-18945-speaking-bear.riv` |
| Teddy (Login Machine) | develophasan | `6408-12409-speaking.riv` |
| Bearded face | ak2665622 | `4532-9211-character-face-animation.riv` |
| Face speak/mute | krdsabdllh53 | `8078-15527-face-speakmute.riv` |
| Floating rig | kouidero | `25311-47232-expressive-floating-character-rig-old-work-share.riv` |
| Mouth movement (lips) | alexiusnwala | `5023-10162-mouth-movement.riv` |
| WufWuf | shabrinashaliha95 | `12148-23106-wufwuf.riv` |

Licences: the community files (`public.rive.app`) are CC BY 4.0, the author in the "By" column.

## The runtime, and the wrapper

The Rive web runtime is `@rive-app/webgl2` (MIT); its source and README are at
`https://github.com/rive-app/rive-wasm/tree/master/js`. `page/pipecat_rive.js` is the wrapper built over that runtime,
from `source/rive.js` and `source/riveModels.js` (`npx vite build --config vite.rive.config.mjs` in `source/`, with
`@rive-app/webgl2` and `vite` installed; built with `@rive-app/webgl2` 2.44.2 and `vite` 6.3.5). The
same bundle is in `examples/6-rive-pipecat/page/`: after a rebuild, copy it there too. It points the runtime at the local `vendor/rive-2.44.2.wasm`, fills the menu with
the characters found in `rive/`, and drives each character's mouth (a number, an enum, a boolean or a trigger, named per
character) from the assistant's level. It is a view of `ConnectConversation`:

```js
import { mountRive } from "./pipecat_rive.js";
const rive = mountRive(element);                   // the menu of the characters in rive/, the first one loaded
ConnectConversation({ way: "press", talk: "#talk", phase: "#phase", views: [rive] });   // rive.level(l), the assistant's level
```

## The server

`server.py`, the press-to-speak server of `../README-PRESS.md` on port 7876:

```python
import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount import (
    PressToSpeakAdapterWebsocketMount,
)

conversation = json.load(open("flow.json"))      # the dict with PromptBlocks and ConversationStates, used as it is

app = FastAPI()
PressToSpeakAdapterWebsocketMount(conversation, language=os.environ["SPEECH_LANGUAGE"], TTSVoice=os.environ["TTS_VOICE"]).MountOnApp(app, "/ws")
app.mount("/page", StaticFiles(directory="page", html=True))      # your page, served at /page/
uvicorn.run(app, host="127.0.0.1", port=7876, log_level="warning")
```

## The page

`page/index.html` is the press-to-speak page of `../README-PRESS.md` with the character filling the page, the karaoke
(`page/karaoke.js`) under it, and the Hold to speak and Click to speak buttons. The file is in this folder as it runs, and
its comment at the top and its rows of named settings for the karaoke's look explain it. Its one call is the following.

```js
document.getElementById("start").onclick = () => ConnectConversation({ way: "press", talk: "#talk", clickTalk: "#click-talk", phase: "#phase", views: [karaoke, rive] });
```

`python server.py`, then open `http://127.0.0.1:7876/page/`, pick a character, press Start, hold Hold to speak while you
speak (or click Click to speak, speak, and click it again). The mouth opens with the assistant's voice. `examples/6-rive-pipecat` is the same page over the Pipecat voice mount.
