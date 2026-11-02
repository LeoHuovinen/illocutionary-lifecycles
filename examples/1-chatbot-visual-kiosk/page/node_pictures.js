// The choices view: a small chatbot of its own, in a brand theme. The assistant's line as a chat bubble, the current node's
// choices as picture cards in one flex row (any number of them, or the node's own single picture when it has no
// choices), and the person's answer as a reply bubble; the chosen card lights up and the others step back.
// Styled with daisyUI (vendor/daisyui-*.full.min.css), an existing component library: chat bubbles, cards and ready
// colour themes (cupcake, bumblebee, valentine, ...), switched from the view's own theme menu. It renders inside a
// shadow root, so the library's styles reach this view and nothing else on the page.
//
//   import { NodePictures } from "./node_pictures.js";
//   const pictures = await NodePictures(element, { design, pictures, theme: "cupcake" });   // design: the loaded export; pictures: the rows described in index.html
//   ConnectConversation({ way: "press", views: [pictures] });   // start(), adapterCallback(), botMessage(), userMessage()
//
// A card lights while the conversation is still on its step: the moment the person's final words name exactly one of the
// step's choices, before the answer arrives; the answer event then confirms it, or moves it to the card the answer
// names. When the conversation moves on, the chosen card goes to the small "last choice" picture above.
//
// A full example of your own page/design.json, with the fields read here:
//   {
//     "title": "My conversation",
//     "nodes": [
//       { "id": "opening-node", "type": "start", "data": {} },
//       { "id": "ask-which-one", "type": "step", "data": { "questions": [
//         { "text": "Which one?", "options": ["First choice", "Second choice"] }
//       ] } },
//       { "id": "ask-why-that-one", "type": "step", "data": { "questions": [
//         { "text": "Why that one?", "options": [] }
//       ] } },
//       { "id": "say-goodbye", "type": "step", "data": { "questions": [] } },
//       { "id": "closing-node", "type": "end", "data": {} }
//     ],
//     "edges": [
//       { "source": "opening-node", "target": "ask-which-one" },
//       { "source": "ask-which-one", "target": "ask-why-that-one" },
//       { "source": "ask-why-that-one", "target": "say-goodbye" },
//       { "source": "say-goodbye", "target": "closing-node" }
//     ]
//   }
//
// Your pictures go in page/img/:
//   page/img/first-choice.jpg
//   page/img/second-choice.jpg
//   page/img/any-image-for-the-question-without-options.jpg
//
// In page/index.html the NodePictures call then has:
//   pictures: {
//     "First choice": "img/first-choice.jpg",                                     // the left side is the option's text
//     "Second choice": "img/second-choice.jpg",                                   // the left side is the option's text
//     "ask-why-that-one": "img/any-image-for-the-question-without-options.jpg",   // the left side is the node's id
//   },
//
// Your own flow.json, whose ConversationStates match these nodes, replaces flow.json beside server.py.
//
// What the person talking to the assistant sees on this page, and when.
//
// When the person presses Start, the conversation is on ConversationStates "0", ask-which-one.
//   Shown    two images, first-choice.jpg above the words "First choice" and second-choice.jpg above the words "Second choice".
//   Why      the question has two fixed options, so the person sees what they can pick.
//   Until    the person says one. That image lights up and the other fades. When the conversation moves on, the chosen
//            image goes to the small "last choice" picture at the top.
//
// Next, the conversation is on ConversationStates "1", ask-why-that-one.
//   Shown    one large image, any-image-for-the-question-without-options.jpg, with no words under it.
//   Why      the question has no fixed options, so there is nothing to pick from, and this one image is shown instead.
//   Until    the question is answered and the conversation moves on. Without its line in pictures, no image is shown here.
//
// Next, the conversation is on ConversationStates "2", say-goodbye, then ConversationStates "3", closing-node.
//   Shown    no new image, only the assistant's words in the chat bubble.
//   Why      neither has options or a line in pictures.

