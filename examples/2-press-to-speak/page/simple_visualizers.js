// A simple bar visualizer of the assistant's voice, written here with no library, as a view of ConnectConversation:
//
//   import { Bars } from "./simple_visualizers.js";
//   ConnectConversation({ way: "press", views: [Bars(element)] });   // takes track() and phase()
//
// The bars are the frequency bands of the assistant's audio (track), in the phase's colour (phase). The press-to-speak and
// Pipecat voice mounts both give the track, so it runs on either.

const PHASE_COLOURS = { listening: "#44cc99", thinking: "#ffcc66", speaking: "#99aadd" };   // the colour of each phase
const IDLE_COLOUR = "#556070";                                                               // before the conversation starts

export function Bars(element, { count = 15 } = {}) {
  const canvas = document.createElement("canvas");
  canvas.style.cssText = "width:100%;height:100%;display:block";
  element.append(canvas);
  const bands = new Uint8Array(128);
  let analyser = null, colour = IDLE_COLOUR;
  (function frame() {                                // every frame: the canvas follows its box, then the bars are drawn
    requestAnimationFrame(frame);
    const width = canvas.clientWidth, height = canvas.clientHeight;
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
    const pen = canvas.getContext("2d");
    pen.clearRect(0, 0, width, height);
    if (!analyser) return;
    analyser.getByteFrequencyData(bands);
    const per = Math.floor(bands.length / 2 / count), slot = width / count;   // the lower half of the spectrum, where the voice is
    pen.fillStyle = colour;
    for (let i = 0; i < count; i++) {
      let sum = 0; for (let j = 0; j < per; j++) sum += bands[i * per + j];
      const bar = Math.max(6, (sum / per / 255) * height * 0.9);
      pen.fillRect(i * slot + slot * 0.2, (height - bar) / 2, slot * 0.6, bar);
    }
  })();
  return {
    track: (track) => {                              // the assistant's audio, measured on an analyser of its own
      const context = new AudioContext();
      analyser = context.createAnalyser(); analyser.fftSize = 256; analyser.smoothingTimeConstant = 0.6;
      context.createMediaStreamSource(new MediaStream([track])).connect(analyser);
    },
    phase: (phase) => { colour = PHASE_COLOURS[phase] || IDLE_COLOUR; },
  };
}
