# Press to speak

Hold a button to speak, over IL's press-to-speak mount (`../README-PRESS.md`). On one page: the assistant's voice as bars twice,
the dashboard (the step, the answers, the turns), the karaoke, and the listening / thinking / speaking word.

`python server.py`, open `http://127.0.0.1:7872/page/`, press Start, hold the button while you speak.

## The two bar visualizers

| | file | what it is |
|---|---|---|
| simple bars | `page/simple_visualizers.js` | written here, no library: the frequency bands of the assistant's audio, in the phase's colour |
| LiveKit bars | `page/livekit_bars.js`, built from `source/livekit_bars.jsx` | LiveKit Agents UI's bar visualizer with its own connecting, listening and thinking sequences; [the original](https://github.com/livekit/components-js/blob/main/packages/shadcn/components/agents-ui/agent-audio-visualizer-bar.tsx), Apache-2.0 (`source/livekit/LICENSE`, `NOTICE`) |

Both are views of `ConnectConversation`: they take the assistant's audio (`track`) and the phase (`phase`). The press-to-speak
mount hands the assistant's audio over as a track, as the Pipecat voice mount does, so both run on either.

To rebuild the LiveKit bars, in `source/` with `react`, `react-dom`, `vite` and `@vitejs/plugin-react` installed:
`npx vite build --config vite.livekit_bars.config.mjs`.

## Adding an orb

No orb is shipped; each is on GitHub. Every one is a React component, so it goes on the page the way the LiveKit bars do:

1. Copy the orb's file (and what it imports) into `source/`, keeping its licence file beside it.
2. Write a mount function like `source/livekit_bars.jsx`: it renders the orb into an element and returns a view, an object
   with the methods the orb needs: `phase(p)` (listening, thinking or speaking), `level(l)` (the assistant's audio level, 0 to 1),
   `track(t)` (the assistant's audio).
3. Build it with a config like `source/vite.livekit_bars.config.mjs`, into `page/`.
4. On the page, import the mount function, call it on an element, and add what it returns to `views`.

| orb | where | licence | what it takes, from the view |
|---|---|---|---|
| OrbKit shader orbs | [zzzzshawn/orbkit](https://github.com/zzzzshawn/orbkit), `orbs/orbs/shdr-11.tsx` and the rest | MIT, except the XorDev shaders listed in its `CREDITS.md`, which are non-commercial only | `<Shdr11 size={180} state={phase === "thinking" \|\| phase === "speaking" ? phase : "idle"} />` |
| ElevenLabs orb | [elevenlabs/ui](https://github.com/elevenlabs/ui/blob/main/apps/www/registry/elevenlabs-ui/ui/orb.tsx) | MIT | `<Orb agentState={{ thinking: "thinking", listening: "listening", speaking: "talking" }[phase] ?? null} volumeMode="manual" getOutputVolume={() => level} getInputVolume={() => 0} />`; it needs `@react-three/fiber` and `@react-three/drei` |
| CircularWaveform | [pipecat-ai/voice-ui-kit](https://github.com/pipecat-ai/voice-ui-kit/tree/main/package/src/visualizers/CircularWaveform) | BSD-2 | `<CircularWaveform size={160} audioTrack={track} isThinking={phase === "thinking"} />` |
| orb-ui | [exprmntl/orb-ui](https://github.com/exprmntl/orb-ui) | MIT | drives itself from a Pipecat client, so it runs only on a Pipecat page that owns that client, not through `ConnectConversation` |
| Thinking Orb | [mahdidavoodi7/expo-thinking-orbs](https://github.com/mahdidavoodi7/expo-thinking-orbs) | MIT | React Native (Skia), not a browser page |

Plasma, Pipecat's shader visualizer, is `examples/7-plasma-visualizer-pipecat`.
