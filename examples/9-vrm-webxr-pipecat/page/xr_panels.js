// Copies parts of the page onto flat panels in the VRM model's 3D scene during a WebXR session, since a WebXR session
// shows only the 3D scene and never the page's HTML.
//
//   import { XrPanels } from "./xr_panels.js";
//   const panels = XrPanels(vrm);                                  // vrm from mountVrm(), which hands out its scene and renderer
//   panels.add(document.getElementById("plasma"), { width: 0.5, x: -0.7, y: 1.2, z: 0.2, tilt: 0, turn: 0.5 });   // metres from the VRM model; tilt around x and turn around y in radians
//
// What WebGL draws, as in Pipecat's plasma visualizer and the Rive web runtime, is copied on every WebXR frame. HTML, as in
// the karaoke and the listening or speaking label, is copied through modern-screenshot only after it changes and no more
// often than once every MIN_GAP_MS, because making a picture from HTML is slow and the frame waits for it. A panel keeps
// the shape of what it copies as that resizes. modern-screenshot 4.6.0 (MIT) is imported from esm.sh, as three.js is.
//
// The module needs only a 3D scene, its renderer and parts of the page, and knows nothing of the VRM model, the voice or
// the conversation. Running the page's requestAnimationFrame on the WebXR frames is a page wide policy that belongs to
// whoever owns the frame loop. Whether a panel copies WebGL or HTML is decided by whether its part of the page holds a
// WebGL drawing.
import * as THREE from "https://esm.sh/three@0.180.0";
import { createContext, domToCanvas } from "https://esm.sh/modern-screenshot@4.6.0";

const SCALE = 2;            // pixels per CSS pixel on the panels, so text stays sharp in VR
const MIN_GAP_MS = 150;     // an HTML panel is copied at most this often, however often its HTML changes
// A copy keeps the page's own placement, so HTML placed on the page, such as the karaoke at the bottom or the label
// centred with a transform, would land outside its own picture. The copy draws it in place instead.
const IN_PLACE = { position: "relative", inset: "auto", top: "0", left: "0", right: "auto", bottom: "auto", transform: "none", margin: "0" };

export function XrPanels({ scene, renderer }) {
  const panels = [];

  // A browser may stop the page's requestAnimationFrame during a WebXR session, and the animations on the page run on it,
  // so during the session the page's requestAnimationFrame callbacks run on the WebXR frames instead.
  const pageRaf = window.requestAnimationFrame.bind(window), pageCancel = window.cancelAnimationFrame.bind(window);
  renderer.xr.addEventListener("sessionstart", () => {
    const session = renderer.xr.getSession(), waiting = new Map(); let next = 1;
    const frame = (time) => {
      const callbacks = [...waiting.values()]; waiting.clear();
      for (const callback of callbacks) { try { callback(time); } catch (e) { console.warn(e); } }
      for (const panel of panels) panel.frame();
      if (renderer.xr.isPresenting) session.requestAnimationFrame(frame);
    };
    session.requestAnimationFrame(frame);
    window.requestAnimationFrame = (callback) => { const id = next++; waiting.set(id, callback); return id; };
    window.cancelAnimationFrame = (id) => waiting.delete(id);
    for (const panel of panels) panel.changed();      // every panel's first picture in the session
  });
  renderer.xr.addEventListener("sessionend", () => { window.requestAnimationFrame = pageRaf; window.cancelAnimationFrame = pageCancel; });

  return {
    add(element, { width = 0.5, x = 0, y = 1.2, z = 0, tilt = 0, turn = 0 } = {}) {
      const canvas = document.createElement("canvas"), context = canvas.getContext("2d");
      const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: texture, transparent: true }));
      mesh.position.set(x, y, z); mesh.rotation.set(tilt, turn, 0); mesh.visible = false; scene.add(mesh);   // shown from its first picture
      // The panel's picture and the panel take the current size and shape of what they copy. three.js gives a texture fixed
      // storage on its first upload, so a picture of a new size needs that storage released, or the copy overflows it.
      const fit = () => {
        const w = element.clientWidth, h = element.clientHeight;
        if (!w || !h) { mesh.visible = false; return false; }   // nothing to show, such as the karaoke between lines
        if (canvas.width !== w * SCALE || canvas.height !== h * SCALE) { canvas.width = w * SCALE; canvas.height = h * SCALE; texture.dispose(); }
        mesh.scale.set(width, width * h / w, 1); mesh.visible = true; return true;
      };

      // What WebGL draws is copied on every frame, and HTML only after it has changed.
      const drawn = () => element.querySelector("canvas");
      let html = null, copying = false, dirty = true, last = 0;
      const copyHtml = async () => {
        copying = true; dirty = false; last = performance.now();
        try {
          if (fit()) {
            html ||= await createContext(element, { scale: SCALE, font: false, style: IN_PLACE });   // built once, reused for every copy
            const picture = await domToCanvas(html);
            context.clearRect(0, 0, canvas.width, canvas.height); context.drawImage(picture, 0, 0, canvas.width, canvas.height);
            drawShadowImages();
            texture.needsUpdate = true;
          }
        } catch (e) { console.warn("xr panel", e); }
        copying = false;
      };
      // modern-screenshot leaves images inside a shadow root blank, as in the picture cards, so each loaded one is drawn
      // into its own place on the copy, cropped the way object-fit cover crops it.
      const drawShadowImages = () => {
        const box = element.getBoundingClientRect();
        for (const host of element.querySelectorAll("*")) if (host.shadowRoot) for (const img of host.shadowRoot.querySelectorAll("img")) {
          if (!img.complete || !img.naturalWidth || !img.offsetWidth) continue;
          const r = img.getBoundingClientRect(), k = Math.max(r.width / img.naturalWidth, r.height / img.naturalHeight);
          const sw = r.width / k, sh = r.height / k, x = (r.left - box.left) * SCALE, y = (r.top - box.top) * SCALE;
          context.save(); context.beginPath(); context.roundRect(x, y, r.width * SCALE, r.height * SCALE, 10 * SCALE); context.clip();
          context.drawImage(img, (img.naturalWidth - sw) / 2, (img.naturalHeight - sh) / 2, sw, sh, x, y, r.width * SCALE, r.height * SCALE);
          context.restore();
        }
      };
      // A change inside a shadow root is not seen from outside it, so each shadow root is watched as well.
      const watch = new MutationObserver(() => { dirty = true; }), what = { subtree: true, childList: true, characterData: true, attributes: true };
      watch.observe(element, what);
      for (const host of [element, ...element.querySelectorAll("*")]) if (host.shadowRoot) watch.observe(host.shadowRoot, what);

      const panel = {
        changed() { dirty = true; },
        frame() {             // called on every WebXR frame
          const source = drawn();
          if (source) { if (fit()) { context.clearRect(0, 0, canvas.width, canvas.height); context.drawImage(source, 0, 0, canvas.width, canvas.height); texture.needsUpdate = true; } return; }
          if (dirty && !copying && performance.now() - last >= MIN_GAP_MS) copyHtml();
        },
      };
      panels.push(panel);
      return panel;
    },
  };
}
