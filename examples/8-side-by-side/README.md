# Example pages side by side

Any example pages next to each other, on one port and over one conversation: say "nod at me" once and the VRM character
nods while Plasma draws the same voice and every page's karaoke shows the same words. The pages may be the examples as
they are or edited ones; a page only has to use `ConnectConversation.js`.

## Choosing the pages

In `server.py`, list the pages, left to right, and the conversation they all show:

```python
PAGES = [                                        # the pages to show, left to right
    "../5-vrm-pipecat/page/index.html",
    "../7-plasma-visualizer-pipecat/page/index.html",
]
LAYOUT = "auto"                                  # "side by side", "stacked" (one under another), or "auto": stacked on a narrow screen
ServeSideBySide(PAGES, flow="../5-vrm-pipecat/flow.json", port=7880, layout=LAYOUT)   # flow: the conversation they all show
```

`LAYOUT`: "side by side" puts the pages next to each other across the screen; "stacked" puts them one under another,
each most of the screen's height, and the page scrolls; "auto" is side by side on a wide screen and stacked on a narrow
one, such as a phone.

`python server.py`, open `http://127.0.0.1:7880/page/`, press Start. On start it prints which mount each page needs and
which one it runs:

```
../5-vrm-pipecat/page/index.html: needs the Pipecat voice mount
../7-plasma-visualizer-pipecat/page/index.html: needs the Pipecat voice mount
running the Pipecat voice mount: every page above runs on it
```

## Choosing the mount

Each page names its mount in its `ConnectConversation({ way: ... })`: "text", "press" (press-to-speak) or "voice" (Pipecat).
The mounts are nested, each giving a page everything the one before gives and more (the header of `ConnectConversation.js`
lists them), so `side_by_side.py` runs Pipecat if any page uses it, else press-to-speak, else text, and every page runs on it: a text page shown beside
a VRM page types into the same Pipecat session, a press-to-speak page's Hold to speak button opens the same microphone.
On the press-to-speak and Pipecat voice mounts typed text and speech are one thing: a line typed while
speaking joins the spoken turn.

Press-to-speak pages and Pipecat pages never run together: one ends a spoken turn when the button is let go, the other when
the person pauses, so a page made for one would behave wrongly on the other. Text pages run beside either. Given both, the
server stops and says which page needs which, naming the example's version on the other mount where there is one:

```
These pages need both the press-to-speak mount and the Pipecat voice mount, which never run together:
  ../3-vrm-press-to-speak/page/index.html: needs the press-to-speak mount; its version on the other mount is ../5-vrm-pipecat/page/index.html
  ../7-plasma-visualizer-pipecat/page/index.html: needs the Pipecat voice mount
Show only pages of one of the two (text pages run beside either): swap a page for its version on the other mount, or change its way between "press" and "voice" as those two versions differ.
```

## How the pages share one conversation

`page/index.html` shows each page in a frame, served from that page's own folder at `/page/frame-N/`, so each page keeps
its own files (models, pictures, view modules). The side-by-side page holds the one connection (`page/side_by_side.js`);
each page's `ConnectConversation.js` sees that it is inside it and joins that connection instead of opening its own. Start
on the side-by-side page presses each page's own Start, then connects; every page then gets every callback of the session.

## The files

- `server.py`: the pages, the conversation, the port.
- `side_by_side.py`: runs Pipecat if any page uses it, else press-to-speak, else text, and serves the pages' folders.
- `page/index.html`, `page/side_by_side.js`: the side-by-side page and its shared connection.
- `page/TextAdapterWebsocketMount.js`, `page/PressToSpeakAdapterWebsocketMount.js`, `page/PipecatVoiceAdapterWebRtcMount.js`,
  `page/pipecat-client.js`, `page/log.js`: IL's browser scripts, for whichever mount runs.