const DAISY = new URL("./vendor/daisyui-4.12.24.full.min.css", import.meta.url).href;
const THEMES = ["cupcake", "bumblebee", "valentine", "lemonade", "garden", "retro", "pastel", "fantasy"];
const css = `
:host{all:initial}
.shell{position:absolute;inset:0;display:flex;flex-direction:column;container-type:size;font-family:ui-rounded,"Nunito","Quicksand",system-ui,sans-serif;
  background:radial-gradient(circle at 1px 1px,oklch(var(--p)/.18) 1.5px,transparent 0) 0 0/18px 18px,oklch(var(--b2));color:oklch(var(--bc))}
.bar{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:30px 12px 8px;background:oklch(var(--p));color:oklch(var(--pc));box-shadow:0 2px 10px oklch(var(--p)/.35)}
.bar .title{font-weight:800;font-size:clamp(13px,4.5cqw,20px);letter-spacing:.01em}
.bar select{font:inherit;font-size:12px;border-radius:999px;border:0;padding:3px 10px;background:oklch(var(--pc)/.2);color:inherit}
.last{display:flex;align-items:center;gap:8px;padding:6px 12px 0;min-height:0;height:15cqh;visibility:hidden}
.last.on{visibility:visible;animation:pop .4s cubic-bezier(.2,.9,.3,1.3) both}
.last img{height:100%;aspect-ratio:1;object-fit:cover;border-radius:12px;border:3px solid oklch(var(--p));box-shadow:0 4px 12px oklch(var(--p)/.35)}
.last .what{font-weight:800;font-size:clamp(11px,3.4cqw,15px)} .last .what small{display:block;font-weight:600;opacity:.65}
.talk{flex:1 1 0;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:6px;padding:8px 10px 56px}
.chat-bubble{font-size:clamp(12px,3.6cqw,16px)}
.you-row{visibility:hidden} .you-row.on{visibility:visible;animation:pop .35s cubic-bezier(.2,.9,.3,1.3) both}
.np{flex:1 1 0;min-height:0;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;align-content:center;gap:3cqmin}
.card{flex:1 1 0;min-width:min(110px,38cqw);max-width:min(240px,70cqw);height:min(100%,70cqh);display:flex;flex-direction:column;overflow:hidden;
  border-radius:var(--rounded-box,1rem);background:oklch(var(--b1));box-shadow:0 6px 18px oklch(var(--bc)/.15);border:3px solid transparent;
  transition:transform .35s cubic-bezier(.2,.9,.3,1.3),opacity .35s,border-color .35s,box-shadow .35s;animation:pop .45s cubic-bezier(.2,.9,.3,1.3) both}
.card.solo{max-width:min(340px,80cqw)}
.pic{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center;background:oklch(var(--b3))}
.pic img{width:100%;height:100%;object-fit:cover}
.name{padding:6px 8px 8px;text-align:center;font-weight:800;font-size:clamp(12px,3.6cqmin,19px);color:oklch(var(--bc))}
.card.chosen{transform:scale(1.07);border-color:oklch(var(--p));box-shadow:0 0 0 4px oklch(var(--p)/.3),0 10px 30px oklch(var(--p)/.45);animation:pop .45s both,pick .9s ease-in-out 1}
.card.chosen .name{background:oklch(var(--p));color:oklch(var(--pc))}
.card.faded{opacity:.4;transform:scale(.93);filter:grayscale(.6)}
@keyframes pop{from{opacity:0;transform:translateY(14px) scale(.85)}to{opacity:1;transform:none}}
@keyframes pick{0%,100%{transform:scale(1.07)}40%{transform:scale(1.15) rotate(-2deg)}70%{transform:scale(1.04) rotate(1deg)}}`;

const json = async (x) => (typeof x === "string" ? (await fetch(x)).json() : x || {});
const el = (tag, cls, text) => Object.assign(document.createElement(tag), cls ? { className: cls } : {}, text != null ? { textContent: text } : {});

