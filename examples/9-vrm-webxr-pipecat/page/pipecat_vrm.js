// A VRM character as one view a page mounts: a scene with the camera on the head, the movements of vrm_motion.js, and
// the mouth on the assistant's level, with a menu of the models present in vrm/ beside the page, and a warning when there is none.
// An Enter VR button shows the character in a VR headset, 1.2 m in front of the viewer.
//
//   import { mountVrm } from "./pipecat_vrm.js";
//   const vrm = mountVrm(element);              // the menu of the models in vrm/, the first one loaded
//   mountVrm(element, { at: { x: 0, y: 0, z: -1.2, tilt: 0, turn: 0 } })   // where the scene stands in VR, metres and radians
//   views: [vrm]                                // in ConnectConversation: level(l), phase(p), botMessage(text), adapterCallback(e)
//   views: [vrm, RTVI_States(vrm)]              // on the Pipecat voice mount: turnState(s) from RTVI_States.js replaces phase(p)
//   XrPanels(vrm)                               // vrm.scene and vrm.renderer, for the panels of xr_panels.js
//
// This module owns the renderer, the WebXR session, the frame loop and placing the VRM model 1.2 m in front of the viewer,
// and hands out its scene and renderer so xr_panels.js can add panels to the same scene.
//
// No model is shipped: VRM_MODELS names each one with its download address, README.md gives the command that fetches
// them into vrm/, and the menu lists only the files found there. three.js and three-vrm are imported from esm.sh (both MIT).
import * as THREE from "https://esm.sh/three@0.180.0";
import { GLTFLoader } from "https://esm.sh/three@0.180.0/examples/jsm/loaders/GLTFLoader.js";
import { VRMLoaderPlugin, VRMUtils } from "https://esm.sh/@pixiv/three-vrm@3.5.5?deps=three@0.180.0";
import { VRButton } from "https://esm.sh/three@0.180.0/examples/jsm/webxr/VRButton.js";
import { VrmMotion } from "./vrm_motion.js";

// VRoid Project's sample avatars: anyone may use, change and pass them on, with no credit (each model's own licence data).
// Amica's file names are shifted by one: its AvatarSample_B.vrm is VRoid's AvatarSample_A, and so on.
const AMICA = "https://raw.githubusercontent.com/semperai/amica/master/public/vrm/";
export const VRM_MODELS = [
  { name: "AvatarSample_A", file: "AvatarSample_A.vrm", download: AMICA + "AvatarSample_B.vrm", by: "VRoid Project" },
  { name: "AvatarSample_B", file: "AvatarSample_B.vrm", download: AMICA + "AvatarSample_C.vrm", by: "VRoid Project" },
  { name: "AvatarSample_C", file: "AvatarSample_C.vrm", download: AMICA + "AvatarSample_D.vrm", by: "VRoid Project" },
].map((m) => ({ ...m, url: new URL(`./vrm/${m.file}`, import.meta.url).href }));

