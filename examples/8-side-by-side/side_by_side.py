"""``ServeSideBySide``, which serves several example pages side by side on one port over one conversation, on the
lowest mount that serves them all.

The package runs a conversation between a user and a language model from a flow, and this module, outside the package,
uses only its folder ``server``, the one of its four folders beside ``core``, ``analyzers`` and ``memory`` that a
program outside it speaks to, through one of the three mounts in
``illocutionary_lifecycles.server.adapter_mounts``. Each page names its way to ``ConnectConversation.js``, "text",
"press" or "voice", and each mount gives a page everything the one before it gives, so the text mount is chosen when
every page can use it, else the press-to-speak mount, else the Pipecat voice mount. The press-to-speak and voice mounts
never run together, because the one ends a turn when the button is let go and the other when the person pauses, so a
page made for one would behave wrongly on the other, and pages that need both stop with an error naming each example's
version on the other mount where one exists. Each page's own folder is served as it is at the path /page/frame-N/, and
this folder's page at /page/ shows them side by side, holding the one connection that each page's
``ConnectConversation.js`` joins.
"""
import json
import os
import re

from fastapi.staticfiles import StaticFiles

ORDER = ["text", "press", "voice"]
MOUNT_NAMES = {"text": "the text mount", "press": "the press-to-speak mount", "voice": "the Pipecat voice mount"}


def NeededWay(page: str) -> str:
    """Return the highest way the page file ``page`` asks for, "text", "press" or "voice", read from the way it gives
    ``ConnectConversation``, or "text" when it names none, as ``ConnectConversation.js`` does. Called by
    ``ServeSideBySide`` in this module."""
    asked = re.findall(r'way:\s*"(text|press|voice)"', open(page, encoding="utf-8").read())
    return max(asked, key=ORDER.index) if asked else "text"


def OtherMountVersion(page: str) -> str | None:
    """Return the path of the same page in the example folder for the other speech mount, or ``None`` when the examples
    folder has none, such as 5-vrm-pipecat for 3-vrm-press-to-speak and 6-rive-pipecat for 4-rive-press-to-speak, the
    folders being matched by their names without the leading number. Called by ``ServeSideBySide`` in this module for
    its error."""
    folder = os.path.dirname(os.path.dirname(os.path.abspath(page)))
    name = os.path.basename(folder)
    unnumbered = re.sub(r"^\d+-", "", name)
    for one, other in (("press-to-speak", "pipecat"), ("pipecat", "press-to-speak")):
        if one not in unnumbered:
            continue
        wanted = unnumbered.replace(one, other)
        for sibling in sorted(os.listdir(os.path.dirname(folder))):
            if re.sub(r"^\d+-", "", sibling) == wanted:
                return page.replace(name, sibling)
    return None


def ServeSideBySide(pages: list, flow: str | None = None, port: int = 7880, layout: str = "auto") -> None:
    """Serve the page files in ``pages`` side by side at the address of 127.0.0.1 on ``port``, path /page/, on the mount
    the module docstring above says is chosen, printing which mount each page needs, and run until stopped.

    ``flow`` is the path of the flow file, by default the ``flow.json`` of the first page's example folder. ``layout``
    is "side by side", "stacked", one page under another, or "auto", side by side on a wide screen and stacked on a narrow
    one such as a phone. The voice comes from the environment variable ``TTS_VOICE``, and the speech mounts also read
    ``SPEECH_LANGUAGE`` or ``STT_VENDOR``. Pages that need both speech
    mounts raise ``SystemExit`` with the error the module docstring above describes. Called by
    ``examples/8-side-by-side/server.py``.
    """
    ways = {page: NeededWay(page) for page in pages}
    if "press" in ways.values() and "voice" in ways.values():
        lines = ["These pages need both the press-to-speak mount and the Pipecat voice mount, which never run together:"]
        for page, asked in ways.items():
            if asked in ("press", "voice"):
                other = OtherMountVersion(page)
                lines.append(f"  {page}: needs {MOUNT_NAMES[asked]}" + (f"; its version on the other mount is {other}" if other else ""))
        lines.append("Show only pages of one of the two (text pages run beside either): swap a page for its version on the other "
                     "mount, or change its way between \"press\" and \"voice\" as those two versions differ.")
        raise SystemExit("\n".join(lines))
    way = max(ways.values(), key=ORDER.index)
    for page, asked in ways.items():
        print(f"{page}: needs {MOUNT_NAMES[asked]}")
    print(f"running {MOUNT_NAMES[way]}: every page above runs on it")
    flow = flow or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(pages[0]))), "flow.json")
    conversation = json.load(open(flow, encoding="utf-8"))
    frames = [f"/page/frame-{n}/{os.path.basename(page)}" for n, page in enumerate(pages)]

    if way == "voice":
        from dotenv import find_dotenv, load_dotenv
        from pipecat.runner.run import app

        from illocutionary_lifecycles.server.adapter_mounts.webrtc_mounts.PipecatVoiceAdapterWebRtcMount import PipecatVoiceAdapterWebRtcMount
        load_dotenv(find_dotenv(usecwd=True), override=True)      # the nearest .env: this folder, then each folder above it
        mount =PipecatVoiceAdapterWebRtcMount(conversation, STTVendor=os.environ["STT_VENDOR"], TTSVoice=os.environ["TTS_VOICE"])
        mount.MountOnApp(app)
    else:
        from fastapi import FastAPI
        app = FastAPI()
        if way == "press":
            from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.PressToSpeakAdapterWebsocketMount import PressToSpeakAdapterWebsocketMount
            PressToSpeakAdapterWebsocketMount(conversation, language=os.environ["SPEECH_LANGUAGE"], TTSVoice=os.environ["TTS_VOICE"]).MountOnApp(app, "/ws")
        else:
            from illocutionary_lifecycles.server.adapter_mounts.websocket_mounts.TextAdapterWebsocketMount import TextAdapterWebsocketMount
            TextAdapterWebsocketMount(conversation).MountOnApp(app, "/ws")

    app.get("/page/side-by-side.json")(lambda: {"way": way, "frames": frames, "layout": layout})   # the side-by-side page reads its pages here
    for n, page in enumerate(pages):                                              # each page's own folder, as it is
        app.mount(f"/page/frame-{n}", StaticFiles(directory=os.path.dirname(os.path.abspath(page)), html=True))
    app.mount("/page", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "page"), html=True))

    if way == "voice":
        mount.StartWebRtcServerProcess(mount.Attend, host="127.0.0.1", port=port)
    else:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