export async function NodePictures(element, { design, pictures, theme = "cupcake" } = {}) {
  const d = await json(design), pics = await json(pictures);
  const host = el("div"); host.style.cssText = "position:absolute;inset:0;z-index:0";
  element.prepend(host);
  const root = host.attachShadow({ mode: "open" });
  root.append(Object.assign(document.createElement("link"), { rel: "stylesheet", href: DAISY }), el("style", null, css));
  const shell = el("div", "shell"); shell.dataset.theme = theme;
  const bar = el("div", "bar"), select = el("select");
  select.append(Object.assign(el("option", null, "Select theme"), { value: "", selected: true, disabled: true }));
  for (const t of THEMES) select.append(Object.assign(el("option", null, t), { value: t }));
  select.onchange = () => { if (select.value) shell.dataset.theme = select.value; };
  bar.append(el("span", "title", d.title || "Your chatbot"), select);
  const talk = el("div", "talk");
  const botRow = el("div", "chat chat-start"), bot = el("div", "chat-bubble");
  const box = el("div", "np");
  const youRow = el("div", "chat chat-end you-row"), you = el("div", "chat-bubble chat-bubble-primary");
  botRow.append(bot); youRow.append(you); talk.append(box, botRow, youRow);   // the choices above, the chat below them
  const last = el("div", "last"), lastImg = el("img"), lastWhat = el("div", "what");
  last.append(lastImg, lastWhat);
  shell.append(bar, last, talk); root.append(shell);

  const start = d.nodes.find((n) => n.type === "start")?.id;
  const first = d.edges.find((e) => e.source === start)?.target;
  const states = d.nodes.filter((n) => n.type === "step" || n.type === "end");
  const order = [...states.filter((n) => n.id === first), ...states.filter((n) => n.id !== first)];

  const card = (name, picture, delay, solo) => {
    const c = el("div", "card" + (solo ? " solo" : "")); c.dataset.name = name.toLowerCase(); c.style.animationDelay = `${delay}ms`;
    const pic = el("div", "pic");
    if (picture) pic.append(Object.assign(el("img"), { src: picture, alt: name }));
    c.append(pic); if (name) c.append(el("div", "name", name));
    return c;
  };
  const show = (node) => {
    box.replaceChildren(); youRow.classList.remove("on");
    if (!node) return;
    bot.textContent = ""; botRow.style.visibility = "hidden";   // only what the assistant actually says on this node fills it
    const options = (node.data?.questions || []).flatMap((x) => (x.options || []).filter((o) => (o || "").trim()));
    if (options.length) options.forEach((o, i) => box.append(card(o, pics[o] ?? pics[o.toLowerCase()], i * 90, false)));
    else if (pics[node.id]) box.append(card("", pics[node.id], 0, true));   // a node with no choices: its own one picture
  };
  const choose = (name) => {
    const chosen = String(name).toLowerCase(), cards = [...box.querySelectorAll(".card")];
    if (!cards.some((c) => c.dataset.name === chosen)) return;
    for (const c of cards) { c.classList.toggle("chosen", c.dataset.name === chosen); c.classList.toggle("faded", c.dataset.name !== chosen); }
    you.textContent = cards.find((c) => c.dataset.name === chosen).querySelector(".name")?.textContent || String(name); youRow.classList.add("on");
  };
  // Moving on: the chosen card becomes the small "last choice" picture, then the next node shows.
  const moveOn = (node) => {
    const c = box.querySelector(".card.chosen");
    if (c) { lastImg.src = c.querySelector("img")?.src || ""; lastImg.style.display = lastImg.src ? "" : "none"; lastWhat.innerHTML = ""; lastWhat.append(el("small", null, "last choice"), document.createTextNode(c.querySelector(".name")?.textContent || "")); last.classList.remove("on"); void last.offsetWidth; last.classList.add("on"); }
    show(node);
  };

  return {
    start: () => show(order[0]),
    adapterCallback(e) {
      if (e.type === "ConversationStateChangedAdapterCallbackHandlerEvent") moveOn(order[e.conversation_state]);
      if (e.type === "QuestionAnsweredAdapterCallbackHandlerEvent" && e.choice) choose(e.choice);
    },
    botMessage(t) {                                        // the assistant's words as they are spoken, on the node now shown
      if (!t) return;
      bot.textContent = bot.textContent ? `${bot.textContent} ${t}` : t; botRow.style.visibility = "visible";
    },
    userMessage(t) {                                       // the person named exactly one option: light it now
      const names = [...box.querySelectorAll(".card")].map((c) => c.dataset.name).filter(Boolean);
      const said = names.filter((n) => new RegExp(`\\b${n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(t));
      if (said.length === 1) choose(said[0]);
    },
  };
}
