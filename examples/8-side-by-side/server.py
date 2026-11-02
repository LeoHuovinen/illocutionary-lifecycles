"""Example pages shown side by side on port 7880 over one conversation, listed in ``PAGES`` and served by
``ServeSideBySide`` from ``side_by_side.py`` beside this file.

The package runs a conversation between a user and a language model from a flow, and this file, outside the package,
shows several example pages joined to one session of it, using only the package's folder ``server``, the one of its four folders beside ``core``, ``analyzers`` and
``memory`` that a program outside it speaks to, through the mount
that ``side_by_side.py`` chooses. A page may be edited as long as it uses ``ConnectConversation.js``. The text mount is
chosen when every page can use it, else the press-to-speak mount, else the Pipecat voice mount, and press-to-speak pages
and Pipecat pages never run together, in which case the run stops and names each example's version on the other mount.
"""
from side_by_side import ServeSideBySide

PAGES = [                                        # the pages to show, left to right
    "../5-vrm-pipecat/page/index.html",
    "../7-plasma-visualizer-pipecat/page/index.html",
]
LAYOUT = "auto"                                  # "side by side", "stacked" (one under another), or "auto": stacked on a narrow screen
ServeSideBySide(PAGES, flow="../5-vrm-pipecat/flow.json", port=7880, layout=LAYOUT)   # flow: the conversation they all show
