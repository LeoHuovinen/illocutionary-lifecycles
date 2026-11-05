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

// One look per turn state, given to update() by RTVI_States.js. The eased settings slide to the new values, and the two
// speeds (plasmaSpeed and colorCycleSpeed) apply at once.
export const PLASMA_TURN_STATES = {
  idle:      { intensity: 1.1, radius: 0.7,  ringVisibility: 0.35, ringBounce: 0,   ringAmplitude: 0.03,  ringThickness: 4, rayLength: 0.3, plasmaSpeed: 0.1, ringSpeed: 0.8, ringVariance: 0.1,  ringSegments: 6, colorCycleSpeed: 0.15, color1: "#2a7a8a", color2: "#2a8a6a", color3: "#4a4a8a" },
  listening: { intensity: 2.3, radius: 0.95, ringVisibility: 0.85, ringBounce: 0.4, ringAmplitude: 0.1,   ringThickness: 8, rayLength: 0.5, plasmaSpeed: 0.3, ringSpeed: 1.0, ringVariance: 0.15, ringSegments: 6, colorCycleSpeed: 0.3,  color1: "#00e5ff", color2: "#00ff9d", color3: "#5ef0ff" },
  thinking:  { intensity: 1.7, radius: 0.7,  ringVisibility: 0.7,  ringBounce: 0.7, ringAmplitude: 0.06,  ringThickness: 5, rayLength: 1.2, plasmaSpeed: 1.5, ringSpeed: 3.0, ringVariance: 0.7,  ringSegments: 9, colorCycleSpeed: 1.2,  color1: "#9b7bff", color2: "#c084fc", color3: "#6366f1" },
  speaking:  { intensity: 2.4, radius: 0.85, ringVisibility: 0.75, ringBounce: 0.2, ringAmplitude: 0.075, ringThickness: 6, rayLength: 0.6, plasmaSpeed: 0.3, ringSpeed: 1.2, ringVariance: 0.2,  ringSegments: 6, colorCycleSpeed: 0.4,  color1: "#22d3ee", color2: "#34d399", color3: "#f0abfc",
               ringThicknessAudio: 9, plasmaVolumeReactivity: 2.2, audioSensitivity: 1.5 },
};

// The word's hue per turn state, for a TurnLabel beside the plasma: the hue of that state's first plasma colour.
export const PLASMA_TURN_HUES = { idle: 187, listening: 187, thinking: 270, speaking: 157 };

export function mountPlasma(element, overrides = {}) {
  const root = createRoot(element);
  const ref = React.createRef();
  const config = { ...SETTINGS, ...overrides };
  let audioTrack = null, size = [element.clientWidth, element.clientHeight];
  const draw = () => root.render(React.createElement(Plasma, {
    key: size.join("x"), width: size[0], height: size[1], alpha: true, initialConfig: config, audioTrack, ref,
  }));
  new ResizeObserver(() => {
    const now = [element.clientWidth, element.clientHeight];
    if (now[0] && now[1] && now.join() !== size.join()) { size = now; draw(); }
  }).observe(element);
  draw();
  return {
    track(track) { audioTrack = track; draw(); },
    update(settings) { Object.assign(config, settings); ref.current?.updateConfig(settings); },
  };
}
