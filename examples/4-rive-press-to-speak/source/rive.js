// A Rive panel, as a plain module. Twenty-nine characters, each with its own mouth binding, driven by the assistant's audio level. The
// level, smoothed (rising 0.8, falling 0.4) and sampled at 30 Hz, picks a closed,
// half-open or open shape for viseme rigs, flips a switch for open/shut rigs, and fires talk triggers; a second
// "speaking" control is held while the assistant speaks where a rig has one.
//
//   import { mountRive } from "./pipecat_rive.js";
//   const rive = mountRive(element);          // a menu of the characters present in rive/, the first one loaded
//   views: [rive]                             // in ConnectConversation: level(l), the assistant's audio level, 0..1
//
// No character is shipped: riveModels.js names each one with its download address, README.md gives the command that
// fetches them into rive/ beside the page, and the menu lists only the files found there. The runtime's WebAssembly is
// served beside the page (vendor/rive-2.44.2.wasm), never from a CDN.
import { Rive, Layout, Fit, Alignment, RuntimeLoader } from "@rive-app/webgl2";
import { RIVE_MODELS as LISTED } from "./riveModels.js";

RuntimeLoader.setWasmUrl(new URL("./vendor/rive-2.44.2.wasm", import.meta.url).href);
RuntimeLoader.setWasmFallbackUrl(null);

// Each in rive/ beside the page, looked up when the page runs. The address is built first and handed over as a value: an
// address written inside new URL(...) is replaced by Vite at build time with the files that were in rive/ then, none.
const riveAddress = (file) => "./rive/" + file;
const RIVE_MODELS = LISTED.map((m) => ({ ...m, url: new URL(riveAddress(m.file), import.meta.url).href }));
export { RIVE_MODELS };
export function mountRive(element, { initial = 0 } = {}) {
  const canvas = document.createElement("canvas"); canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
  const select = document.createElement("select"); select.style.cssText = "position:absolute;top:6px;right:8px;z-index:4;font:12px system-ui;border-radius:999px;padding:2px 8px;background:#1f2633;color:#dde;border:1px solid #3a4456";
  select.append(Object.assign(document.createElement("option"), { textContent: "Looking in rive/…", value: "", disabled: true, selected: true }));
  element.append(canvas, select);
  const r = { rive: null, ctl: null, speak: null, spec: null, flip: 0, lastShape: null, lastFire: 0, wasSpeaking: false };
  let raw = 0, smooth = 0;

  // The canvas's drawing surface is its displayed size times the pixel density, set before Rive starts and again on every
  // resize, so the character is never stretched from the canvas's default 300x150.
  const fit = () => { const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return; const d = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * d); canvas.height = Math.round(h * d); try { r.rive?.resizeDrawingSurfaceToCanvas(d); } catch {} };
  new ResizeObserver(fit).observe(element); fit();

  // Drive the mouth from the level.
  const drive = () => {
    smooth += (raw - smooth) * (raw > smooth ? 0.8 : 0.4); const level = smooth;
    const s = r.spec; if (!s || !r.ctl) return;
    const o = Math.min(1, level * 1.6); const speaking = o > 0.04; const now = performance.now();
    try {
      if (s.kind.endsWith("number") || s.kind.endsWith("enum")) {
        let value = s.closed;
        if (speaking && s.shapes?.length) { r.flip = (r.flip + 1) % 3; const n = s.shapes.length; let i = Math.min(n - 1, Math.floor(o * n)); if (r.flip === 0 && i > 0) i -= 1; value = s.shapes[i]; }
        if (value !== r.lastShape) { r.ctl.value = value; r.lastShape = value; }
      } else if (s.kind.endsWith("boolean")) {
        if (speaking !== r.lastShape) { r.ctl.value = speaking; r.lastShape = speaking; }
      } else if (s.kind.endsWith("trigger")) {
        if (speaking && now - r.lastFire > 1500) { r.ctl.fire(); r.lastFire = now; }
      }
      if (r.speak) {
        if (s.speaking.kind.endsWith("boolean")) { if (r.speak.value !== speaking) r.speak.value = speaking; }
        else if (s.speaking.kind.endsWith("trigger") && speaking && !r.wasSpeaking) r.speak.fire();
      }
      r.wasSpeaking = speaking;
    } catch (e) { console.warn("rive drive", e); }
  };
  setInterval(drive, 1000 / 30);

  // Load or swap the file and resolve its binding.
  const load = (spec) => {
    fit();
    try { r.rive?.cleanup(); } catch {}
    r.ctl = null; r.speak = null; r.spec = spec; r.lastShape = null;
    const find = (inst) => {
      const machine = spec.machine; const inputs = machine ? inst.stateMachineInputs(machine) || [] : [];
      const smInput = (name) => inputs.find((i) => i.name === name) || null;
      const vmi = inst.viewModelInstance || (() => { const vm = (spec.vm && inst.viewModelByName?.(spec.vm)) || inst.defaultViewModel?.() || inst.viewModelByIndex?.(0); const i = vm?.defaultInstance?.() || vm?.instanceByIndex?.(0) || vm?.instance?.(); if (i) inst.bindViewModelInstance?.(i); return i; })();
      const vmProp = (kind, path) => { if (!vmi) return null; const fn = kind.endsWith("number") ? "number" : kind.endsWith("enum") ? "enum" : kind.endsWith("boolean") ? "boolean" : "trigger"; try { return vmi[fn]?.(path) || null; } catch { return null; } };
      const get = (kind, path) => (kind.startsWith("sm-") ? smInput(path) : vmProp(kind, path));
      return { ctl: get(spec.kind, spec.path), speak: spec.speaking ? get(spec.speaking.kind, spec.speaking.path) : null };
    };
    const rive = new Rive({ src: spec.url, canvas, autoplay: true, autoBind: true, artboard: spec.artboard || undefined, stateMachines: spec.machine || undefined,
      layout: new Layout({ fit: Fit.Contain, alignment: Alignment.Center }),
      onLoad: () => { fit(); const f = find(rive); r.ctl = f.ctl; r.speak = f.speak; r.rive = rive; } });
    r.rive = rive;
  };
  select.onchange = () => { if (select.value !== "") load(RIVE_MODELS[+select.value]); };
  // The menu: only the characters whose file is in rive/ beside the page (README.md downloads them).
  Promise.all(RIVE_MODELS.map((m) => fetch(m.url, { method: "HEAD" }).then((res) => res.ok, () => false))).then((present) => {
    const found = RIVE_MODELS.map((m, i) => i).filter((i) => present[i]);
    select.options[0].textContent = found.length ? "Select character" : "No characters in rive/: see README.md";
    if (!found.length) element.insertAdjacentHTML("beforeend", '<div style="position:absolute;inset:0;display:grid;place-items:center;font:600 16px system-ui;color:#a33">No character: download one, see README.md</div>');   // the warning, nothing else
    found.forEach((i) => select.append(Object.assign(document.createElement("option"), { textContent: RIVE_MODELS[i].name, value: String(i), title: RIVE_MODELS[i].by })));
    const first = found.includes(initial) ? initial : found[0];
    if (first !== undefined) { select.value = String(first); load(RIVE_MODELS[first]); }
  });
  return { level: (l) => { raw = l; } };
}
