// The side-by-side page's one connection, shared by every page it shows. Each shown page's ConnectConversation.js finds
// window.SideBySideConversation and joins through it instead of connecting itself: every page gets every callback of the
// one session, and its typing and its Hold to speak button drive that session.
//
//   import { ShowSideBySide } from "./side_by_side.js";
//   const sideBySide = ShowSideBySide(element, { way, frames });   // way: the mount server.py runs; frames: the pages
//   startButton.onclick = () => sideBySide.start(phaseElement);     // from a click: Safari and iOS want a gesture
const MOUNT_SCRIPTS = { text: "./TextAdapterWebsocketMount.js", press: "./PressToSpeakAdapterWebsocketMount.js", voice: "./PipecatVoiceAdapterWebRtcMount.js" };

export function ShowSideBySide(element, { way, frames }) {
  const joinedPages = new Set();                     // each shown page's callback function
  let connection = null;
  window.SideBySideConversation = {                  // what a shown page's ConnectConversation.js uses instead of its mount
    Connect(on) {
      joinedPages.add(on);
      return { sendText: (text) => connection?.sendText(text), talk: (open) => connection?.talk?.(open), close: () => joinedPages.delete(on) };
    },
  };
  const iframes = frames.map((src) => Object.assign(document.createElement("iframe"), { src, title: src }));
  for (const frame of iframes) frame.style.cssText = "border:0;width:100%;height:100%;display:block";
  for (const frame of iframes) frame.addEventListener("load", () => {   // each page's own Start is hidden: this page's Start starts them all
    const startButton = frame.contentDocument?.getElementById("start");
    if (startButton) startButton.style.display = "none";
  });
  element.replaceChildren(...iframes);
  return {
    async start(phaseElement) {
      for (const frame of iframes) {                 // each page joins as its own Start button would; then that button is spent
        const startButton = frame.contentDocument?.getElementById("start");
        if (startButton && !startButton.disabled) { startButton.click(); startButton.disabled = true; }
      }
      const mount = await import(MOUNT_SCRIPTS[way] || MOUNT_SCRIPTS.text);
      connection = await mount.Connect((name, ...args) => {
        if (name === "onPhase" && phaseElement) phaseElement.textContent = args[0];
        for (const on of joinedPages) { try { on(name, ...args); } catch (e) { console.warn(name, e); } }
      }, {});
    },
  };
}
