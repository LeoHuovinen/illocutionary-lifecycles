// The basic movements of a VRM character in conversation, as one wrapper a VRM page imports:
//
//   import { VrmMotion } from "./vrm_motion.js";
//   const motion = VrmMotion();
//   loader.load(..., (gltf) => { vrm = ...; motion.attach(vrm); });   // after the VRM is set up
//   motion.update(dt, level);                                          // every frame, before vrm.update(dt)
//   onPhase: (p) => motion.phase(p),                                   // "listening" | "thinking" | "speaking"
//   onBotText: (t) => motion.text(t),                                  // the assistant's words: punctuation starts a glance
//
// What it does:
//   - the arms down along the body, every frame: vrm.update() rebuilds the humanoid from its rest pose (the T-pose)
//     each tick, so a one-time rotation is undone on the very next frame;
//   - idle life on the head: slow, small, out-of-phase sines on pitch and yaw, none on roll;
//   - listening: the head leans 6 degrees to a side chosen at random on entry;
//   - speaking: a gentle bob on pitch, and a glance away and back on each spoken comma (weak) or full stop (strong),
//     ignored while a glance is still returning (speechBeat);
//   - every phase offset eases with a fixed 0.12 s time constant, so a phase change does not snap the pose.
// Also:
//   - blinks: fast close, slower open, every 2 to 6 s, sometimes double, and one at the start of each glance
//     (Trutoiu et al. 2011);
//   - eye contact: the eyes counter the head's idle drift, lean and nods so they stay on the viewer, plus small saccades
//     that jump and hold, rarer and smaller while listening (Lee, Badler & Badler 2002). Eye angles go through the model's
//     own lookAt range maps, since a model's eyes may turn only 8 to 12 degrees for a 90 degree input;
//   - breathing on the chest and the shoulders, about 15 breaths a minute;
//   - the mouth: opens fast and closes slower so syllables separate, capped, partly rounded, and shut for at least
//     60 ms when the voice drops mid-speech; only while the assistant speaks, so room noise never moves the lips;
//   - speaking nods on the voice's onsets, a short dip when the level rises after a quiet stretch;
//   - listening nods on the user's pauses: one nod when the user stops for 0.2 to 0.6 s after at least 1 s of speech,
//     read from the page's own microphone. The microphone is opened at the first phase, which follows the Start click.
// Not here: emotions, gestures and the other reactions.

const DEG = Math.PI / 180;
const SMOOTH_TAU = 0.12;
const halfSine = (t, span) => (t >= 0 && t < span ? Math.sin(Math.PI * t / span) : 0);

