// LiveKit Agents UI's bar visualizer (its connecting, listening and thinking sequences; the heights from the assistant's audio),
// as a view of ConnectConversation a plain page mounts. Built into ../page/livekit_bars.js:
//   npx vite build --config vite.livekit_bars.config.mjs      (with react, react-dom, vite and @vitejs/plugin-react installed)
//
//   import { mountLiveKitBars } from "./livekit_bars.js";
//   ConnectConversation({ way: "press", views: [mountLiveKitBars(element)] });   // takes phase() and track()
//
// The original: https://github.com/livekit/components-js/blob/main/packages/shadcn/components/agents-ui/agent-audio-visualizer-bar.tsx
// (Apache-2.0: livekit/LICENSE and livekit/NOTICE here). livekit/BarsPort.jsx is a port of it.
import React, { useSyncExternalStore } from "react";
import { createRoot } from "react-dom/client";
import LiveKitBars from "./livekit/BarsPort.jsx";

const css = `.livekit-bars .panel{display:contents} .livekit-bars .panel h2,.livekit-bars .muted{display:none}
.livekit-bars .bars{display:flex;align-items:center;justify-content:center;gap:6px;height:140px}
.livekit-bars .bars span{width:10px;min-height:8px;border-radius:5px;background:#2b3245;transition:height .08s linear}
.livekit-bars .bars span[data-hi="true"]{background:#5ad1c0}`;

export function mountLiveKitBars(element) {
  if (!document.getElementById("livekit-bars-css")) document.head.append(Object.assign(document.createElement("style"), { id: "livekit-bars-css", textContent: css }));
  let state = { phase: "idle", track: null };
  const listeners = new Set();
  const store = { subscribe: (fn) => { listeners.add(fn); return () => listeners.delete(fn); }, get: () => state };
  const set = (change) => { state = { ...state, ...change }; listeners.forEach((fn) => fn()); };
  function Bars() { const v = useSyncExternalStore(store.subscribe, store.get); return <div className="livekit-bars"><LiveKitBars phase={v.phase} track={v.track} /></div>; }
  createRoot(element).render(<Bars />);
  return { phase: (phase) => set({ phase }), track: (track) => set({ track }) };
}
