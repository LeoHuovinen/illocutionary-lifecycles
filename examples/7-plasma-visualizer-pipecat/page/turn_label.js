// The turn-state word, one state machine and one label envelope, as one view a page mounts.
//
//   import { TurnLabel } from "./turn_label.js";
//   const label = TurnLabel(element, { hue: 187 });   // element holds the word; hue is the base colour
//   views: [label]                                    // in ConnectConversation: rtvi() on the Pipecat voice mount, phase() on press-to-speak
//
// On the Pipecat voice mount it runs the state machine on the raw RTVI events below. The press-to-speak mount has no RTVI,
// so there the word follows that mount's own phase (listening, thinking, speaking), drawn the same way.
//
// The machine, hardcoded:
//   user starts                    -> listening
//   no new transcript for 750 ms   -> thinking  (fires just before the slow VAD stop, so a pause reads as thinking)
//   UserStoppedSpeaking            -> thinking  (backstop if the timer has not fired)
//   any bot output (audio start, BotOutput, BotTtsText, BotTtsStarted) -> speaking  (snapback: a stuck thinking clears)
//   bot audio stops                -> idle
// LLM start and stop are not used; only the speech and audio events above move the label.
//
// The label: leaving listening latches "Thinking…" until a concrete next state (speaking or a new
// listening) arrives; each change fades in over 500 ms from the old label's current alpha, holds 1 s (thinking 2.5 s)
// and fades out over 2 s. "Getting ready to speak…" replaces "Thinking…" once the reply is composed (imminent()).

const THINK_AFTER_SILENCE_MS = 750;
const LBL_IN = 500, LBL_HOLD = 1000, LBL_OUT = 2000;

export function TurnLabel(element, { hue = 187, sat = 80, light = 60, hues = {} } = {}) {   // hues: a hue per state, e.g. { thinking: 270 }
  let raw = "idle", silenceTimer = 0, replyImminent = false, drivenByRtvi = false;
  const L = { state: null, t0: 0, a0: 0, rawPrev: null, imm: undefined };

  const setTurnState = (s) => { raw = s; };
  const armThinking = () => { clearTimeout(silenceTimer); silenceTimer = setTimeout(() => setTurnState("thinking"), THINK_AFTER_SILENCE_MS); };
  const snapSpeaking = () => { clearTimeout(silenceTimer); replyImminent = false; setTurnState("speaking"); };

  const alphaOf = (now) => {
    const HOLD = LBL_HOLD + (L.state === "thinking" ? 1500 : 0), e = now - L.t0;
    if (e < LBL_IN) return L.a0 + (1 - L.a0) * (e / LBL_IN);
    if (e < LBL_IN + HOLD) return 1;
    if (e < LBL_IN + HOLD + LBL_OUT) return 1 - (e - LBL_IN - HOLD) / LBL_OUT;
    return 0;
  };

  (function draw() {
    requestAnimationFrame(draw);
    const now = performance.now();
    let state = raw;
    const leftListening = L.rawPrev === "listening" && raw !== "listening";
    if (leftListening || raw === "thinking") state = "thinking";
    L.rawPrev = raw;
    if (L.state === "thinking" && raw !== "speaking" && raw !== "listening") state = "thinking";
    if (state !== L.state) { L.a0 = L.state == null ? 0 : alphaOf(now); L.state = state; L.t0 = now; }
    if (state === "thinking" && L.imm !== replyImminent) { L.imm = replyImminent; L.a0 = L.state == null ? 0 : alphaOf(now); L.t0 = now; }
    const alpha = Math.max(0, Math.min(1, alphaOf(now)));
    const word = state === "speaking" ? "Speaking" : state === "listening" ? "Listening"
      : state === "thinking" ? (replyImminent ? "Getting ready to speak…" : "Thinking…") : "Idle";
    let s = sat, l = light;                                          // per-state hue tweaks
    if (state === "thinking") l = Math.max(0, l - 12);
    else if (state === "listening") l = Math.min(100, l + 14);
    else if (state === "speaking") s = Math.min(100, s + 18);
    else s = Math.max(0, s - 22);
    if (element.textContent !== word) element.textContent = word;
    element.style.opacity = alpha;
    element.style.color = `hsl(${hues[state] ?? hue} ${s}% ${l}%)`;
  })();

  return {
    rtvi(name) {
      drivenByRtvi = true;
      if (name === "UserStartedSpeaking") { clearTimeout(silenceTimer); replyImminent = false; setTurnState("listening"); }
      else if (name === "UserTranscript") { setTurnState("listening"); armThinking(); }
      else if (name === "UserStoppedSpeaking") { clearTimeout(silenceTimer); setTurnState("thinking"); }
      else if (["BotStartedSpeaking", "BotOutput", "BotTtsText", "BotTtsStarted"].includes(name)) snapSpeaking();
      else if (name === "BotStoppedSpeaking") setTurnState("idle");
    },
    phase(phase) {                                                   // the press-to-speak mount, which has no RTVI
      if (drivenByRtvi) return;
      if (phase === "listening" || phase === "thinking" || phase === "speaking") { clearTimeout(silenceTimer); setTurnState(phase); }
    },
    imminent() { replyImminent = true; },                            // the reply is composed, its audio on the way
  };
}
