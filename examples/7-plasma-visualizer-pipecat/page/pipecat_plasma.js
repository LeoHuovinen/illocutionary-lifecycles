// Pipecat's Plasma visualizer from voice-ui-kit, for a plain page.
//
//   import { mountPlasma } from "./pipecat_plasma.js";
//   const plasma = mountPlasma(element, { effectScale: 0.94 });
//   views: [plasma]     // in ConnectConversation, plasma.track() gets the assistant's audio

import React from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client?deps=react@18.3.1";
import { Plasma } from "https://esm.sh/@pipecat-ai/voice-ui-kit@0.14.1/webgl?deps=react@18.3.1,react-dom@18.3.1";

const SETTINGS = {
  backgroundColor: "#1f2937",
  ringBounce: 0.2,
  ringAmplitude: 0.075,
  ringThicknessAudio: 7.5,
  audioSensitivity: 0.9,
  plasmaVolumeReactivity: 0.9,
  effectScale: 0.275,
  ringDistance: 0,
  ringVariance: 0.175,
  ringVisibility: 0.6,
  ringSegments: 6,
  ringThickness: 6,
  ringSpread: 0.04,
  colorCycleSpeed: 0.25,
  intensity: 2,
  radius: 0.825,
  glowFalloff: 1,
  glowThreshold: 0,
  plasmaSpeed: 0.15,
  rayLength: 0.5,
  color1: "#00e5ff",
  color2: "#00ff9d",
  color3: "#9b7bff",
  audioEnabled: true,
};

export function mountPlasma(element, overrides = {}) {
  const root = createRoot(element);
  const config = { ...SETTINGS, ...overrides };
  let audioTrack = null, size = [element.clientWidth, element.clientHeight];
  const draw = () => root.render(React.createElement(Plasma, {
    key: size.join("x"), width: size[0], height: size[1], alpha: true, initialConfig: config, audioTrack,
  }));
  new ResizeObserver(() => {
    const now = [element.clientWidth, element.clientHeight];
    if (now[0] && now[1] && now.join() !== size.join()) { size = now; draw(); }
  }).observe(element);
  draw();
  return { track(track) { audioTrack = track; draw(); } };
}
