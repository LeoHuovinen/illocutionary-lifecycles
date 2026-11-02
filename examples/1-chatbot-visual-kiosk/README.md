# The choices as pictures

A small chatbot in a brand theme: the assistant's line as a chat bubble, the current step's choices as picture cards, the
person's answer as a reply bubble; the chosen card lights up. It runs on the press server of `../README-PRESS.md` (hold a
button to speak, no Pipecat), because the view needs the assistant's words and the person's words as they come. Read the main `README.md` at the top of the repository
and `../README-PRESS.md` first; this file adds the view. The simplest working case is this folder.

## The four things you replace, and nothing else

| What | What it is | Where yours comes from |
|---|---|---|
| `flow.json` | the JSON object whose top-level fields are `PromptBlocks` and `ConversationStates`, which `json.load` reads into the dict `server.py` passes to the mount class as its first argument | your own version of this file, in the same form |
| `page/design.json` | the JSON object with the top-level fields `nodes`, `edges` and `title`; `NodePictures` reads each node's `data.questions[].options` from it | your own JSON file whose nodes match the `ConversationStates` of your `flow.json`, in the form shown in full at the top of `page/node_pictures.js` |
| the `pictures` rows in `page/index.html` | a name to a picture: an option's text as written in `design.json` (`"Pizza"`), or a step's node id (`"pizza"`) for a step without options | written by hand in the `NodePictures` call, one row per option or step |
| `page/img/` | the pictures | your own; this folder's four are from Wikimedia Commons, credited in the comment at the top of `page/index.html`, and replaced by yours |

The nodes of `page/design.json` must match the `ConversationStates` of `flow.json`, or the cards will not match the questions. A name missing from
the `pictures` rows gives a card with no picture, and nothing breaks. Option names are matched as written, then lower-cased.

## Where the themes come from

The look is daisyUI 4.12.24 (`page/vendor/daisyui-4.12.24.full.min.css`, an existing component library, MIT): its chat
bubbles, cards and colour themes. The view's menu offers eight of its themes, listed at the top of `node_pictures.js`
(`THEMES = ["cupcake", "bumblebee", "valentine", "lemonade", "garden", "retro", "pastel", "fantasy"]`); the stylesheet
carries all thirty-two of daisyUI's themes, so any other name from daisyUI's theme list goes into that array and works.
The starting theme is the `theme` option of `NodePictures(...)` on the page. The view renders inside a shadow root, so
the library's styles reach the view and nothing else on the page.

## The view module

```js
import { NodePictures } from "./node_pictures.js";
const pictures = await NodePictures(element, {
  design,                                          // the loaded object
  pictures: { "Pizza": "img/pizza.jpg", "Burger": "img/burger.jpg" },   // one row per picture; the page has the full list
  theme: "cupcake",
});
ConnectConversation({ way: "press", talk: "#talk", clickTalk: "#click-talk", phase: "#phase", views: [karaoke, pictures] });
// ConnectConversation calls the view's four methods
//   start()               the conversation has started on its first step
//   adapterCallback(e)    state changes move to the next step's cards, answers confirm the choice
//   botMessage(t)         the assistant's words fill its bubble
//   userMessage(t)        the user's words, a card they name lights at once
```

## The server and the page

`server.py` is the press server of `../README-PRESS.md` on port 7874, nothing added. `page/index.html` is the press page with
the view filling the page, given with the karaoke as the `views` of the one `ConnectConversation` call above; both files
are in this folder as they run. `python server.py`, then open `http://127.0.0.1:7874/page/`, press Start, then hold
Hold to speak while you speak, or click Click to speak, speak, and click it again. Every mount gives a view these four methods, so the same view runs on the
voice server of `../README-VOICE.md` once the page's `way` is "voice" and its two buttons are taken out. On the text server
the page would also need an input to type into, since it has none.