export function VrmMotion() {
  let vrm = null, phase = "idle", phaseT = 0, tiltDir = 1;
  const eased = { roll: 0, pitch: 0 };
  let blinkT = -1, nextBlink = 1 + Math.random() * 3;
  let sacc = { yaw: 0, pitch: 0 }, nextSacc = 0.5;
  let glance = null;                                   // { t, span, amp, dir }
  let mouth = 0, shutFor = 0, quietFor = 0, speakNodT = -1, listenNodT = -1;
  let mic = null, userTalk = 0, userQuiet = 0;
  let command = null;                                  // { name, t }: a one-shot gesture asked for by an incremental phrase result

  const arms = (h) => {
    for (const [side, sign] of [["left", 1], ["right", -1]]) {
      h.getNormalizedBoneNode(`${side}UpperArm`)?.rotation.set(0.06, 0, sign * 1.22);   // Z swings the arm down, X brings it forward
      h.getNormalizedBoneNode(`${side}LowerArm`)?.rotation.set(0.12, 0, sign * 0.18);   // so the forearm does not clip the torso
      h.getNormalizedBoneNode(`${side}Hand`)?.rotation.set(0, 0, sign * 0.08);
    }
  };

  // Degrees the eyes should actually turn -> the lookAt input that turns them that far on this model.
  const eyes = (yaw, pitch) => {
    const a = vrm.lookAt?.applier;
    if (!vrm.lookAt) return;
    const gain = (m) => (m && m.outputScale ? m.inputMaxValue / m.outputScale : 1);
    const h = (gain(a?.rangeMapHorizontalInner) + gain(a?.rangeMapHorizontalOuter)) / 2;
    vrm.lookAt.yaw = yaw * h;
    vrm.lookAt.pitch = pitch * gain(pitch >= 0 ? a?.rangeMapVerticalUp : a?.rangeMapVerticalDown);
  };

  const blink = (dt) => {
    nextBlink -= dt;
    if (blinkT < 0 && nextBlink <= 0) { blinkT = 0; nextBlink = 2 + Math.random() * 4 - (Math.random() < 0.15 ? 1.7 : 0); }
    let b = 0;
    if (blinkT >= 0) {
      blinkT += dt;
      b = blinkT < 0.08 ? blinkT / 0.08 : blinkT < 0.25 ? 1 - (blinkT - 0.08) / 0.17 : (blinkT = -1, 0);
    }
    vrm.expressionManager?.setValue("blink", b);
  };

  const openMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
      const context = new AudioContext(), analyser = context.createAnalyser(); analyser.fftSize = 1024;
      context.createMediaStreamSource(stream).connect(analyser);
      mic = { analyser, samples: new Float32Array(analyser.fftSize) };
    } catch { mic = false; }                          // no microphone: no listening nods, everything else runs
  };
  const userLevel = () => {
    if (!mic) return 0;
    mic.analyser.getFloatTimeDomainData(mic.samples);
    let sum = 0; for (const v of mic.samples) sum += v * v;
    return Math.sqrt(sum / mic.samples.length);
  };

  // The phase's own offsets on the head, in degrees (pitch up positive), before easing.
  const target = (t) => {
    const fade = Math.min(t / 0.4, 1);
    if (phase === "listening") return { roll: 6 * tiltDir * fade, pitch: 0 };
    if (phase === "speaking") return { roll: 0, pitch: 0.6 * Math.sin(2 * Math.PI * 0.55 * t) * fade };
    return { roll: 0, pitch: 0 };
  };

  const api = {
    attach(model) {
      vrm = model;
      if (vrm.lookAt) vrm.lookAt.autoUpdate = false;    // yaw and pitch are set here every frame, never a target
      arms(vrm.humanoid);
    },
    phase(p) {
      if (mic === null) { mic = undefined; openMic(); }
      if (p === phase) return;
      phase = p; phaseT = 0; userTalk = 0; userQuiet = 0;
      tiltDir = Math.random() < 0.5 ? 1 : -1;          // which side the head leans
    },
    text(t) {                                          // speechBeat: a comma is a weak beat, a full stop a strong one
      if (phase !== "speaking" && phase !== "thinking") return;
      if (glance || !/[,;:.?!]/.test(t)) return;       // still returning: let it land
      const strong = /[.?!]/.test(t);
      glance = { t: 0, dir: Math.random() < 0.5 ? 1 : -1,
                 span: strong ? 1.5 + 0.4 * Math.random() : 0.9 + 0.3 * Math.random(),
                 amp: strong ? 0.45 + 0.2 * Math.random() : 0.22 + 0.12 * Math.random() };
      if (blinkT < 0) blinkT = 0;   // a glance starts with a blink
    },
    command(name) {                                    // nod, shake_head, look_left, look_right, look_center, close_eyes
      if (name === "look_center") { glance = null; command = null; return; }
      if (name === "look_left" || name === "look_right") { glance = { t: 0, dir: name === "look_left" ? 1 : -1, span: 1.6, amp: 0.6 }; return; }
      command = { name, t: 0 };
    },
    update(dt, level = 0) {
      if (!vrm) return;
      dt = Math.min(dt, 0.1);
      phaseT += dt;
      const h = vrm.humanoid, t = performance.now() / 1000;
      const goal = target(phaseT), ease = 1 - Math.exp(-dt / SMOOTH_TAU);
      for (const k in eased) { eased[k] += (goal[k] - eased[k]) * ease; if (Math.abs(goal[k] - eased[k]) < 0.01) eased[k] = goal[k]; }

      // Speaking nods on the voice's onsets; listening nods on the user's pauses.
      if (phase === "speaking") {
        if (level < 0.15) quietFor += dt; else if (level > 0.35 && quietFor >= 0.15) { speakNodT = 0; quietFor = 0; }
      }
      if (phase === "listening" && mic) {
        const u = userLevel();
        if (u > 0.02) { userTalk += dt; userQuiet = 0; }
        else if (userTalk > 0) {
          userQuiet += dt;
          if (userQuiet >= 0.2 && userTalk >= 1 && listenNodT < 0) { listenNodT = 0; userTalk = 0; }
          if (userQuiet > 0.6) userTalk = 0;
        }
      }
      let nod = 0, shake = 0, eyesShut = 0;
      if (command) {                                   // the asked-for gesture, over the idle life
        command.t += dt;
        if (command.name === "nod") nod -= 6 * Math.abs(Math.sin(2 * Math.PI * command.t / 0.5));          // two dips over a second
        if (command.name === "shake_head") shake = 10 * Math.sin(2 * Math.PI * command.t / 0.45);           // side to side
        if (command.name === "close_eyes") eyesShut = Math.min(1, command.t / 0.2);
        if (command.t > (command.name === "close_eyes" ? 1.5 : 1.0)) command = null;
      }
      if (speakNodT >= 0) { speakNodT += dt; nod -= 3 * halfSine(speakNodT, 0.25); if (speakNodT > 0.25) speakNodT = -1; }
      if (listenNodT >= 0) { listenNodT += dt; nod -= 4 * halfSine(listenNodT, 0.6); if (listenNodT > 0.6) listenNodT = -1; }

      // The glance: eyes, head yaw and a little roll, one half-sine away and back.
      let gEye = 0, gYaw = 0, gRoll = 0;
      if (glance) {
        glance.t += dt;
        const env = halfSine(glance.t, glance.span);
        gEye = glance.amp * glance.dir * env * 10; gYaw = glance.amp * 8 * glance.dir * env; gRoll = glance.amp * -3 * glance.dir * env;
        if (glance.t >= glance.span) glance = null;
      }

      // Head: idle life + the phase's lean and bob + nods + the glance. Pitch here is "up positive".
      const idleYaw = Math.sin(t * 0.6) * 2.4, idlePitch = -Math.sin(t * 0.9) * 1.6;
      const headPitch = eased.pitch + nod + idlePitch, headYaw = idleYaw + gYaw + shake;
      arms(h);
      h.getNormalizedBoneNode("head")?.rotation.set(-headPitch * DEG, headYaw * DEG, (eased.roll + gRoll) * DEG);

      // Breathing on the chest and the shoulders.
      const br = Math.sin(2 * Math.PI * 0.25 * t);
      h.getNormalizedBoneNode("chest")?.rotation.set(br * 0.6 * DEG, 0, 0);
      h.getNormalizedBoneNode("upperChest")?.rotation.set(br * 0.4 * DEG, 0, 0);
      h.getNormalizedBoneNode("leftShoulder")?.rotation.set(0, 0, -br * 0.5 * DEG);
      h.getNormalizedBoneNode("rightShoulder")?.rotation.set(0, 0, br * 0.5 * DEG);

      // Eyes: counter the head except the glance, so they stay on the viewer; then the saccade, then the glance.
      nextSacc -= dt;
      if (nextSacc <= 0) {
        const amp = phase === "listening" ? 0.6 : 1.2;
        sacc = { yaw: (Math.random() * 2 - 1) * amp, pitch: (Math.random() * 2 - 1) * amp * 0.5 };
        nextSacc = phase === "listening" ? 0.8 + Math.random() * 1.5 : 0.3 + Math.random() * 1.2;
      }
      eyes(-idleYaw + sacc.yaw + gEye, -(eased.pitch + nod + idlePitch) + sacc.pitch);
      blink(dt);

      // The mouth: fast open, slower close, shut briefly when the voice drops, only while the assistant speaks.
      const speaking = phase === "speaking";
      if (speaking && level < 0.05 && mouth > 0.1) shutFor = 0.06;
      shutFor = Math.max(0, shutFor - dt);
      const want = speaking && shutFor === 0 ? Math.min(1, level) : 0;
      mouth += (want - mouth) * (1 - Math.exp(-dt / (want > mouth ? 0.04 : 0.08)));
      const aa = Math.min(0.7, mouth);
      vrm.expressionManager?.setValue("aa", aa);
      vrm.expressionManager?.setValue("oh", 0.3 * aa);
      if (eyesShut) vrm.expressionManager?.setValue("blink", eyesShut);
    },
  };
  return api;
}
