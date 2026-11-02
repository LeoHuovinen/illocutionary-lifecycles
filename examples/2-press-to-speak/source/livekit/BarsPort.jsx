// LiveKit Agents UI BarVisualizer, ported: the per-state highlight sequences are its own
// (connecting sweeps in from both ends, listening pulses the centre, thinking scans), and the
// bar heights come from bands of the assistant's track. It takes the phase and the
// track as props. LiveKit Agents UI is Apache-2.0: see LICENSE and NOTICE here.
import React, { useEffect, useRef, useState } from "react";

const connectingSeq = (n) => Array.from({ length: n }, (_, x) => [x, n - 1 - x]);
const listeningSeq = (n) => [[Math.floor(n / 2)], [-1]];
const thinkingSeq = (n) => [...Array.from({ length: n }, (_, x) => [x]), ...Array.from({ length: n }, (_, x) => [n - 1 - x])];
const intervals = { connecting: 2000, listening: 500, thinking: 150 };

function useBands(track, n) {
  const [bands, setBands] = useState(() => new Array(n).fill(0));
  useEffect(() => {
    if (!track) { setBands(new Array(n).fill(0)); return; }
    const ctx = new AudioContext();
    const src = ctx.createMediaStreamSource(new MediaStream([track]));
    const an = ctx.createAnalyser(); an.fftSize = 256; an.smoothingTimeConstant = 0.6;
    src.connect(an);
    const data = new Uint8Array(an.frequencyBinCount);
    let id;
    const tick = () => {
      an.getByteFrequencyData(data);
      const per = Math.floor(data.length / 2 / n);
      setBands(Array.from({ length: n }, (_, i) => { let s = 0; for (let j = 0; j < per; j++) s += data[i * per + j]; return s / per / 255; }));
      id = requestAnimationFrame(tick);
    };
    id = requestAnimationFrame(tick);
    return () => { cancelAnimationFrame(id); try { src.disconnect(); } catch {} if (ctx.state !== "closed") ctx.close().catch(() => {}); };
  }, [track, n]);
  return bands;
}

export default function BarsPanel({ phase, track }) {
  const v = { phase, botTrack: track };
  const n = 15;
  const bands = useBands(v.botTrack, n);
  const [idx, setIdx] = useState(0);
  const seqRef = useRef([[]]);
  useEffect(() => {
    const s = v.phase;
    seqRef.current = s === "thinking" ? thinkingSeq(n) : s === "connecting" ? connectingSeq(n) : s === "listening" ? listeningSeq(n) : s === "speaking" ? [Array.from({ length: n }, (_, i) => i)] : [[]];
    setIdx(0);
    const ms = (intervals[s] ?? 100) / (s === "connecting" ? n : 1);
    const t = setInterval(() => setIdx((i) => i + 1), ms);
    return () => clearInterval(t);
  }, [v.phase]);
  const hi = seqRef.current[idx % seqRef.current.length] || [];
  return (
    <div className="panel">
      <h2>LiveKit Agents UI bars <small>ported state sequences: connecting, listening, thinking, speaking</small></h2>
      <div className="bars">
        {bands.map((b, i) => <span key={i} data-hi={hi.includes(i)} style={{ height: `${Math.min(100, Math.max(12, b * 100 + 5))}%` }} />)}
      </div>
      <div className="muted">state: {v.phase}</div>
    </div>
  );
}