export function mountVrm(element, { at = { x: 0, y: 0, z: -1.2, tilt: 0, turn: 0 } } = {}) {
  const canvas = document.createElement("canvas"); canvas.style.cssText = "width:100%;height:100%;display:block";
  const select = document.createElement("select"); select.style.cssText = "position:absolute;top:6px;right:8px;z-index:4;font:12px system-ui;border-radius:999px;padding:2px 8px;background:#1f2633;color:#dde;border:1px solid #3a4456";
  select.append(Object.assign(document.createElement("option"), { textContent: "Looking in vrm/…", value: "", disabled: true, selected: true }));
  element.append(canvas, select);

  // The character.
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.xr.enabled = true; element.append(VRButton.createButton(renderer));
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(28, 1, 0.1, 20);
  scene.add(new THREE.DirectionalLight(0xffffff, Math.PI).translateZ(1).translateY(1), new THREE.AmbientLight(0xffffff, 0.6));
  const loader = new GLTFLoader(); loader.register((parser) => new VRMLoaderPlugin(parser));
  let vrm = null, level = 0, turnStates = false;   // turnStates: RTVI_States.js has taken over from phase()
  const motion = VrmMotion();
  const load = (url) => {
    if (vrm) { scene.remove(vrm.scene); VRMUtils.deepDispose(vrm.scene); vrm = null; }
    loader.load(url, (gltf) => {
      vrm = gltf.userData.vrm; VRMUtils.combineSkeletons(vrm.scene); VRMUtils.rotateVRM0(vrm); motion.attach(vrm);
      scene.add(vrm.scene); vrm.update(0); vrm.scene.updateMatrixWorld(true);
      const y = vrm.humanoid.getNormalizedBoneNode("head").getWorldPosition(new THREE.Vector3()).y;
      camera.position.set(0, y - 0.1, 1.4); camera.lookAt(0, y - 0.1, 0);
    });
  };
  // The canvas takes the size its panel has, whatever the window: the drawing buffer and the camera follow it.
  const fit = () => { const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h || renderer.xr.isPresenting) return;
    renderer.setPixelRatio(window.devicePixelRatio || 1); renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); };
  new ResizeObserver(fit).observe(element); fit();
  const clock = new THREE.Clock();
  // In VR the viewer starts at the floor's origin looking along -z, so the character moves 1.2 m that way and faces them.
  // at: where the scene stands in VR, in metres from the viewer's starting point, tilted around x and turned around y in radians.
  renderer.xr.addEventListener("sessionstart", () => { scene.position.set(at.x, at.y, at.z); scene.rotation.set(at.tilt || 0, at.turn || 0, 0); });
  renderer.xr.addEventListener("sessionend", () => { scene.position.set(0, 0, 0); scene.rotation.set(0, 0, 0); fit(); });
  renderer.setAnimationLoop(() => {   // in VR the headset times the frames, which requestAnimationFrame cannot
    const dt = clock.getDelta();
    motion.update(dt, level); vrm?.update(dt);
    renderer.render(scene, camera);
  });

  // The menu: only the models whose file is in vrm/ beside the page (README.md downloads them).
  select.onchange = () => { if (select.value !== "") load(VRM_MODELS[+select.value].url); };
  Promise.all(VRM_MODELS.map((m) => fetch(m.url, { method: "HEAD" }).then((res) => res.ok, () => false))).then((present) => {
    const found = VRM_MODELS.map((m, i) => i).filter((i) => present[i]);
    select.options[0].textContent = found.length ? "Select model" : "No models in vrm/: see README.md";
    if (!found.length) element.insertAdjacentHTML("beforeend", '<div style="position:absolute;inset:0;display:grid;place-items:center;font:600 16px system-ui;color:#f66">No model: download one, see README.md</div>');   // the warning, nothing else
    found.forEach((i) => select.append(Object.assign(document.createElement("option"), { textContent: VRM_MODELS[i].name, value: String(i), title: VRM_MODELS[i].by })));
    if (found.length) { select.value = String(found[0]); load(VRM_MODELS[found[0]].url); }
  });

  return {
    scene, renderer,                            // the VRM model's scene and its renderer, for xr_panels.js to add panels to
    level: (l) => { level = l; },               // the assistant's audio level, 0..1: the mouth
    phase: (p) => { if (!turnStates) motion.phase(p); },   // listening | thinking | speaking: the head and the eyes
    turnState: (s) => { turnStates = true; motion.phase(s); },   // idle | listening | thinking | speaking, from RTVI_States.js
    botMessage: (t) => motion.text(t),          // the assistant's words: punctuation starts a glance
    // The "motion" incremental phrase instance of flow.json, read while the person speaks: "nod at me", "shake your
    // head", "look left" move the character at once.
    adapterCallback: (e) => { if (e.type === "IncrementalPhraseAdapterCallbackHandlerEvent" && e.InstanceIdentifier === "motion" && e.category && e.category !== "none") motion.command(e.category); },
  };
}
