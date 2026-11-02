var an = { exports: {} }, dr = an.exports, Xn;
function fr() {
  return Xn || (Xn = 1, (function(At, sn) {
    (function(vt, Me) {
      At.exports = Me();
    })(dr, () => (
      /******/
      (() => {
        var Ft = [
          ,
          /* 1 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              Animation: () => (
                /* reexport safe */
                oe.Animation
              )
              /* harmony export */
            });
            var oe = ae(2);
          }),
          /* 2 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              Animation: () => (
                /* binding */
                oe
              )
              /* harmony export */
            });
            var oe = (
              /** @class */
              (function() {
                function C(I, te, N, ne) {
                  this.animation = I, this.artboard = te, this.playing = ne, this.loopCount = 0, this.scrubTo = null, this.instance = new N.LinearAnimationInstance(I, te);
                }
                return Object.defineProperty(C.prototype, "name", {
                  /**
                   * Returns the animation's name
                   */
                  get: function() {
                    return this.animation.name;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(C.prototype, "time", {
                  /**
                   * Returns the animation's name
                   */
                  get: function() {
                    return this.instance.time;
                  },
                  /**
                   * Sets the animation's current time
                   */
                  set: function(I) {
                    this.instance.time = I;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(C.prototype, "loopValue", {
                  /**
                   * Returns the animation's loop type
                   */
                  get: function() {
                    return this.animation.loopValue;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(C.prototype, "needsScrub", {
                  /**
                   * Indicates whether the animation needs to be scrubbed.
                   * @returns `true` if the animation needs to be scrubbed, `false` otherwise.
                   */
                  get: function() {
                    return this.scrubTo !== null;
                  },
                  enumerable: !1,
                  configurable: !0
                }), C.prototype.advance = function(I) {
                  this.scrubTo === null ? this.instance.advance(I) : (this.instance.time = 0, this.instance.advance(this.scrubTo), this.scrubTo = null);
                }, C.prototype.apply = function(I) {
                  this.instance.apply(I);
                }, C.prototype.cleanup = function() {
                  this.instance.delete();
                }, C;
              })()
            );
          }),
          /* 3 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              RuntimeLoader: () => (
                /* binding */
                te
              )
              /* harmony export */
            });
            var oe = ae(4), C = ae(5), I = function() {
              return I = Object.assign || function(N) {
                for (var ne, Y = 1, F = arguments.length; Y < F; Y++) {
                  ne = arguments[Y];
                  for (var ie in ne) Object.prototype.hasOwnProperty.call(ne, ie) && (N[ie] = ne[ie]);
                }
                return N;
              }, I.apply(this, arguments);
            }, te = (
              /** @class */
              (function() {
                function N() {
                }
                return N.notifyError = function(ne) {
                  var Y;
                  for (N.isLoading = !1; N.errorCallbackQueue.length > 0; )
                    (Y = N.errorCallbackQueue.shift()) === null || Y === void 0 || Y(ne);
                  N.callBackQueue = [];
                }, N.loadRuntime = function() {
                  var ne = N.wasmURL, Y = N.wasmBinary;
                  N.enablePerfMarks && performance.mark("rive:wasm-init:start"), oe.default(I({
                    // Loads Wasm bundle
                    locateFile: function() {
                      return ne;
                    }
                  }, Y ? { wasmBinary: Y } : {})).then(function(F) {
                    var ie;
                    for (N.enablePerfMarks && (performance.mark("rive:wasm-init:end"), performance.measure("rive:wasm-init", "rive:wasm-init:start", "rive:wasm-init:end")), N.runtime = F, N.errorCallbackQueue = []; N.callBackQueue.length > 0; )
                      (ie = N.callBackQueue.shift()) === null || ie === void 0 || ie(N.runtime);
                  }).catch(function(F) {
                    var ie = {
                      message: (F == null ? void 0 : F.message) || "Unknown error",
                      type: (F == null ? void 0 : F.name) || "Error",
                      // Some browsers may provide additional WebAssembly-specific details
                      wasmError: F instanceof WebAssembly.CompileError || F instanceof WebAssembly.RuntimeError,
                      originalError: F
                    };
                    console.debug("Rive WASM load error details:", ie);
                    var V = N.wasmFallbackURL, T = V !== null && ne.toLowerCase() === V.toLowerCase();
                    if (V !== null && !T)
                      console.warn("Failed to load WASM from ".concat(ne, " (").concat(ie.message, "), trying fallback URL: ").concat(V)), N.wasmBinary = null, N.setWasmUrl(V), N.loadRuntime();
                    else {
                      var O = T ? "the configured WASM URL or its fallback (".concat(V, ")") : ne, G = [
                        "Could not load Rive WASM file from ".concat(O, "."),
                        "Possible reasons:",
                        "- Network connection is down",
                        "- WebAssembly is not supported in this environment",
                        "- The WASM file is corrupted or incompatible",
                        `
Error details:`,
                        "- Type: ".concat(ie.type),
                        "- Message: ".concat(ie.message),
                        "- WebAssembly-specific error: ".concat(ie.wasmError),
                        `
To resolve, you may need to:`,
                        "1. Check your network connection",
                        "2. Set a new WASM source via RuntimeLoader.setWasmUrl()",
                        "3. Call RuntimeLoader.awaitInstance() again"
                      ].join(`
`);
                      console.error(G), N.notifyError(new Error(G));
                    }
                  });
                }, N.getInstance = function(ne, Y) {
                  N.isLoading || (N.isLoading = !0, N.loadRuntime()), N.runtime ? ne(N.runtime) : (N.callBackQueue.push(ne), Y && N.errorCallbackQueue.push(Y));
                }, N.awaitInstance = function() {
                  return new Promise(function(ne, Y) {
                    return N.getInstance(ne, Y);
                  });
                }, N.setWasmUrl = function(ne) {
                  N.wasmURL = ne;
                }, N.getWasmUrl = function() {
                  return N.wasmURL;
                }, N.setWasmFallbackUrl = function(ne) {
                  N.wasmFallbackURL = ne;
                }, N.getWasmFallbackUrl = function() {
                  return N.wasmFallbackURL;
                }, N.setWasmBinary = function(ne) {
                  if (ne instanceof ArrayBuffer || ne === null) {
                    N.wasmBinary = ne;
                    return;
                  }
                  console.error("setWasmBinary expects an ArrayBuffer or null");
                }, N.getWasmBinary = function() {
                  return N.wasmBinary;
                }, N.isLoading = !1, N.callBackQueue = [], N.wasmURL = "https://unpkg.com/".concat(C.name, "@").concat(C.version, "/rive.wasm"), N.wasmFallbackURL = "https://cdn.jsdelivr.net/npm/".concat(C.name, "@").concat(C.version, "/rive_fallback.wasm"), N.wasmBinary = null, N.errorCallbackQueue = [], N.enablePerfMarks = !1, N;
              })()
            );
          }),
          /* 4 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              default: () => C
              /* harmony export */
            });
            var oe = (() => {
              var te, N;
              var I = (N = (te = globalThis.document) == null ? void 0 : te.currentScript) == null ? void 0 : N.src;
              return async function(ne = {}) {
                var Y, F = ne, ie = !!globalThis.window, V = !!globalThis.WorkerGlobalScope;
                function T() {
                  function n(R) {
                    const j = p;
                    h = o = 0, p = /* @__PURE__ */ new Map(), j.forEach((D) => {
                      try {
                        D(R);
                      } catch (ee) {
                        console.error(ee);
                      }
                    }), this.Ra(), E && E.ub();
                  }
                  let o = 0, h = 0, p = /* @__PURE__ */ new Map(), E = null, k = null;
                  this.requestAnimationFrame = function(R) {
                    o || (o = requestAnimationFrame(n.bind(this)));
                    const j = ++h;
                    return p.set(j, R), j;
                  }, this.cancelAnimationFrame = function(R) {
                    p.delete(R), o && p.size == 0 && (cancelAnimationFrame(o), o = 0);
                  }, this.qb = function(R) {
                    k && (document.body.remove(k), k = null), R || (k = document.createElement("div"), k.style.backgroundColor = "black", k.style.position = "fixed", k.style.right = 0, k.style.top = 0, k.style.color = "white", k.style.padding = "4px", k.innerHTML = "RIVE FPS", R = function(j) {
                      k.innerHTML = "RIVE FPS " + j.toFixed(1);
                    }, document.body.appendChild(k)), E = new function() {
                      let j = 0, D = 0;
                      this.ub = function() {
                        var ee = performance.now();
                        D ? (++j, ee -= D, 1e3 < ee && (R(1e3 * j / ee), j = D = 0)) : (D = ee, j = 0);
                      };
                    }();
                  }, this.Ra = function() {
                  };
                }
                function O() {
                  console.assert(!0);
                  const n = /* @__PURE__ */ new Map();
                  let o = -1 / 0;
                  this.push = function(h) {
                    return h = h + 255 >> 8, n.has(h) && clearTimeout(n.get(h)), n.set(h, setTimeout(function() {
                      n.delete(h), n.length == 0 ? o = -1 / 0 : h == o && (o = Math.max(...n.keys()), console.assert(o < h));
                    }, 1e3)), o = Math.max(h, o), o << 8;
                  };
                }
                const G = F.onRuntimeInitialized;
                F.onRuntimeInitialized = function() {
                  G && G(), F.startFileScripts = function(R) {
                    const j = F.riveScripting;
                    return R && j && R.startScripts ? j.prepare().then(function() {
                      return R.startScripts(), R;
                    }) : Promise.resolve(R);
                  };
                  let n = F.decodeAudio;
                  F.decodeAudio = function(R, j, D = null) {
                    R = n(R, D ?? null), j(R);
                  };
                  let o = F.decodeFont;
                  F.decodeFont = function(R, j, D = null) {
                    R = o(R, D ?? null), j(R);
                  };
                  const h = F.FileAsset.prototype.decode;
                  F.FileAsset.prototype.decode = function(R, j) {
                    return h.call(this, R, j ?? null);
                  };
                  let p = F.setFallbackFontCb;
                  F.setFallbackFontCallback = typeof p == "function" ? function(R) {
                    p(R);
                  } : function() {
                    console.warn("Module.setFallbackFontCallback called, but text support is not enabled in this build.");
                  };
                  const E = F.FileAssetLoader;
                  F.ptrToAsset = (R) => {
                    let j = F.ptrToFileAsset(R);
                    return j.isImage ? F.ptrToImageAsset(R) : j.isFont ? F.ptrToFontAsset(R) : j.isAudio ? F.ptrToAudioAsset(R) : j;
                  }, F.CustomFileAssetLoader = E.extend("CustomFileAssetLoader", { __construct: function({ loadContents: R }) {
                    this.__parent.__construct.call(this), this.eb = R;
                  }, loadContents: function(R, j) {
                    return R = F.ptrToAsset(R), this.eb(R, j);
                  } }), F.CDNFileAssetLoader = E.extend("CDNFileAssetLoader", { __construct: function(R) {
                    this.__parent.__construct.call(this), this.gb = R ?? null;
                  }, loadContents: function(R) {
                    let j = F.ptrToAsset(R);
                    if (R = j.cdnUuid, R === "") return !1;
                    const D = this.gb ?? null;
                    return (function(ee, w) {
                      var e = new XMLHttpRequest();
                      e.responseType = "arraybuffer", e.onreadystatechange = function() {
                        e.readyState == 4 && e.status == 200 && w(e);
                      }, e.open("GET", ee, !0), e.send(null);
                    })(j.cdnBaseUrl + "/" + R, (ee) => {
                      j.decode(new Uint8Array(ee.response), D);
                    }), !0;
                  } }), F.FallbackFileAssetLoader = E.extend("FallbackFileAssetLoader", { __construct: function() {
                    this.__parent.__construct.call(this), this.Qa = [];
                  }, addLoader: function(R) {
                    this.Qa.push(R);
                  }, loadContents: function(R, j) {
                    for (let D of this.Qa) if (D.loadContents(R, j)) return !0;
                    return !1;
                  } });
                  let k = F.computeAlignment;
                  F.computeAlignment = function(R, j, D, ee, w = 1) {
                    return k.call(this, R, j, D, ee, w);
                  };
                }, (function() {
                  function n(w, e) {
                    const r = w.kb, m = w.da, v = w.ca, _ = w.Ba ?? { i: !1 }, a = (c, u) => {
                      c = new Uint8Array(e().buffer, c, u);
                      const d = 4096 < u ? w.Ga(u) : w.ua(u);
                      if (d === 0) throw Error(`could not stage ${u} bytes for the host`);
                      return w.Z().set(c, d), _.i && (_.la += u), d;
                    }, t = (c, u) => {
                      c !== 0 && 4096 < u && w.Da(c);
                    }, s = (c, u, d) => {
                      new Uint8Array(e().buffer, u, d).set(w.Z().subarray(c, c + d)), _.i && (_.ja += d);
                    }, f = (c) => (u) => {
                      const d = new Uint32Array(e().buffer, u - 4, 1)[0], S = m();
                      let y = 0;
                      try {
                        y = a(u, d), r.md(c, y, d);
                      } finally {
                        t(y, d), v(S);
                      }
                    };
                    return {
                      env: { seed: () => Date.now() * Math.random(), emscripten_get_now: () => performance.now(), emscripten_date_now: () => Date.now(), trace: (c, u, d, S, y, P, U) => {
                        var pe = console, Oe = pe.log;
                        const Ze = e().buffer, Ct = new Uint32Array(Ze, c - 4, 1)[0];
                        return c = new TextDecoder("utf-16le").decode(new Uint8Array(Ze, c, Ct)), Oe.call(pe, "trace: " + c, ...[d, S, y, P, U].slice(0, u));
                      }, "console.log": f(0), "console.debug": f(0), "console.info": f(0), "console.warn": f(0), "console.error": f(0), "console.time": f(1), "console.timeLog": f(2), "console.timeEnd": f(3) },
                      rive_rt_v1: { log: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, d), r.Zg(c, y, d);
                        } finally {
                          t(y, d), v(S);
                        }
                      }, mark_needs_update: r.$g, budget_exceeded: r.Tg, error: (c, u) => {
                        const d = m();
                        let S = 0;
                        try {
                          S = a(c, u), r.Xg(S, u);
                        } finally {
                          t(S, u), v(d);
                        }
                      }, now: () => performance.now(), date_now: () => Date.now(), debug_enter: r.Ug, debug_line: r.Wg, debug_leave: r.Vg, utc_offset: r.ah, is_dst: r.Yg, zone_name: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, d);
                          const P = r.bh(c, y, d);
                          return s(y, u, d), P;
                        } finally {
                          t(y, d), v(S);
                        }
                      } },
                      rive_data_v1: {
                        view_model: r.ie,
                        root_view_model: r.ce,
                        global_view_model: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Jd(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        global_view_model_names: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.Kd(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        context: r.yd,
                        context_parent: r.zd,
                        context_view_model: r.Bd,
                        context_release: r.Ad,
                        has_view_model: (c, u) => {
                          const d = m();
                          let S = 0;
                          try {
                            return S = a(c, u), r.Ld(S, u);
                          } finally {
                            t(S, u), v(d);
                          }
                        },
                        new_view_model: (c, u, d, S) => {
                          const y = m();
                          let P = 0, U = 0;
                          try {
                            return P = a(c, u), U = a(d, S), r.Zd(P, u, U, S);
                          } finally {
                            t(U, S), t(P, u), v(y);
                          }
                        },
                        vmi_release: r.xe,
                        vmi_number: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.ve(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_boolean: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.ne(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_string: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.ye(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_trigger: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Ae(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_color: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.oe(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_view_model: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Be(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_property: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0, pe = 0;
                          try {
                            U = a(u, d), pe = a(S, 4 * y);
                            const Oe = r.we(c, U, d, pe, y);
                            return s(pe, S, 4 * y), Oe;
                          } finally {
                            t(pe, 4 * y), t(U, d), v(P);
                          }
                        },
                        vmi_instance: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.te(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_symbol_index: r.ze,
                        vmi_equal: r.qe,
                        view_model_get: r.je,
                        vmi_list: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.ue(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_enum: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.pe(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_image: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.se(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_font: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.re(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_blob: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.me(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        vmi_artboard: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.le(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        image_get: r.Md,
                        image_set: r.Nd,
                        font_get: r.Gd,
                        font_set: r.Id,
                        font_release: r.Hd,
                        blob_present: r.sd,
                        blob_get: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.qd(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        blob_name: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.rd(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        blob_set: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d), r.td(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        blob_clear: r.pd,
                        artboard_get: r.nd,
                        artboard_set: r.od,
                        enum_get: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.Dd(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(
                              y,
                              d
                            ), v(S);
                          }
                        },
                        enum_set: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d), r.Ed(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        enum_values: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.Fd(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        prop_release: r.be,
                        trigger_fire: r.ge,
                        list_length: r.Rd,
                        list_push: r.Td,
                        list_pop: r.Sd,
                        list_shift: r.Xd,
                        list_clear: r.Od,
                        list_swap: r.Yd,
                        list_insert: r.Qd,
                        list_remove: r.Ud,
                        list_remove_at: r.Wd,
                        list_remove_all_of: r.Vd,
                        list_get: r.Pd,
                        view_model_set: r.ke,
                        color_get: r.wd,
                        color_set: r.xd,
                        number_get: r.$d,
                        number_set: r.ae,
                        boolean_get: r.ud,
                        boolean_set: r.vd,
                        string_get: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.ee(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        string_changed: r.de,
                        string_set: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d), r.fe(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        watch: r.Ce,
                        unwatch: r.he,
                        convert_result: (c, u, d, S, y, P) => {
                          const U = m();
                          let pe = 0;
                          try {
                            pe = a(y, P), r.Cd(c, u, d, S, pe, P);
                          } finally {
                            t(pe, P), v(U);
                          }
                        }
                      },
                      rive_artboard_v1: {
                        release: r.vc,
                        advance: r.Ob,
                        draw: r.Wb,
                        instance: r.fc,
                        data: r.Vb,
                        width: r.Ac,
                        height: r.ec,
                        set_width: r.zc,
                        set_height: r.yc,
                        frame_origin: r.cc,
                        set_frame_origin: r.xc,
                        bounds: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.Ub(c, y, d), s(y, u, 4 * d);
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        pointer_event: r.tc,
                        scroll_event: r.wc,
                        gamepad_event: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.dc(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        animation: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Pb(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        animation_release: r.Sb,
                        animation_duration: r.Rb,
                        animation_advance: r.Qb,
                        animation_set_time: r.Tb,
                        add_to_path: r.Nb,
                        node: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.hc(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        node_release: r.oc,
                        node_transform: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.rc(c, y, d), s(y, u, 4 * d);
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_set: r.pc,
                        node_world_transform: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.sc(c, y, d), s(y, u, 4 * d);
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_set_world_transform: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.qc(c, y, d);
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_decompose: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.jc(
                              c,
                              y,
                              d
                            );
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_path_verbs: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.nc(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        node_path_points: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.mc(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_paint: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.kc(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        node_children: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.ic(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(
                              y,
                              4 * d
                            ), v(S);
                          }
                        },
                        node_parent: r.lc,
                        property_key: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.uc(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        draw_visit: r.Yb,
                        draw_modulated: r.Xb,
                        drawable_draw: r.Zb,
                        drawable_value: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            P = a(d, 4 * S);
                            const U = r.bc(c, u, P, S);
                            return s(P, d, 4 * S), U;
                          } finally {
                            t(P, 4 * S), v(y);
                          }
                        },
                        drawable_string: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            P = a(d, S);
                            const U = r.ac(c, u, P, S);
                            return s(P, d, S), U;
                          } finally {
                            t(P, S), v(y);
                          }
                        },
                        drawable_properties: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d);
                            const P = r.$b(c, y, d);
                            return s(y, u, d), P;
                          } finally {
                            t(y, d), v(S);
                          }
                        }
                      },
                      rive_audio_v1: {
                        source: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Tc(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        source_release: r.Wc,
                        source_duration: r.Vc,
                        source_sample_rate: r.Xc,
                        source_channels: r.Uc,
                        play: r.Bc,
                        play_at_time: r.Dc,
                        play_in_time: r.Fc,
                        play_at_frame: r.Cc,
                        play_in_frame: r.Ec,
                        time: r.Yc,
                        time_frame: r.Zc,
                        sample_rate: r.Gc,
                        sound_release: r.Kc,
                        sound_play: r.Jc,
                        sound_pause: r.Ic,
                        sound_resume: r.Lc,
                        sound_stop: r.Pc,
                        sound_seek: r.Mc,
                        sound_seek_frame: r.Nc,
                        sound_completed: r.Hc,
                        sound_time: r.Qc,
                        sound_time_frame: r.Rc,
                        sound_volume: r.Sc,
                        sound_set_volume: r.Oc
                      },
                      rive_path_v1: { new: r.Eg, update: (c, u, d, S, y, P) => {
                        const U = m();
                        let pe = 0, Oe = 0;
                        try {
                          pe = a(u, d), Oe = a(S, 4 * y), r.Hg(c, pe, d, Oe, y, P);
                        } finally {
                          t(Oe, 4 * y), t(pe, d), v(U);
                        }
                      }, release: r.Gg, add: r.Cg, verbs: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, d);
                          const P = r.Ig(c, y, d);
                          return s(y, u, d), P;
                        } finally {
                          t(y, d), v(S);
                        }
                      }, points: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, 4 * d);
                          const P = r.Fg(c, y, d);
                          return s(y, u, 4 * d), P;
                        } finally {
                          t(y, 4 * d), v(S);
                        }
                      }, effect_result: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          P = a(c, u), U = a(d, 4 * S), r.Dg(P, u, U, S);
                        } finally {
                          t(U, 4 * S), t(P, u), v(y);
                        }
                      } },
                      rive_measure_v1: { path_new: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          return P = a(c, u), U = a(d, 4 * S), r.hg(P, u, U, S);
                        } finally {
                          t(U, 4 * S), t(P, u), v(y);
                        }
                      }, contours_new: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          return P = a(c, u), U = a(d, 4 * S), r.cg(P, u, U, S);
                        } finally {
                          t(U, 4 * S), t(P, u), v(y);
                        }
                      }, contour_next: r.bg, length: r.gg, is_closed: r.fg, pos_tan: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          P = a(d, 4 * S), r.ig(c, u, P, S), s(P, d, 4 * S);
                        } finally {
                          t(P, 4 * S), v(y);
                        }
                      }, warp: (c, u, d, S, y) => {
                        const P = m();
                        let U = 0;
                        try {
                          U = a(S, 4 * y), r.kg(c, u, d, U, y), s(U, S, 4 * y);
                        } finally {
                          t(U, 4 * y), v(P);
                        }
                      }, extract: r.dg, extract_read: (c, u, d, S, y) => {
                        const P = m();
                        let U = 0, pe = 0;
                        try {
                          U = a(u, d), pe = a(S, 4 * y);
                          const Oe = r.eg(c, U, d, pe, y);
                          return s(U, u, d), s(pe, S, 4 * y), Oe;
                        } finally {
                          t(pe, 4 * y), t(U, d), v(P);
                        }
                      }, release: r.jg },
                      rive_paint_v1: { new: r.wg, release: r.xg, style: r.Ag, color: r.tg, thickness: r.Bg, join: r.vg, cap: r.sg, blend_mode: r.rg, feather: r.ug, shader: r.yg, shader_transform: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, 4 * d), r.zg(c, y, d);
                        } finally {
                          t(
                            y,
                            4 * d
                          ), v(S);
                        }
                      } },
                      rive_canvas_v1: { new: r.hd, release: r.jd, width: r.ld, height: r.fd, resize: r.kd, image: r.gd, begin_frame: r.dd, end_frame: r.ed },
                      rive_gpu_v1: {
                        features: (c, u) => {
                          const d = m();
                          let S = 0;
                          try {
                            S = a(c, 4 * u);
                            const y = r.pf(S, u);
                            return s(S, c, 4 * u), y;
                          } finally {
                            t(S, 4 * u), v(d);
                          }
                        },
                        canvas_new: r.lf,
                        canvas_release: r.mf,
                        canvas_color_view: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.jf(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        canvas_image: r.kf,
                        canvas_resize: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0;
                          try {
                            U = a(S, 4 * y);
                            const pe = r.nf(c, u, d, U, y);
                            return s(U, S, 4 * y), pe;
                          } finally {
                            t(U, 4 * y), v(P);
                          }
                        },
                        target_view: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.Of(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        pass_begin: (c, u, d, S) => {
                          const y = m();
                          let P = 0, U = 0;
                          try {
                            return P = a(c, u), U = a(d, S), r.rf(P, u, U, S);
                          } finally {
                            t(U, S), t(P, u), v(y);
                          }
                        },
                        pass_set_pipeline: r.zf,
                        pass_set_vertex_buffer: r.Cf,
                        pass_set_index_buffer: r.yf,
                        pass_set_bind_group: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0;
                          try {
                            U = a(S, y), r.wf(c, u, d, U, y);
                          } finally {
                            t(U, y), v(P);
                          }
                        },
                        pass_set_viewport: r.Df,
                        pass_set_scissor: r.Af,
                        pass_set_stencil_reference: r.Bf,
                        pass_set_blend_color: r.xf,
                        pass_draw: r.sf,
                        pass_draw_indexed: r.tf,
                        pass_finish: r.uf,
                        pass_release: r.vf,
                        image_view: r.qf,
                        buffer_new: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0;
                          try {
                            return U = a(S, y), r.ff(c, u, d, U, y);
                          } finally {
                            t(U, y), v(P);
                          }
                        },
                        buffer_update: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            P = a(d, S), r.hf(c, u, P, S);
                          } finally {
                            t(P, S), v(y);
                          }
                        },
                        buffer_release: r.gf,
                        texture_new: (c, u) => {
                          const d = m();
                          let S = 0;
                          try {
                            return S = a(c, u), r.Pf(S, u);
                          } finally {
                            t(S, u), v(d);
                          }
                        },
                        texture_upload: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0, pe = 0;
                          try {
                            U = a(u, d), pe = a(S, y), r.Rf(c, U, d, pe, y);
                          } finally {
                            t(pe, y), t(U, d), v(P);
                          }
                        },
                        texture_release: r.Qf,
                        sampler_new: (c, u) => {
                          const d = m();
                          let S = 0;
                          try {
                            return S = a(c, u), r.Gf(S, u);
                          } finally {
                            t(S, u), v(d);
                          }
                        },
                        sampler_release: r.Hf,
                        texture_view_new: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Sf(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        texture_view_release: r.Tf,
                        shader_target: r.Nf,
                        shader_asset_bytes: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0, pe = 0;
                          try {
                            U = a(u, d), pe = a(S, y);
                            const Oe = r.If(c, U, d, pe, y);
                            return s(pe, S, y), Oe;
                          } finally {
                            t(
                              pe,
                              y
                            ), t(U, d), v(P);
                          }
                        },
                        shader_asset_id: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.Jf(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        shader_module_from_asset: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            return P = a(u, d), r.Kf(c, P, d, S);
                          } finally {
                            t(P, d), v(y);
                          }
                        },
                        shader_module_new: (c, u, d, S) => {
                          const y = m();
                          let P = 0, U = 0;
                          try {
                            return P = a(c, u), U = a(d, S), r.Lf(P, u, U, S);
                          } finally {
                            t(U, S), t(P, u), v(y);
                          }
                        },
                        shader_module_release: r.Mf,
                        bind_group_layout_new: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            return y = a(u, d), r.bf(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        bind_group_layout_release: r.cf,
                        bind_group_layout_from_shader: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            return P = a(d, 4 * S), r.$e(c, u, P, S);
                          } finally {
                            t(P, 4 * S), v(y);
                          }
                        },
                        bind_group_layout_from_shaders: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0;
                          try {
                            return U = a(S, 4 * y), r.af(c, u, d, U, y);
                          } finally {
                            t(U, 4 * y), v(P);
                          }
                        },
                        bind_group_new: (c, u, d, S, y, P, U) => {
                          const pe = m();
                          let Oe = 0, Ze = 0, Ct = 0;
                          try {
                            return Oe = a(u, d), Ze = a(S, y), Ct = a(P, U), r.df(c, Oe, d, Ze, y, Ct, U);
                          } finally {
                            t(Ct, U), t(Ze, y), t(Oe, d), v(pe);
                          }
                        },
                        bind_group_release: r.ef,
                        pipeline_new: (c, u, d, S) => {
                          const y = m();
                          let P = 0, U = 0;
                          try {
                            return P = a(c, u), U = a(d, S), r.Ef(P, u, U, S);
                          } finally {
                            t(U, S), t(P, u), v(y);
                          }
                        },
                        pipeline_release: r.Ff
                      },
                      rive_mat4_v1: { multiply: (c, u, d, S, y, P) => {
                        const U = m();
                        let pe = 0, Oe = 0, Ze = 0;
                        try {
                          pe = a(c, u), Oe = a(d, S), Ze = a(y, P), r.ag(pe, u, Oe, S, Ze, P), s(pe, c, u);
                        } finally {
                          t(Ze, P), t(Oe, S), t(pe, u), v(U);
                        }
                      }, invert: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          P = a(c, u), U = a(d, S);
                          const pe = r.$f(P, u, U, S);
                          return s(P, c, u), pe;
                        } finally {
                          t(U, S), t(P, u), v(y);
                        }
                      } },
                      rive_buffer_v1: { new: r.ad, update: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, d), r.cd(c, y, d);
                        } finally {
                          t(y, d), v(S);
                        }
                      }, release: r.bd },
                      rive_mesh_instances_v1: {
                        new: r.lg,
                        resize: r.ng,
                        update: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            P = a(d, S), r.og(c, u, P, S);
                          } finally {
                            t(P, S), v(y);
                          }
                        },
                        release: r.mg
                      },
                      rive_blob_v1: { asset_bytes: (c, u, d, S, y) => {
                        const P = m();
                        let U = 0, pe = 0;
                        try {
                          U = a(u, d), pe = a(S, y);
                          const Oe = r.$c(c, U, d, pe, y);
                          return s(pe, S, y), Oe;
                        } finally {
                          t(pe, y), t(U, d), v(P);
                        }
                      } },
                      rive_image_v1: { from_asset: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          return y = a(u, d), r.Wf(c, y, d);
                        } finally {
                          t(y, d), v(S);
                        }
                      }, width: r.Zf, height: r.Xf, release: r.Yf, decode: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          return y = a(c, u), r.Uf(y, u, d);
                        } finally {
                          t(y, u), v(S);
                        }
                      }, decode_cancel: r.Vf },
                      rive_font_v1: { from_asset: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          return y = a(u, d), r.Re(c, y, d);
                        } finally {
                          t(y, d), v(S);
                        }
                      }, decode: (c, u) => {
                        const d = m();
                        let S = 0;
                        try {
                          return S = a(c, u), r.Pe(S, u);
                        } finally {
                          t(S, u), v(d);
                        }
                      }, release: r.Xe, metrics: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, 4 * d), r.We(c, y, d), s(y, u, 4 * d);
                        } finally {
                          t(y, 4 * d), v(S);
                        }
                      }, weight: r.Ye, is_italic: r.Ve, axis_count: r.Ne, axis: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          P = a(d, 4 * S), r.Me(c, u, P, S), s(P, d, 4 * S);
                        } finally {
                          t(P, 4 * S), v(y);
                        }
                      }, axis_value: r.Oe, features: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, 4 * d);
                          const P = r.Qe(c, y, d);
                          return s(y, u, 4 * d), P;
                        } finally {
                          t(y, 4 * d), v(S);
                        }
                      }, has_glyph: r.Ue, with_options: (c, u, d, S, y) => {
                        const P = m();
                        let U = 0, pe = 0;
                        try {
                          return U = a(u, 4 * d), pe = a(S, 4 * y), r.Ze(c, U, d, pe, y);
                        } finally {
                          t(pe, 4 * y), t(U, 4 * d), v(P);
                        }
                      }, glyph_verbs: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          P = a(d, S);
                          const U = r.Te(c, u, P, S);
                          return s(P, d, S), U;
                        } finally {
                          t(P, S), v(y);
                        }
                      }, glyph_points: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          P = a(d, 4 * S);
                          const U = r.Se(c, u, P, S);
                          return s(P, d, 4 * S), U;
                        } finally {
                          t(P, 4 * S), v(y);
                        }
                      } },
                      rive_text_v1: {
                        new: r.rh,
                        release: r.sh,
                        append: (c, u, d, S, y, P, U, pe, Oe) => {
                          const Ze = m();
                          let Ct = 0;
                          try {
                            Ct = a(u, d), r.hh(c, Ct, d, S, y, P, U, pe, Oe);
                          } finally {
                            t(Ct, d), v(Ze);
                          }
                        },
                        clear: r.kh,
                        layout: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, d), r.oh(c, y, d);
                          } finally {
                            t(y, d), v(S);
                          }
                        },
                        draw: r.lh,
                        bounds: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d), r.ih(c, y, d), s(y, u, 4 * d);
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        length: r.ph,
                        lines: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.qh(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        runs: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(
                              u,
                              4 * d
                            );
                            const P = r.th(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        glyphs: (c, u, d) => {
                          const S = m();
                          let y = 0;
                          try {
                            y = a(u, 4 * d);
                            const P = r.mh(c, y, d);
                            return s(y, u, 4 * d), P;
                          } finally {
                            t(y, 4 * d), v(S);
                          }
                        },
                        hit_test: r.nh,
                        caret: (c, u, d, S) => {
                          const y = m();
                          let P = 0;
                          try {
                            P = a(d, 4 * S);
                            const U = r.jh(c, u, P, S);
                            return s(P, d, 4 * S), U;
                          } finally {
                            t(P, 4 * S), v(y);
                          }
                        },
                        selection_rects: (c, u, d, S, y) => {
                          const P = m();
                          let U = 0;
                          try {
                            U = a(S, 4 * y);
                            const pe = r.uh(c, u, d, U, y);
                            return s(U, S, 4 * y), pe;
                          } finally {
                            t(U, 4 * y), v(P);
                          }
                        }
                      },
                      rive_shader_v1: { linear: r.dh, radial: r.eh, release: r.fh },
                      rive_test_v1: { blob: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          P = a(c, u), U = a(d, S);
                          const pe = r.gh(P, u, U, S);
                          return s(U, d, S), pe;
                        } finally {
                          t(U, S), t(P, u), v(y);
                        }
                      } },
                      rive_transition_v1: { child_draw: r.vh, child_width: r.xh, child_height: r.wh },
                      rive_renderer_v1: { save: r.Rg, restore: r.Qg, transform: r.Sg, draw_path: r.Ng, clip_path: r.Jg, modulate_opacity: r.Pg, modulate_color: r.Og, draw_image: r.Kg, draw_image_mesh: r.Lg, draw_image_mesh_instanced: r.Mg },
                      rive_net_v1: { fetch: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          return y = a(c, u), r.pg(y, u, d);
                        } finally {
                          t(
                            y,
                            u
                          ), v(S);
                        }
                      }, fetch_cancel: r.qg },
                      rive_file_v1: { decode: (c, u, d, S) => {
                        const y = m();
                        let P = 0, U = 0;
                        try {
                          P = a(c, u), U = a(d, 4 * S);
                          const pe = r.Ke(P, u, U, S);
                          return s(U, d, 4 * S), pe;
                        } finally {
                          t(U, 4 * S), t(P, u), v(y);
                        }
                      }, release: r.Le, artboard_count: r.De, artboard_name: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          P = a(d, S);
                          const U = r.Ee(c, u, P, S);
                          return s(P, d, S), U;
                        } finally {
                          t(P, S), v(y);
                        }
                      }, bindable: (c, u, d, S) => {
                        const y = m();
                        let P = 0;
                        try {
                          return P = a(u, d), r.Fe(c, P, d, S);
                        } finally {
                          t(P, d), v(y);
                        }
                      }, bindable_release: r.Je, bindable_name: (c, u, d) => {
                        const S = m();
                        let y = 0;
                        try {
                          y = a(u, d);
                          const P = r.Ie(c, y, d);
                          return s(y, u, d), P;
                        } finally {
                          t(y, d), v(S);
                        }
                      }, bindable_data: r.Ge, bindable_equal: r.He }
                    };
                  }
                  function o(w, e) {
                    const r = e.Ba ?? { i: !1 }, m = () => {
                      const a = Error(e.j);
                      throw e.j = null, a;
                    }, v = () => {
                      throw Error("librive faulted in a nested script call");
                    }, _ = () => {
                      throw Error("script VM was released");
                    };
                    return {
                      Zg: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(0)),
                      $g: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(1)),
                      Tg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(2)),
                      Xg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(3)),
                      Ug: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(4)),
                      Wg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(5)),
                      Vg: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g);
                        } catch (s) {
                          var t = s;
                          throw e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(6)),
                      ah: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(7)),
                      Yg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(8)),
                      bh: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(9)),
                      ie: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(10)),
                      ce: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(11)),
                      Jd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(12)),
                      Kd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(13)),
                      yd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(14)),
                      zd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(15)),
                      Bd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(16)),
                      Ad: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(17)),
                      Ld: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(18)),
                      Zd: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(19)),
                      xe: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(20)),
                      ve: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(21)),
                      ne: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(22)),
                      ye: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(23)),
                      Ae: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(24)),
                      oe: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(25)),
                      Be: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(26)),
                      we: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(27)),
                      te: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(28)),
                      ze: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(29)),
                      qe: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(30)),
                      je: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(31)),
                      ue: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(32)),
                      pe: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(33)),
                      se: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(34)),
                      re: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(35)),
                      me: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(
                            e.g,
                            t,
                            s,
                            f
                          );
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(36)),
                      le: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(37)),
                      Md: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(38)),
                      Nd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(39)),
                      Gd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(40)),
                      Id: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(41)),
                      Hd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(42)),
                      sd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(43)),
                      qd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(
                            e.g,
                            t,
                            s,
                            f
                          );
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(44)),
                      rd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(45)),
                      td: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(46)),
                      pd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(47)),
                      nd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(
                            e.g,
                            t
                          );
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(48)),
                      od: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(49)),
                      Dd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(50)),
                      Ed: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(51)),
                      Fd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(52)),
                      be: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(53)),
                      ge: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(54)),
                      Rd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(55)),
                      Td: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(56)),
                      Sd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(57)),
                      Xd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(58)),
                      Od: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(59)),
                      Yd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(60)),
                      Qd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(61)),
                      Ud: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(62)),
                      Wd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(63)),
                      Vd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(64)),
                      Pd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(65)),
                      ke: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(66)),
                      wd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(67)),
                      xd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(68)),
                      $d: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(69)),
                      ae: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(70)),
                      ud: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(71)),
                      vd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(72)),
                      ee: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(73)),
                      de: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(74)),
                      fe: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(75)),
                      Ce: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(76)),
                      he: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(77)),
                      Cd: /* @__PURE__ */ ((a) => (t, s, f, c, u, d) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(78)),
                      vc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(79)),
                      Ob: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(80)),
                      Wb: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(81)),
                      fc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(82)),
                      Vb: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(83)),
                      Ac: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(84)),
                      ec: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(85)),
                      zc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(86)),
                      yc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(87)),
                      cc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(88)),
                      xc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(
                            e.g,
                            t,
                            s
                          );
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(89)),
                      Ub: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(90)),
                      tc: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(91)),
                      wc: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S, y, P) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let U;
                        try {
                          U = a(e.g, t, s, f, c, u, d, S, y, P);
                        } catch (pe) {
                          throw t = pe, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), U;
                      })(w(92)),
                      dc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(93)),
                      Pb: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(94)),
                      Sb: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(95)),
                      Rb: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(96)),
                      Qb: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(97)),
                      Tb: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(98)),
                      Nb: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S, y) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S, y);
                        } catch (P) {
                          throw t = P, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(99)),
                      hc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(100)),
                      oc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(101)),
                      rc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(102)),
                      pc: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(103)),
                      sc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(104)),
                      qc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(105)),
                      jc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(106)),
                      nc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(107)),
                      mc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(108)),
                      kc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(109)),
                      ic: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(110)),
                      lc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(111)),
                      uc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(112)),
                      Yb: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(113)),
                      Xb: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(114)),
                      Zb: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(115)),
                      bc: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(116)),
                      ac: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(117)),
                      $b: ((a) => a === void 0 ? h("rive_artboard_v1", "drawable_properties") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(118)),
                      Tc: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(119)),
                      Wc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(120)),
                      Vc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(121)),
                      Xc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(122)),
                      Uc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(123)),
                      Bc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(124)),
                      Dc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(125)),
                      Fc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(126)),
                      Cc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(127)),
                      Ec: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(128)),
                      Yc: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(129)),
                      Zc: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(130)),
                      Gc: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(131)),
                      Kc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(132)),
                      Jc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(133)),
                      Ic: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(134)),
                      Lc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(135)),
                      Pc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(136)),
                      Mc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(137)),
                      Nc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(138)),
                      Hc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(139)),
                      Qc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(140)),
                      Rc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(141)),
                      Sc: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(142)),
                      Oc: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(143)),
                      Eg: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(144)),
                      Hg: /* @__PURE__ */ ((a) => (t, s, f, c, u, d) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(145)),
                      Gg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(146)),
                      Cg: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S, y) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S, y);
                        } catch (P) {
                          throw t = P, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(147)),
                      Ig: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(148)),
                      Fg: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(149)),
                      Dg: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(150)),
                      hg: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(151)),
                      cg: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(152)),
                      bg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(153)),
                      gg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(154)),
                      fg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(155)),
                      ig: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(156)),
                      kg: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(157)),
                      dg: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(158)),
                      eg: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(159)),
                      jg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(160)),
                      wg: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(161)),
                      xg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(162)),
                      Ag: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(163)),
                      tg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(164)),
                      Bg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(165)),
                      vg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(166)),
                      sg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(167)),
                      rg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(168)),
                      ug: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(169)),
                      yg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(170)),
                      zg: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(171)),
                      hd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(172)),
                      jd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(173)),
                      ld: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(174)),
                      fd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(175)),
                      kd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(176)),
                      gd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(177)),
                      dd: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(178)),
                      ed: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(179)),
                      pf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(180)),
                      lf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(181)),
                      mf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(182)),
                      jf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(183)),
                      kf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(184)),
                      nf: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(185)),
                      Of: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(186)),
                      rf: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(
                            e.g,
                            t,
                            s,
                            f,
                            c
                          );
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(187)),
                      zf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(188)),
                      Cf: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(189)),
                      yf: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(190)),
                      wf: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(
                            e.g,
                            t,
                            s,
                            f,
                            c,
                            u
                          );
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(191)),
                      Df: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S);
                        } catch (y) {
                          throw t = y, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(192)),
                      Af: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(193)),
                      Bf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(194)),
                      xf: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(195)),
                      sf: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(196)),
                      tf: /* @__PURE__ */ ((a) => (t, s, f, c, u, d) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(197)),
                      uf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(198)),
                      vf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(
                            e.g,
                            t
                          );
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(199)),
                      qf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(200)),
                      ff: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(201)),
                      hf: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(202)),
                      gf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(203)),
                      Pf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(204)),
                      Rf: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(205)),
                      Qf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(206)),
                      Gf: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(207)),
                      Hf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(208)),
                      Sf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(209)),
                      Tf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(210)),
                      Nf: /* @__PURE__ */ ((a) => () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(211)),
                      If: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(212)),
                      Jf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(213)),
                      Kf: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(214)),
                      Lf: ((a) => a === void 0 ? h("rive_gpu_v1", "shader_module_new") : (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(215)),
                      Mf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(216)),
                      bf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(217)),
                      cf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(218)),
                      $e: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(219)),
                      af: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(220)),
                      df: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let y;
                        try {
                          y = a(e.g, t, s, f, c, u, d, S);
                        } catch (P) {
                          throw t = P, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), y;
                      })(w(221)),
                      ef: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(222)),
                      Ef: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(223)),
                      Ff: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(224)),
                      ag: /* @__PURE__ */ ((a) => (t, s, f, c, u, d) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(225)),
                      $f: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(226)),
                      ad: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(227)),
                      cd: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(228)),
                      bd: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(229)),
                      lg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(230)),
                      ng: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(231)),
                      og: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(232)),
                      mg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(233)),
                      $c: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(234)),
                      Wf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(235)),
                      Zf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(236)),
                      Xf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(237)),
                      Yf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(238)),
                      Uf: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(239)),
                      Vf: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(240)),
                      Re: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(241)),
                      Pe: ((a) => a === void 0 ? h("rive_font_v1", "decode") : (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(242)),
                      Xe: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(243)),
                      We: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(244)),
                      Ye: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(245)),
                      Ve: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(246)),
                      Ne: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(247)),
                      Me: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(248)),
                      Oe: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(249)),
                      Qe: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(250)),
                      Ue: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(251)),
                      Ze: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(252)),
                      Te: ((a) => a === void 0 ? h(
                        "rive_font_v1",
                        "glyph_verbs"
                      ) : (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(253)),
                      Se: ((a) => a === void 0 ? h("rive_font_v1", "glyph_points") : (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(254)),
                      rh: ((a) => a === void 0 ? h("rive_text_v1", "new") : () => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          var t = a(e.g);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), t;
                      })(w(255)),
                      sh: ((a) => a === void 0 ? h("rive_text_v1", "release") : (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(256)),
                      hh: ((a) => a === void 0 ? h("rive_text_v1", "append") : (t, s, f, c, u, d, S, y, P) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S, y, P);
                        } catch (U) {
                          throw t = U, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(257)),
                      kh: ((a) => a === void 0 ? h("rive_text_v1", "clear") : (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(258)),
                      oh: ((a) => a === void 0 ? h(
                        "rive_text_v1",
                        "layout"
                      ) : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(259)),
                      lh: ((a) => a === void 0 ? h("rive_text_v1", "draw") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(260)),
                      ih: ((a) => a === void 0 ? h("rive_text_v1", "bounds") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(261)),
                      ph: ((a) => a === void 0 ? h("rive_text_v1", "length") : (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(262)),
                      qh: ((a) => a === void 0 ? h("rive_text_v1", "lines") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(263)),
                      th: ((a) => a === void 0 ? h("rive_text_v1", "runs") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(264)),
                      mh: ((a) => a === void 0 ? h("rive_text_v1", "glyphs") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(265)),
                      nh: ((a) => a === void 0 ? h("rive_text_v1", "hit_test") : (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(266)),
                      jh: ((a) => a === void 0 ? h("rive_text_v1", "caret") : (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(267)),
                      uh: ((a) => a === void 0 ? h("rive_text_v1", "selection_rects") : (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let d;
                        try {
                          d = a(e.g, t, s, f, c, u);
                        } catch (S) {
                          throw t = S, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), d;
                      })(w(268)),
                      dh: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let y;
                        try {
                          y = a(e.g, t, s, f, c, u, d, S);
                        } catch (P) {
                          throw t = P, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), y;
                      })(w(269)),
                      eh: /* @__PURE__ */ ((a) => (t, s, f, c, u, d) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let S;
                        try {
                          S = a(e.g, t, s, f, c, u, d);
                        } catch (y) {
                          throw t = y, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), S;
                      })(w(270)),
                      fh: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(271)),
                      gh: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(272)),
                      vh: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(273)),
                      xh: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(274)),
                      wh: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(275)),
                      Rg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(276)),
                      Qg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(277)),
                      Sg: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S);
                        } catch (y) {
                          throw t = y, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(278)),
                      Ng: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(279)),
                      Jg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(280)),
                      Pg: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(281)),
                      Og: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(282)),
                      Kg: /* @__PURE__ */ ((a) => (t, s, f, c, u) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(
                            e.g,
                            t,
                            s,
                            f,
                            c,
                            u
                          );
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(283)),
                      Lg: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S, y) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S, y);
                        } catch (P) {
                          throw t = P, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(284)),
                      Mg: /* @__PURE__ */ ((a) => (t, s, f, c, u, d, S) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f, c, u, d, S);
                        } catch (y) {
                          throw t = y, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(285)),
                      pg: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(286)),
                      qg: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(287)),
                      Ke: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(288)),
                      Le: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(289)),
                      De: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(290)),
                      Ee: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(291)),
                      Fe: /* @__PURE__ */ ((a) => (t, s, f, c) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let u;
                        try {
                          u = a(e.g, t, s, f, c);
                        } catch (d) {
                          throw t = d, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), u;
                      })(w(292)),
                      Je: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t);
                        } catch (s) {
                          throw t = s, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(293)),
                      Ie: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let c;
                        try {
                          c = a(e.g, t, s, f);
                        } catch (u) {
                          throw t = u, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), c;
                      })(w(294)),
                      Ge: /* @__PURE__ */ ((a) => (t) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let s;
                        try {
                          s = a(e.g, t);
                        } catch (f) {
                          throw t = f, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), s;
                      })(w(295)),
                      He: /* @__PURE__ */ ((a) => (t, s) => {
                        e.g === 0 && _(), r.i && r.l++;
                        let f;
                        try {
                          f = a(e.g, t, s);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        return e.h && v(), e.j !== null && m(), f;
                      })(w(296)),
                      md: /* @__PURE__ */ ((a) => (t, s, f) => {
                        e.g === 0 && _(), r.i && r.l++;
                        try {
                          a(e.g, t, s, f);
                        } catch (c) {
                          throw t = c, e.h = !0, t;
                        }
                        e.h && v(), e.j !== null && m();
                      })(w(297))
                    };
                  }
                  function h(w, e) {
                    return () => {
                      throw Error("failed to call unlinked import function " + w + "." + e);
                    };
                  }
                  function p(w) {
                    return w = [0, ...w, 11], new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, w.length + 2, 1, w.length, ...w]);
                  }
                  function E(w, e) {
                    let r = 0, m = 0, v;
                    do
                      v = w[e++], r |= (v & 127) << m, m += 7;
                    while (v & 128);
                    return [r >>> 0, e];
                  }
                  function k(w) {
                    const e = [];
                    do {
                      const r = w & 127;
                      w >>>= 7, e.push(w ? r | 128 : r);
                    } while (w);
                    return e;
                  }
                  function R(w) {
                    for (var e = [], r = -1, m = 8; m < w.length; ) {
                      const [v, _] = E(w, m + 1);
                      w[m] === 8 ? r = E(w, _)[0] : e.push({ id: w[m], at: m, body: _, end: _ + v }), m = _ + v;
                    }
                    if (0 > r || !e.some((v) => v.id === 7)) return w;
                    m = [w.subarray(0, 8)];
                    for (const v of e) {
                      if (v.id !== 7) {
                        m.push(w.subarray(v.at, v.end));
                        continue;
                      }
                      const [_, a] = E(w, v.body);
                      e = Array.from("__riveLiftedStart", (f) => f.charCodeAt(0)), e = [...k(e.length), ...e, 0, ...k(r)];
                      const t = k(_ + 1), s = w.subarray(a, v.end);
                      m.push(Uint8Array.from([7, ...k(t.length + s.length + e.length), ...t]), s, Uint8Array.from(e));
                    }
                    w = new Uint8Array(m.reduce((v, _) => v + _.length, 0)), r = 0;
                    for (const v of m) w.set(v, r), r += v.length;
                    return w;
                  }
                  const j = [253, 12, ...Array(16).fill(0)], D = p([...j]), ee = p([...j, ...j, 253, 128, 2]);
                  (function(w) {
                    function e(u, d) {
                      const S = n({ kb: o(_.Bb, u.L), Z: _.Z, da: _.da, ua: _.ua, ca: _.ca, Ga: _.Ga, Da: _.Da, Ba: t }, () => {
                        if (u.memory === null) throw Error("script passed memory to the host while its module was still starting");
                        return u.memory;
                      });
                      for (const y of WebAssembly.Module.imports(d)) if (y.kind === "function") {
                        let P, U, pe, Oe;
                        (pe = (P = S)[U = y.module] ?? (P[U] = {}))[Oe = y.name] ?? (pe[Oe] = h(y.module, y.name));
                      }
                      return S;
                    }
                    function r(u, d) {
                      const S = _.da();
                      for (const { name: y } of WebAssembly.Module.exports(d)) {
                        if (!y.startsWith("__rive")) continue;
                        d = 3 * y.length + 1;
                        const P = _.ua(d);
                        _.ab(y, P, d), _.exports._rive_web_vm_module_export(u.L.g, P);
                      }
                      _.ca(S);
                    }
                    function m(u, d) {
                      var P, U;
                      u.memory = d.exports.memory, u.Aa = null;
                      const S = _.exports._rive_web_vm_booting;
                      S(u.L.g);
                      const y = _.da();
                      try {
                        (U = (P = d.exports).__riveLiftedStart) == null || U.call(P);
                      } catch (pe) {
                        throw _.ca(y), u.L.j = null, pe;
                      } finally {
                        S(0);
                      }
                      u.instance = d;
                    }
                    async function v(u) {
                      try {
                        const S = await WebAssembly.compile(R(u.Aa));
                        if (u.L.g !== 0) {
                          r(u, S);
                          var d = await WebAssembly.instantiate(S, e(u, S));
                          u.L.g !== 0 && m(u, d);
                        }
                      } catch (S) {
                        u.error = String((S == null ? void 0 : S.message) ?? S);
                      }
                    }
                    let _ = null;
                    const a = /* @__PURE__ */ new Map(), t = { i: !1, l: 0, la: 0, ja: 0, ka: 0, ma: 0 }, s = w.riveScriptingValidate ?? ((u) => WebAssembly.validate(u));
                    let f = null;
                    const c = { ib(u) {
                      _ ?? (_ = u);
                    }, register(u, d) {
                      d = d.slice();
                      var S = a.set;
                      f ?? (f = { Xa: s(D), Mb: s(ee) });
                      var y = f.Xa && f.Mb || s(d) ? null : f.Xa ? "this browser lacks WebAssembly relaxed SIMD, so this file's scripts are off; bake with wasmSimd: on to support it" : "this browser lacks WebAssembly SIMD, so this file's scripts are off; bake with wasmSimd: off to support it";
                      S.call(a, u, {
                        L: { g: u, j: null, h: !1, Ba: t },
                        Aa: d,
                        instance: null,
                        memory: null,
                        V: null,
                        error: y,
                        names: /* @__PURE__ */ new Map()
                      });
                    }, release(u) {
                      const d = a.get(u);
                      d && (d.L.g = 0, a.delete(u));
                    }, Jb() {
                      const u = [];
                      for (const d of a.values()) if (d.instance === null && d.error === null) {
                        let S;
                        (S = d).V ?? (S.V = v(d)), u.push(d.V);
                      }
                      return Promise.all(u);
                    }, start(u) {
                      if (u = a.get(u), !u) return "script module was never registered";
                      if (u.instance === null && u.error === null) {
                        if (u.V !== null) return "script module is still being prepared";
                        try {
                          const d = new WebAssembly.Module(R(u.Aa));
                          r(u, d), m(u, new WebAssembly.Instance(d, e(u, d)));
                        } catch (d) {
                          u.error = String((d == null ? void 0 : d.message) ?? d);
                        }
                      }
                      return u.error;
                    }, V(u) {
                      return u = a.get(u), (u == null ? void 0 : u.instance) === null && u.error === null && u.V !== null ? 1 : 0;
                    }, Ab(u, d) {
                      var S, y;
                      return typeof ((y = (S = a.get(u)) == null ? void 0 : S.instance) == null ? void 0 : y.exports[_.Ja(d)]) == "function" ? 1 : 0;
                    }, call(u, d, S, y, P, U, pe) {
                      if (u = a.get(u), !u || u.instance === null) return 1;
                      let Oe = u.names.get(d);
                      if (Oe === void 0 && (Oe = u.instance.exports[_.Ja(d)] ?? null, u.names.set(d, Oe)), typeof Oe != "function") return 1;
                      try {
                        d = y >> 3;
                        const Ze = Oe(..._.Pa().subarray(d, d + S));
                        return _.Pa()[P >> 3] = typeof Ze == "number" ? Ze : 0, 0;
                      } catch (Ze) {
                        return u.L.j = null, _.ab(String((Ze == null ? void 0 : Ze.message) ?? Ze), U, pe), u.L.h ? 3 : 2;
                      }
                    }, Kb(u, d) {
                      (u = a.get(u)) && (u.L.j = _.Ja(d));
                    }, read(u, d, S, y) {
                      var P;
                      return u = (P = a.get(u)) == null ? void 0 : P.memory, !u || d + y > u.buffer.byteLength ? 0 : (_.Z().set(new Uint8Array(u.buffer, d, y), S), t.i && (t.ka += y), 1);
                    }, write(u, d, S, y) {
                      var P;
                      return u = (P = a.get(u)) == null ? void 0 : P.memory, !u || d + y > u.buffer.byteLength ? 0 : (new Uint8Array(u.buffer, d, y).set(_.Z().subarray(S, S + y)), t.i && (t.ma += y), 1);
                    }, Ch(u, d) {
                      var S;
                      return u = (S = a.get(u)) == null ? void 0 : S.memory, !u || d >= u.buffer.byteLength ? -1 : (u = new Uint8Array(u.buffer).indexOf(0, d), 0 > u ? -1 : u - d);
                    }, Hb(u) {
                      var d;
                      return (u = (d = a.get(u)) == null ? void 0 : d.memory) ? u.buffer.byteLength >>> 16 : 0;
                    }, mb(u) {
                      t.i = !!u, t.l = 0, t.la = 0, t.ja = 0, t.ka = 0, t.ma = 0;
                    }, Cb() {
                      return { hostCalls: t.l, bytesStaged: t.la, bytesCopiedOut: t.ja, bytesRead: t.ka, bytesWritten: t.ma };
                    } };
                    return c.prepare = c.Jb, c.countHostCalls = c.mb, c.hostCallCounts = c.Cb, w.riveScripting = c;
                  })(F);
                })();
                const le = F.onRuntimeInitialized;
                F.onRuntimeInitialized = function() {
                  function n(v) {
                    this.G = v, this.cb = v.getContext("2d"), this.La = p, this.O = [], this.aa = 0, this.clear = function() {
                      console.assert(this.aa == 0), this.O = [], E.delete(this);
                    }, this.save = function() {
                      ++this.aa, this.O.push(p.save.bind(p));
                    }, this.restore = function() {
                      0 < this.aa && (this.O.push(p.restore.bind(p)), --this.aa);
                    }, this.transform = function(_) {
                      this.O.push(p.transform.bind(p, _));
                    }, this.align = function(_, a, t, s, f = 1) {
                      this.O.push(p.align.bind(p, _, a, t, s, f));
                    }, this.flush = function() {
                      console.assert(this.aa == 0), E.add(this), p.Ka || h();
                    }, this.bindContext = function() {
                      const _ = this.La;
                      _ && _.T && $t(_.T);
                    }, this.delete = function() {
                    };
                  }
                  function o(v, _ = !1) {
                    var a = { alpha: !0, depth: _, stencil: _, antialias: _, premultipliedAlpha: !0, preserveDrawingBuffer: 0, powerPreference: "high-performance", failIfMajorPerformanceCaveat: 0, enableExtensionsByDefault: !1, explicitSwapControl: 0, renderViaOffscreenBackBuffer: 0 };
                    if (_ = v.getContext("webgl2", a), !_) return null;
                    a = sr(_, a), $t(a);
                    const t = k(v.width, v.height);
                    t.T = a, t.G = v, t.za = v.width, t.ya = v.height, t.P = _, t.jb = function() {
                      this.T && $t(this.T);
                    };
                    var s = t.delete;
                    return t.delete = function() {
                      var c;
                      this.jb(), s.call(this);
                      var f = this.T;
                      yt === rt[f] && (yt = null), typeof JSEvents == "object" && JSEvents.Hh(rt[f].F.canvas), (c = rt[f]) != null && c.F.canvas && (rt[f].F.canvas.bb = void 0), this.T = this.G = this.za = this.ya = this.P = rt[f] = null;
                    }, t;
                  }
                  function h() {
                    if (p) {
                      var v = p.fb, _ = 0, a = 0, t = 0, s = Array(E.size), f = 0;
                      for (var c of E) c.X = Math.min(c.G.width, v), c.W = Math.min(c.G.height, v), c.wa = c.W * c.X, _ = Math.max(_, c.X), a = Math.max(a, c.W), t += c.wa, s[f++] = c;
                      if (E.clear(), !(0 >= t)) {
                        for (_ = 1 << (0 >= _ ? 0 : 32 - Math.clz32(_ - 1)), a = 1 << (0 >= a ? 0 : 32 - Math.clz32(a - 1)); a * _ < t; ) _ <= a ? _ *= 2 : a *= 2;
                        for (_ = Math.min(_, v), _ = Math.min(a, v), s.sort((S, y) => y.wa - S.wa), t = new F.DynamicRectanizer(v), c = 0; c < s.length; ) {
                          for (t.reset(_, a), f = c; f < s.length; ++f) {
                            var u = s[f], d = t.addRect(u.X, u.W);
                            if (0 > d) {
                              console.assert(f > c);
                              break;
                            }
                            u.ha = d & 65535, u.ia = d >> 16;
                          }
                          for (u = D.push(t.drawWidth()), d = ee.push(t.drawHeight()), console.assert(u >= t.drawWidth()), console.assert(d >= t.drawHeight()), console.assert(u <= v), console.assert(d <= v), p.G.width != u && (p.G.width = u), p.G.height != d && (p.G.height = d), p.clear(), u = c; u < f; ++u) {
                            d = s[u], p.saveClipRect(d.ha, d.ia, d.ha + d.X, d.ia + d.W);
                            let S = new F.Mat2D();
                            S.xx = d.X / d.G.width, S.yy = d.W / d.G.height, S.xy = S.yx = 0, S.tx = d.ha, S.ty = d.ia, p.transform(S);
                            for (const y of d.O) y();
                            p.restoreClipRect(), d.O = [];
                          }
                          for (p.flush(); c < f; ++c) u = s[c], d = u.cb, d.globalCompositeOperation = "copy", d.drawImage(p.G, u.ha, u.ia, u.X, u.W, 0, 0, u.G.width, u.G.height);
                          c = f;
                        }
                      }
                    }
                  }
                  le && le();
                  let p = null;
                  const E = /* @__PURE__ */ new Set(), k = F.makeRenderer;
                  F.makeRenderer = function(v, _) {
                    if (!p) {
                      let a = function(t) {
                        var s = document.createElement("canvas");
                        return s.width = 1, s.height = 1, p = o(s, t), p ? (p.Ka = !!p.P.getExtension("WEBGL_shader_pixel_local_storage"), p.fb = Math.min(p.P.getParameter(p.P.MAX_RENDERBUFFER_SIZE), p.P.getParameter(p.P.MAX_TEXTURE_SIZE)), p.xa = !p.Ka, (t = p.P.getExtension("WEBGL_debug_renderer_info")) && (s = p.P.getParameter(t.UNMASKED_RENDERER_WEBGL), p.P.getParameter(t.UNMASKED_VENDOR_WEBGL).includes("Google") && s.includes("ANGLE Metal Renderer") && (p.xa = !1)), p) : null;
                      };
                      if (p = a(!0), !p) throw "Unable to create WebGL context, your environment may not support WebGL. Try out @rive-app/canvas as an alternative.";
                      p.xa || (p = a(!1));
                    }
                    return _ ? new n(v) : o(v, p.xa);
                  };
                  const R = F.Artboard.prototype.delete;
                  F.Artboard.prototype.delete = function() {
                    this.hb = !0, R.call(this);
                  };
                  const j = F.Artboard.prototype.draw;
                  F.Artboard.prototype.draw = function(v) {
                    v.O ? v.O.push(() => {
                      this.hb || j.call(this, v.La);
                    }) : j.call(this, v);
                  };
                  const D = new O(), ee = new O(), w = new T();
                  F.requestAnimationFrame = w.requestAnimationFrame.bind(w), F.cancelAnimationFrame = w.cancelAnimationFrame.bind(w), F.enableFPSCounter = w.qb.bind(w), w.Ra = h, F.resolveAnimationFrame = h;
                  let e = F.load;
                  F.load = function(v, _, a = !0, t = null) {
                    const s = new F.FallbackFileAssetLoader();
                    return _ !== void 0 && s.addLoader(_), a && (_ = new F.CDNFileAssetLoader(t), s.addLoader(_)), F.startFileScripts(e(v, s, t ?? null));
                  };
                  const r = F.WebGL2Renderer.prototype.clear;
                  F.WebGL2Renderer.prototype.clear = function() {
                    $t(this.T);
                    const v = this.G;
                    (this.za != v.width || this.ya != v.height) && (this.resize(v.width, v.height), this.za = v.width, this.ya = v.height), r.call(this);
                  }, F.decodeImage = function(v, _, a = null) {
                    v = F.decodeWebGL2Image(v, a ?? null), _(v);
                  };
                  let m = F.Renderer.prototype.align;
                  F.Renderer.prototype.align = function(v, _, a, t, s = 1) {
                    m.call(this, v, _, a, t, s);
                  };
                };
                var me = "./this.program";
                V && (I = self.location.href);
                var K = "", X, re;
                if (ie || V) {
                  try {
                    K = new URL(".", I).href;
                  } catch {
                  }
                  V && (re = (n) => {
                    var o = new XMLHttpRequest();
                    return o.open("GET", n, !1), o.responseType = "arraybuffer", o.send(null), new Uint8Array(o.response);
                  }), X = async (n) => {
                    if (Ae(n)) return new Promise((h, p) => {
                      var E = new XMLHttpRequest();
                      E.open("GET", n, !0), E.responseType = "arraybuffer", E.onload = () => {
                        E.status == 200 || E.status == 0 && E.response ? h(E.response) : p(E.status);
                      }, E.onerror = p, E.send(null);
                    });
                    var o = await fetch(n, { credentials: "same-origin" });
                    if (o.ok) return o.arrayBuffer();
                    throw Error(o.status + " : " + o.url);
                  };
                }
                var Z = console.log.bind(console), fe = console.error.bind(console), q, Be = !1, Ae = (n) => n.startsWith("file://"), _e, se, A, x, H, Q, B, z, J, ve, Ie = !1;
                function we() {
                  var n = Pt.buffer;
                  F.HEAP8 = A = new Int8Array(n), H = new Int16Array(n), F.HEAPU8 = x = new Uint8Array(n), F.HEAPU16 = Q = new Uint16Array(n), F.HEAP32 = B = new Int32Array(n), F.HEAPU32 = z = new Uint32Array(n), F.HEAPF32 = J = new Float32Array(n), ve = new Float64Array(n);
                }
                function be(n) {
                  var o;
                  throw (o = F.onAbort) == null || o.call(F, n), n = "Aborted(" + n + ")", fe(n), Be = !0, n = new WebAssembly.RuntimeError(n + ". Build with -sASSERTIONS for more info."), se == null || se(n), n;
                }
                var Se;
                async function ge(n) {
                  if (!q) try {
                    var o = await X(n);
                    return new Uint8Array(o);
                  } catch {
                  }
                  if (n == Se && q) n = new Uint8Array(q);
                  else if (re) n = re(n);
                  else throw "both async and sync fetching of the wasm failed";
                  return n;
                }
                async function Re(n, o) {
                  try {
                    var h = await ge(n);
                    return await WebAssembly.instantiate(h, o);
                  } catch (p) {
                    fe(`failed to asynchronously prepare wasm: ${p}`), be(p);
                  }
                }
                async function ke(n) {
                  var o = Se;
                  if (!q && !Ae(o)) try {
                    var h = fetch(o, { credentials: "same-origin" });
                    return await WebAssembly.instantiateStreaming(h, n);
                  } catch (p) {
                    fe(`wasm streaming compile failed: ${p}`), fe("falling back to ArrayBuffer instantiation");
                  }
                  return Re(o, n);
                }
                var Fe, xe, Ne = (n) => {
                  for (; 0 < n.length; ) n.shift()(F);
                }, Xe = [], Qe = [], ot = () => {
                  var n = F.preRun.shift();
                  Qe.push(n);
                }, Ue = (n) => _n(n), at = () => bn(), qe = globalThis.TextDecoder && new TextDecoder(), st = (n, o, h, p) => {
                  if (h = o + h, p) return h;
                  for (; n[o] && !(o >= h); ) ++o;
                  return o;
                }, lt = (n, o = 0, h, p) => {
                  if (h = st(n, o, h, p), 16 < h - o && n.buffer && qe) return qe.decode(n.subarray(o, h));
                  for (p = ""; o < h; ) {
                    var E = n[o++];
                    if (E & 128) {
                      var k = n[o++] & 63;
                      if ((E & 224) == 192) p += String.fromCharCode((E & 31) << 6 | k);
                      else {
                        var R = n[o++] & 63;
                        E = (E & 240) == 224 ? (E & 15) << 12 | k << 6 | R : (E & 7) << 18 | k << 12 | R << 6 | n[o++] & 63, 65536 > E ? p += String.fromCharCode(E) : (E -= 65536, p += String.fromCharCode(55296 | E >> 10, 56320 | E & 1023));
                      }
                    } else p += String.fromCharCode(E);
                  }
                  return p;
                }, Te = (n, o) => Object.defineProperty(o, "name", { value: n }), it = [], Ye = [0, 1, , 1, null, 1, !0, 1, !1, 1], ye = class extends Error {
                  constructor(n) {
                    super(n), this.name = "BindingError";
                  }
                }, et = (n) => {
                  if (!n) throw new ye(`Cannot use deleted val. handle = ${n}`);
                  return Ye[n];
                }, pt = (n) => {
                  switch (n) {
                    case void 0:
                      return 2;
                    case null:
                      return 4;
                    case !0:
                      return 6;
                    case !1:
                      return 8;
                    default:
                      const o = it.pop() || Ye.length;
                      return Ye[o] = n, Ye[o + 1] = 1, o;
                  }
                };
                class Rt extends Error {
                }
                var We = (n) => {
                  for (var o = ""; ; ) {
                    var h = x[n++];
                    if (!h) return o;
                    o += String.fromCharCode(h);
                  }
                }, De = {}, Le = (n, o) => {
                  if (o === void 0) throw new ye("ptr should not be undefined");
                  for (; n.C; ) o = n.fa(o), n = n.C;
                  return o;
                }, Mt = {}, Xt = (n) => {
                  n = Tn(n);
                  var o = We(n);
                  return kt(n), o;
                }, Wt = (n, o) => {
                  var h = Mt[n];
                  if (h === void 0) throw n = `${o} has unknown type ${Xt(n)}`, new ye(n);
                  return h;
                }, Lt = () => {
                }, mt = !1, xt = (n) => globalThis.FinalizationRegistry ? (mt = new FinalizationRegistry((o) => {
                  o = o.m, --o.count.value, o.count.value === 0 && (o.D ? o.J.N(o.D) : o.v.o.N(o.u));
                }), xt = (o) => {
                  var h = o.m;
                  return h.D && mt.register(o, { m: h }, o), o;
                }, Lt = (o) => {
                  mt.unregister(o);
                }, xt(n)) : (xt = (o) => o, n), Nt = {}, Tt = (n) => {
                  for (; n.length; ) {
                    var o = n.pop();
                    n.pop()(o);
                  }
                };
                function Ot(n) {
                  return this.s(z[n >> 2]);
                }
                var g = {}, i = {}, l = class extends Error {
                  constructor(n) {
                    super(n), this.name = "InternalError";
                  }
                }, b = (n, o, h) => {
                  function p(j) {
                    if (j = h(j), j.length !== n.length) throw new l("Mismatched type converter count");
                    for (var D = 0; D < n.length; ++D) L(n[D], j[D]);
                  }
                  n.forEach((j) => i[j] = o);
                  var E = Array(o.length), k = [], R = 0;
                  for (let [j, D] of o.entries()) Mt.hasOwnProperty(D) ? E[j] = Mt[D] : (k.push(D), g.hasOwnProperty(D) || (g[D] = []), g[D].push(() => {
                    E[j] = Mt[D], ++R, R === k.length && p(E);
                  }));
                  k.length === 0 && p(E);
                };
                function M(n, o, h = {}) {
                  var p = o.name;
                  if (!n) throw new ye(`type "${p}" must have a positive integer typeid pointer`);
                  if (Mt.hasOwnProperty(n)) {
                    if (h.Db) return;
                    throw new ye(`Cannot register type '${p}' twice`);
                  }
                  Mt[n] = o, delete i[n], g.hasOwnProperty(n) && (o = g[n], delete g[n], o.forEach((E) => E()));
                }
                function L(n, o, h = {}) {
                  return M(n, o, h);
                }
                var $ = (n) => {
                  throw new ye(n.m.v.o.name + " instance already deleted");
                };
                function ue() {
                }
                var he = {}, de = (n, o, h) => {
                  if (n[o].A === void 0) {
                    var p = n[o];
                    n[o] = function(...E) {
                      if (!n[o].A.hasOwnProperty(E.length)) throw new ye(`Function '${h}' called with an invalid number of arguments (${E.length}) - expects one of (${n[o].A})!`);
                      return n[o].A[E.length].apply(this, E);
                    }, n[o].A = [], n[o].A[p.R] = p;
                  }
                }, Ee = (n, o, h) => {
                  if (F.hasOwnProperty(n)) {
                    if (h === void 0 || F[n].A !== void 0 && F[n].A[h] !== void 0) throw new ye(`Cannot register public name '${n}' twice`);
                    if (de(F, n, n), F[n].A.hasOwnProperty(h)) throw new ye(`Cannot register multiple overloads of a function with the same number of arguments (${h})!`);
                    F[n].A[h] = o;
                  } else F[n] = o, F[n].R = h;
                }, Pe = (n) => {
                  n = n.replace(/[^a-zA-Z0-9_]/g, "$");
                  var o = n.charCodeAt(0);
                  return 48 <= o && 57 >= o ? `_${n}` : n;
                };
                function Ve(n, o, h, p, E, k, R, j) {
                  this.name = n, this.constructor = o, this.M = h, this.N = p, this.C = E, this.vb = k, this.fa = R, this.ob = j, this.Ta = [];
                }
                var ze = (n, o, h) => {
                  for (; o !== h; ) {
                    if (!o.fa) throw new ye(`Expected null or instance of ${h.name}, got an instance of ${o.name}`);
                    n = o.fa(n), o = o.C;
                  }
                  return n;
                }, Ke = (n) => {
                  if (n === null) return "null";
                  var o = typeof n;
                  return o === "object" || o === "array" || o === "function" ? n.toString() : "" + n;
                };
                function tt(n, o) {
                  if (o === null) {
                    if (this.Ea) throw new ye(`null is not a valid ${this.name}`);
                    return 0;
                  }
                  if (!o.m) throw new ye(`Cannot pass "${Ke(o)}" as a ${this.name}`);
                  if (!o.m.u) throw new ye(`Cannot pass deleted object as a pointer of type ${this.name}`);
                  return ze(o.m.u, o.m.v.o, this.o);
                }
                function wt(n, o) {
                  if (o === null) {
                    if (this.Ea) throw new ye(`null is not a valid ${this.name}`);
                    if (this.pa) {
                      var h = this.Ha();
                      return n !== null && n.push(this.N, h), h;
                    }
                    return 0;
                  }
                  if (!o || !o.m) throw new ye(`Cannot pass "${Ke(o)}" as a ${this.name}`);
                  if (!o.m.u) throw new ye(`Cannot pass deleted object as a pointer of type ${this.name}`);
                  if (!this.oa && o.m.v.oa) throw new ye(`Cannot convert argument of type ${o.m.J ? o.m.J.name : o.m.v.name} to parameter type ${this.name}`);
                  if (h = ze(o.m.u, o.m.v.o, this.o), this.pa) {
                    if (o.m.D === void 0) throw new ye("Passing raw pointer to smart pointer is illegal");
                    switch (this.Bh) {
                      case 0:
                        if (o.m.J === this) h = o.m.D;
                        else throw new ye(`Cannot convert argument of type ${o.m.J ? o.m.J.name : o.m.v.name} to parameter type ${this.name}`);
                        break;
                      case 1:
                        h = o.m.D;
                        break;
                      case 2:
                        if (o.m.J === this) h = o.m.D;
                        else {
                          var p = o.clone();
                          h = this.Lb(h, pt(() => p.delete())), n !== null && n.push(this.N, h);
                        }
                        break;
                      default:
                        throw new ye("Unsupported sharing policy");
                    }
                  }
                  return h;
                }
                function _t(n, o) {
                  if (o === null) {
                    if (this.Ea) throw new ye(`null is not a valid ${this.name}`);
                    return 0;
                  }
                  if (!o.m) throw new ye(`Cannot pass "${Ke(o)}" as a ${this.name}`);
                  if (!o.m.u) throw new ye(`Cannot pass deleted object as a pointer of type ${this.name}`);
                  if (o.m.v.oa) throw new ye(`Cannot convert argument of type ${o.m.v.name} to parameter type ${this.name}`);
                  return ze(o.m.u, o.m.v.o, this.o);
                }
                var bt = (n, o, h) => o === h ? n : h.C === void 0 ? null : (n = bt(n, o, h.C), n === null ? null : h.ob(n)), St = (n, o) => (o = Le(n, o), De[o]), ht = (n, o) => {
                  if (!o.v || !o.u) throw new l("makeClassHandle requires ptr and ptrType");
                  if (!!o.J != !!o.D) throw new l("Both smartPtrType and smartPtr must be specified");
                  return o.count = { value: 1 }, xt(Object.create(n, { m: { value: o, writable: !0 } }));
                };
                function ut(n, o, h, p, E, k, R, j, D, ee, w) {
                  this.name = n, this.o = o, this.Ea = h, this.oa = p, this.pa = E, this.Ib = k, this.Bh = R, this.Va = j, this.Ha = D, this.Lb = ee, this.N = w, E || o.C !== void 0 ? this.B = wt : (this.B = p ? tt : _t, this.H = null);
                }
                var dt = (n, o, h) => {
                  if (!F.hasOwnProperty(n)) throw new l("Replacing nonexistent public symbol");
                  F[n].A !== void 0 && h !== void 0 ? F[n].A[h] = o : (F[n] = o, F[n].R = h);
                }, He = {}, ft = (n, o, h = []) => (n.includes("j") ? (n = n.replace(/p/g, "i"), o = (0, He[n])(o, ...h)) : o = Jt.get(o)(...h), o), je = (n, o) => (...h) => ft(n, o, h), Je = (n, o) => {
                  n = We(n);
                  var h = n.includes("j") ? je(n, o) : Jt.get(o);
                  if (typeof h != "function") throw new ye(`unknown function pointer with signature ${n}: ${o}`);
                  return h;
                };
                class nt extends Error {
                }
                var ct = (n, o) => {
                  function h(k) {
                    E[k] || Mt[k] || (i[k] ? i[k].forEach(h) : (p.push(k), E[k] = !0));
                  }
                  var p = [], E = {};
                  throw o.forEach(h), new nt(`${n}: ` + p.map(Xt).join([", "]));
                };
                function Bt(n) {
                  for (var o = 1; o < n.length; ++o) if (n[o] !== null && n[o].H === void 0) return !0;
                  return !1;
                }
                function Zt(n, o, h, p, E) {
                  var k = o.length;
                  if (2 > k) throw new ye("argTypes array size mismatch! Must at least get return value and 'this' types!");
                  var R = o[1] !== null && h !== null, j = Bt(o), D = !o[0].Fb, ee = k - 2, w = Array(ee), e = [], r = [];
                  return Te(n, function(...m) {
                    if (r.length = 0, e.length = R ? 2 : 1, e[0] = E, R) {
                      var v = o[1].B(r, this);
                      e[1] = v;
                    }
                    for (var _ = 0; _ < ee; ++_) w[_] = o[_ + 2].B(r, m[_]), e.push(w[_]);
                    if (m = p(...e), j) Tt(r);
                    else for (_ = R ? 1 : 2; _ < o.length; _++) {
                      var a = _ === 1 ? v : w[_ - 2];
                      o[_].H !== null && o[_].H(a);
                    }
                    return v = D ? o[0].s(m) : void 0, v;
                  });
                }
                var qt = (n, o) => {
                  for (var h = [], p = 0; p < n; p++) h.push(z[o + 4 * p >> 2]);
                  return h;
                }, ln = (n) => {
                  n = n.trim();
                  const o = n.indexOf("(");
                  return o === -1 ? n : n.slice(0, o);
                }, Sn = (n, o, h) => {
                  if (!(n instanceof Object)) throw new ye(`${h} with invalid "this": ${n}`);
                  if (!(n instanceof o.o.constructor)) throw new ye(`${h} incompatible with "this" of type ${n.constructor.name}`);
                  if (!n.m.u) throw new ye(`cannot call emscripten binding method ${h} on deleted object`);
                  return ze(n.m.u, n.m.v.o, o.o);
                }, un = (n) => {
                  9 < n && --Ye[n + 1] === 0 && (Ye[n] = void 0, it.push(n));
                }, Yn = { name: "emscripten::val", s: (n) => {
                  var o = et(n);
                  return un(n), o;
                }, B: (n, o) => pt(o), I: Ot, H: null }, cn = (n, o, h) => {
                  switch (o) {
                    case 1:
                      return h ? function(p) {
                        return this.s(A[p]);
                      } : function(p) {
                        return this.s(x[p]);
                      };
                    case 2:
                      return h ? function(p) {
                        return this.s(H[p >> 1]);
                      } : function(p) {
                        return this.s(Q[p >> 1]);
                      };
                    case 4:
                      return h ? function(p) {
                        return this.s(B[p >> 2]);
                      } : function(p) {
                        return this.s(z[p >> 2]);
                      };
                    default:
                      throw new TypeError(`invalid integer width (${o}): ${n}`);
                  }
                }, zn = (n, o) => {
                  switch (o) {
                    case 4:
                      return function(h) {
                        return this.s(J[h >> 2]);
                      };
                    case 8:
                      return function(h) {
                        return this.s(ve[h >> 3]);
                      };
                    default:
                      throw new TypeError(`invalid float width (${o}): ${n}`);
                  }
                }, $n = (n, o, h) => {
                  switch (o) {
                    case 1:
                      return h ? (p) => A[p] : (p) => x[p];
                    case 2:
                      return h ? (p) => H[p >> 1] : (p) => Q[p >> 1];
                    case 4:
                      return h ? (p) => B[p >> 2] : (p) => z[p >> 2];
                    default:
                      throw new TypeError(`invalid integer width (${o}): ${n}`);
                  }
                }, It = (n, o, h) => {
                  var p = x;
                  if (!(0 < h)) return 0;
                  var E = o;
                  h = o + h - 1;
                  for (var k = 0; k < n.length; ++k) {
                    var R = n.codePointAt(k);
                    if (127 >= R) {
                      if (o >= h) break;
                      p[o++] = R;
                    } else if (2047 >= R) {
                      if (o + 1 >= h) break;
                      p[o++] = 192 | R >> 6, p[o++] = 128 | R & 63;
                    } else if (65535 >= R) {
                      if (o + 2 >= h) break;
                      p[o++] = 224 | R >> 12, p[o++] = 128 | R >> 6 & 63, p[o++] = 128 | R & 63;
                    } else {
                      if (o + 3 >= h) break;
                      p[o++] = 240 | R >> 18, p[o++] = 128 | R >> 12 & 63, p[o++] = 128 | R >> 6 & 63, p[o++] = 128 | R & 63, k++;
                    }
                  }
                  return p[o] = 0, o - E;
                }, hn = (n) => {
                  for (var o = 0, h = 0; h < n.length; ++h) {
                    var p = n.charCodeAt(h);
                    127 >= p ? o++ : 2047 >= p ? o += 2 : 55296 <= p && 57343 >= p ? (o += 4, ++h) : o += 3;
                  }
                  return o;
                }, En = globalThis.TextDecoder ? new TextDecoder("utf-16le") : void 0, Qn = (n, o, h) => {
                  if (n >>= 1, o = st(Q, n, o / 2, h), 16 < o - n && En) return En.decode(Q.subarray(n, o));
                  for (h = ""; n < o; ++n) h += String.fromCharCode(Q[n]);
                  return h;
                }, Jn = (n, o, h) => {
                  if (h ?? (h = 2147483647), 2 > h) return 0;
                  h -= 2;
                  var p = o;
                  h = h < 2 * n.length ? h / 2 : n.length;
                  for (var E = 0; E < h; ++E) H[o >> 1] = n.charCodeAt(E), o += 2;
                  return H[o >> 1] = 0, o - p;
                }, Zn = (n) => 2 * n.length, qn = (n, o, h) => {
                  var p = "";
                  n >>= 2;
                  for (var E = 0; !(E >= o / 4); E++) {
                    var k = z[n + E];
                    if (!k && !h) break;
                    p += String.fromCodePoint(k);
                  }
                  return p;
                }, er = (n, o, h) => {
                  if (h ?? (h = 2147483647), 4 > h) return 0;
                  var p = o;
                  h = p + h - 4;
                  for (var E = 0; E < n.length; ++E) {
                    var k = n.codePointAt(E);
                    if (65535 < k && E++, B[o >> 2] = k, o += 4, o + 4 > h) break;
                  }
                  return B[o >> 2] = 0, o - p;
                }, tr = (n) => {
                  for (var o = 0, h = 0; h < n.length; ++h) 65535 < n.codePointAt(h) && h++, o += 4;
                  return o;
                }, dn = [], nr = (n) => {
                  var o = dn.length;
                  return dn.push(n), o;
                }, rr = (n, o) => {
                  for (var h = Array(n), p = 0; p < n; ++p) h[p] = Wt(z[o + 4 * p >> 2], `parameter ${p}`);
                  return h;
                }, ir = {}, An = (n) => {
                  var o = ir[n];
                  return o === void 0 ? We(n) : o;
                }, or = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335], ar = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334], fn = [], Fn = (n) => {
                  n.Eh = n.getExtension("WEBGL_draw_instanced_base_vertex_base_instance");
                }, Mn = (n) => {
                  n.Gh = n.getExtension("WEBGL_multi_draw_instanced_base_vertex_base_instance");
                }, W, In = (n) => {
                  var o = "EXT_color_buffer_float EXT_conservative_depth EXT_disjoint_timer_query_webgl2 EXT_texture_norm16 NV_shader_noperspective_interpolation WEBGL_clip_cull_distance EXT_clip_control EXT_color_buffer_half_float EXT_depth_clamp EXT_float_blend EXT_polygon_offset_clamp EXT_texture_compression_bptc EXT_texture_compression_rgtc EXT_texture_filter_anisotropic KHR_parallel_shader_compile OES_texture_float_linear WEBGL_blend_func_extended WEBGL_compressed_texture_astc WEBGL_compressed_texture_etc WEBGL_compressed_texture_etc1 WEBGL_compressed_texture_s3tc WEBGL_compressed_texture_s3tc_srgb WEBGL_debug_renderer_info WEBGL_debug_shaders WEBGL_lose_context WEBGL_multi_draw WEBGL_polygon_mode".split(" ");
                  return (n.getSupportedExtensions() || []).filter((h) => o.includes(h));
                }, kn = 1, Yt = [], gt = [], en = [], zt = [], Dt = [], Et = [], tn = [], rt = [], Ut = [], Cn = {}, Rn = {}, vn = 4, xn = 0, nn = (n) => {
                  for (var o = kn++, h = n.length; h < o; h++) n[h] = null;
                  return o;
                }, Vt = (n, o, h, p) => {
                  for (var E = 0; E < n; E++) {
                    var k = W[h](), R = k && nn(p);
                    k ? (k.name = R, p[R] = k) : $e || ($e = 1282), B[o + 4 * E >> 2] = R;
                  }
                }, sr = (n, o) => {
                  var h = nn(rt), p = { handle: h, attributes: o, version: o.Fh, F: n };
                  if (n.canvas && (n.canvas.bb = p), rt[h] = p, (typeof o.pb > "u" || o.pb) && ((n = p) || (n = yt), !n.Eb)) {
                    n.Eb = !0, o = n.F, o.Gb = o.getExtension("WEBGL_multi_draw"), o.sb = o.getExtension("EXT_polygon_offset_clamp"), o.rb = o.getExtension("EXT_clip_control"), o.Dh = o.getExtension("WEBGL_polygon_mode"), Fn(o), Mn(o), 2 <= n.version && (o.Na = o.getExtension("EXT_disjoint_timer_query_webgl2")), (2 > n.version || !o.Na) && (o.Na = o.getExtension("EXT_disjoint_timer_query"));
                    for (var E of In(o)) E.includes("lose_context") || E.includes("debug") || o.getExtension(E);
                  }
                  return h;
                }, $t = (n) => (yt = rt[n], F.ctx = W = yt == null ? void 0 : yt.F, !(n && !W)), $e, yt, pn = {}, Pn = () => {
                  var p;
                  if (!gn) {
                    var n = {
                      USER: "web_user",
                      LOGNAME: "web_user",
                      PATH: "/",
                      PWD: "/",
                      HOME: "/home/web_user",
                      LANG: (((p = globalThis.navigator) == null ? void 0 : p.language) ?? "C").replace("-", "_") + ".UTF-8",
                      _: me || "./this.program"
                    }, o;
                    for (o in pn) pn[o] === void 0 ? delete n[o] : n[o] = pn[o];
                    var h = [];
                    for (o in n) h.push(`${o}=${n[o]}`);
                    gn = h;
                  }
                  return gn;
                }, gn, lr = [null, [], []], mn = [], yn = () => {
                  var n = In(W);
                  return n = n.concat(n.map((o) => "GL_" + o));
                }, jn = (n, o, h) => {
                  if (o) {
                    var p = void 0;
                    switch (n) {
                      case 36346:
                        p = 1;
                        break;
                      case 36344:
                        h != 0 && h != 1 && ($e || ($e = 1280));
                        return;
                      case 34814:
                      case 36345:
                        p = 0;
                        break;
                      case 34466:
                        var E = W.getParameter(34467);
                        p = E ? E.length : 0;
                        break;
                      case 33309:
                        if (2 > yt.version) {
                          $e || ($e = 1282);
                          return;
                        }
                        p = yn().length;
                        break;
                      case 33307:
                      case 33308:
                        if (2 > yt.version) {
                          $e || ($e = 1280);
                          return;
                        }
                        p = n == 33307 ? 3 : 0;
                    }
                    if (p === void 0) switch (E = W.getParameter(n), typeof E) {
                      case "number":
                        p = E;
                        break;
                      case "boolean":
                        p = E ? 1 : 0;
                        break;
                      case "string":
                        $e || ($e = 1280);
                        return;
                      case "object":
                        if (E === null) switch (n) {
                          case 34964:
                          case 35725:
                          case 34965:
                          case 36006:
                          case 36007:
                          case 32873:
                          case 34229:
                          case 36662:
                          case 36663:
                          case 35053:
                          case 35055:
                          case 36010:
                          case 35097:
                          case 35869:
                          case 32874:
                          case 36389:
                          case 35983:
                          case 35368:
                          case 34068:
                            p = 0;
                            break;
                          default:
                            $e || ($e = 1280);
                            return;
                        }
                        else {
                          if (E instanceof Float32Array || E instanceof Uint32Array || E instanceof Int32Array || E instanceof Array) {
                            for (n = 0; n < E.length; ++n) switch (h) {
                              case 0:
                                B[o + 4 * n >> 2] = E[n];
                                break;
                              case 2:
                                J[o + 4 * n >> 2] = E[n];
                                break;
                              case 4:
                                A[o + n] = E[n] ? 1 : 0;
                            }
                            return;
                          }
                          try {
                            p = E.name | 0;
                          } catch (k) {
                            $e || ($e = 1280), fe(`GL_INVALID_ENUM in glGet${h}v: Unknown object returned from WebGL getParameter(${n})! (error: ${k})`);
                            return;
                          }
                        }
                        break;
                      default:
                        $e || ($e = 1280), fe(`GL_INVALID_ENUM in glGet${h}v: Native code calling glGet${h}v(${n}) and it returns ${E} of type ${typeof E}!`);
                        return;
                    }
                    switch (h) {
                      case 1:
                        h = p, z[o >> 2] = h, z[o + 4 >> 2] = (h - z[o >> 2]) / 4294967296;
                        break;
                      case 0:
                        B[o >> 2] = p;
                        break;
                      case 2:
                        J[o >> 2] = p;
                        break;
                      case 4:
                        A[o] = p ? 1 : 0;
                    }
                  } else $e || ($e = 1281);
                }, Kt = (n) => {
                  var o = hn(n) + 1, h = Qt(o);
                  return h && It(n, h, o), h;
                }, Ln = (n) => n.slice(-1) == "]" && n.lastIndexOf("["), rn = (n) => (n -= 5120, n == 0 ? A : n == 1 ? x : n == 2 ? H : n == 4 ? B : n == 6 ? J : n == 5 || n == 28922 || n == 28520 || n == 30779 || n == 30782 ? z : Q), ur = (n) => Hn(n);
                (() => {
                  let n = ue.prototype;
                  Object.assign(n, { isAliasOf: function(h) {
                    if (!(this instanceof ue && h instanceof ue)) return !1;
                    var p = this.m.v.o, E = this.m.u;
                    h.m = h.m;
                    var k = h.m.v.o;
                    for (h = h.m.u; p.C; ) E = p.fa(E), p = p.C;
                    for (; k.C; ) h = k.fa(h), k = k.C;
                    return p === k && E === h;
                  }, clone: function() {
                    if (this.m.u || $(this), this.m.$) return this.m.count.value += 1, this;
                    var h = xt, p = Object, E = p.create, k = Object.getPrototypeOf(this), R = this.m;
                    return h = h(E.call(p, k, { m: { value: { count: R.count, ba: R.ba, $: R.$, u: R.u, v: R.v, D: R.D, J: R.J } } })), h.m.count.value += 1, h.m.ba = !1, h;
                  }, delete() {
                    if (this.m.u || $(this), this.m.ba && !this.m.$) throw new ye("Object already scheduled for deletion");
                    Lt(this);
                    var h = this.m;
                    --h.count.value, h.count.value === 0 && (h.D ? h.J.N(h.D) : h.v.o.N(h.u)), this.m.$ || (this.m.D = void 0, this.m.u = void 0);
                  }, isDeleted: function() {
                    return !this.m.u;
                  }, deleteLater: function() {
                    if (this.m.u || $(this), this.m.ba && !this.m.$) throw new ye("Object already scheduled for deletion");
                    return this.m.ba = !0, this;
                  } });
                  const o = Symbol.dispose;
                  o && (n[o] = n.delete);
                })(), Object.assign(ut.prototype, { wb(n) {
                  return this.Va && (n = this.Va(n)), n;
                }, Ma(n) {
                  var o;
                  (o = this.N) == null || o.call(this, n);
                }, I: Ot, s: function(n) {
                  function o() {
                    return this.pa ? ht(this.o.M, { v: this.Ib, u: h, J: this, D: n }) : ht(this.o.M, { v: this, u: n });
                  }
                  var h = this.wb(n);
                  if (!h) return this.Ma(n), null;
                  var p = St(this.o, h);
                  if (p !== void 0)
                    return p.m.count.value === 0 ? (p.m.u = h, p.m.D = n, p.clone()) : (p = p.clone(), this.Ma(n), p);
                  if (p = this.o.vb(h), p = he[p], !p) return o.call(this);
                  p = this.oa ? p.lb : p.pointerType;
                  var E = bt(h, this.o, p.o);
                  return E === null ? o.call(this) : this.pa ? ht(p.o.M, { v: p, u: E, J: this, D: n }) : ht(p.o.M, { v: p, u: E });
                } });
                for (let n = 0; 32 > n; ++n) mn.push(Array(n));
                if (F.print && (Z = F.print), F.printErr && (fe = F.printErr), F.wasmBinary && (q = F.wasmBinary), F.thisProgram && (me = F.thisProgram), F.preInit) for (typeof F.preInit == "function" && (F.preInit = [F.preInit]); 0 < F.preInit.length; ) F.preInit.shift()();
                var cr = {
                  346227: (n, o, h, p, E) => {
                    if (typeof window > "u" || (window.AudioContext || window.webkitAudioContext) === void 0) return 0;
                    if (typeof window.miniaudio > "u") {
                      window.miniaudio = { referenceCount: 0 }, window.miniaudio.device_type = {}, window.miniaudio.device_type.playback = n, window.miniaudio.device_type.capture = o, window.miniaudio.device_type.duplex = h, window.miniaudio.device_state = {}, window.miniaudio.device_state.stopped = p, window.miniaudio.device_state.started = E;
                      let k = window.miniaudio;
                      k.devices = [], k.track_device = function(R) {
                        for (var j = 0; j < k.devices.length; ++j) if (k.devices[j] == null) return k.devices[j] = R, j;
                        return k.devices.push(R), k.devices.length - 1;
                      }, k.untrack_device_by_index = function(R) {
                        for (k.devices[R] = null; 0 < k.devices.length && k.devices[k.devices.length - 1] == null; ) k.devices.pop();
                      }, k.untrack_device = function(R) {
                        for (var j = 0; j < k.devices.length; ++j) if (k.devices[j] == R) return k.untrack_device_by_index(j);
                      }, k.get_device_by_index = function(R) {
                        return k.devices[R];
                      }, k.unlock_event_types = [
                        "touchend",
                        "click"
                      ], k.unlock = function() {
                        for (var R = 0; R < k.devices.length; ++R) {
                          var j = k.devices[R];
                          j != null && j.K != null && j.state === k.device_state.started && j.K.resume().then(() => {
                            Wn(j.Sa);
                          }, (D) => {
                            console.error("Failed to resume audiocontext", D);
                          });
                        }
                        k.unlock_event_types.map(function(D) {
                          document.removeEventListener(D, k.unlock, !0);
                        });
                      }, k.unlock_event_types.map(function(R) {
                        document.addEventListener(R, k.unlock, !0);
                      });
                    }
                    return window.miniaudio.referenceCount += 1, 1;
                  },
                  348405: () => {
                    typeof window.miniaudio < "u" && (window.miniaudio.unlock_event_types.map(function(n) {
                      document.removeEventListener(
                        n,
                        window.miniaudio.unlock,
                        !0
                      );
                    }), --window.miniaudio.referenceCount, window.miniaudio.referenceCount === 0 && delete window.miniaudio);
                  },
                  348709: () => navigator.mediaDevices !== void 0 && navigator.mediaDevices.getUserMedia !== void 0,
                  348813: () => {
                    try {
                      var n = new (window.AudioContext || window.webkitAudioContext)(), o = n.sampleRate;
                      return n.close(), o;
                    } catch {
                      return 0;
                    }
                  },
                  348984: (n, o, h, p, E, k) => {
                    if (typeof window.miniaudio > "u") return -1;
                    var R = {}, j = {};
                    return n == window.miniaudio.device_type.playback && h != 0 && (j.sampleRate = h), R.K = new (window.AudioContext || window.webkitAudioContext)(j), R.K.suspend(), R.state = window.miniaudio.device_state.stopped, h = 0, n != window.miniaudio.device_type.playback && (h = o), R.S = R.K.createScriptProcessor(p, h, o), R.S.onaudioprocess = function(D) {
                      if ((R.na == null || R.na.length == 0) && (R.na = new Float32Array(J.buffer, E, p * o)), n == window.miniaudio.device_type.capture || n == window.miniaudio.device_type.duplex) {
                        for (var ee = 0; ee < o; ee += 1) for (var w = D.inputBuffer.getChannelData(ee), e = R.na, r = 0; r < p; r += 1) e[r * o + ee] = w[r];
                        Nn(k, p, E);
                      }
                      if (n == window.miniaudio.device_type.playback || n == window.miniaudio.device_type.duplex) for (Un(k, p, E), ee = 0; ee < D.outputBuffer.numberOfChannels; ++ee) for (w = D.outputBuffer.getChannelData(ee), e = R.na, r = 0; r < p; r += 1) w[r] = e[r * o + ee];
                      else for (ee = 0; ee < D.outputBuffer.numberOfChannels; ++ee) D.outputBuffer.getChannelData(ee).fill(0);
                    }, n != window.miniaudio.device_type.capture && n != window.miniaudio.device_type.duplex || navigator.mediaDevices.getUserMedia({ audio: !0, video: !1 }).then(function(D) {
                      R.va = R.K.createMediaStreamSource(D), R.va.connect(R.S), R.S.connect(R.K.destination);
                    }).catch(function(D) {
                      console.log("Failed to get user media: " + D);
                    }), n == window.miniaudio.device_type.playback && R.S.connect(R.K.destination), R.Sa = k, window.miniaudio.track_device(R);
                  },
                  351861: (n) => window.miniaudio.get_device_by_index(n).K.sampleRate,
                  351934: (n) => {
                    n = window.miniaudio.get_device_by_index(n), n.S !== void 0 && (n.S.onaudioprocess = function() {
                    }, n.S.disconnect(), n.S = void 0), n.va !== void 0 && (n.va.disconnect(), n.va = void 0), n.K.close(), n.K = void 0, n.Sa = void 0;
                  },
                  352334: (n) => {
                    window.miniaudio.untrack_device_by_index(n);
                  },
                  352384: (n) => {
                    n = window.miniaudio.get_device_by_index(n), n.K.resume(), n.state = window.miniaudio.device_state.started;
                  },
                  352523: (n) => {
                    n = window.miniaudio.get_device_by_index(n), n.K.suspend(), n.state = window.miniaudio.device_state.stopped;
                  }
                }, kt, Qt, Tn, On, Bn, wn, Dn, Wn, Nn, Un, Vn, Kn, _n, Hn, bn, Pt, Jt, Gn = {
                  __syscall_fcntl64: function() {
                    return 0;
                  },
                  __syscall_ioctl: function() {
                    return 0;
                  },
                  __syscall_openat: function() {
                  },
                  _abort_js: () => be(""),
                  _embind_create_inheriting_constructor: (n, o, h) => {
                    n = We(n), o = Wt(o, "wrapper"), h = et(h);
                    var p = o.o, E = p.M, k = p.C.M, R = p.C.constructor;
                    return n = Te(n, function(...j) {
                      for (var D of p.C.Ta) if (this[D] === k[D]) throw new Rt(`Pure virtual function ${D} must be implemented in JavaScript`);
                      Object.defineProperty(this, "__parent", { value: E }), this.__construct(...j);
                    }), E.__construct = function(...j) {
                      if (this === E) throw new ye("Pass correct 'this' to __construct");
                      j = R.implement(this, ...j), Lt(j);
                      var D = j.m;
                      if (j.notifyOnDestruction(), D.$ = !0, Object.defineProperties(this, { m: { value: D } }), xt(this), j = D.u, j = Le(p, j), De.hasOwnProperty(j)) throw new ye(`Tried to register registered instance: ${j}`);
                      De[j] = this;
                    }, E.__destruct = function() {
                      if (this === E) throw new ye("Pass correct 'this' to __destruct");
                      Lt(this);
                      var j = this.m.u;
                      if (j = Le(p, j), De.hasOwnProperty(j)) delete De[j];
                      else throw new ye(`Tried to unregister unregistered instance: ${j}`);
                    }, n.prototype = Object.create(E), Object.assign(n.prototype, h), pt(n);
                  },
                  _embind_finalize_value_object: (n) => {
                    var o = Nt[n];
                    delete Nt[n];
                    var h = o.Ha, p = o.N, E = o.Oa, k = E.map((R) => R.zb).concat(E.map((R) => R.zh));
                    b([n], k, (R) => {
                      var j = {}, D, ee;
                      for ([D, ee] of E.entries()) {
                        const w = R[D], e = ee.xb, r = ee.yb, m = R[D + E.length], v = ee.yh, _ = ee.Ah;
                        j[ee.tb] = { read: (a) => w.s(e(r, a)), write: (a, t) => {
                          var s = [];
                          v(_, a, m.B(s, t)), Tt(s);
                        }, optional: w.optional };
                      }
                      return [{ name: o.name, s: (w) => {
                        var e = {}, r;
                        for (r in j) e[r] = j[r].read(w);
                        return p(w), e;
                      }, B: (w, e) => {
                        for (var r in j) if (!(r in e || j[r].optional)) throw new TypeError(`Missing field: "${r}"`);
                        var m = h();
                        for (r in j) j[r].write(m, e[r]);
                        return w !== null && w.push(p, m), m;
                      }, I: Ot, H: p }];
                    });
                  },
                  _embind_register_bigint: () => {
                  },
                  _embind_register_bool: (n, o, h, p) => {
                    o = We(o), L(n, {
                      name: o,
                      s: function(E) {
                        return !!E;
                      },
                      B: function(E, k) {
                        return k ? h : p;
                      },
                      I: function(E) {
                        return this.s(x[E]);
                      },
                      H: null
                    });
                  },
                  _embind_register_class: (n, o, h, p, E, k, R, j, D, ee, w, e, r) => {
                    w = We(w), k = Je(E, k), j && (j = Je(R, j)), ee && (ee = Je(D, ee)), r = Je(e, r);
                    var m = Pe(w);
                    Ee(m, function() {
                      ct(`Cannot construct ${w} due to unbound types`, [p]);
                    }), b([n, o, h], p ? [p] : [], (v) => {
                      if (v = v[0], p)
                        var _ = v.o, a = _.M;
                      else a = ue.prototype;
                      v = Te(w, function(...c) {
                        if (Object.getPrototypeOf(this) !== t) throw new ye(`Use 'new' to construct ${w}`);
                        if (s.U === void 0) throw new ye(`${w} has no accessible constructor`);
                        var u = s.U[c.length];
                        if (u === void 0) throw new ye(`Tried to invoke ctor of ${w} with invalid number of parameters (${c.length}) - expected (${Object.keys(s.U).toString()}) parameters instead!`);
                        return u.apply(this, c);
                      });
                      var t = Object.create(a, { constructor: { value: v } });
                      v.prototype = t;
                      var s = new Ve(w, v, t, r, _, k, j, ee);
                      if (s.C) {
                        var f;
                        (f = s.C).ga ?? (f.ga = []), s.C.ga.push(s);
                      }
                      return _ = new ut(w, s, !0, !1, !1), f = new ut(w + "*", s, !1, !1, !1), a = new ut(w + " const*", s, !1, !0, !1), he[n] = { pointerType: f, lb: a }, dt(m, v), [_, f, a];
                    });
                  },
                  _embind_register_class_class_function: (n, o, h, p, E, k, R) => {
                    var j = qt(h, p);
                    o = We(o), o = ln(o), k = Je(E, k), b([], [n], (D) => {
                      function ee() {
                        ct(`Cannot call ${w} due to unbound types`, j);
                      }
                      D = D[0];
                      var w = `${D.name}.${o}`;
                      o.startsWith("@@") && (o = Symbol[o.substring(2)]);
                      var e = D.o.constructor;
                      return e[o] === void 0 ? (ee.R = h - 1, e[o] = ee) : (de(e, o, w), e[o].A[h - 1] = ee), b([], j, (r) => {
                        if (r = Zt(w, [r[0], null].concat(r.slice(1)), null, k, R), e[o].A === void 0 ? (r.R = h - 1, e[o] = r) : e[o].A[h - 1] = r, D.o.ga) for (const m of D.o.ga) m.constructor.hasOwnProperty(o) || (m.constructor[o] = r);
                        return [];
                      }), [];
                    });
                  },
                  _embind_register_class_class_property: (n, o, h, p, E, k, R, j) => {
                    o = We(o), k = Je(E, k), b([], [n], (D) => {
                      D = D[0];
                      var ee = `${D.name}.${o}`, w = { get() {
                        ct(`Cannot access ${ee} due to unbound types`, [h]);
                      }, enumerable: !0, configurable: !0 };
                      return w.set = j ? () => {
                        ct(`Cannot access ${ee} due to unbound types`, [h]);
                      } : () => {
                        throw new ye(`${ee} is a read-only property`);
                      }, Object.defineProperty(D.o.constructor, o, w), b([], [h], (e) => {
                        e = e[0];
                        var r = { get() {
                          return e.s(k(p));
                        }, enumerable: !0 };
                        return j && (j = Je(R, j), r.set = (m) => {
                          var v = [];
                          j(p, e.B(v, m)), Tt(v);
                        }), Object.defineProperty(D.o.constructor, o, r), [];
                      }), [];
                    });
                  },
                  _embind_register_class_constructor: (n, o, h, p, E, k) => {
                    var R = qt(o, h);
                    E = Je(p, E), b([], [n], (j) => {
                      j = j[0];
                      var D = `constructor ${j.name}`;
                      if (j.o.U === void 0 && (j.o.U = []), j.o.U[o - 1] !== void 0) throw new ye(`Cannot register multiple constructors with identical number of parameters (${o - 1}) for class '${j.name}'! Overload resolution is currently only performed using the parameter count, not actual type info!`);
                      return j.o.U[o - 1] = () => {
                        ct(`Cannot construct ${j.name} due to unbound types`, R);
                      }, b([], R, (ee) => (ee.splice(1, 0, null), j.o.U[o - 1] = Zt(D, ee, null, E, k), [])), [];
                    });
                  },
                  _embind_register_class_function: (n, o, h, p, E, k, R, j) => {
                    var D = qt(h, p);
                    o = We(o), o = ln(o), k = Je(E, k), b([], [n], (ee) => {
                      function w() {
                        ct(`Cannot call ${e} due to unbound types`, D);
                      }
                      ee = ee[0];
                      var e = `${ee.name}.${o}`;
                      o.startsWith("@@") && (o = Symbol[o.substring(2)]), j && ee.o.Ta.push(o);
                      var r = ee.o.M, m = r[o];
                      return m === void 0 || m.A === void 0 && m.className !== ee.name && m.R === h - 2 ? (w.R = h - 2, w.className = ee.name, r[o] = w) : (de(r, o, e), r[o].A[h - 2] = w), b([], D, (v) => (v = Zt(e, v, ee, k, R), r[o].A === void 0 ? (v.R = h - 2, r[o] = v) : r[o].A[h - 2] = v, [])), [];
                    });
                  },
                  _embind_register_class_property: (n, o, h, p, E, k, R, j, D, ee) => {
                    o = We(o), E = Je(p, E), b([], [n], (w) => {
                      w = w[0];
                      var e = `${w.name}.${o}`, r = { get() {
                        ct(`Cannot access ${e} due to unbound types`, [h, R]);
                      }, enumerable: !0, configurable: !0 };
                      return r.set = D ? () => ct(`Cannot access ${e} due to unbound types`, [h, R]) : () => {
                        throw new ye(e + " is a read-only property");
                      }, Object.defineProperty(w.o.M, o, r), b([], D ? [h, R] : [h], (m) => {
                        var v = m[0], _ = { get() {
                          var t = Sn(this, w, e + " getter");
                          return v.s(E(k, t));
                        }, enumerable: !0 };
                        if (D) {
                          D = Je(j, D);
                          var a = m[1];
                          _.set = function(t) {
                            var s = Sn(this, w, e + " setter"), f = [];
                            D(ee, s, a.B(f, t)), Tt(f);
                          };
                        }
                        return Object.defineProperty(w.o.M, o, _), [];
                      }), [];
                    });
                  },
                  _embind_register_emval: (n) => L(n, Yn),
                  _embind_register_enum: (n, o, h, p, E) => {
                    switch (o = We(o), E = E === 0 ? "object" : E === 1 ? "number" : "string", E) {
                      case "object":
                        let R = function() {
                        };
                        R.values = {}, L(n, { name: o, constructor: R, valueType: E, s: function(j) {
                          return this.constructor.values[j];
                        }, B: (j, D) => D.value, I: cn(o, h, p), H: null }), Ee(o, R);
                        break;
                      case "number":
                        var k = {};
                        L(n, {
                          name: o,
                          Fa: k,
                          valueType: E,
                          s: (j) => j,
                          B: (j, D) => D,
                          I: cn(o, h, p),
                          H: null
                        }), Ee(o, k), delete F[o].R;
                        break;
                      case "string":
                        k = {}, L(n, { name: o, $a: {}, Wa: {}, Fa: k, valueType: E, s: function(j) {
                          return this.Wa[j];
                        }, B: function(j, D) {
                          return this.$a[D];
                        }, I: cn(o, h, p), H: null }), Ee(o, k), delete F[o].R;
                    }
                  },
                  _embind_register_enum_value: (n, o, h) => {
                    var p = Wt(n, "enum");
                    switch (o = We(o), p.valueType) {
                      case "object":
                        n = p.constructor, p = Object.create(p.constructor.prototype, { value: { value: h }, constructor: { value: Te(`${p.name}_${o}`, function() {
                        }) } }), n.values[h] = p, n[o] = p;
                        break;
                      case "number":
                        p.Fa[o] = h;
                        break;
                      case "string":
                        p.$a[o] = h, p.Wa[h] = o, p.Fa[o] = o;
                    }
                  },
                  _embind_register_float: (n, o, h) => {
                    o = We(o), L(n, { name: o, s: (p) => p, B: (p, E) => E, I: zn(o, h), H: null });
                  },
                  _embind_register_function: (n, o, h, p, E, k) => {
                    var R = qt(o, h);
                    n = We(n), n = ln(n), E = Je(p, E), Ee(n, function() {
                      ct(`Cannot call ${n} due to unbound types`, R);
                    }, o - 1), b([], R, (j) => (dt(n, Zt(n, [j[0], null].concat(j.slice(1)), null, E, k), o - 1), []));
                  },
                  _embind_register_integer: (n, o, h, p, E) => {
                    o = We(o);
                    let k = (j) => j;
                    if (p === 0) {
                      var R = 32 - 8 * h;
                      k = (j) => j << R >>> R, E = k(E);
                    }
                    L(n, { name: o, s: k, B: (j, D) => D, I: $n(
                      o,
                      h,
                      p !== 0
                    ), H: null });
                  },
                  _embind_register_memory_view: (n, o, h) => {
                    function p(k) {
                      return new E(A.buffer, z[k + 4 >> 2], z[k >> 2]);
                    }
                    var E = [Int8Array, Uint8Array, Int16Array, Uint16Array, Int32Array, Uint32Array, Float32Array, Float64Array][o];
                    h = We(h), L(n, { name: h, s: p, I: p }, { Db: !0 });
                  },
                  _embind_register_std_string: (n, o) => {
                    o = We(o), L(n, { name: o, s(h) {
                      var p = (p = h + 4) ? lt(x, p, z[h >> 2], !0) : "";
                      return kt(h), p;
                    }, B(h, p) {
                      p instanceof ArrayBuffer && (p = new Uint8Array(p));
                      var E = typeof p == "string";
                      if (!(E || ArrayBuffer.isView(p) && p.BYTES_PER_ELEMENT == 1)) throw new ye("Cannot pass non-string to std::string");
                      var k = E ? hn(p) : p.length, R = Qt(4 + k + 1), j = R + 4;
                      return z[R >> 2] = k, E ? It(p, j, k + 1) : x.set(p, j), h !== null && h.push(kt, R), R;
                    }, I: Ot, H(h) {
                      kt(h);
                    } });
                  },
                  _embind_register_std_wstring: (n, o, h) => {
                    if (h = We(h), o === 2)
                      var p = Qn, E = Jn, k = Zn;
                    else p = qn, E = er, k = tr;
                    L(n, { name: h, s: (R) => {
                      var j = p(R + 4, z[R >> 2] * o, !0);
                      return kt(R), j;
                    }, B: (R, j) => {
                      if (typeof j != "string") throw new ye(`Cannot pass non-string to C++ string type ${h}`);
                      var D = k(j), ee = Qt(4 + D + o);
                      return z[ee >> 2] = D / o, E(j, ee + 4, D + o), R !== null && R.push(kt, ee), ee;
                    }, I: Ot, H(R) {
                      kt(R);
                    } });
                  },
                  _embind_register_value_object: (n, o, h, p, E, k) => {
                    Nt[n] = { name: We(o), Ha: Je(h, p), N: Je(E, k), Oa: [] };
                  },
                  _embind_register_value_object_field: (n, o, h, p, E, k, R, j, D, ee) => {
                    Nt[n].Oa.push({ tb: We(o), zb: h, xb: Je(p, E), yb: k, zh: R, yh: Je(j, D), Ah: ee });
                  },
                  _embind_register_void: (n, o) => {
                    o = We(o), L(n, { Fb: !0, name: o, s: () => {
                    }, B: () => {
                    } });
                  },
                  _emscripten_throw_longjmp: () => {
                    throw 1 / 0;
                  },
                  _emval_create_invoker: (n, o, h) => {
                    var [p, ...E] = rr(n, o), k = p.B.bind(p), R = E.map((D) => D.I.bind(D));
                    n--;
                    var j = Array(n);
                    return o = `methodCaller<(${E.map((D) => D.name)}) => ${p.name}>`, nr(Te(o, (D, ee, w, e) => {
                      for (var r = 0, m = 0; m < n; ++m) j[m] = R[m](e + r), r += 8;
                      switch (h) {
                        case 0:
                          var v = et(D).apply(null, j);
                          break;
                        case 2:
                          v = Reflect.construct(et(D), j);
                          break;
                        case 3:
                          v = j[0];
                          break;
                        case 1:
                          v = et(D)[An(ee)](...j);
                      }
                      return D = [], v = k(D, v), D.length && (z[w >> 2] = pt(D)), v;
                    }));
                  },
                  _emval_decref: un,
                  _emval_get_property: (n, o) => (n = et(n), o = et(o), pt(n[o])),
                  _emval_incref: (n) => {
                    9 < n && (Ye[n + 1] += 1);
                  },
                  _emval_invoke: (n, o, h, p, E) => dn[n](o, h, p, E),
                  _emval_new_array: () => pt([]),
                  _emval_new_cstring: (n) => pt(An(n)),
                  _emval_new_object: () => pt({}),
                  _emval_run_destructors: (n) => {
                    var o = et(n);
                    Tt(o), un(n);
                  },
                  _emval_set_property: (n, o, h) => {
                    n = et(n), o = et(o), h = et(h), n[o] = h;
                  },
                  _gmtime_js: function(n, o, h) {
                    n = new Date(1e3 * (o + 2097152 >>> 0 < 4194305 - !!n ? (n >>> 0) + 4294967296 * o : NaN)), B[h >> 2] = n.getUTCSeconds(), B[h + 4 >> 2] = n.getUTCMinutes(), B[h + 8 >> 2] = n.getUTCHours(), B[h + 12 >> 2] = n.getUTCDate(), B[h + 16 >> 2] = n.getUTCMonth(), B[h + 20 >> 2] = n.getUTCFullYear() - 1900, B[h + 24 >> 2] = n.getUTCDay(), B[h + 28 >> 2] = (n.getTime() - Date.UTC(n.getUTCFullYear(), 0, 1, 0, 0, 0, 0)) / 864e5 | 0;
                  },
                  _localtime_js: function(n, o, h) {
                    n = new Date(1e3 * (o + 2097152 >>> 0 < 4194305 - !!n ? (n >>> 0) + 4294967296 * o : NaN)), B[h >> 2] = n.getSeconds(), B[h + 4 >> 2] = n.getMinutes(), B[h + 8 >> 2] = n.getHours(), B[h + 12 >> 2] = n.getDate(), B[h + 16 >> 2] = n.getMonth(), B[h + 20 >> 2] = n.getFullYear() - 1900, B[h + 24 >> 2] = n.getDay(), o = n.getFullYear(), B[h + 28 >> 2] = (o % 4 !== 0 || o % 100 === 0 && o % 400 !== 0 ? ar : or)[n.getMonth()] + n.getDate() - 1 | 0, B[h + 36 >> 2] = -(60 * n.getTimezoneOffset()), o = new Date(n.getFullYear(), 6, 1).getTimezoneOffset();
                    var p = new Date(n.getFullYear(), 0, 1).getTimezoneOffset();
                    B[h + 32 >> 2] = (o != p && n.getTimezoneOffset() == Math.min(
                      p,
                      o
                    )) | 0;
                  },
                  _timegm_js: function(n) {
                    var o = new Date(Date.UTC(B[n + 20 >> 2] + 1900, B[n + 16 >> 2], B[n + 12 >> 2], B[n + 8 >> 2], B[n + 4 >> 2], B[n >> 2], 0));
                    return B[n + 24 >> 2] = o.getUTCDay(), B[n + 28 >> 2] = (o.getTime() - Date.UTC(o.getUTCFullYear(), 0, 1, 0, 0, 0, 0)) / 864e5 | 0, n = o.getTime() / 1e3, Kn((Fe = n, 1 <= +Math.abs(Fe) ? 0 < Fe ? +Math.floor(Fe / 4294967296) >>> 0 : ~~+Math.ceil((Fe - +(~~Fe >>> 0)) / 4294967296) >>> 0 : 0)), n >>> 0;
                  },
                  _tzset_js: (n, o, h, p) => {
                    var E = (/* @__PURE__ */ new Date()).getFullYear(), k = new Date(E, 0, 1).getTimezoneOffset();
                    E = new Date(E, 6, 1).getTimezoneOffset(), z[n >> 2] = 60 * Math.max(k, E), B[o >> 2] = +(k != E), o = (R) => {
                      var j = Math.abs(R);
                      return `UTC${0 <= R ? "-" : "+"}${String(Math.floor(j / 60)).padStart(2, "0")}${String(j % 60).padStart(2, "0")}`;
                    }, n = o(k), o = o(E), E < k ? (It(n, h, 17), It(o, p, 17)) : (It(n, p, 17), It(o, h, 17));
                  },
                  beginPixelLocalStorageWEBGL: function(n, o, h) {
                    (n = rt[n].F.ta) && n.beginPixelLocalStorageWEBGL(new Uint32Array(Pt.buffer, 4 * h, o));
                  },
                  clock_time_get: function(n, o, h, p) {
                    return 0 <= n && 3 >= n ? (n = Math.round(1e6 * (n === 0 ? Date.now() : performance.now())), xe = [n >>> 0, (Fe = n, 1 <= +Math.abs(Fe) ? 0 < Fe ? +Math.floor(Fe / 4294967296) >>> 0 : ~~+Math.ceil((Fe - +(~~Fe >>> 0)) / 4294967296) >>> 0 : 0)], B[p >> 2] = xe[0], B[p + 4 >> 2] = xe[1], 0) : 28;
                  },
                  decode_image: function(n, o, h) {
                    var p = F.images;
                    p || (p = /* @__PURE__ */ new Map(), F.images = p);
                    var E = new Image();
                    p.set(n, E), o = F.HEAP8.subarray(o, o + h), h = new Uint8Array(h), h.set(o), E.src = URL.createObjectURL(new Blob([h], { type: "image/png" })), E.onload = function() {
                      F._setWebImage(n, E.width, E.height);
                    };
                  },
                  delete_image: function(n) {
                    var o = F.images;
                    o && o.get(n) && o.delete(n);
                  },
                  emscripten_asm_const_int: (n, o, h) => {
                    fn.length = 0;
                    for (var p; p = x[o++]; ) {
                      var E = p != 105;
                      E &= p != 112, h += E && h % 8 ? 4 : 0, fn.push(p == 112 ? z[h >> 2] : p == 105 ? B[h >> 2] : ve[h >> 3]), h += E ? 8 : 4;
                    }
                    return cr[n](...fn);
                  },
                  emscripten_date_now: () => Date.now(),
                  emscripten_get_now: () => performance.now(),
                  emscripten_resize_heap: (n) => {
                    var o = x.length;
                    if (n >>>= 0, 2147483648 < n) return !1;
                    for (var h = 1; 4 >= h; h *= 2) {
                      var p = o * (1 + 0.2 / h);
                      p = Math.min(p, n + 100663296);
                      e: {
                        p = (Math.min(2147483648, 65536 * Math.ceil(Math.max(n, p) / 65536)) - Pt.buffer.byteLength + 65535) / 65536 | 0;
                        try {
                          Pt.grow(p), we();
                          var E = 1;
                          break e;
                        } catch {
                        }
                        E = void 0;
                      }
                      if (E) return !0;
                    }
                    return !1;
                  },
                  emscripten_webgl_enable_extension: (n, o) => (n = rt[n], o = o ? lt(x, o) : "", o.startsWith("GL_") && (o = o.slice(3)), o == "WEBGL_draw_instanced_base_vertex_base_instance" && Fn(W), o == "WEBGL_multi_draw_instanced_base_vertex_base_instance" && Mn(W), o == "WEBGL_multi_draw" && (W.Gb = W.getExtension("WEBGL_multi_draw")), o == "EXT_polygon_offset_clamp" && (W.sb = W.getExtension("EXT_polygon_offset_clamp")), o == "EXT_clip_control" && (W.rb = W.getExtension("EXT_clip_control")), o == "WEBGL_polygon_mode" && (W.Dh = W.getExtension("WEBGL_polygon_mode")), !!n.F.getExtension(o)),
                  emscripten_webgl_get_current_context: () => yt ? yt.handle : 0,
                  emscripten_webgl_make_context_current: (n) => $t(n) ? 0 : -5,
                  enable_WEBGL_provoking_vertex: function(n) {
                    return n = rt[n].F, n.Ua = n.getExtension("WEBGL_provoking_vertex"), !!n.Ua;
                  },
                  enable_WEBGL_shader_pixel_local_storage_coherent: function(n) {
                    n = rt[n].F;
                    const o = n.getExtension("WEBGL_shader_pixel_local_storage");
                    if (o && o.isCoherent()) {
                      if (o.framebufferTexturePixelLocalStorageWEBGL.length == 5) return n.ta = o, !0;
                      console.warn("WEBGL_shader_pixel_local_storage is advertised, but a deprecated version has been detected. Disabling.");
                    }
                    return !1;
                  },
                  endPixelLocalStorageWEBGL: function(n, o, h) {
                    (n = rt[n].F.ta) && n.endPixelLocalStorageWEBGL(new Uint32Array(Pt.buffer, 4 * h, o));
                  },
                  environ_get: (n, o) => {
                    var h = 0, p = 0, E;
                    for (E of Pn()) {
                      var k = o + h;
                      z[n + p >> 2] = k, h += It(E, k, 1 / 0) + 1, p += 4;
                    }
                    return 0;
                  },
                  environ_sizes_get: (n, o) => {
                    var h = Pn();
                    z[n >> 2] = h.length, n = 0;
                    for (var p of h) n += hn(p) + 1;
                    return z[o >> 2] = n, 0;
                  },
                  fd_close: () => 52,
                  fd_read: () => 52,
                  fd_seek: function() {
                    return 70;
                  },
                  fd_write: (n, o, h, p) => {
                    for (var E = 0, k = 0; k < h; k++) {
                      var R = z[o >> 2], j = z[o + 4 >> 2];
                      o += 8;
                      for (var D = 0; D < j; D++) {
                        var ee = n, w = x[R + D], e = lr[ee];
                        w === 0 || w === 10 ? ((ee === 1 ? Z : fe)(lt(e)), e.length = 0) : e.push(w);
                      }
                      E += j;
                    }
                    return z[p >> 2] = E, 0;
                  },
                  framebufferPixelLocalClearValuefvWEBGL: function(n, o, h, p, E, k) {
                    (n = rt[n].F.ta) && n.framebufferPixelLocalClearValuefvWEBGL(o, [h, p, E, k]);
                  },
                  framebufferTexturePixelLocalStorageWEBGL: function(n, o, h, p, E, k) {
                    (n = rt[n].F.ta) && n.framebufferTexturePixelLocalStorageWEBGL(o, Dt[h], p, E, k);
                  },
                  glActiveTexture: (n) => W.activeTexture(n),
                  glAttachShader: (n, o) => {
                    W.attachShader(gt[n], Et[o]);
                  },
                  glBindAttribLocation: (n, o, h) => {
                    W.bindAttribLocation(
                      gt[n],
                      o,
                      h ? lt(x, h) : ""
                    );
                  },
                  glBindBuffer: (n, o) => {
                    n == 35051 ? W.Ca = o : n == 35052 && (W.Y = o), W.bindBuffer(n, Yt[o]);
                  },
                  glBindBufferRange: (n, o, h, p, E) => {
                    W.bindBufferRange(n, o, Yt[h], p, E);
                  },
                  glBindFramebuffer: (n, o) => {
                    W.bindFramebuffer(n, en[o]);
                  },
                  glBindRenderbuffer: (n, o) => {
                    W.bindRenderbuffer(n, zt[o]);
                  },
                  glBindSampler: (n, o) => {
                    W.bindSampler(n, Ut[o]);
                  },
                  glBindTexture: (n, o) => {
                    W.bindTexture(n, Dt[o]);
                  },
                  glBindVertexArray: (n) => {
                    W.bindVertexArray(tn[n]);
                  },
                  glBlendColor: (n, o, h, p) => W.blendColor(n, o, h, p),
                  glBlendEquation: (n) => W.blendEquation(n),
                  glBlendEquationSeparate: (n, o) => W.blendEquationSeparate(n, o),
                  glBlendFunc: (n, o) => W.blendFunc(n, o),
                  glBlendFuncSeparate: (n, o, h, p) => W.blendFuncSeparate(n, o, h, p),
                  glBlitFramebuffer: (n, o, h, p, E, k, R, j, D, ee) => W.blitFramebuffer(n, o, h, p, E, k, R, j, D, ee),
                  glBufferData: (n, o, h, p) => {
                    h && o ? W.bufferData(n, x, p, h, o) : W.bufferData(n, o, p);
                  },
                  glBufferSubData: (n, o, h, p) => {
                    h && W.bufferSubData(n, o, x, p, h);
                  },
                  glCheckFramebufferStatus: (n) => W.checkFramebufferStatus(n),
                  glClear: (n) => W.clear(n),
                  glClearBufferfi: (n, o, h, p) => W.clearBufferfi(n, o, h, p),
                  glClearBufferfv: (n, o, h) => {
                    W.clearBufferfv(
                      n,
                      o,
                      J,
                      h >> 2
                    );
                  },
                  glClearBufferiv: (n, o, h) => {
                    W.clearBufferiv(n, o, B, h >> 2);
                  },
                  glClearBufferuiv: (n, o, h) => {
                    W.clearBufferuiv(n, o, z, h >> 2);
                  },
                  glClearColor: (n, o, h, p) => W.clearColor(n, o, h, p),
                  glClearDepthf: (n) => W.clearDepth(n),
                  glClearStencil: (n) => W.clearStencil(n),
                  glColorMask: (n, o, h, p) => {
                    W.colorMask(!!n, !!o, !!h, !!p);
                  },
                  glCompileShader: (n) => {
                    W.compileShader(Et[n]);
                  },
                  glCompressedTexSubImage2D: (n, o, h, p, E, k, R, j, D) => {
                    W.Y || !j ? W.compressedTexSubImage2D(n, o, h, p, E, k, R, j, D) : W.compressedTexSubImage2D(n, o, h, p, E, k, R, x, D, j);
                  },
                  glCompressedTexSubImage3D: (n, o, h, p, E, k, R, j, D, ee, w) => {
                    W.Y ? W.compressedTexSubImage3D(n, o, h, p, E, k, R, j, D, ee, w) : W.compressedTexSubImage3D(n, o, h, p, E, k, R, j, D, x, w, ee);
                  },
                  glCreateProgram: () => {
                    var n = nn(gt), o = W.createProgram();
                    return o.name = n, o.sa = o.qa = o.ra = 0, o.Ia = 1, gt[n] = o, n;
                  },
                  glCreateShader: (n) => {
                    var o = nn(Et);
                    return Et[o] = W.createShader(n), o;
                  },
                  glCullFace: (n) => W.cullFace(n),
                  glDeleteBuffers: (n, o) => {
                    for (var h = 0; h < n; h++) {
                      var p = B[o + 4 * h >> 2], E = Yt[p];
                      E && (W.deleteBuffer(E), E.name = 0, Yt[p] = null, p == W.Ca && (W.Ca = 0), p == W.Y && (W.Y = 0));
                    }
                  },
                  glDeleteFramebuffers: (n, o) => {
                    for (var h = 0; h < n; ++h) {
                      var p = B[o + 4 * h >> 2], E = en[p];
                      E && (W.deleteFramebuffer(E), E.name = 0, en[p] = null);
                    }
                  },
                  glDeleteProgram: (n) => {
                    if (n) {
                      var o = gt[n];
                      o ? (W.deleteProgram(o), o.name = 0, gt[n] = null) : $e || ($e = 1281);
                    }
                  },
                  glDeleteRenderbuffers: (n, o) => {
                    for (var h = 0; h < n; h++) {
                      var p = B[o + 4 * h >> 2], E = zt[p];
                      E && (W.deleteRenderbuffer(E), E.name = 0, zt[p] = null);
                    }
                  },
                  glDeleteSamplers: (n, o) => {
                    for (var h = 0; h < n; h++) {
                      var p = B[o + 4 * h >> 2], E = Ut[p];
                      E && (W.deleteSampler(E), E.name = 0, Ut[p] = null);
                    }
                  },
                  glDeleteShader: (n) => {
                    if (n) {
                      var o = Et[n];
                      o ? (W.deleteShader(o), Et[n] = null) : $e || ($e = 1281);
                    }
                  },
                  glDeleteTextures: (n, o) => {
                    for (var h = 0; h < n; h++) {
                      var p = B[o + 4 * h >> 2], E = Dt[p];
                      E && (W.deleteTexture(E), E.name = 0, Dt[p] = null);
                    }
                  },
                  glDeleteVertexArrays: (n, o) => {
                    for (var h = 0; h < n; h++) {
                      var p = B[o + 4 * h >> 2];
                      W.deleteVertexArray(tn[p]), tn[p] = null;
                    }
                  },
                  glDepthFunc: (n) => W.depthFunc(n),
                  glDepthMask: (n) => {
                    W.depthMask(!!n);
                  },
                  glDepthRangef: (n, o) => W.depthRange(n, o),
                  glDisable: (n) => W.disable(n),
                  glDisableVertexAttribArray: (n) => {
                    W.disableVertexAttribArray(n);
                  },
                  glDrawArrays: (n, o, h) => {
                    W.drawArrays(n, o, h);
                  },
                  glDrawArraysInstanced: (n, o, h, p) => {
                    W.drawArraysInstanced(n, o, h, p);
                  },
                  glDrawBuffers: (n, o) => {
                    for (var h = mn[n], p = 0; p < n; p++) h[p] = B[o + 4 * p >> 2];
                    W.drawBuffers(h);
                  },
                  glDrawElements: (n, o, h, p) => {
                    W.drawElements(n, o, h, p);
                  },
                  glDrawElementsInstanced: (n, o, h, p, E) => {
                    W.drawElementsInstanced(n, o, h, p, E);
                  },
                  glEnable: (n) => W.enable(n),
                  glEnableVertexAttribArray: (n) => {
                    W.enableVertexAttribArray(n);
                  },
                  glFlush: () => W.flush(),
                  glFramebufferRenderbuffer: (n, o, h, p) => {
                    W.framebufferRenderbuffer(n, o, h, zt[p]);
                  },
                  glFramebufferTexture2D: (n, o, h, p, E) => {
                    W.framebufferTexture2D(
                      n,
                      o,
                      h,
                      Dt[p],
                      E
                    );
                  },
                  glFramebufferTextureLayer: (n, o, h, p, E) => {
                    W.framebufferTextureLayer(n, o, Dt[h], p, E);
                  },
                  glFrontFace: (n) => W.frontFace(n),
                  glGenBuffers: (n, o) => {
                    Vt(n, o, "createBuffer", Yt);
                  },
                  glGenFramebuffers: (n, o) => {
                    Vt(n, o, "createFramebuffer", en);
                  },
                  glGenRenderbuffers: (n, o) => {
                    Vt(n, o, "createRenderbuffer", zt);
                  },
                  glGenSamplers: (n, o) => {
                    Vt(n, o, "createSampler", Ut);
                  },
                  glGenTextures: (n, o) => {
                    Vt(n, o, "createTexture", Dt);
                  },
                  glGenVertexArrays: (n, o) => {
                    Vt(n, o, "createVertexArray", tn);
                  },
                  glGenerateMipmap: (n) => W.generateMipmap(n),
                  glGetFloatv: (n, o) => jn(
                    n,
                    o,
                    2
                  ),
                  glGetFramebufferAttachmentParameteriv: (n, o, h, p) => {
                    n = W.getFramebufferAttachmentParameter(n, o, h), (n instanceof WebGLRenderbuffer || n instanceof WebGLTexture) && (n = n.name | 0), B[p >> 2] = n;
                  },
                  glGetIntegerv: (n, o) => jn(n, o, 0),
                  glGetProgramInfoLog: (n, o, h, p) => {
                    n = W.getProgramInfoLog(gt[n]), n === null && (n = "(unknown error)"), o = 0 < o && p ? It(n, p, o) : 0, h && (B[h >> 2] = o);
                  },
                  glGetProgramiv: (n, o, h) => {
                    if (h) if (n >= kn) $e || ($e = 1281);
                    else if (n = gt[n], o == 35716) n = W.getProgramInfoLog(n), n === null && (n = "(unknown error)"), B[h >> 2] = n.length + 1;
                    else if (o == 35719) {
                      if (!n.sa) {
                        var p = W.getProgramParameter(n, 35718);
                        for (o = 0; o < p; ++o) n.sa = Math.max(n.sa, W.getActiveUniform(n, o).name.length + 1);
                      }
                      B[h >> 2] = n.sa;
                    } else if (o == 35722) {
                      if (!n.qa) for (p = W.getProgramParameter(n, 35721), o = 0; o < p; ++o) n.qa = Math.max(n.qa, W.getActiveAttrib(n, o).name.length + 1);
                      B[h >> 2] = n.qa;
                    } else if (o == 35381) {
                      if (!n.ra) for (p = W.getProgramParameter(n, 35382), o = 0; o < p; ++o) n.ra = Math.max(n.ra, W.getActiveUniformBlockName(n, o).length + 1);
                      B[h >> 2] = n.ra;
                    } else B[h >> 2] = W.getProgramParameter(n, o);
                    else $e || ($e = 1281);
                  },
                  glGetShaderInfoLog: (n, o, h, p) => {
                    n = W.getShaderInfoLog(Et[n]), n === null && (n = "(unknown error)"), o = 0 < o && p ? It(n, p, o) : 0, h && (B[h >> 2] = o);
                  },
                  glGetShaderiv: (n, o, h) => {
                    h ? o == 35716 ? (n = W.getShaderInfoLog(Et[n]), n === null && (n = "(unknown error)"), B[h >> 2] = n ? n.length + 1 : 0) : o == 35720 ? (n = W.getShaderSource(Et[n]), B[h >> 2] = n ? n.length + 1 : 0) : B[h >> 2] = W.getShaderParameter(Et[n], o) : $e || ($e = 1281);
                  },
                  glGetString: (n) => {
                    var o = Cn[n];
                    if (!o) {
                      switch (n) {
                        case 7939:
                          o = Kt(yn().join(" "));
                          break;
                        case 7936:
                        case 7937:
                        case 37445:
                        case 37446:
                          (o = W.getParameter(n)) || $e || ($e = 1280), o = o ? Kt(o) : 0;
                          break;
                        case 7938:
                          o = Kt(`OpenGL ES 3.0 (${W.getParameter(7938)})`);
                          break;
                        case 35724:
                          o = W.getParameter(35724);
                          var h = o.match(/^WebGL GLSL ES ([0-9]\.[0-9][0-9]?)(?:$| .*)/);
                          h !== null && (h[1].length == 3 && (h[1] += "0"), o = `OpenGL ES GLSL ES ${h[1]} (${o})`), o = Kt(o);
                          break;
                        default:
                          $e || ($e = 1280);
                      }
                      Cn[n] = o;
                    }
                    return o;
                  },
                  glGetStringi: (n, o) => {
                    if (2 > yt.version) return $e || ($e = 1282), 0;
                    var h = Rn[n];
                    if (h) return 0 > o || o >= h.length ? ($e || ($e = 1281), 0) : h[o];
                    switch (n) {
                      case 7939:
                        return h = yn().map(Kt), h = Rn[n] = h, 0 > o || o >= h.length ? ($e || ($e = 1281), 0) : h[o];
                      default:
                        return $e || ($e = 1280), 0;
                    }
                  },
                  glGetUniformBlockIndex: (n, o) => W.getUniformBlockIndex(gt[n], o ? lt(x, o) : ""),
                  glGetUniformLocation: (n, o) => {
                    if (o = o ? lt(x, o) : "", n = gt[n]) {
                      var h = n, p = h.ea, E = h.Za, k;
                      if (!p) {
                        h.ea = p = {}, h.Ya = {};
                        var R = W.getProgramParameter(h, 35718);
                        for (k = 0; k < R; ++k) {
                          var j = W.getActiveUniform(h, k), D = j.name;
                          j = j.size;
                          var ee = Ln(D);
                          ee = 0 < ee ? D.slice(0, ee) : D;
                          var w = h.Ia;
                          for (h.Ia += j, E[ee] = [j, w], D = 0; D < j; ++D) p[w] = D, h.Ya[w++] = ee;
                        }
                      }
                      if (h = n.ea, p = 0, E = o, k = Ln(o), 0 < k && (p = parseInt(o.slice(k + 1)) >>> 0, E = o.slice(0, k)), (E = n.Za[E]) && p < E[0] && (p += E[1], h[p] = h[p] || W.getUniformLocation(n, o))) return p;
                    } else $e || ($e = 1281);
                    return -1;
                  },
                  glInvalidateFramebuffer: (n, o, h) => {
                    for (var p = mn[o], E = 0; E < o; E++) p[E] = B[h + 4 * E >> 2];
                    W.invalidateFramebuffer(n, p);
                  },
                  glLinkProgram: (n) => {
                    n = gt[n], W.linkProgram(n), n.ea = 0, n.Za = {};
                  },
                  glPixelStorei: (n, o) => {
                    n == 3317 ? vn = o : n == 3314 && (xn = o), W.pixelStorei(n, o);
                  },
                  glPolygonOffset: (n, o) => W.polygonOffset(n, o),
                  glReadBuffer: (n) => W.readBuffer(n),
                  glReadPixels: (n, o, h, p, E, k, R) => {
                    if (W.Ca) W.readPixels(n, o, h, p, E, k, R);
                    else {
                      var j = rn(k);
                      R >>>= 31 - Math.clz32(j.BYTES_PER_ELEMENT), W.readPixels(n, o, h, p, E, k, j, R);
                    }
                  },
                  glRenderbufferStorage: (n, o, h, p) => W.renderbufferStorage(n, o, h, p),
                  glRenderbufferStorageMultisample: (n, o, h, p, E) => W.renderbufferStorageMultisample(n, o, h, p, E),
                  glSamplerParameterf: (n, o, h) => {
                    W.samplerParameterf(Ut[n], o, h);
                  },
                  glSamplerParameteri: (n, o, h) => {
                    W.samplerParameteri(Ut[n], o, h);
                  },
                  glScissor: (n, o, h, p) => W.scissor(n, o, h, p),
                  glShaderSource: (n, o, h, p) => {
                    for (var E = "", k = 0; k < o; ++k) {
                      var R = (R = z[h + 4 * k >> 2]) ? lt(x, R, p ? z[p + 4 * k >> 2] : void 0) : "";
                      E += R;
                    }
                    W.shaderSource(Et[n], E);
                  },
                  glStencilFunc: (n, o, h) => W.stencilFunc(n, o, h),
                  glStencilFuncSeparate: (n, o, h, p) => W.stencilFuncSeparate(n, o, h, p),
                  glStencilMask: (n) => W.stencilMask(n),
                  glStencilMaskSeparate: (n, o) => W.stencilMaskSeparate(n, o),
                  glStencilOp: (n, o, h) => W.stencilOp(n, o, h),
                  glStencilOpSeparate: (n, o, h, p) => W.stencilOpSeparate(n, o, h, p),
                  glTexParameteri: (n, o, h) => W.texParameteri(n, o, h),
                  glTexStorage2D: (n, o, h, p, E) => W.texStorage2D(n, o, h, p, E),
                  glTexStorage3D: (n, o, h, p, E, k) => W.texStorage3D(n, o, h, p, E, k),
                  glTexSubImage2D: (n, o, h, p, E, k, R, j, D) => {
                    if (W.Y) W.texSubImage2D(
                      n,
                      o,
                      h,
                      p,
                      E,
                      k,
                      R,
                      j,
                      D
                    );
                    else if (D) {
                      var ee = rn(j);
                      W.texSubImage2D(n, o, h, p, E, k, R, j, ee, D >>> 31 - Math.clz32(ee.BYTES_PER_ELEMENT));
                    } else {
                      if (D) {
                        ee = rn(j);
                        var w = k * ((xn || E) * ({ 5: 3, 6: 4, 8: 2, 29502: 3, 29504: 4, 26917: 2, 26918: 2, 29846: 3, 29847: 4 }[R - 6402] || 1) * ee.BYTES_PER_ELEMENT + vn - 1 & -vn);
                        D = ee.subarray(D >>> 31 - Math.clz32(ee.BYTES_PER_ELEMENT), D + w >>> 31 - Math.clz32(ee.BYTES_PER_ELEMENT));
                      } else D = null;
                      W.texSubImage2D(n, o, h, p, E, k, R, j, D);
                    }
                  },
                  glTexSubImage3D: (n, o, h, p, E, k, R, j, D, ee, w) => {
                    if (W.Y) W.texSubImage3D(n, o, h, p, E, k, R, j, D, ee, w);
                    else if (w) {
                      var e = rn(ee);
                      W.texSubImage3D(n, o, h, p, E, k, R, j, D, ee, e, w >>> 31 - Math.clz32(e.BYTES_PER_ELEMENT));
                    } else W.texSubImage3D(n, o, h, p, E, k, R, j, D, ee, null);
                  },
                  glUniform1i: (n, o) => {
                    var h = W, p = h.uniform1i, E = W.nb;
                    if (E) {
                      var k = E.ea[n];
                      typeof k == "number" && (E.ea[n] = k = W.getUniformLocation(E, E.Ya[n] + (0 < k ? `[${k}]` : ""))), n = k;
                    } else $e || ($e = 1282), n = void 0;
                    p.call(h, n, o);
                  },
                  glUniformBlockBinding: (n, o, h) => {
                    n = gt[n], W.uniformBlockBinding(n, o, h);
                  },
                  glUseProgram: (n) => {
                    n = gt[n], W.useProgram(n), W.nb = n;
                  },
                  glVertexAttribDivisor: (n, o) => {
                    W.vertexAttribDivisor(n, o);
                  },
                  glVertexAttribIPointer: (n, o, h, p, E) => {
                    W.vertexAttribIPointer(n, o, h, p, E);
                  },
                  glVertexAttribPointer: (n, o, h, p, E, k) => {
                    W.vertexAttribPointer(n, o, h, !!p, E, k);
                  },
                  glViewport: (n, o, h, p) => W.viewport(n, o, h, p),
                  invoke_vii: hr,
                  isWindowsBrowser: function() {
                    return -1 < navigator.platform.indexOf("Win");
                  },
                  provokingVertexWEBGL: function(n, o) {
                    (n = rt[n].F.Ua) && n.provokingVertexWEBGL(o);
                  },
                  riveWebCall: function(n, o, h, p, E, k, R) {
                    return F.riveScripting.call(n, o, h, p, E, k, R);
                  },
                  riveWebHasExport: function(n, o) {
                    return F.riveScripting.Ab(n, o);
                  },
                  riveWebMemoryPages: function(n) {
                    return F.riveScripting.Hb(n);
                  },
                  riveWebPreparing: function(n) {
                    return F.riveScripting.V(n);
                  },
                  riveWebRaise: function(n, o) {
                    F.riveScripting.Kb(n, o);
                  },
                  riveWebReadMemory: function(n, o, h, p) {
                    return F.riveScripting.read(n, o, h, p);
                  },
                  riveWebRegister: function(n, o, h) {
                    const p = F.riveScripting;
                    return p ? (p.ib({ exports: F, Bb: (E) => (E = z[(Dn() >> 2) + E], E === 0 ? void 0 : Jt.get(E)), Z: () => x, Pa: () => ve, da: at, ua: ur, ca: Ue, Ga: Qt, Da: kt, Ja: (E) => E ? lt(x, E) : "", ab: (E, k, R) => It(E, k, R) }), p.register(n, x.subarray(o, o + h)), 1) : 0;
                  },
                  riveWebRelease: function(n) {
                    var o;
                    (o = F.riveScripting) == null || o.release(n);
                  },
                  riveWebStart: function(n) {
                    return n = F.riveScripting.start(n), n === null ? 0 : Kt(n);
                  },
                  riveWebStringLength: function(n, o) {
                    return F.riveScripting.Ch(n, o);
                  },
                  riveWebWriteMemory: function(n, o, h, p) {
                    return F.riveScripting.write(n, o, h, p);
                  },
                  upload_image: function(n, o) {
                    var h = F.images;
                    h && (o = h.get(o)) && (n = rt[n].F, n.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL, !0), n.texImage2D(n.TEXTURE_2D, 0, n.RGBA, n.RGBA, n.UNSIGNED_BYTE, o), n.pixelStorei(n.UNPACK_PREMULTIPLY_ALPHA_WEBGL, !1));
                  },
                  wasm_start_image_decode: function(n, o, h) {
                    o = new Uint8Array(
                      Pt.buffer,
                      o,
                      h
                    );
                    var p = new Uint8Array(h);
                    p.set(o), Promise.resolve().then(function() {
                      return createImageBitmap(new Blob([p]));
                    }).then(function(E) {
                      var k = new OffscreenCanvas(E.width, E.height).getContext("2d");
                      k.drawImage(E, 0, 0), k = k.getImageData(0, 0, E.width, E.height);
                      var R = k.data.length, j = On(R);
                      j ? (new Uint8Array(Pt.buffer, j, R).set(k.data), Bn(n, E.width, E.height, j, R)) : wn(n);
                    }).catch(function() {
                      wn(n);
                    });
                  }
                };
                function hr(n, o, h) {
                  var p = bn();
                  try {
                    Jt.get(n)(o, h);
                  } catch (E) {
                    if (_n(p), E !== E + 0) throw E;
                    Vn(1, 0);
                  }
                }
                var on;
                return on = await (async function() {
                  function n(h) {
                    return h = on = h.exports, kt = h.free, Qt = h.malloc, F._setWebImage = h.setWebImage, Tn = h.__getTypeName, On = F._wasm_image_decode_alloc = h.wasm_image_decode_alloc, Bn = F._wasm_image_decode_complete = h.wasm_image_decode_complete, wn = F._wasm_image_decode_error = h.wasm_image_decode_error, F._rive_web_vm_module_export = h.rive_web_vm_module_export, F._rive_web_vm_booting = h.rive_web_vm_booting, Dn = F._rive_web_calls = h.rive_web_calls, Wn = F._ma_device__on_notification_unlocked = h.ma_device__on_notification_unlocked, F._ma_malloc_emscripten = h.ma_malloc_emscripten, F._ma_free_emscripten = h.ma_free_emscripten, Nn = F._ma_device_process_pcm_frames_capture__webaudio = h.ma_device_process_pcm_frames_capture__webaudio, Un = F._ma_device_process_pcm_frames_playback__webaudio = h.ma_device_process_pcm_frames_playback__webaudio, Vn = h.setThrew, Kn = h._emscripten_tempret_set, _n = h._emscripten_stack_restore, Hn = h._emscripten_stack_alloc, bn = h.emscripten_stack_get_current, He.vij = h.dynCall_vij, He.iij = h.dynCall_iij, He.ji = h.dynCall_ji, He.iijii = h.dynCall_iijii, He.iiiji = h.dynCall_iiiji, He.iiji = h.dynCall_iiji, He.jii = h.dynCall_jii, He.vijj = h.dynCall_vijj, He.jiji = h.dynCall_jiji, Pt = h.memory, Jt = h.__indirect_function_table, we(), on;
                  }
                  var o = { env: Gn, wasi_snapshot_preview1: Gn };
                  return F.instantiateWasm ? new Promise((h) => {
                    F.instantiateWasm(o, (p, E) => {
                      h(n(p));
                    });
                  }) : (Se ?? (Se = F.locateFile ? F.locateFile("webgl2_advanced.wasm", K) : K + "webgl2_advanced.wasm"), n((await ke(o)).instance));
                })(), (function() {
                  function n() {
                    var h;
                    if (F.calledRun = !0, !Be) {
                      if (Ie = !0, on.__wasm_call_ctors(), _e == null || _e(F), (h = F.onRuntimeInitialized) == null || h.call(F), F.postRun) for (typeof F.postRun == "function" && (F.postRun = [F.postRun]); F.postRun.length; ) {
                        var o = F.postRun.shift();
                        Xe.push(o);
                      }
                      Ne(Xe);
                    }
                  }
                  if (F.preRun) for (typeof F.preRun == "function" && (F.preRun = [F.preRun]); F.preRun.length; ) ot();
                  Ne(Qe), F.setStatus ? (F.setStatus("Running..."), setTimeout(() => {
                    setTimeout(() => F.setStatus(""), 1), n();
                  }, 1)) : n();
                })(), Ie ? Y = F : Y = new Promise((n, o) => {
                  _e = n, se = o;
                }), Y;
              };
            })();
            const C = oe;
          }),
          /* 5 */
          /***/
          ((Ce) => {
            Ce.exports = /* @__PURE__ */ JSON.parse(`{"name":"@rive-app/webgl2","version":"2.44.2","description":"Rive's webgl2 based web api.","main":"rive.js","homepage":"https://rive.app","repository":{"type":"git","url":"https://github.com/rive-app/rive-wasm/tree/master/js"},"keywords":["rive","animation"],"author":"Rive","contributors":["Luigi Rosso <luigi@rive.app> (https://rive.app)","Maxwell Talbot <max@rive.app> (https://rive.app)","Arthur Vivian <arthur@rive.app> (https://rive.app)","Umberto Sonnino <umberto@rive.app> (https://rive.app)","Matthew Sullivan <matt.j.sullivan@gmail.com> (mailto:matt.j.sullivan@gmail.com)","Chris Dalton <chris@rive.app> (https://rive.app)"],"license":"MIT","files":["rive.js","rive.wasm","rive_fallback.wasm","rive.js.map","rive.d.ts","rive_advanced.mjs.d.ts","runtimeLoader.d.ts","utils","semantics"],"typings":"rive.d.ts","dependencies":{},"browser":{"fs":false,"path":false}}`);
          }),
          /* 6 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              AccessibilityOverlay: () => (
                /* reexport safe */
                C.AccessibilityOverlay
              ),
              /* harmony export */
              CHECK_STATE_MASK: () => (
                /* reexport safe */
                I.CHECK_STATE_MASK
              ),
              /* harmony export */
              CHECK_STATE_OFFSET: () => (
                /* reexport safe */
                I.CHECK_STATE_OFFSET
              ),
              /* harmony export */
              SemanticActionType: () => (
                /* reexport safe */
                I.SemanticActionType
              ),
              /* harmony export */
              SemanticCheckState: () => (
                /* reexport safe */
                I.SemanticCheckState
              ),
              /* harmony export */
              SemanticMode: () => (
                /* reexport safe */
                I.SemanticMode
              ),
              /* harmony export */
              SemanticRole: () => (
                /* reexport safe */
                I.SemanticRole
              ),
              /* harmony export */
              SemanticState: () => (
                /* reexport safe */
                I.SemanticState
              ),
              /* harmony export */
              SemanticTrait: () => (
                /* reexport safe */
                I.SemanticTrait
              ),
              /* harmony export */
              SemanticTreeModel: () => (
                /* reexport safe */
                oe.SemanticTreeModel
              ),
              /* harmony export */
              checkStateOf: () => (
                /* reexport safe */
                I.checkStateOf
              ),
              /* harmony export */
              hasState: () => (
                /* reexport safe */
                I.hasState
              ),
              /* harmony export */
              hasTrait: () => (
                /* reexport safe */
                I.hasTrait
              ),
              /* harmony export */
              roleName: () => (
                /* reexport safe */
                I.roleName
              ),
              /* harmony export */
              stateNames: () => (
                /* reexport safe */
                I.stateNames
              ),
              /* harmony export */
              traitNames: () => (
                /* reexport safe */
                I.traitNames
              )
              /* harmony export */
            });
            var oe = ae(7), C = ae(9), I = ae(8);
          }),
          /* 7 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              SemanticTreeModel: () => (
                /* binding */
                I
              )
              /* harmony export */
            });
            var oe = ae(8), C = function(T, O, G) {
              if (G || arguments.length === 2) for (var le = 0, me = O.length, K; le < me; le++)
                (K || !(le in O)) && (K || (K = Array.prototype.slice.call(O, 0, le)), K[le] = O[le]);
              return T.concat(K || Array.prototype.slice.call(O));
            }, I = (
              /** @class */
              (function() {
                function T() {
                  this._nodesById = /* @__PURE__ */ new Map(), this._roots = [], this._semanticVersion = 0, this._geometryVersion = 0, this._geometryChangedIds = /* @__PURE__ */ new Set(), this._semanticChangedIds = /* @__PURE__ */ new Set(), this._debug = !1;
                }
                return Object.defineProperty(T.prototype, "nodeCount", {
                  get: function() {
                    return this._nodesById.size;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(T.prototype, "semanticVersion", {
                  /** Bumped when semantic content or tree structure changes. */
                  get: function() {
                    return this._semanticVersion;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(T.prototype, "geometryVersion", {
                  /** Bumped when node bounds change without a semantic/structural change. */
                  get: function() {
                    return this._geometryVersion;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(T.prototype, "geometryChangedIds", {
                  /** Node IDs whose bounds changed in the most recent {@link applyDiff}. */
                  get: function() {
                    return this._geometryChangedIds;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(T.prototype, "semanticChangedIds", {
                  /**
                   * Node IDs whose semantic fields (role/label/value/hint/flags/headingLevel)
                   * changed in the most recent {@link applyDiff}. Structural changes (moves,
                   * child reorders, removals) bump {@link semanticVersion} but don't mark
                   * nodes here — element attributes don't depend on tree position.
                   */
                  get: function() {
                    return this._semanticChangedIds;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(T.prototype, "roots", {
                  /** Root node IDs in sibling order. */
                  get: function() {
                    return this._roots;
                  },
                  enumerable: !1,
                  configurable: !0
                }), T.prototype.nodeById = function(O) {
                  return this._nodesById.get(O);
                }, T.prototype.focusedNode = function() {
                  for (var O = this._nodesById.values(), G = O.next(); !G.done; G = O.next())
                    if ((0, oe.hasState)(G.value.stateFlags, oe.SemanticState.Focused))
                      return G.value;
                }, T.prototype.siblingIndexOf = function(O) {
                  var G = this._nodesById.get(O);
                  if (!G)
                    return -1;
                  if (G.parentId < 0)
                    return this._roots.indexOf(O);
                  var le = this._nodesById.get(G.parentId);
                  return le ? le.children.indexOf(O) : -1;
                }, T.prototype.detach = function(O) {
                  var G = this._nodesById.get(O);
                  if (G)
                    if (G.parentId < 0) {
                      var le = this._roots.indexOf(O);
                      le !== -1 && this._roots.splice(le, 1);
                    } else {
                      var me = this._nodesById.get(G.parentId);
                      if (me) {
                        var le = me.children.indexOf(O);
                        le !== -1 && me.children.splice(le, 1);
                      }
                    }
                }, T.prototype.attach = function(O, G, le) {
                  var me = this._nodesById.get(O);
                  if (me)
                    if (G < 0) {
                      me.parentId = -1;
                      var K = te(le, 0, this._roots.length);
                      this._roots.splice(K, 0, O);
                    } else {
                      var X = this._nodesById.get(G);
                      if (!X)
                        me.parentId = -1, this._roots.push(O);
                      else {
                        me.parentId = G;
                        var K = te(le, 0, X.children.length);
                        X.children.splice(K, 0, O);
                      }
                    }
                }, T.prototype.removeSubtree = function(O) {
                  var G = this._nodesById.get(O);
                  if (G) {
                    for (var le = C([], G.children, !0), me = 0, K = le; me < K.length; me++) {
                      var X = K[me];
                      this.removeSubtree(X);
                    }
                    this.detach(O), this._nodesById.delete(O);
                  }
                }, T.prototype.applyDiff = function(O) {
                  var G, le, me = this;
                  this._geometryChangedIds.clear(), this._semanticChangedIds.clear();
                  for (var K = !1, X = !1, re = function() {
                    K = !0;
                  }, Z = function(Ue) {
                    K = !0, me._semanticChangedIds.add(Ue);
                  }, fe = function(Ue) {
                    X = !0, me._geometryChangedIds.add(Ue);
                  }, q = 0, Be = O.removed; q < Be.length; q++) {
                    var Ae = Be[q];
                    this._nodesById.has(Ae) && (this.removeSubtree(Ae), re());
                  }
                  for (var _e = 0, se = O.added; _e < se.length; _e++) {
                    var A = se[_e], x = this._nodesById.get(A.id);
                    x ? (Y(x, A) && (ie(x, A), Z(A.id)), F(x, A) && (V(x, A), fe(A.id))) : (this._nodesById.set(A.id, ne(A)), Z(A.id), fe(A.id)), this.detach(A.id), this.attach(A.id, A.parentId, A.siblingIndex);
                  }
                  for (var H = 0, Q = O.moved; H < Q.length; H++) {
                    var A = Q[H], x = this._nodesById.get(A.id);
                    if (x) {
                      var B = x.parentId !== A.parentId, z = this.siblingIndexOf(A.id), J = F(x, A);
                      J && (V(x, A), fe(A.id)), this.detach(A.id), this.attach(A.id, A.parentId, A.siblingIndex), (B || this.siblingIndexOf(A.id) !== z) && re();
                    }
                  }
                  for (var ve = 0, Ie = O.childrenUpdated; ve < Ie.length; ve++) {
                    var we = Ie[ve];
                    if (we.parentId < 0) {
                      var be = we.childIds.filter(function(Ue) {
                        return me._nodesById.has(Ue);
                      });
                      if (!N(this._roots, be)) {
                        this._roots.length = 0, (G = this._roots).push.apply(G, be);
                        for (var Se = 0, ge = this._roots; Se < ge.length; Se++) {
                          var Ae = ge[Se], Re = this._nodesById.get(Ae);
                          Re && (Re.parentId = -1);
                        }
                        re();
                      }
                    } else {
                      var ke = this._nodesById.get(we.parentId);
                      if (!ke)
                        continue;
                      var be = we.childIds.filter(function(at) {
                        return me._nodesById.has(at);
                      });
                      if (!N(ke.children, be)) {
                        ke.children.length = 0, (le = ke.children).push.apply(le, be);
                        for (var Fe = 0, xe = ke.children; Fe < xe.length; Fe++) {
                          var Ae = xe[Fe], Re = this._nodesById.get(Ae);
                          Re && (Re.parentId = we.parentId);
                        }
                        re();
                      }
                    }
                  }
                  for (var Ne = 0, Xe = O.updatedSemantic; Ne < Xe.length; Ne++) {
                    var A = Xe[Ne], x = this._nodesById.get(A.id);
                    x && Y(x, A) && (ie(x, A), Z(A.id));
                  }
                  for (var Qe = 0, ot = O.updatedGeometry; Qe < ot.length; Qe++) {
                    var A = ot[Qe], x = this._nodesById.get(A.id);
                    x && F(x, A) && (V(x, A), fe(A.id));
                  }
                  !K && !X || (K && this._semanticVersion++, X && this._geometryVersion++, this._debug && this.logDiff(O, K, X));
                }, Object.defineProperty(T.prototype, "debug", {
                  /** Enable/disable debug logging of diffs to the console. */
                  set: function(O) {
                    this._debug = O;
                  },
                  enumerable: !1,
                  configurable: !0
                }), T.prototype.logDiff = function(O, G, le) {
                  for (var me = [
                    "[rive:semantics] semantic v".concat(this._semanticVersion) + (le ? " geometry v".concat(this._geometryVersion) : "") + (G ? "" : " (geometry-only)")
                  ], K = 0, X = O.removed; K < X.length; K++) {
                    var re = X[K];
                    me.push("  - removed #".concat(re));
                  }
                  for (var Z = 0, fe = O.added; Z < fe.length; Z++) {
                    var q = fe[Z];
                    me.push("  + added #".concat(q.id, " ").concat((0, oe.roleName)(q.role)) + (q.label ? ' "'.concat(q.label, '"') : "") + " bounds:(".concat(q.minX.toFixed(1), ",").concat(q.minY.toFixed(1), ")-(").concat(q.maxX.toFixed(1), ",").concat(q.maxY.toFixed(1), ")") + " states=[".concat((0, oe.stateNames)(q.stateFlags), "]") + " traits=[".concat((0, oe.traitNames)(q.traitFlags), "]"));
                  }
                  for (var Be = 0, Ae = O.moved; Be < Ae.length; Be++) {
                    var q = Ae[Be];
                    me.push("  ~ moved #".concat(q.id, " → parent=").concat(q.parentId, " idx=").concat(q.siblingIndex) + " bounds:(".concat(q.minX.toFixed(1), ",").concat(q.minY.toFixed(1), ")-(").concat(q.maxX.toFixed(1), ",").concat(q.maxY.toFixed(1), ")"));
                  }
                  for (var _e = 0, se = O.childrenUpdated; _e < se.length; _e++) {
                    var A = se[_e];
                    me.push("  ↕ children of ".concat(A.parentId < 0 ? "root" : "#" + A.parentId, ": [").concat(A.childIds.join(", "), "]"));
                  }
                  for (var x = 0, H = O.updatedSemantic; x < H.length; x++) {
                    var q = H[x];
                    me.push("  ✎ semantic #".concat(q.id, " ").concat((0, oe.roleName)(q.role)) + (q.label ? ' "'.concat(q.label, '"') : "") + " states=[".concat((0, oe.stateNames)(q.stateFlags), "]") + " traits=[".concat((0, oe.traitNames)(q.traitFlags), "]"));
                  }
                  for (var Q = 0, B = O.updatedGeometry; Q < B.length; Q++) {
                    var q = B[Q];
                    me.push("  ⊞ geometry #".concat(q.id, " (").concat(q.minX.toFixed(1), ",").concat(q.minY.toFixed(1), ")-(").concat(q.maxX.toFixed(1), ",").concat(q.maxY.toFixed(1), ")"));
                  }
                  console.log(me.join(`
`));
                }, T.prototype.flattened = function() {
                  for (var O = this, G = [], le = function(re, Z) {
                    var fe = O._nodesById.get(re);
                    if (fe) {
                      G.push({ depth: Z, node: fe });
                      for (var q = 0, Be = fe.children; q < Be.length; q++) {
                        var Ae = Be[q];
                        le(Ae, Z + 1);
                      }
                    }
                  }, me = 0, K = this._roots; me < K.length; me++) {
                    var X = K[me];
                    le(X, 0);
                  }
                  return G;
                }, T;
              })()
            );
            function te(T, O, G) {
              return T < O ? O : T > G ? G : T;
            }
            function N(T, O) {
              if (T.length !== O.length)
                return !1;
              for (var G = 0; G < T.length; G++)
                if (T[G] !== O[G])
                  return !1;
              return !0;
            }
            function ne(T) {
              return {
                id: T.id,
                parentId: -1,
                role: T.role,
                label: T.label,
                value: T.value,
                hint: T.hint,
                stateFlags: T.stateFlags,
                traitFlags: T.traitFlags,
                headingLevel: T.headingLevel,
                minX: T.minX,
                minY: T.minY,
                maxX: T.maxX,
                maxY: T.maxY,
                children: []
              };
            }
            function Y(T, O) {
              return T.role !== O.role || T.label !== O.label || T.value !== O.value || T.hint !== O.hint || T.stateFlags !== O.stateFlags || T.traitFlags !== O.traitFlags || T.headingLevel !== O.headingLevel;
            }
            function F(T, O) {
              return T.minX !== O.minX || T.minY !== O.minY || T.maxX !== O.maxX || T.maxY !== O.maxY;
            }
            function ie(T, O) {
              T.role = O.role, T.label = O.label, T.value = O.value, T.hint = O.hint, T.stateFlags = O.stateFlags, T.traitFlags = O.traitFlags, T.headingLevel = O.headingLevel;
            }
            function V(T, O) {
              T.minX = O.minX, T.minY = O.minY, T.maxX = O.maxX, T.maxY = O.maxY;
            }
          }),
          /* 8 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              CHECK_STATE_MASK: () => (
                /* binding */
                ne
              ),
              /* harmony export */
              CHECK_STATE_OFFSET: () => (
                /* binding */
                N
              ),
              /* harmony export */
              SemanticActionType: () => (
                /* binding */
                T
              ),
              /* harmony export */
              SemanticCheckState: () => (
                /* binding */
                te
              ),
              /* harmony export */
              SemanticMode: () => (
                /* binding */
                F
              ),
              /* harmony export */
              SemanticRole: () => (
                /* binding */
                oe
              ),
              /* harmony export */
              SemanticState: () => (
                /* binding */
                C
              ),
              /* harmony export */
              SemanticTrait: () => (
                /* binding */
                ie
              ),
              /* harmony export */
              checkStateOf: () => (
                /* binding */
                Y
              ),
              /* harmony export */
              hasState: () => (
                /* binding */
                I
              ),
              /* harmony export */
              hasTrait: () => (
                /* binding */
                V
              ),
              /* harmony export */
              roleName: () => (
                /* binding */
                fe
              ),
              /* harmony export */
              stateNames: () => (
                /* binding */
                q
              ),
              /* harmony export */
              traitNames: () => (
                /* binding */
                Be
              )
              /* harmony export */
            });
            var oe = {
              none: 0,
              button: 1,
              link: 2,
              checkbox: 3,
              switchControl: 4,
              slider: 5,
              textField: 6,
              text: 7,
              image: 8,
              group: 9,
              list: 10,
              listItem: 11,
              tab: 12,
              tabList: 13,
              dialog: 14,
              alertDialog: 15,
              radioGroup: 16,
              radioButton: 17
            }, C = {
              None: 0,
              // Trait-gated
              Expanded: 1,
              // requires Expandable
              Selected: 2,
              // requires Selectable
              // Bits 2-3 are the check state field, not independent flags -- see SemanticCheckState.
              Toggled: 16,
              // requires Toggleable
              Required: 32,
              // requires Requirable
              Disabled: 64,
              // requires Enablable
              Focused: 128,
              // requires Focusable
              // Non-trait
              Hidden: 256,
              LiveRegion: 512,
              ReadOnly: 1024,
              Modal: 2048,
              Obscured: 4096,
              Multiline: 8192
            };
            function I(Ae, _e) {
              return (Ae & _e) !== 0;
            }
            var te = {
              Unchecked: 0,
              Checked: 1,
              Mixed: 2
            }, N = 2, ne = 3 << N;
            function Y(Ae) {
              var _e = (Ae & ne) >> N;
              return _e >= te.Mixed ? te.Mixed : _e;
            }
            var F = {
              Disabled: "disabled",
              Enabled: "enabled"
            }, ie = {
              None: 0,
              Expandable: 1,
              Selectable: 2,
              Checkable: 4,
              Toggleable: 8,
              Requirable: 16,
              Enablable: 32,
              Focusable: 64
            };
            function V(Ae, _e) {
              return (Ae & _e) !== 0;
            }
            for (var T = {
              tap: 0,
              increase: 1,
              decrease: 2
            }, O = {}, G = 0, le = Object.entries(oe); G < le.length; G++) {
              var me = le[G], K = me[0], X = me[1];
              O[X] = K;
            }
            var re = Object.entries(C).filter(function(Ae) {
              var _e = Ae[1];
              return _e !== 0;
            }), Z = Object.entries(ie).filter(function(Ae) {
              var _e = Ae[1];
              return _e !== 0;
            });
            function fe(Ae) {
              var _e;
              return (_e = O[Ae]) !== null && _e !== void 0 ? _e : "unknown(".concat(Ae, ")");
            }
            function q(Ae) {
              if (Ae === 0)
                return "none";
              for (var _e = [], se = 0, A = re; se < A.length; se++) {
                var x = A[se], H = x[0], Q = x[1];
                Ae & Q && _e.push(H);
              }
              switch (Y(Ae)) {
                case te.Checked:
                  _e.push("Checked");
                  break;
                case te.Mixed:
                  _e.push("Mixed");
                  break;
              }
              return _e.join(", ") || "none";
            }
            function Be(Ae) {
              if (Ae === 0)
                return "none";
              for (var _e = [], se = 0, A = Z; se < A.length; se++) {
                var x = A[se], H = x[0], Q = x[1];
                Ae & Q && _e.push(H);
              }
              return _e.join(", ") || "none";
            }
          }),
          /* 9 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              AccessibilityOverlay: () => (
                /* binding */
                ne
              )
              /* harmony export */
            });
            var oe = ae(10), C = ae(11), I = ae(8), te = !1;
            function N(se) {
              if (!te) {
                var A = se.offsetParent;
                if (A) {
                  for (var x = function(ve) {
                    return ve === "auto" || ve === "scroll" || ve === "overlay";
                  }, H = null, Q = se.parentElement, B = 32, z = 0; Q && Q !== document.documentElement && z < B; z++, Q = Q.parentElement) {
                    var J = getComputedStyle(Q);
                    if (x(J.overflowX) || x(J.overflowY)) {
                      H = Q;
                      break;
                    }
                  }
                  !H || H.contains(A) || (te = !0, console.warn('[Rive] Semantics: give the element wrapping the <canvas> "position: relative" (or another positioned value) so the semantic overlay scrolls with the canvas. Without it, screen readers may scroll to stale positions when the canvas is inside a scrolling container.'));
                }
              }
            }
            var ne = (
              /** @class */
              (function() {
                function se(A) {
                  var x = this, H, Q;
                  this.elements = /* @__PURE__ */ new Map(), this.descElements = /* @__PURE__ */ new Map(), this.lastSemanticVersion = -1, this.lastGeometryVersion = -1, this.pendingTextGeometry = [], this.textGeometryKeys = /* @__PURE__ */ new WeakMap(), this.appliedNodes = /* @__PURE__ */ new WeakMap(), this.lastCanvasPositioning = {
                    width: -1,
                    height: -1,
                    offsetTop: -1,
                    offsetLeft: -1
                  }, this._geometryDirty = !0, this.isUpdating = !1, this.editingHostNodeId = null, this.editingHostSemanticVersion = -1, this.transformContainer = null, this._artboardBounds = { minX: 0, minY: 0, maxX: 0, maxY: 0 }, this.repositionTimer = null, this.canvasResizeObserver = null, this.parentResizeObserver = null, this.positionObserver = null, this._onWindowResize = function() {
                    return x.scheduleReposition();
                  }, this.instanceId = A.instanceId, this.fireAction = A.fireAction, this.requestFocus = A.requestFocus, this.clearFocus = A.clearFocus, this.canvas = A.canvas, this.semanticsOptions = A.semanticsOptions, this.allowFocusInterrupt = (H = A.allowFocusInterrupt) !== null && H !== void 0 ? H : !1, this.isEditingHostFocused = (Q = A.isEditingHostFocused) !== null && Q !== void 0 ? Q : (function() {
                    return !1;
                  }), this.container = this.createContainer(A.canvas), this.attachPositionObservers(), N(A.canvas);
                }
                return se.prototype.setEditingHostNode = function(A) {
                  if (this.editingHostNodeId !== A) {
                    var x = this.editingHostNodeId;
                    if (this.editingHostNodeId = A, x !== null) {
                      var H = this.elements.get(x);
                      if (H) {
                        var Q = this.appliedNodes.get(H);
                        Q && this.isAriaHidden(Q) ? K(H, "aria-hidden", "true") : X(H, "aria-hidden");
                      }
                    }
                    if (A !== null) {
                      var B = this.elements.get(A);
                      B && K(B, "aria-hidden", "true");
                    }
                  }
                }, se.prototype.syncEditingHost = function(A, x, H) {
                  var Q;
                  if (!(!H && A.semanticVersion === this.editingHostSemanticVersion)) {
                    this.editingHostSemanticVersion = A.semanticVersion;
                    var B = A.focusedNode();
                    if (B === void 0 || B.role !== I.SemanticRole.textField) {
                      this.editingHostNodeId !== null && (x.resetDecoration(), this.setEditingHostNode(null));
                      return;
                    }
                    x.setSecure((0, I.hasState)(B.stateFlags, I.SemanticState.Obscured)), x.decorate({
                      "aria-label": B.label || null,
                      "aria-readonly": (0, I.hasState)(B.stateFlags, I.SemanticState.ReadOnly) ? "true" : null,
                      "aria-multiline": (0, I.hasState)(B.stateFlags, I.SemanticState.Multiline) ? "true" : null,
                      // Trait-gated to match applyAttributes.
                      "aria-required": (0, I.hasTrait)(B.traitFlags, I.SemanticTrait.Requirable) && (0, I.hasState)(B.stateFlags, I.SemanticState.Required) ? "true" : null,
                      // The hint span applyAttributes maintains (update() runs earlier in the frame).
                      "aria-describedby": B.hint && ((Q = this.descElements.get(B.id)) === null || Q === void 0 ? void 0 : Q.id) || null
                    }), this.setEditingHostNode(B.id);
                  }
                }, se.prototype.hasEditingHost = function() {
                  return this.editingHostNodeId !== null;
                }, se.prototype.releaseEditingHost = function(A, x) {
                  var H;
                  if (x == null || x.resetDecoration(), this.setEditingHostNode(null), this.editingHostSemanticVersion = -1, !!(x != null && x.hasDomFocus())) {
                    var Q = (H = A == null ? void 0 : A.focusedNode()) === null || H === void 0 ? void 0 : H.id;
                    Q !== void 0 && this.focusNodeElement(Q);
                  }
                }, se.prototype.focusNodeElement = function(A) {
                  var x = this.elements.get(A);
                  x && this.focusElementInPlace(x);
                }, se.prototype.focusElementInPlace = function(A) {
                  var x, H;
                  this.syncContainerBeforeFocus(), A.focus({ preventScroll: !0 }), (H = (x = this.canvas).scrollIntoView) === null || H === void 0 || H.call(x, {
                    block: "nearest",
                    inline: "nearest",
                    behavior: "instant"
                  }), this.syncContainerGeometry(), this.observePosition();
                }, se.prototype.getSemanticOverlayContainer = function() {
                  return this.container;
                }, se.prototype.attachPositionObservers = function() {
                  var A = this;
                  this.canvasResizeObserver = new ResizeObserver(function() {
                    return A.scheduleReposition();
                  }), this.canvasResizeObserver.observe(this.canvas);
                  var x = this.canvas.parentElement;
                  x && (this.parentResizeObserver = new ResizeObserver(function() {
                    return A.scheduleReposition();
                  }), this.parentResizeObserver.observe(x)), window.addEventListener("resize", this._onWindowResize), this.observePosition();
                }, se.prototype.observePosition = function() {
                  var A = this, x;
                  if (!(typeof IntersectionObserver > "u")) {
                    (x = this.positionObserver) === null || x === void 0 || x.disconnect(), this.positionObserver = null;
                    var H = this.canvas.getBoundingClientRect();
                    if (!(!H.width || !H.height)) {
                      var Q = function(J) {
                        return "".concat(-Math.round(J), "px");
                      }, B = [
                        H.top,
                        // top:    viewport top → canvas top
                        window.innerWidth - H.right,
                        // right:  viewport right → canvas right
                        window.innerHeight - H.bottom,
                        // bottom: viewport bottom → canvas bottom
                        H.left
                        // left:   viewport left → canvas left
                      ].map(Q).join(" "), z = !1;
                      this.positionObserver = new IntersectionObserver(function() {
                        if (!z) {
                          z = !0;
                          return;
                        }
                        A.scheduleReposition();
                      }, { threshold: 1, rootMargin: B }), this.positionObserver.observe(this.canvas);
                    }
                  }
                }, se.prototype.scheduleReposition = function() {
                  var A = this;
                  this._geometryDirty = !0, this.repositionTimer === null && (this.repositionTimer = setTimeout(function() {
                    A.repositionTimer = null, A.syncContainerGeometry(), A.observePosition();
                  }, 500));
                }, se.prototype.syncContainerGeometry = function() {
                  var A = this.canvas.getBoundingClientRect(), x = (0, C.canvasOffset)(this.canvas), H = x.top, Q = x.left, B = A.width !== this.lastCanvasPositioning.width || A.height !== this.lastCanvasPositioning.height;
                  return !B && H === this.lastCanvasPositioning.offsetTop && Q === this.lastCanvasPositioning.offsetLeft ? !1 : (this.container.style.top = H + "px", this.container.style.left = Q + "px", this.container.style.width = A.width + "px", this.container.style.height = A.height + "px", this.container.tabIndex = -1, this.lastCanvasPositioning.width = A.width, this.lastCanvasPositioning.height = A.height, this.lastCanvasPositioning.offsetTop = H, this.lastCanvasPositioning.offsetLeft = Q, B);
                }, se.prototype.syncContainerBeforeFocus = function() {
                  this.syncContainerGeometry() && (this._geometryDirty = !0);
                }, se.prototype.createContainer = function(A) {
                  var x, H, Q = document.createElement("div");
                  Q.id = "rive-a11y-".concat(this.instanceId), Q.setAttribute("role", "region"), Q.setAttribute("aria-label", (H = (x = this.semanticsOptions) === null || x === void 0 ? void 0 : x.riveCanvasLabel) !== null && H !== void 0 ? H : "Rive animation");
                  var B = A.getBoundingClientRect(), z = (0, C.canvasOffset)(this.canvas), J = z.top, ve = z.left;
                  return Q.style.cssText = [
                    "position:absolute",
                    "top:".concat(J, "px"),
                    "left:".concat(ve, "px"),
                    "line-height:normal",
                    "font-size:16px",
                    "width:".concat(B.width, "px"),
                    "height:".concat(B.height, "px"),
                    "overflow:hidden",
                    "pointer-events:none",
                    // Visually hidden but still in the accessibility tree.
                    // `display:none` and `visibility:hidden` would hide from AT.
                    "opacity:0"
                  ].join(";"), A.insertAdjacentElement("afterend", Q), Q;
                }, se.prototype.needsUpdate = function(A) {
                  var x = A.semanticVersion !== this.lastSemanticVersion, H = A.geometryVersion !== this.lastGeometryVersion, Q = this._geometryDirty || !this.transformContainer;
                  return !x && !H && !Q ? null : { semanticChanged: x, nodeGeometryChanged: H, layoutChanged: Q };
                }, se.prototype.update = function(A, x, H, Q, B) {
                  var z = B ?? this.needsUpdate(A);
                  !z && x && (z = {
                    semanticChanged: !1,
                    nodeGeometryChanged: !1,
                    layoutChanged: !0
                  }), z && this.performUpdate(A, x, H, Q, z);
                }, se.prototype.performUpdate = function(A, x, H, Q, B) {
                  var z, J = B.semanticChanged, ve = B.nodeGeometryChanged, Ie = A.semanticVersion - this.lastSemanticVersion > 1;
                  if (this.lastSemanticVersion = A.semanticVersion, this.lastGeometryVersion = A.geometryVersion, this.isUpdating = !0, this._artboardBounds = Q, x && (this.syncContainerGeometry(), this.syncTransformContainer(x, H, Q), this._geometryDirty = !1), J) {
                    var we = (z = this.transformContainer) !== null && z !== void 0 ? z : this.container, be = /* @__PURE__ */ new Set();
                    this.rebuildChildren(
                      we,
                      A.roots,
                      A,
                      0,
                      // parentLeft in artboard space (transform container origin)
                      0,
                      // parentTop  in artboard space
                      be,
                      Ie
                    );
                    var Se = [];
                    this.elements.forEach(function(Ne, Xe) {
                      be.has(Xe) || Se.push(Xe);
                    });
                    for (var ge = 0, Re = Se; ge < Re.length; ge++) {
                      var ke = Re[ge], Fe = this.elements.get(ke);
                      Fe && Fe.parentNode && Fe.parentNode.removeChild(Fe), this.elements.delete(ke);
                      var xe = this.descElements.get(ke);
                      xe && xe.parentNode && xe.parentNode.removeChild(xe), this.descElements.delete(ke);
                    }
                  } else ve && this.updateGeometryForChangedNodes(A);
                  this.flushTextGeometry(), this.isUpdating = !1;
                }, se.prototype.destroy = function() {
                  var A, x, H;
                  this.repositionTimer !== null && (clearTimeout(this.repositionTimer), this.repositionTimer = null), window.removeEventListener("resize", this._onWindowResize), (A = this.canvasResizeObserver) === null || A === void 0 || A.disconnect(), (x = this.parentResizeObserver) === null || x === void 0 || x.disconnect(), (H = this.positionObserver) === null || H === void 0 || H.disconnect(), this.container.parentNode && this.container.parentNode.removeChild(this.container), this.elements.clear(), this.descElements.clear(), this.pendingTextGeometry.length = 0;
                }, se.prototype.rebuildChildren = function(A, x, H, Q, B, z, J) {
                  for (var ve = 0; ve < x.length; ve++) {
                    var Ie = x[ve], we = H.nodeById(Ie);
                    if (we) {
                      z.add(Ie);
                      var be = this.elements.get(Ie), Se = !be;
                      be || (be = this.createElement(we), this.elements.set(Ie, be)), (Se || J || H.semanticChangedIds.has(Ie)) && this.applyAttributes(be, we), this.applyPosition(be, we, Q, B);
                      var ge = A.children[ve];
                      if (ge !== be && (ge ? A.insertBefore(be, ge) : A.appendChild(be)), (0, I.hasTrait)(we.traitFlags, I.SemanticTrait.Focusable) && (0, I.hasState)(we.stateFlags, I.SemanticState.Focused)) {
                        var Re = document.activeElement, ke = Re == null ? void 0 : Re.closest('[aria-modal="true"]'), Fe = !!ke && this.container.contains(ke) && !ke.contains(be);
                        Ie !== this.editingHostNodeId && Re !== be && !Fe && !this.isEditingHostFocused() && this.canMoveFocus() && (this.syncContainerBeforeFocus(), be.focus({ preventScroll: !0 }));
                      }
                      we.children.length > 0 && this.rebuildChildren(be, we.children, H, we.minX, we.minY, z, J), Se && this.autoFocusDialogOnAppear(be, we, H);
                    }
                  }
                }, se.prototype.updateGeometryForChangedNodes = function(A) {
                  for (var x, H, Q = 0, B = Array.from(A.geometryChangedIds); Q < B.length; Q++) {
                    var z = B[Q], J = A.nodeById(z);
                    if (J) {
                      var ve = 0, Ie = 0, we = (x = this.transformContainer) !== null && x !== void 0 ? x : this.container;
                      if (J.parentId >= 0) {
                        var be = A.nodeById(J.parentId);
                        be && (ve = be.minX, Ie = be.minY, we = (H = this.elements.get(J.parentId)) !== null && H !== void 0 ? H : we);
                      }
                      this.updateNodeGeometrySubtree(A, z, ve, Ie, we);
                    }
                  }
                }, se.prototype.updateNodeGeometrySubtree = function(A, x, H, Q, B) {
                  var z = A.nodeById(x);
                  if (z) {
                    var J = this.elements.get(x);
                    if (J) {
                      this.applyPosition(J, z, H, Q);
                      for (var ve = 0, Ie = z.children; ve < Ie.length; ve++) {
                        var we = Ie[ve];
                        this.updateNodeGeometrySubtree(A, we, z.minX, z.minY, J);
                      }
                    }
                  }
                }, se.prototype.canMoveFocus = function() {
                  var A = document.activeElement, x = A === this.canvas || this.container.contains(A);
                  return x || this.allowFocusInterrupt;
                }, se.prototype.autoFocusDialogOnAppear = function(A, x, H) {
                  var Q;
                  if (q(x.role, x.stateFlags) && this.canMoveFocus()) {
                    var B = document.activeElement;
                    if (!(B && B !== A && A.contains(B))) {
                      var z = (Q = this.routeDefaultFocusTarget(x, H)) !== null && Q !== void 0 ? Q : A;
                      z.hasAttribute("tabindex") || z.setAttribute("tabindex", "-1"), document.activeElement !== z && z.focus({ preventScroll: !0 });
                    }
                  }
                }, se.prototype.routeDefaultFocusTarget = function(A, x) {
                  for (var H, Q = 0, B = A.children; Q < B.length; Q++) {
                    var z = B[Q], J = x.nodeById(z);
                    if (J) {
                      var ve = this.elements.get(z);
                      if (ve && Be(J))
                        return ve;
                      if (J.children.length > 0 || !J.label) {
                        var Ie = this.routeDefaultFocusTarget(J, x);
                        if (Ie)
                          return Ie;
                        continue;
                      }
                      if (ve)
                        return (H = ve.querySelector(":scope > span")) !== null && H !== void 0 ? H : ve;
                    }
                  }
                  return null;
                }, Object.defineProperty(se.prototype, "nodeIdPrefix", {
                  // ---- Element creation ----
                  /** Shared `id` prefix for all semantic node elements of this instance. */
                  get: function() {
                    return "rive-".concat(this.instanceId, "-sem-");
                  },
                  enumerable: !1,
                  configurable: !0
                }), se.prototype.nodeIdFromElement = function(A) {
                  if (!A.id.startsWith(this.nodeIdPrefix))
                    return null;
                  var x = A.id.slice(this.nodeIdPrefix.length);
                  if (!x)
                    return null;
                  var H = Number(x);
                  return Number.isNaN(H) ? null : H;
                }, se.prototype.createElement = function(A) {
                  var x = Ae(A.role), H = document.createElement(x);
                  if (H.id = "".concat(this.nodeIdPrefix).concat(A.id), H.style.cssText = le, A.role === I.SemanticRole.text) {
                    var Q = document.createElement("span");
                    Q.style.cssText = me, H.appendChild(Q);
                  }
                  return this.attachActionHandlers(H, A), H;
                }, se.prototype.attachRovingNav = function(A, x) {
                  var H = this;
                  A.addEventListener("keydown", function(Q) {
                    var B = null;
                    if (Q.key === "ArrowRight" || Q.key === "ArrowDown" ? B = "next" : Q.key === "ArrowLeft" || Q.key === "ArrowUp" ? B = "prev" : x.includeHomeEnd && Q.key === "Home" ? B = "first" : x.includeHomeEnd && Q.key === "End" && (B = "last"), !!B) {
                      (0, oe.claimKeyEvent)(Q);
                      var z = x.members(), J = z.indexOf(A);
                      if (!(J < 0)) {
                        var ve = z.length, Ie = B === "next" ? z[(J + 1) % ve] : B === "prev" ? z[(J - 1 + ve) % ve] : B === "first" ? z[0] : z[ve - 1];
                        if (Ie && Ie !== A) {
                          H.focusElementInPlace(Ie);
                          var we = H.nodeIdFromElement(Ie);
                          we !== null && H.fireAction(we, I.SemanticActionType.tap);
                        }
                      }
                    }
                  });
                }, se.prototype.attachActionHandlers = function(A, x) {
                  var H = this, Q = x.role, B = x.id;
                  if (Z(Q)) {
                    A.addEventListener("click", function() {
                      H.fireAction(B, I.SemanticActionType.tap);
                    });
                    var z = Q === I.SemanticRole.link ? ["Enter"] : ["Enter", " "];
                    A.addEventListener("keydown", function(J) {
                      z.includes(J.key) && ((0, oe.claimKeyEvent)(J), H.fireAction(B, I.SemanticActionType.tap));
                    });
                  }
                  Q === I.SemanticRole.slider && A.addEventListener("keydown", function(J) {
                    J.key === "ArrowRight" || J.key === "ArrowUp" ? ((0, oe.claimKeyEvent)(J), H.fireAction(B, I.SemanticActionType.increase)) : (J.key === "ArrowLeft" || J.key === "ArrowDown") && ((0, oe.claimKeyEvent)(J), H.fireAction(B, I.SemanticActionType.decrease));
                  }), Q === I.SemanticRole.tab && this.attachRovingNav(A, {
                    includeHomeEnd: !0,
                    members: function() {
                      var J = A.parentElement;
                      return J ? Array.from(J.children).filter(function(ve) {
                        return ve instanceof HTMLElement && ve.getAttribute("role") === "tab";
                      }) : [];
                    }
                  }), Q === I.SemanticRole.radioButton && this.attachRovingNav(A, {
                    includeHomeEnd: !1,
                    members: function() {
                      var J, ve = (J = A.closest('[role="radiogroup"]')) !== null && J !== void 0 ? J : A.parentElement;
                      return ve ? Array.from(ve.querySelectorAll('[role="radio"]')) : [];
                    }
                  }), (0, I.hasTrait)(x.traitFlags, I.SemanticTrait.Focusable) && A.addEventListener("focus", function() {
                    H.requestFocus(B);
                  });
                }, se.prototype.isAriaHidden = function(A) {
                  var x = A.role, H = A.stateFlags, Q = x === I.SemanticRole.image && !A.label, B = A.id === this.editingHostNodeId;
                  return (0, I.hasState)(H, I.SemanticState.Hidden) || // Obscured text fields stay reachable (value withheld, like a native password input).
                  (0, I.hasState)(H, I.SemanticState.Obscured) && x !== I.SemanticRole.textField || Q || B;
                }, se.prototype.applyAttributes = function(A, x) {
                  var H, Q, B;
                  this.appliedNodes.set(A, x);
                  var z = x.role, J = x.stateFlags, ve = x.traitFlags, Ie = _e(z);
                  if (Ie ? K(A, "role", Ie) : X(A, "role"), z === I.SemanticRole.link && K(A, "role", "link"), fe(z) || (0, I.hasTrait)(ve, I.SemanticTrait.Focusable) || z === I.SemanticRole.listItem ? K(A, "tabindex", "-1") : X(A, "tabindex"), x.label ? K(A, "aria-label", x.label) : X(A, "aria-label"), z === I.SemanticRole.slider) {
                    if (x.value) {
                      var we = parseFloat(x.value);
                      Number.isFinite(we) ? K(A, "aria-valuenow", String(we)) : X(A, "aria-valuenow"), K(A, "aria-valuetext", x.value);
                    } else
                      X(A, "aria-valuenow"), X(A, "aria-valuetext");
                    K(A, "aria-orientation", "horizontal"), re(A, "aria-readonly", (0, I.hasState)(J, I.SemanticState.ReadOnly));
                  } else
                    X(A, "aria-valuenow"), X(A, "aria-valuetext"), X(A, "aria-orientation"), X(A, "aria-readonly");
                  if (x.hint) {
                    var be = "rive-".concat(this.instanceId, "-desc-").concat(x.id), Se = this.descElements.get(x.id);
                    Se || (Se = document.createElement("span"), Se.id = be, Se.style.cssText = G, this.container.appendChild(Se), this.descElements.set(x.id, Se)), Se.textContent !== x.hint && (Se.textContent = x.hint), K(A, "aria-describedby", be);
                  } else {
                    X(A, "aria-describedby");
                    var ge = this.descElements.get(x.id);
                    ge && (ge.parentNode && ge.parentNode.removeChild(ge), this.descElements.delete(x.id));
                  }
                  if (z === I.SemanticRole.text) {
                    var Re = (H = A.querySelector(":scope > span")) !== null && H !== void 0 ? H : A, ke = (Q = x.label) !== null && Q !== void 0 ? Q : "";
                    Re.textContent !== ke && (Re.textContent = ke), X(A, "aria-label"), x.headingLevel > 0 ? (K(A, "role", "heading"), K(A, "aria-level", String(x.headingLevel))) : X(A, "aria-level");
                  }
                  if ((0, I.hasTrait)(ve, I.SemanticTrait.Expandable) && Y.has(z) ? re(A, "aria-expanded", (0, I.hasState)(J, I.SemanticState.Expanded)) : X(A, "aria-expanded"), z === I.SemanticRole.tab || (0, I.hasTrait)(ve, I.SemanticTrait.Selectable) && F.has(z) ? re(A, "aria-selected", (0, I.hasState)(J, I.SemanticState.Selected)) : X(A, "aria-selected"), (0, I.hasTrait)(ve, I.SemanticTrait.Checkable) && ie.has(z)) {
                    var Fe = (0, I.checkStateOf)(J);
                    Fe === I.SemanticCheckState.Mixed && V.has(z) ? K(A, "aria-checked", "mixed") : re(A, "aria-checked", Fe === I.SemanticCheckState.Checked);
                  } else
                    X(A, "aria-checked");
                  if ((0, I.hasTrait)(ve, I.SemanticTrait.Toggleable) ? (T.has(z) ? re(A, "aria-pressed", (0, I.hasState)(J, I.SemanticState.Toggled)) : X(A, "aria-pressed"), z === I.SemanticRole.switchControl && re(A, "aria-checked", (0, I.hasState)(J, I.SemanticState.Toggled))) : X(A, "aria-pressed"), (0, I.hasTrait)(ve, I.SemanticTrait.Requirable) && O.has(z) ? re(A, "aria-required", (0, I.hasState)(J, I.SemanticState.Required)) : X(A, "aria-required"), (0, I.hasTrait)(ve, I.SemanticTrait.Enablable) ? re(A, "aria-disabled", (0, I.hasState)(J, I.SemanticState.Disabled)) : X(A, "aria-disabled"), this.isAriaHidden(x) ? K(A, "aria-hidden", "true") : X(A, "aria-hidden"), (0, I.hasState)(J, I.SemanticState.LiveRegion) ? K(A, "aria-live", "polite") : X(A, "aria-live"), z === I.SemanticRole.textField)
                    if (re(A, "aria-readonly", (0, I.hasState)(J, I.SemanticState.ReadOnly)), re(A, "aria-multiline", (0, I.hasState)(J, I.SemanticState.Multiline)), x.children.length === 0) {
                      var xe = (0, I.hasState)(J, I.SemanticState.Obscured) ? "" : (B = x.value) !== null && B !== void 0 ? B : "";
                      A.textContent !== xe && (A.textContent = xe);
                    } else
                      for (var Ne = 0, Xe = Array.from(A.childNodes); Ne < Xe.length; Ne++) {
                        var Qe = Xe[Ne];
                        Qe.nodeType === Node.TEXT_NODE && Qe.remove();
                      }
                  else
                    X(A, "aria-multiline");
                  q(z, J) ? K(A, "aria-modal", "true") : X(A, "aria-modal");
                }, se.prototype.applyPosition = function(A, x, H, Q) {
                  var B = this._artboardBounds, z = Math.max(x.minX, B.minX), J = Math.max(x.minY, B.minY), ve = Math.min(x.maxX, B.maxX), Ie = Math.min(x.maxY, B.maxY), we = z - H, be = J - Q, Se = Math.max(0, ve - z), ge = Math.max(0, Ie - J), Re = Math.round(we), ke = Math.round(be), Fe = Math.round(Se) + "px", xe = Math.round(ge) + "px", Ne = Re + "px", Xe = ke + "px";
                  A.style.left !== Ne && (A.style.left = Ne), A.style.top !== Xe && (A.style.top = Xe), A.style.width !== Fe && (A.style.width = Fe), A.style.height !== xe && (A.style.height = xe), A.style.transform && (A.style.transform = ""), x.role === I.SemanticRole.text && this.pendingTextGeometry.push(A);
                }, se.prototype.flushTextGeometry = function() {
                  var A;
                  if (this.pendingTextGeometry.length !== 0) {
                    for (var x = [], H = 0, Q = this.pendingTextGeometry; H < Q.length; H++) {
                      var B = Q[H], z = (A = B.querySelector(":scope > span")) !== null && A !== void 0 ? A : B, J = "".concat(B.style.width, "|").concat(B.style.height, "|").concat(z.textContent);
                      this.textGeometryKeys.get(B) !== J && (z.style.width = "auto", z.style.height = "auto", z.style.transformOrigin = "0 0", z.style.transform = "", x.push({ host: B, span: z, key: J }));
                    }
                    this.pendingTextGeometry.length = 0;
                    for (var ve = x.map(function(be) {
                      var Se = be.host, ge = be.span, Re = Se.getBoundingClientRect(), ke = ge.getBoundingClientRect();
                      if (ke.width > 0 && ke.height > 0) {
                        var Fe = Re.width / ke.width, xe = Re.height / ke.height;
                        return "scale(".concat(Fe, ", ").concat(xe, ")");
                      }
                      return "none";
                    }), Ie = 0; Ie < x.length; Ie++) {
                      var we = x[Ie], B = we.host, z = we.span, J = we.key;
                      z.style.transform = ve[Ie], this.textGeometryKeys.set(B, J);
                    }
                  }
                }, se.prototype.syncTransformContainer = function(A, x, H) {
                  if (!this.transformContainer) {
                    var Q = document.createElement("div");
                    Q.style.cssText = [
                      "position:absolute",
                      "top:0",
                      "left:0",
                      // overflow:visible — artboard viewport clamping is done per-node in
                      // applyPosition
                      "overflow:visible",
                      "pointer-events:none",
                      "transform-origin:0 0"
                    ].join(";"), this.container.appendChild(Q), this.transformContainer = Q;
                  }
                  var B = H.maxX - H.minX, z = H.maxY - H.minY;
                  this.transformContainer.style.width = Math.round(B) + "px", this.transformContainer.style.height = Math.round(z) + "px";
                  var J = this.lastCanvasPositioning.width, ve = this.lastCanvasPositioning.height, Ie = 1 / (x || 1), we = this.canvas.width > 0 && J > 0 ? J / this.canvas.width : Ie, be = this.canvas.height > 0 && ve > 0 ? ve / this.canvas.height : Ie, Se = A.xx * we, ge = A.xy * be, Re = A.yx * we, ke = A.yy * be, Fe = A.tx * we, xe = A.ty * be;
                  this.transformContainer.style.transform = "matrix(".concat(Se, ",").concat(ge, ",").concat(Re, ",").concat(ke, ",").concat(Fe, ",").concat(xe, ")");
                }, se;
              })()
            ), Y = /* @__PURE__ */ new Set([
              I.SemanticRole.button,
              I.SemanticRole.link,
              I.SemanticRole.checkbox,
              I.SemanticRole.switchControl,
              I.SemanticRole.tab
            ]), F = /* @__PURE__ */ new Set([
              I.SemanticRole.tab
            ]), ie = /* @__PURE__ */ new Set([
              I.SemanticRole.checkbox,
              I.SemanticRole.radioButton,
              I.SemanticRole.switchControl
            ]), V = /* @__PURE__ */ new Set([
              I.SemanticRole.checkbox
            ]), T = /* @__PURE__ */ new Set([
              I.SemanticRole.button
            ]), O = /* @__PURE__ */ new Set([
              I.SemanticRole.checkbox,
              I.SemanticRole.textField,
              I.SemanticRole.radioGroup
            ]), G = [
              "position:absolute",
              "width:1px",
              "height:1px",
              "overflow:hidden",
              "pointer-events:none",
              "left:-9999px"
            ].join(";"), le = [
              "position:absolute",
              "pointer-events:none",
              "box-sizing:border-box",
              "overflow:visible",
              "margin:0",
              "padding:0",
              "transform-origin: 0px 0px 0px",
              "border:none",
              "background:transparent",
              "color:transparent"
              // "list-style:none",
            ].join(";"), me = [
              "display:inline-block",
              "white-space:nowrap",
              "pointer-events:none"
            ].join(";");
            function K(se, A, x) {
              se.getAttribute(A) !== x && se.setAttribute(A, x);
            }
            function X(se, A) {
              se.hasAttribute(A) && se.removeAttribute(A);
            }
            function re(se, A, x) {
              K(se, A, x ? "true" : "false");
            }
            function Z(se) {
              switch (se) {
                case I.SemanticRole.button:
                case I.SemanticRole.link:
                case I.SemanticRole.checkbox:
                case I.SemanticRole.switchControl:
                case I.SemanticRole.tab:
                case I.SemanticRole.radioButton:
                  return !0;
                default:
                  return !1;
              }
            }
            function fe(se) {
              switch (se) {
                case I.SemanticRole.button:
                case I.SemanticRole.link:
                case I.SemanticRole.checkbox:
                case I.SemanticRole.switchControl:
                case I.SemanticRole.slider:
                case I.SemanticRole.tab:
                case I.SemanticRole.radioButton:
                case I.SemanticRole.textField:
                  return !0;
                default:
                  return !1;
              }
            }
            function q(se, A) {
              return se === I.SemanticRole.alertDialog || se === I.SemanticRole.dialog && (0, I.hasState)(A, I.SemanticState.Modal);
            }
            function Be(se) {
              return fe(se.role) || (0, I.hasTrait)(se.traitFlags, I.SemanticTrait.Focusable);
            }
            function Ae(se) {
              switch (se) {
                case I.SemanticRole.link:
                  return "a";
                case I.SemanticRole.text:
                  return "div";
                default:
                  return "div";
              }
            }
            function _e(se) {
              switch (se) {
                case I.SemanticRole.none:
                  return "group";
                case I.SemanticRole.button:
                  return "button";
                case I.SemanticRole.link:
                  return null;
                // native <a>
                case I.SemanticRole.checkbox:
                  return "checkbox";
                case I.SemanticRole.switchControl:
                  return "switch";
                case I.SemanticRole.slider:
                  return "slider";
                case I.SemanticRole.textField:
                  return "textbox";
                case I.SemanticRole.image:
                  return "img";
                case I.SemanticRole.group:
                  return "group";
                case I.SemanticRole.list:
                  return "list";
                case I.SemanticRole.listItem:
                  return "listitem";
                case I.SemanticRole.tab:
                  return "tab";
                case I.SemanticRole.tabList:
                  return "tablist";
                case I.SemanticRole.dialog:
                  return "dialog";
                case I.SemanticRole.alertDialog:
                  return "alertdialog";
                case I.SemanticRole.radioGroup:
                  return "radiogroup";
                case I.SemanticRole.radioButton:
                  return "radio";
                case I.SemanticRole.text:
                  return null;
                default:
                  return null;
              }
            }
          }),
          /* 10 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              claimKeyEvent: () => (
                /* binding */
                C
              ),
              /* harmony export */
              isKeyEventClaimed: () => (
                /* binding */
                I
              )
              /* harmony export */
            });
            var oe = /* @__PURE__ */ new WeakSet();
            function C(te) {
              te.preventDefault(), oe.add(te);
            }
            function I(te) {
              return oe.has(te);
            }
          }),
          /* 11 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              canvasOffset: () => (
                /* binding */
                oe
              )
              /* harmony export */
            });
            function oe(C) {
              var I = C.offsetTop, te = C.offsetLeft, N = C.offsetParent;
              if (!N)
                return { top: I, left: te };
              for (var ne = C.parentElement; ne && ne !== N; ne = ne.parentElement)
                I -= ne.scrollTop, te -= ne.scrollLeft;
              return { top: I, left: te };
            }
          }),
          /* 12 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              AudioAssetWrapper: () => (
                /* reexport safe */
                te.AudioAssetWrapper
              ),
              /* harmony export */
              AudioWrapper: () => (
                /* reexport safe */
                te.AudioWrapper
              ),
              /* harmony export */
              BLANK_URL: () => (
                /* reexport safe */
                I.BLANK_URL
              ),
              /* harmony export */
              CustomFileAssetLoaderWrapper: () => (
                /* reexport safe */
                te.CustomFileAssetLoaderWrapper
              ),
              /* harmony export */
              FileAssetWrapper: () => (
                /* reexport safe */
                te.FileAssetWrapper
              ),
              /* harmony export */
              FileFinalizer: () => (
                /* reexport safe */
                te.FileFinalizer
              ),
              /* harmony export */
              FocusSessionState: () => (
                /* reexport safe */
                C.FocusSessionState
              ),
              /* harmony export */
              FontAssetWrapper: () => (
                /* reexport safe */
                te.FontAssetWrapper
              ),
              /* harmony export */
              FontWrapper: () => (
                /* reexport safe */
                te.FontWrapper
              ),
              /* harmony export */
              ImageAssetWrapper: () => (
                /* reexport safe */
                te.ImageAssetWrapper
              ),
              /* harmony export */
              ImageWrapper: () => (
                /* reexport safe */
                te.ImageWrapper
              ),
              /* harmony export */
              KeyboardInteractions: () => (
                /* reexport safe */
                C.KeyboardInteractions
              ),
              /* harmony export */
              RiveFont: () => (
                /* reexport safe */
                N.RiveFont
              ),
              /* harmony export */
              createFinalization: () => (
                /* reexport safe */
                te.createFinalization
              ),
              /* harmony export */
              finalizationRegistry: () => (
                /* reexport safe */
                te.finalizationRegistry
              ),
              /* harmony export */
              registerTouchInteractions: () => (
                /* reexport safe */
                oe.registerTouchInteractions
              ),
              /* harmony export */
              sanitizeUrl: () => (
                /* reexport safe */
                I.sanitizeUrl
              )
              /* harmony export */
            });
            var oe = ae(13), C = ae(14), I = ae(17), te = ae(18), N = ae(19);
          }),
          /* 13 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              registerTouchInteractions: () => (
                /* binding */
                ne
              )
              /* harmony export */
            });
            var oe = void 0, C = 16, I = 1, te = function(Y, F, ie) {
              var V, T = [];
              if (F)
                for (var O = 0; O < Y.length; O++) {
                  var G = Y[O];
                  T.push({
                    clientX: G.clientX,
                    clientY: G.clientY,
                    identifier: G.identifier
                  });
                }
              else {
                var le = ie !== null ? (V = Array.from(Y).find(function(me) {
                  return me.identifier === ie;
                })) !== null && V !== void 0 ? V : null : Y[0];
                le && T.push({
                  clientX: le.clientX,
                  clientY: le.clientY,
                  identifier: le.identifier
                });
              }
              return T;
            }, N = function(Y, F, ie, V) {
              var T, O = Y;
              return !((T = O.changedTouches) === null || T === void 0) && T.length ? (!F && ["touchstart", "touchmove"].includes(Y.type) && Y.preventDefault(), te(O.changedTouches, ie, V)) : [
                {
                  clientX: Y.clientX,
                  clientY: Y.clientY,
                  identifier: 0
                }
              ];
            }, ne = function(Y) {
              var F = Y.canvas, ie = Y.artboard, V = Y.stateMachines, T = V === void 0 ? [] : V, O = Y.renderer, G = Y.rive, le = Y.fit, me = Y.alignment, K = Y.isTouchScrollEnabled, X = K === void 0 ? !1 : K, re = Y.dispatchPointerExit, Z = re === void 0 ? !0 : re, fe = Y.enableMultiTouch, q = fe === void 0 ? !1 : fe, Be = Y.layoutScaleFactor, Ae = Be === void 0 ? 1 : Be, _e = Y.advanceAndDrain, se = Y.summonKeyboard, A = Y.isTextProxyFocused;
              if (!F || !T.length || !O || !G || !ie || typeof window > "u")
                return null;
              for (var x = 0, H = T; x < H.length; x++) {
                var Q = H[x];
                Q.cancelScroll();
              }
              var B = null, z = !1, J = null, ve = function(ge, Re) {
                var ke = G.computeAlignment(le, me, {
                  minX: 0,
                  minY: 0,
                  maxX: ge.width,
                  maxY: ge.height
                }, ie.bounds, Ae), Fe = new G.Mat2D();
                ke.invert(Fe);
                var xe = Re.map(function(Ne) {
                  var Xe = Ne.clientX, Qe = Ne.clientY, ot = Xe - ge.left, Ue = Qe - ge.top, at = new G.Vec2D(ot, Ue), qe = G.mapXY(Fe, at), st = { x: qe.x(), y: qe.y() };
                  return qe.delete(), at.delete(), st;
                });
                return Fe.delete(), ke.delete(), xe;
              }, Ie = function(ge) {
                var Re;
                if (z && ge instanceof MouseEvent) {
                  ge.type === "mousedown" && (A != null && A()) && ge.preventDefault(), ge.type == "mouseup" && (z = !1);
                  return;
                }
                z = X && ge.type === "touchend" && B === "touchstart", B = ge.type;
                var ke = ge.currentTarget.getBoundingClientRect();
                if (!q && ge.type === "touchstart" && J === null) {
                  var Fe = (Re = ge.changedTouches) === null || Re === void 0 ? void 0 : Re[0];
                  Fe && (J = Fe.identifier);
                }
                var xe = N(ge, X, q, q ? null : J), Ne = xe.filter(function(De) {
                  return De.clientX || De.clientY;
                });
                switch (ve(ke, Ne).forEach(function(De, Le) {
                  Ne[Le].transformedX = De.x, Ne[Le].transformedY = De.y;
                }), ge.type) {
                  /**
                   * There's a 2px buffer for a hitRadius when translating the pointer coordinates
                   * down to the state machine. In cases where the hitbox is about that much away
                   * from the Artboard border, we don't have exact precision on determining pointer
                   * exit. We're therefore adding to the translated coordinates on mouseout of a canvas
                   * to ensure that we report the mouse has truly exited the hitarea.
                   * https://github.com/rive-app/rive-cpp/blob/master/src/animation/state_machine_instance.cpp#L336
                   *
                   */
                  case "mouseout":
                    for (var Xe = function(De) {
                      Z ? xe.forEach(function(Le) {
                        De.pointerExit(Le.transformedX, Le.transformedY, Le.identifier);
                      }) : xe.forEach(function(Le) {
                        De.pointerMove(Le.transformedX, Le.transformedY, Le.identifier);
                      });
                    }, Qe = 0, ot = T; Qe < ot.length; Qe++) {
                      var Ue = ot[Qe];
                      Xe(Ue);
                    }
                    break;
                  // Pointer moving/hovering on the canvas
                  case "touchmove":
                  case "mouseover":
                  case "mousemove": {
                    for (var at = function(De) {
                      xe.forEach(function(Le) {
                        De.pointerMove(Le.transformedX, Le.transformedY, Le.identifier);
                      });
                    }, qe = 0, st = T; qe < st.length; qe++) {
                      var Ue = st[qe];
                      at(Ue);
                    }
                    break;
                  }
                  // Pointer click initiated but not released yet on the canvas
                  case "touchstart":
                  case "mousedown": {
                    for (var lt = function(De) {
                      xe.forEach(function(Le) {
                        De.pointerDown(Le.transformedX, Le.transformedY, Le.identifier);
                      });
                    }, Te = 0, it = T; Te < it.length; Te++) {
                      var Ue = it[Te];
                      lt(Ue);
                    }
                    _e(0, { pointerDown: !0 });
                    break;
                  }
                  // Pointer click released on the canvas
                  case "touchend": {
                    for (var Ye = function(De) {
                      xe.forEach(function(Le) {
                        De.pointerUp(Le.transformedX, Le.transformedY, Le.identifier), De.pointerExit(Le.transformedX, Le.transformedY, Le.identifier);
                      });
                    }, ye = 0, et = T; ye < et.length; ye++) {
                      var Ue = et[ye];
                      Ye(Ue);
                    }
                    _e(0), se == null || se(), !q && xe.some(function(De) {
                      return De.identifier === J;
                    }) && (J = null);
                    break;
                  }
                  case "mouseup": {
                    for (var pt = function(De) {
                      xe.forEach(function(Le) {
                        De.pointerUp(Le.transformedX, Le.transformedY, Le.identifier);
                      });
                    }, Rt = 0, We = T; Rt < We.length; Rt++) {
                      var Ue = We[Rt];
                      pt(Ue);
                    }
                    _e(0), se == null || se();
                    break;
                  }
                }
              }, we = function() {
                J = null;
              }, be = function(ge) {
                if (!(ge.ctrlKey || !ge.cancelable)) {
                  var Re = ge.deltaMode, ke = ge.deltaX, Fe = ge.deltaY;
                  ge.shiftKey && !ke && (ke = Fe, Fe = 0);
                  var xe = ge.currentTarget.getBoundingClientRect(), Ne = Re === WheelEvent.DOM_DELTA_LINE ? C : Re === WheelEvent.DOM_DELTA_PAGE ? xe.width : 1, Xe = Re === WheelEvent.DOM_DELTA_LINE ? C : Re === WheelEvent.DOM_DELTA_PAGE ? xe.height : 1, Qe = -ke * Ne, ot = -Fe * Xe;
                  if (!(!Qe && !ot)) {
                    var Ue = ve(xe, [
                      { clientX: ge.clientX, clientY: ge.clientY },
                      { clientX: ge.clientX + Qe, clientY: ge.clientY + ot }
                    ]), at = Ue[0], qe = Ue[1], st = Re === WheelEvent.DOM_DELTA_PIXEL, lt = ge.timeStamp / 1e3, Te = T.filter(function(ye) {
                      return ye.hasScrollLatch();
                    }), it = Te.concat(T.filter(function(ye) {
                      return Te.indexOf(ye) === -1;
                    })), Ye = it.some(function(ye) {
                      return ye.pointerScroll(at.x, at.y, qe.x - at.x, qe.y - at.y, I, st, lt, 0) !== 0;
                    });
                    Ye && (ge.preventDefault(), _e(0));
                  }
                }
              }, Se = Ie.bind(oe);
              return F.addEventListener("mouseover", Se), F.addEventListener("mouseout", Se), F.addEventListener("mousemove", Se), F.addEventListener("mousedown", Se), F.addEventListener("mouseup", Se), F.addEventListener("touchmove", Se, {
                passive: X
              }), F.addEventListener("touchstart", Se, {
                passive: X
              }), F.addEventListener("touchend", Se), F.addEventListener("touchcancel", we), F.addEventListener("wheel", be, { passive: !1 }), function() {
                F.removeEventListener("mouseover", Se), F.removeEventListener("mouseout", Se), F.removeEventListener("mousemove", Se), F.removeEventListener("mousedown", Se), F.removeEventListener("mouseup", Se), F.removeEventListener("touchmove", Se), F.removeEventListener("touchstart", Se), F.removeEventListener("touchend", Se), F.removeEventListener("touchcancel", we), F.removeEventListener("wheel", be);
              };
            };
          }),
          /* 14 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              FocusSessionState: () => (
                /* binding */
                F
              ),
              /* harmony export */
              KeyboardInteractions: () => (
                /* binding */
                ie
              )
              /* harmony export */
            });
            var oe = ae(15), C = ae(10), I = ae(16), te = /* @__PURE__ */ new Set([
              "Space",
              "ArrowLeft",
              "ArrowRight",
              "ArrowUp",
              "ArrowDown",
              "Backspace",
              "Delete",
              "Home",
              "End",
              "Enter",
              "NumpadEnter"
            ]);
            function N(V) {
              return V.key.length === 1 && !V.ctrlKey && !V.metaKey;
            }
            function ne(V) {
              return V === oe.Key.left || V === oe.Key.right || V === oe.Key.up || V === oe.Key.down;
            }
            function Y(V) {
              return V.altKey || V.ctrlKey || V.metaKey;
            }
            var F;
            (function(V) {
              V.NotFocused = "notFocused", V.EntryPending = "entryPending", V.RiveFocused = "riveFocused";
            })(F || (F = {}));
            var ie = (
              /** @class */
              (function() {
                function V(T) {
                  var O = T.canvas, G = T.stateMachine, le = T.hasFocusNodes, me = T.getOverlayElement, K = this, X, re;
                  this.focusSessionState = F.NotFocused, this.canvasHasFocus = !1, this.focusDomainReleased = !1, this.currentOverlayElement = null, this.claimedKeyCodes = /* @__PURE__ */ new Set(), this.textInputSessionActive = !1, this.onCopy = function(Z) {
                    var fe;
                    Z.preventDefault();
                    var q = K.mainSm.selectedText();
                    q && ((fe = Z.clipboardData) === null || fe === void 0 || fe.setData("text/plain", q));
                  }, this.onCanvasFocus = function(Z) {
                    if (K.syncOverlayListener(), K.canvasHasFocus = !0, K.focusDomainReleased = !1, !(K.isInFocusDomain(Z.relatedTarget) || !K.hasFocusNodes || K.mainSm.focusState().hasFocus) && (K.focusSessionState = F.EntryPending, !!K.isKeyboardDrivenFocus())) {
                      var fe = K.cameFromBeforeCanvas(Z.relatedTarget);
                      (fe ? K.mainSm.focusNext() : K.mainSm.focusPrevious()) && (K.focusSessionState = F.RiveFocused);
                    }
                  }, this.onCanvasBlur = function(Z) {
                    K.inputProxy.owns(Z.relatedTarget) || (K.focusSessionState = F.NotFocused, K.canvasHasFocus = !1, !K.blurStaysWithRive(Z.relatedTarget) && K.mainSm.clearFocus());
                  }, this.onOverlayFocusIn = function(Z) {
                    K.isInOverlay(Z.target) && (K.focusDomainReleased = !1, K.hasFocusNodes && K.focusSessionState === F.NotFocused && (K.focusSessionState = K.mainSm.focusState().hasFocus ? F.RiveFocused : F.EntryPending));
                  }, this.onFocusDomainHostFocusIn = function(Z) {
                    K.syncOverlayListener(), K.onOverlayFocusIn(Z), K.inputProxy.owns(Z.target) && (K.focusDomainReleased = !1);
                  }, this.onKeyDown = function(Z) {
                    if (K.syncOverlayListener(), !(Z.isComposing || Z.keyCode === 229) && !K.focusDomainReleased && K.shouldRiveHandleKeyEvent(Z)) {
                      if (Z.key === "Tab" && K.hasFocusNodes) {
                        if (K.mainSm.focusState().hasFocus && K.mainSm.keyInput(oe.Key.tab, (0, oe.modifiersFromEvent)(Z), !0, Z.repeat)) {
                          Z.preventDefault();
                          return;
                        }
                        var fe = !Z.shiftKey, q = fe ? K.mainSm.focusNext() : K.mainSm.focusPrevious(), Be = K.mainSm.focusState();
                        q || Be.hasFocus ? (K.focusSessionState = F.RiveFocused, Z.preventDefault()) : (document.activeElement !== K.canvas && K.isInFocusDomain(document.activeElement) && K.canvas.focus({ preventScroll: !0 }), K.focusSessionState = F.NotFocused, K.focusDomainReleased = !0, K.canvasHasFocus = !1), K.syncOverlayListener();
                        return;
                      }
                      if ((0, C.isKeyEventClaimed)(Z)) {
                        K.claimedKeyCodes.add(Z.code);
                        return;
                      }
                      K.claimedKeyCodes.delete(Z.code);
                      var Ae = K.textInputSessionActive && K.inputProxy.owns(Z.target), _e = K.mainSm.focusState().expectsKeyboardInput, se = (0, oe.keyboardEventToRiveKey)(Z), A = se !== null && K.mainSm.keyInput(se, (0, oe.modifiersFromEvent)(Z), !0, Z.repeat);
                      if (!A && se !== null && ne(se) && !Y(Z) && (A = K.focusInDirection(se) || K.mainSm.focusState().hasFocus), N(Z)) {
                        if (Ae)
                          return;
                        if (K.textInputSessionActive && K.isInFocusDomain(Z.target)) {
                          K.inputProxy.focus();
                          return;
                        }
                        !K.textInputSessionActive && _e && K.mainSm.textInput(Z.key);
                      }
                      var x = Ae || _e;
                      (A || x && !Y(Z) && te.has(Z.code)) && Z.preventDefault();
                    }
                  }, this.onKeyUp = function(Z) {
                    if (!(Z.isComposing || Z.keyCode === 229) && !K.claimedKeyCodes.delete(Z.code) && K.focusSessionState !== F.NotFocused) {
                      var fe = (0, oe.keyboardEventToRiveKey)(Z);
                      fe !== null && K.mainSm.keyInput(fe, (0, oe.modifiersFromEvent)(Z), !1, !1);
                    }
                  }, this.canvas = O, this.mainSm = G, this.hasFocusNodes = le, this.getOverlayElement = me, this.focusDomainHost = (X = O.parentElement) !== null && X !== void 0 ? X : document, O.addEventListener("focus", this.onCanvasFocus), O.addEventListener("blur", this.onCanvasBlur), O.addEventListener("keydown", this.onKeyDown), O.addEventListener("keyup", this.onKeyUp), this.focusDomainHost.addEventListener("focusin", this.onFocusDomainHostFocusIn), this.syncOverlayListener(), this.inputProxy = new I.TextInputProxy({
                    container: (re = O.parentElement) !== null && re !== void 0 ? re : document.body,
                    canvas: O,
                    textInput: function(Z) {
                      return K.mainSm.textInput(Z);
                    },
                    // Proxy keystrokes go through the same handlers as the canvas.
                    onKeyDown: this.onKeyDown,
                    onKeyUp: this.onKeyUp,
                    onCopy: this.onCopy,
                    onBlur: function(Z) {
                      return K.handleProxyBlur(Z);
                    }
                  });
                }
                return V.prototype.isTextInputSessionActive = function() {
                  return this.textInputSessionActive;
                }, V.prototype.isEditingHostFocused = function() {
                  return this.textInputSessionActive && this.inputProxy.hasDomFocus();
                }, V.prototype.beginTextInputSession = function(T) {
                  this.textInputSessionActive = !0, this.focusSessionState = F.RiveFocused, T && this.inputProxy.focus();
                }, V.prototype.endTextInputSession = function(T) {
                  T === void 0 && (T = !1), this.textInputSessionActive && (this.textInputSessionActive = !1, this.inputProxy.endSession(), !(T || !this.inputProxy.hasDomFocus()) && this.canvas.focus({ preventScroll: !0 }));
                }, V.prototype.summonForPointer = function() {
                  this.textInputSessionActive ? this.inputProxy.focus() : this.beginTextInputSession(!0);
                }, Object.defineProperty(V.prototype, "editingHost", {
                  /** The text-input proxy, for the semantics layer to decorate while editing. */
                  get: function() {
                    return this.inputProxy;
                  },
                  enumerable: !1,
                  configurable: !0
                }), V.prototype.handleProxyBlur = function(T) {
                  this.textInputSessionActive && (this.blurStaysWithRive(T) || (this.mainSm.clearFocus(), this.endTextInputSession(!0), this.focusSessionState = F.NotFocused));
                }, V.prototype.setFocusSessionState = function(T) {
                  this.focusSessionState = T;
                }, V.prototype.notifyRiveFocused = function() {
                  this.focusSessionState = F.RiveFocused;
                }, V.prototype.blurStaysWithRive = function(T) {
                  return this.isInFocusDomain(T) || T === null && !document.hasFocus();
                }, V.prototype.focusInDirection = function(T) {
                  switch (T) {
                    case oe.Key.left:
                      return this.mainSm.focusLeft();
                    case oe.Key.right:
                      return this.mainSm.focusRight();
                    case oe.Key.up:
                      return this.mainSm.focusUp();
                    case oe.Key.down:
                      return this.mainSm.focusDown();
                    default:
                      return !1;
                  }
                }, V.prototype.shouldRiveHandleKeyEvent = function(T) {
                  if (this.focusSessionState === F.NotFocused)
                    return !1;
                  var O = this.isInFocusDomain(document.activeElement) || this.isInOverlay(T.target), G = T.target === this.canvas;
                  return O || this.canvasHasFocus || G;
                }, V.prototype.isInFocusDomain = function(T) {
                  return T === this.canvas || this.inputProxy.owns(T) ? !0 : this.isInOverlay(T);
                }, V.prototype.isInOverlay = function(T) {
                  var O, G, le;
                  return T instanceof Node && (le = (G = (O = this.getOverlayElement) === null || O === void 0 ? void 0 : O.call(this)) === null || G === void 0 ? void 0 : G.contains(T)) !== null && le !== void 0 ? le : !1;
                }, V.prototype.syncOverlayListener = function() {
                  var T, O, G, le, me, K, X, re, Z = (O = (T = this.getOverlayElement) === null || T === void 0 ? void 0 : T.call(this)) !== null && O !== void 0 ? O : null;
                  Z !== this.currentOverlayElement && ((G = this.currentOverlayElement) === null || G === void 0 || G.removeEventListener("focusin", this.onOverlayFocusIn), (le = this.currentOverlayElement) === null || le === void 0 || le.removeEventListener("keydown", this.onKeyDown), (me = this.currentOverlayElement) === null || me === void 0 || me.removeEventListener("keyup", this.onKeyUp), this.currentOverlayElement = Z, (K = this.currentOverlayElement) === null || K === void 0 || K.addEventListener("focusin", this.onOverlayFocusIn), (X = this.currentOverlayElement) === null || X === void 0 || X.addEventListener("keydown", this.onKeyDown), (re = this.currentOverlayElement) === null || re === void 0 || re.addEventListener("keyup", this.onKeyUp));
                }, V.prototype.isKeyboardDrivenFocus = function() {
                  try {
                    return this.canvas.matches(":focus-visible");
                  } catch {
                    return !1;
                  }
                }, V.prototype.cameFromBeforeCanvas = function(T) {
                  if (!T)
                    return !0;
                  var O = this.canvas.compareDocumentPosition(T);
                  return O & Node.DOCUMENT_POSITION_PRECEDING ? !0 : !(O & Node.DOCUMENT_POSITION_FOLLOWING);
                }, V.prototype.cleanup = function() {
                  var T, O, G;
                  this.canvas.removeEventListener("focus", this.onCanvasFocus), this.canvas.removeEventListener("blur", this.onCanvasBlur), this.canvas.removeEventListener("keydown", this.onKeyDown), this.canvas.removeEventListener("keyup", this.onKeyUp), this.claimedKeyCodes.clear(), this.focusDomainHost.removeEventListener("focusin", this.onFocusDomainHostFocusIn), (T = this.currentOverlayElement) === null || T === void 0 || T.removeEventListener("focusin", this.onOverlayFocusIn), (O = this.currentOverlayElement) === null || O === void 0 || O.removeEventListener("keydown", this.onKeyDown), (G = this.currentOverlayElement) === null || G === void 0 || G.removeEventListener("keyup", this.onKeyUp), this.inputProxy.hasDomFocus() && this.canvas.focus({ preventScroll: !0 }), this.inputProxy.cleanup(), this.textInputSessionActive = !1;
                }, V;
              })()
            );
          }),
          /* 15 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              Key: () => (
                /* binding */
                C
              ),
              /* harmony export */
              KeyModifiers: () => (
                /* binding */
                I
              ),
              /* harmony export */
              keyboardEventToRiveKey: () => (
                /* binding */
                Y
              ),
              /* harmony export */
              modifiersFromEvent: () => (
                /* binding */
                F
              )
              /* harmony export */
            });
            var oe = function(ie, V, T) {
              if (T || arguments.length === 2) for (var O = 0, G = V.length, le; O < G; O++)
                (le || !(O in V)) && (le || (le = Array.prototype.slice.call(V, 0, O)), le[O] = V[O]);
              return ie.concat(le || Array.prototype.slice.call(V));
            }, C = {
              space: 32,
              apostrophe: 39,
              // '
              comma: 44,
              // ,
              minus: 45,
              // -
              period: 46,
              // .
              slash: 47,
              // /
              key0: 48,
              key1: 49,
              key2: 50,
              key3: 51,
              key4: 52,
              key5: 53,
              key6: 54,
              key7: 55,
              key8: 56,
              key9: 57,
              semicolon: 59,
              // ;
              equal: 61,
              // =
              a: 65,
              b: 66,
              c: 67,
              d: 68,
              e: 69,
              f: 70,
              g: 71,
              h: 72,
              i: 73,
              j: 74,
              k: 75,
              l: 76,
              m: 77,
              n: 78,
              o: 79,
              p: 80,
              q: 81,
              r: 82,
              s: 83,
              t: 84,
              u: 85,
              v: 86,
              w: 87,
              x: 88,
              y: 89,
              z: 90,
              leftBracket: 91,
              // [
              backslash: 92,
              // \
              rightBracket: 93,
              // ]
              graveAccent: 96,
              // `
              world1: 161,
              // non-US #1
              world2: 162,
              // non-US #2
              escape: 256,
              enter: 257,
              tab: 258,
              backspace: 259,
              insert: 260,
              deleteKey: 261,
              right: 262,
              left: 263,
              down: 264,
              up: 265,
              pageUp: 266,
              pageDown: 267,
              home: 268,
              end: 269,
              capsLock: 280,
              scrollLock: 281,
              numLock: 282,
              printScreen: 283,
              pause: 284,
              f1: 290,
              f2: 291,
              f3: 292,
              f4: 293,
              f5: 294,
              f6: 295,
              f7: 296,
              f8: 297,
              f9: 298,
              f10: 299,
              f11: 300,
              f12: 301,
              f13: 302,
              f14: 303,
              f15: 304,
              f16: 305,
              f17: 306,
              f18: 307,
              f19: 308,
              f20: 309,
              f21: 310,
              f22: 311,
              f23: 312,
              f24: 313,
              f25: 314,
              kp0: 320,
              kp1: 321,
              kp2: 322,
              kp3: 323,
              kp4: 324,
              kp5: 325,
              kp6: 326,
              kp7: 327,
              kp8: 328,
              kp9: 329,
              kpDecimal: 330,
              kpDivide: 331,
              kpMultiply: 332,
              kpSubtract: 333,
              kpAdd: 334,
              kpEnter: 335,
              kpEqual: 336,
              leftShift: 340,
              leftControl: 341,
              leftAlt: 342,
              leftSuper: 343,
              rightShift: 344,
              rightControl: 345,
              rightAlt: 346,
              rightSuper: 347,
              menu: 348
            }, I = {
              none: 0,
              shift: 1,
              ctrl: 2,
              alt: 4,
              meta: 8
            }, te = {
              // Modifiers are keys too (the editor sends them), and are also in the bitmask.
              ShiftLeft: C.leftShift,
              ShiftRight: C.rightShift,
              ControlLeft: C.leftControl,
              ControlRight: C.rightControl,
              AltLeft: C.leftAlt,
              AltRight: C.rightAlt,
              MetaLeft: C.leftSuper,
              MetaRight: C.rightSuper,
              KeyA: C.a,
              KeyB: C.b,
              KeyC: C.c,
              KeyD: C.d,
              KeyE: C.e,
              KeyF: C.f,
              KeyG: C.g,
              KeyH: C.h,
              KeyI: C.i,
              KeyJ: C.j,
              KeyK: C.k,
              KeyL: C.l,
              KeyM: C.m,
              KeyN: C.n,
              KeyO: C.o,
              KeyP: C.p,
              KeyQ: C.q,
              KeyR: C.r,
              KeyS: C.s,
              KeyT: C.t,
              KeyU: C.u,
              KeyV: C.v,
              KeyW: C.w,
              KeyX: C.x,
              KeyY: C.y,
              KeyZ: C.z,
              Digit0: C.key0,
              Digit1: C.key1,
              Digit2: C.key2,
              Digit3: C.key3,
              Digit4: C.key4,
              Digit5: C.key5,
              Digit6: C.key6,
              Digit7: C.key7,
              Digit8: C.key8,
              Digit9: C.key9,
              Numpad0: C.kp0,
              Numpad1: C.kp1,
              Numpad2: C.kp2,
              Numpad3: C.kp3,
              Numpad4: C.kp4,
              Numpad5: C.kp5,
              Numpad6: C.kp6,
              Numpad7: C.kp7,
              Numpad8: C.kp8,
              Numpad9: C.kp9,
              NumpadDecimal: C.kpDecimal,
              NumpadDivide: C.kpDivide,
              NumpadMultiply: C.kpMultiply,
              NumpadSubtract: C.kpSubtract,
              NumpadAdd: C.kpAdd,
              NumpadEnter: C.kpEnter,
              NumpadEqual: C.kpEqual,
              Minus: C.minus,
              Equal: C.equal,
              BracketLeft: C.leftBracket,
              BracketRight: C.rightBracket,
              Backslash: C.backslash,
              Semicolon: C.semicolon,
              Quote: C.apostrophe,
              Backquote: C.graveAccent,
              Comma: C.comma,
              Period: C.period,
              Slash: C.slash,
              IntlBackslash: C.world1,
              IntlRo: C.world2,
              Space: C.space,
              Enter: C.enter,
              Tab: C.tab,
              Backspace: C.backspace,
              Insert: C.insert,
              Delete: C.deleteKey,
              Escape: C.escape,
              ArrowRight: C.right,
              ArrowLeft: C.left,
              ArrowDown: C.down,
              ArrowUp: C.up,
              PageUp: C.pageUp,
              PageDown: C.pageDown,
              Home: C.home,
              End: C.end,
              CapsLock: C.capsLock,
              ScrollLock: C.scrollLock,
              NumLock: C.numLock,
              PrintScreen: C.printScreen,
              Pause: C.pause,
              ContextMenu: C.menu,
              F1: C.f1,
              F2: C.f2,
              F3: C.f3,
              F4: C.f4,
              F5: C.f5,
              F6: C.f6,
              F7: C.f7,
              F8: C.f8,
              F9: C.f9,
              F10: C.f10,
              F11: C.f11,
              F12: C.f12,
              F13: C.f13,
              F14: C.f14,
              F15: C.f15,
              F16: C.f16,
              F17: C.f17,
              F18: C.f18,
              F19: C.f19,
              F20: C.f20,
              F21: C.f21,
              F22: C.f22,
              F23: C.f23,
              F24: C.f24,
              F25: C.f25
            }, N = (function() {
              for (var ie = {
                " ": C.space,
                "'": C.apostrophe,
                ",": C.comma,
                "-": C.minus,
                ".": C.period,
                "/": C.slash,
                ";": C.semicolon,
                "=": C.equal,
                "[": C.leftBracket,
                "\\": C.backslash,
                "]": C.rightBracket,
                "`": C.graveAccent
              }, V = 0; V < 26; V++)
                ie[String.fromCharCode(97 + V)] = C.a + V;
              for (var T = 0; T <= 9; T++)
                ie[String(T)] = C.key0 + T;
              return ie;
            })(), ne = new Set(oe([
              "Enter",
              "Tab",
              "Backspace",
              "Insert",
              "Delete",
              "Escape",
              "ArrowRight",
              "ArrowLeft",
              "ArrowDown",
              "ArrowUp",
              "PageUp",
              "PageDown",
              "Home",
              "End",
              "CapsLock",
              "ScrollLock",
              "NumLock",
              "PrintScreen",
              "Pause",
              "ContextMenu"
            ], Array.from({ length: 25 }, function(ie, V) {
              return "F".concat(V + 1);
            }), !0));
            function Y(ie) {
              var V, T, O = ie.code, G = ie.key;
              if (ne.has(G))
                return O === "NumpadEnter" ? C.kpEnter : (V = te[G]) !== null && V !== void 0 ? V : null;
              if (!O.startsWith("Digit") && !O.startsWith("Numpad") && G) {
                var le = N[G.toLowerCase()];
                if (le !== void 0)
                  return le;
              }
              return (T = te[O]) !== null && T !== void 0 ? T : null;
            }
            function F(ie) {
              var V = I.none;
              return ie.shiftKey && (V |= I.shift), ie.ctrlKey && (V |= I.ctrl), ie.altKey && (V |= I.alt), ie.metaKey && (V |= I.meta), V;
            }
          }),
          /* 16 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              TextInputProxy: () => (
                /* binding */
                te
              )
              /* harmony export */
            });
            var oe = ae(11), C = 16, I = /* @__PURE__ */ new Set([
              "type",
              "value",
              "style",
              "tabindex",
              "autocapitalize",
              "autocomplete",
              "autocorrect",
              "spellcheck"
            ]), te = (
              /** @class */
              (function() {
                function ne(Y) {
                  var F = this;
                  this.composing = !1, this.decoratedKeys = /* @__PURE__ */ new Set(), this.lastLeft = NaN, this.lastTop = NaN, this.reposition = function() {
                    return F.positionOverCanvas();
                  }, this.onCompositionStart = function() {
                    F.composing = !0;
                  }, this.onCompositionEnd = function() {
                    F.composing = !1, F.commit();
                  }, this.onInput = function() {
                    F.composing || F.commit();
                  }, this.onPaste = function(ie) {
                    var V, T = (V = ie.clipboardData) === null || V === void 0 ? void 0 : V.getData("text/plain");
                    T && (ie.preventDefault(), F.params.textInput(T.replace(/\r\n?/g, `
`)));
                  }, this.onBlur = function(ie) {
                    F.params.onBlur(ie.relatedTarget);
                  }, this.params = Y, this.element = this.createElement(), this.positionOverCanvas(), this.params.container.appendChild(this.element);
                }
                return ne.prototype.listeners = function() {
                  return [
                    ["keydown", this.reposition],
                    ["beforeinput", this.reposition],
                    ["keydown", this.params.onKeyDown],
                    ["keyup", this.params.onKeyUp],
                    ["input", this.onInput],
                    ["compositionstart", this.onCompositionStart],
                    ["compositionend", this.onCompositionEnd],
                    ["paste", this.onPaste],
                    ["copy", this.params.onCopy],
                    ["blur", this.onBlur]
                  ];
                }, ne.prototype.createElement = function() {
                  var Y = document.createElement("input");
                  Y.type = "text", Y.tabIndex = -1, Y.setAttribute("aria-hidden", "true"), Y.setAttribute("autocapitalize", "off"), Y.setAttribute("autocomplete", "off"), Y.setAttribute("autocorrect", "off"), Y.spellcheck = !1, Y.style.cssText = "position:absolute;width:1px;height:1px;padding:0;margin:0;border:0;outline:none;opacity:0;background:transparent;color:transparent;caret-color:transparent;overflow:hidden;resize:none;z-index:0;pointer-events:none;" + "font-size:".concat(C, "px;line-height:1;");
                  for (var F = 0, ie = this.listeners(); F < ie.length; F++) {
                    var V = ie[F], T = V[0], O = V[1];
                    Y.addEventListener(T, O);
                  }
                  return Y;
                }, ne.prototype.positionOverCanvas = function() {
                  var Y = (0, oe.canvasOffset)(this.params.canvas), F = Y.top, ie = Y.left;
                  if (window.innerHeight > 0) {
                    var V = this.params.canvas.getBoundingClientRect();
                    F += N(V.top, 0, window.innerHeight - C) - V.top, ie += N(V.left, 0, window.innerWidth - C) - V.left;
                  }
                  ie !== this.lastLeft && (this.element.style.left = "".concat(ie, "px"), this.lastLeft = ie), F !== this.lastTop && (this.element.style.top = "".concat(F, "px"), this.lastTop = F);
                }, ne.prototype.commit = function() {
                  var Y = this.element.value;
                  Y && (this.element.value = "", this.params.textInput(Y));
                }, ne.prototype.endSession = function() {
                  this.element.value = "", this.composing = !1, this.resetDecoration();
                }, ne.prototype.focus = function() {
                  this.positionOverCanvas(), this.element.focus({ preventScroll: !0 });
                }, ne.prototype.hasDomFocus = function() {
                  return document.activeElement === this.element;
                }, ne.prototype.owns = function(Y) {
                  return Y === this.element;
                }, ne.prototype.decorate = function(Y) {
                  this.element.removeAttribute("aria-hidden");
                  for (var F = 0, ie = Object.entries(Y); F < ie.length; F++) {
                    var V = ie[F], T = V[0], O = V[1];
                    I.has(T.toLowerCase()) || (O === null ? (this.element.removeAttribute(T), this.decoratedKeys.delete(T)) : (this.element.getAttribute(T) !== O && this.element.setAttribute(T, O), this.decoratedKeys.add(T)));
                  }
                }, ne.prototype.setSecure = function(Y) {
                  var F = Y ? "password" : "text";
                  this.element.type !== F && (this.element.type = F);
                }, ne.prototype.resetDecoration = function() {
                  var Y = this;
                  this.setSecure(!1), this.decoratedKeys.forEach(function(F) {
                    return Y.element.removeAttribute(F);
                  }), this.decoratedKeys.clear(), this.element.setAttribute("aria-hidden", "true");
                }, ne.prototype.cleanup = function() {
                  for (var Y = 0, F = this.listeners(); Y < F.length; Y++) {
                    var ie = F[Y], V = ie[0], T = ie[1];
                    this.element.removeEventListener(V, T);
                  }
                  this.element.remove();
                }, ne;
              })()
            );
            function N(ne, Y, F) {
              return Math.min(Math.max(ne, Y), Math.max(Y, F));
            }
          }),
          /* 17 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              BLANK_URL: () => (
                /* binding */
                Y
              ),
              /* harmony export */
              sanitizeUrl: () => (
                /* binding */
                V
              )
              /* harmony export */
            });
            var oe = /^([^\w]*)(javascript|data|vbscript)/im, C = /&#(\w+)(^\w|;)?/g, I = /&(newline|tab);/gi, te = /[\u0000-\u001F\u007F-\u009F\u2000-\u200D\uFEFF]/gim, N = /^.+(:|&colon;)/gim, ne = [".", "/"], Y = "about:blank";
            function F(T) {
              return ne.indexOf(T[0]) > -1;
            }
            function ie(T) {
              var O = T.replace(te, "");
              return O.replace(C, function(G, le) {
                return String.fromCharCode(le);
              });
            }
            function V(T) {
              if (!T)
                return Y;
              var O = ie(T).replace(I, "").replace(te, "").trim();
              if (!O)
                return Y;
              if (F(O))
                return O;
              var G = O.match(N);
              if (!G)
                return O;
              var le = G[0];
              return oe.test(le) ? Y : O;
            }
          }),
          /* 18 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              AudioAssetWrapper: () => (
                /* binding */
                T
              ),
              /* harmony export */
              AudioWrapper: () => (
                /* binding */
                ne
              ),
              /* harmony export */
              CustomFileAssetLoaderWrapper: () => (
                /* binding */
                F
              ),
              /* harmony export */
              FileAssetWrapper: () => (
                /* binding */
                ie
              ),
              /* harmony export */
              FileFinalizer: () => (
                /* binding */
                C
              ),
              /* harmony export */
              FontAssetWrapper: () => (
                /* binding */
                O
              ),
              /* harmony export */
              FontWrapper: () => (
                /* binding */
                Y
              ),
              /* harmony export */
              ImageAssetWrapper: () => (
                /* binding */
                V
              ),
              /* harmony export */
              ImageWrapper: () => (
                /* binding */
                N
              ),
              /* harmony export */
              createFinalization: () => (
                /* binding */
                K
              ),
              /* harmony export */
              finalizationRegistry: () => (
                /* binding */
                me
              )
              /* harmony export */
            });
            var oe = /* @__PURE__ */ (function() {
              var X = function(re, Z) {
                return X = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(fe, q) {
                  fe.__proto__ = q;
                } || function(fe, q) {
                  for (var Be in q) Object.prototype.hasOwnProperty.call(q, Be) && (fe[Be] = q[Be]);
                }, X(re, Z);
              };
              return function(re, Z) {
                if (typeof Z != "function" && Z !== null)
                  throw new TypeError("Class extends value " + String(Z) + " is not a constructor or null");
                X(re, Z);
                function fe() {
                  this.constructor = re;
                }
                re.prototype = Z === null ? Object.create(Z) : (fe.prototype = Z.prototype, new fe());
              };
            })(), C = (
              /** @class */
              (function() {
                function X(re, Z) {
                  Z === void 0 && (Z = null), this.selfUnref = !1, this._file = re, this._session = Z;
                }
                return X.prototype.unref = function() {
                  this._file && this._file.unref(), this._session && (this._session.delete(), this._session = null);
                }, X.prototype.release = function() {
                  this._file = null, this._session = null;
                }, X;
              })()
            ), I = (
              /** @class */
              (function() {
                function X(re) {
                  this._finalizableObject = re;
                }
                return X.prototype.unref = function() {
                  this._finalizableObject.unref();
                }, X;
              })()
            ), te = (
              /** @class */
              (function() {
                function X() {
                  this.selfUnref = !1;
                }
                return X.prototype.unref = function() {
                }, X;
              })()
            ), N = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re(Z) {
                  var fe = X.call(this) || this;
                  return fe._nativeImage = Z, fe;
                }
                return Object.defineProperty(re.prototype, "nativeImage", {
                  get: function() {
                    return this._nativeImage;
                  },
                  enumerable: !1,
                  configurable: !0
                }), re.prototype.unref = function() {
                  this.selfUnref && this._nativeImage.unref();
                }, re;
              })(te)
            ), ne = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re(Z) {
                  var fe = X.call(this) || this;
                  return fe._nativeAudio = Z, fe;
                }
                return Object.defineProperty(re.prototype, "nativeAudio", {
                  get: function() {
                    return this._nativeAudio;
                  },
                  enumerable: !1,
                  configurable: !0
                }), re.prototype.unref = function() {
                  this.selfUnref && this._nativeAudio.unref();
                }, re;
              })(te)
            ), Y = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re(Z) {
                  var fe = X.call(this) || this;
                  return fe._nativeFont = Z, fe;
                }
                return Object.defineProperty(re.prototype, "nativeFont", {
                  get: function() {
                    return this._nativeFont;
                  },
                  enumerable: !1,
                  configurable: !0
                }), re.prototype.unref = function() {
                  this.selfUnref && this._nativeFont.unref();
                }, re;
              })(te)
            ), F = (
              /** @class */
              (function() {
                function X(re, Z, fe) {
                  fe === void 0 && (fe = null), this._assetLoaderCallback = Z, this._session = fe, this.assetLoader = new re.CustomFileAssetLoader({
                    loadContents: this.loadContents.bind(this)
                  });
                }
                return X.prototype.loadContents = function(re, Z) {
                  var fe;
                  if (re.isImage)
                    fe = new V(re, this._session);
                  else if (re.isAudio)
                    fe = new T(re, this._session);
                  else if (re.isFont)
                    fe = new O(re, this._session);
                  else
                    return !1;
                  return this._assetLoaderCallback(fe, Z);
                }, X;
              })()
            ), ie = (
              /** @class */
              (function() {
                function X(re, Z) {
                  Z === void 0 && (Z = null), this._nativeFileAsset = re, this._session = Z;
                }
                return X.prototype.decode = function(re) {
                  this._nativeFileAsset.decode(re, this._session);
                }, Object.defineProperty(X.prototype, "name", {
                  get: function() {
                    return this._nativeFileAsset.name;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "fileExtension", {
                  get: function() {
                    return this._nativeFileAsset.fileExtension;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "uniqueFilename", {
                  get: function() {
                    return this._nativeFileAsset.uniqueFilename;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "isAudio", {
                  get: function() {
                    return this._nativeFileAsset.isAudio;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "isImage", {
                  get: function() {
                    return this._nativeFileAsset.isImage;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "isFont", {
                  get: function() {
                    return this._nativeFileAsset.isFont;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "cdnUuid", {
                  get: function() {
                    return this._nativeFileAsset.cdnUuid;
                  },
                  enumerable: !1,
                  configurable: !0
                }), Object.defineProperty(X.prototype, "nativeFileAsset", {
                  get: function() {
                    return this._nativeFileAsset;
                  },
                  enumerable: !1,
                  configurable: !0
                }), X;
              })()
            ), V = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re() {
                  return X !== null && X.apply(this, arguments) || this;
                }
                return re.prototype.setRenderImage = function(Z) {
                  this._nativeFileAsset.setRenderImage(Z.nativeImage);
                }, re;
              })(ie)
            ), T = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re() {
                  return X !== null && X.apply(this, arguments) || this;
                }
                return re.prototype.setAudioSource = function(Z) {
                  this._nativeFileAsset.setAudioSource(Z.nativeAudio);
                }, re;
              })(ie)
            ), O = (
              /** @class */
              (function(X) {
                oe(re, X);
                function re() {
                  return X !== null && X.apply(this, arguments) || this;
                }
                return re.prototype.setFont = function(Z) {
                  this._nativeFileAsset.setFont(Z.nativeFont);
                }, re;
              })(ie)
            ), G = (
              /** @class */
              (function() {
                function X(re) {
                }
                return X.prototype.register = function(re) {
                  re.selfUnref = !0;
                }, X.prototype.unregister = function(re) {
                }, X;
              })()
            ), le = typeof FinalizationRegistry < "u" ? FinalizationRegistry : G, me = new le(function(X) {
              X == null || X.unref();
            }), K = function(X, re) {
              var Z = new I(re);
              me.register(X, Z);
            };
          }),
          /* 19 */
          /***/
          ((Ce, ce, ae) => {
            ae.r(ce), ae.d(ce, {
              /* harmony export */
              RiveFont: () => (
                /* binding */
                C
              )
              /* harmony export */
            });
            var oe = ae(3), C = (
              /** @class */
              (function() {
                function I() {
                }
                return I.setFallbackFontCallback = function(te) {
                  I._fallbackFontCallback = te ?? null, I._wireFallbackProc();
                }, I._fontToPtr = function(te) {
                  var N;
                  if (te == null)
                    return null;
                  var ne = te.nativeFont, Y = (N = ne == null ? void 0 : ne.ptr) === null || N === void 0 ? void 0 : N.call(ne);
                  return Y ?? null;
                }, I._getFallbackPtr = function(te, N) {
                  return N < 0 || N >= te.length ? null : I._fontToPtr(te[N]);
                }, I._wireFallbackProc = function() {
                  oe.RuntimeLoader.getInstance(function(te) {
                    var N = I._fallbackFontCallback;
                    N ? te.setFallbackFontCallback((function(ne, Y, F) {
                      var ie = N(ne, F);
                      return ie ? Array.isArray(ie) ? I._getFallbackPtr(ie, Y) : Y === 0 ? I._fontToPtr(ie) : null : null;
                    })) : te.setFallbackFontCallback(null);
                  });
                }, I._fallbackFontCallback = null, I;
              })()
            );
          })
          /******/
        ], vt = {};
        function Me(Ce) {
          var ce = vt[Ce];
          if (ce !== void 0)
            return ce.exports;
          var ae = vt[Ce] = {
            /******/
            // no module.id needed
            /******/
            // no module.loaded needed
            /******/
            exports: {}
            /******/
          };
          return Ft[Ce](ae, ae.exports, Me), ae.exports;
        }
        Me.d = (Ce, ce) => {
          for (var ae in ce)
            Me.o(ce, ae) && !Me.o(Ce, ae) && Object.defineProperty(Ce, ae, { enumerable: !0, get: ce[ae] });
        }, Me.o = (Ce, ce) => Object.prototype.hasOwnProperty.call(Ce, ce), Me.r = (Ce) => {
          typeof Symbol < "u" && Symbol.toStringTag && Object.defineProperty(Ce, Symbol.toStringTag, { value: "Module" }), Object.defineProperty(Ce, "__esModule", { value: !0 });
        };
        var jt = {};
        return (() => {
          Me.r(jt), Me.d(jt, {
            /* harmony export */
            Alignment: () => (
              /* binding */
              V
            ),
            /* harmony export */
            DataEnum: () => (
              /* binding */
              lt
            ),
            /* harmony export */
            DataType: () => (
              /* binding */
              qe
            ),
            /* harmony export */
            DeprecationKeys: () => (
              /* binding */
              x
            ),
            /* harmony export */
            DrawOptimizationOptions: () => (
              /* binding */
              T
            ),
            /* harmony export */
            EventType: () => (
              /* binding */
              q
            ),
            /* harmony export */
            Fit: () => (
              /* binding */
              ie
            ),
            /* harmony export */
            Layout: () => (
              /* binding */
              O
            ),
            /* harmony export */
            LoopType: () => (
              /* binding */
              we
            ),
            /* harmony export */
            Rive: () => (
              /* binding */
              at
            ),
            /* harmony export */
            RiveEventType: () => (
              /* binding */
              me
            ),
            /* harmony export */
            RiveFile: () => (
              /* binding */
              Ue
            ),
            /* harmony export */
            RiveFont: () => (
              /* reexport safe */
              oe.RiveFont
            ),
            /* harmony export */
            RuntimeLoader: () => (
              /* reexport safe */
              ce.RuntimeLoader
            ),
            /* harmony export */
            SemanticMode: () => (
              /* reexport safe */
              ae.SemanticMode
            ),
            /* harmony export */
            StateMachineInput: () => (
              /* binding */
              le
            ),
            /* harmony export */
            StateMachineInputType: () => (
              /* binding */
              G
            ),
            /* harmony export */
            Testing: () => (
              /* binding */
              xt
            ),
            /* harmony export */
            ViewModel: () => (
              /* binding */
              st
            ),
            /* harmony export */
            ViewModelInstance: () => (
              /* binding */
              it
            ),
            /* harmony export */
            ViewModelInstanceArtboard: () => (
              /* binding */
              Wt
            ),
            /* harmony export */
            ViewModelInstanceAssetFont: () => (
              /* binding */
              Xt
            ),
            /* harmony export */
            ViewModelInstanceAssetImage: () => (
              /* binding */
              Mt
            ),
            /* harmony export */
            ViewModelInstanceBoolean: () => (
              /* binding */
              pt
            ),
            /* harmony export */
            ViewModelInstanceColor: () => (
              /* binding */
              Le
            ),
            /* harmony export */
            ViewModelInstanceEnum: () => (
              /* binding */
              We
            ),
            /* harmony export */
            ViewModelInstanceList: () => (
              /* binding */
              De
            ),
            /* harmony export */
            ViewModelInstanceNumber: () => (
              /* binding */
              et
            ),
            /* harmony export */
            ViewModelInstanceString: () => (
              /* binding */
              ye
            ),
            /* harmony export */
            ViewModelInstanceTrigger: () => (
              /* binding */
              Rt
            ),
            /* harmony export */
            ViewModelInstanceValue: () => (
              /* binding */
              Ye
            ),
            /* harmony export */
            decodeAudio: () => (
              /* binding */
              Nt
            ),
            /* harmony export */
            decodeFont: () => (
              /* binding */
              Ot
            ),
            /* harmony export */
            decodeImage: () => (
              /* binding */
              Tt
            )
            /* harmony export */
          });
          var Ce = Me(1), ce = Me(3), ae = Me(6), oe = Me(12), C = /* @__PURE__ */ (function() {
            var g = function(i, l) {
              return g = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(b, M) {
                b.__proto__ = M;
              } || function(b, M) {
                for (var L in M) Object.prototype.hasOwnProperty.call(M, L) && (b[L] = M[L]);
              }, g(i, l);
            };
            return function(i, l) {
              if (typeof l != "function" && l !== null)
                throw new TypeError("Class extends value " + String(l) + " is not a constructor or null");
              g(i, l);
              function b() {
                this.constructor = i;
              }
              i.prototype = l === null ? Object.create(l) : (b.prototype = l.prototype, new b());
            };
          })(), I = function() {
            return I = Object.assign || function(g) {
              for (var i, l = 1, b = arguments.length; l < b; l++) {
                i = arguments[l];
                for (var M in i) Object.prototype.hasOwnProperty.call(i, M) && (g[M] = i[M]);
              }
              return g;
            }, I.apply(this, arguments);
          }, te = function(g, i, l, b) {
            function M(L) {
              return L instanceof l ? L : new l(function($) {
                $(L);
              });
            }
            return new (l || (l = Promise))(function(L, $) {
              function ue(Ee) {
                try {
                  de(b.next(Ee));
                } catch (Pe) {
                  $(Pe);
                }
              }
              function he(Ee) {
                try {
                  de(b.throw(Ee));
                } catch (Pe) {
                  $(Pe);
                }
              }
              function de(Ee) {
                Ee.done ? L(Ee.value) : M(Ee.value).then(ue, he);
              }
              de((b = b.apply(g, i || [])).next());
            });
          }, N = function(g, i) {
            var l = { label: 0, sent: function() {
              if (L[0] & 1) throw L[1];
              return L[1];
            }, trys: [], ops: [] }, b, M, L, $ = Object.create((typeof Iterator == "function" ? Iterator : Object).prototype);
            return $.next = ue(0), $.throw = ue(1), $.return = ue(2), typeof Symbol == "function" && ($[Symbol.iterator] = function() {
              return this;
            }), $;
            function ue(de) {
              return function(Ee) {
                return he([de, Ee]);
              };
            }
            function he(de) {
              if (b) throw new TypeError("Generator is already executing.");
              for (; $ && ($ = 0, de[0] && (l = 0)), l; ) try {
                if (b = 1, M && (L = de[0] & 2 ? M.return : de[0] ? M.throw || ((L = M.return) && L.call(M), 0) : M.next) && !(L = L.call(M, de[1])).done) return L;
                switch (M = 0, L && (de = [de[0] & 2, L.value]), de[0]) {
                  case 0:
                  case 1:
                    L = de;
                    break;
                  case 4:
                    return l.label++, { value: de[1], done: !1 };
                  case 5:
                    l.label++, M = de[1], de = [0];
                    continue;
                  case 7:
                    de = l.ops.pop(), l.trys.pop();
                    continue;
                  default:
                    if (L = l.trys, !(L = L.length > 0 && L[L.length - 1]) && (de[0] === 6 || de[0] === 2)) {
                      l = 0;
                      continue;
                    }
                    if (de[0] === 3 && (!L || de[1] > L[0] && de[1] < L[3])) {
                      l.label = de[1];
                      break;
                    }
                    if (de[0] === 6 && l.label < L[1]) {
                      l.label = L[1], L = de;
                      break;
                    }
                    if (L && l.label < L[2]) {
                      l.label = L[2], l.ops.push(de);
                      break;
                    }
                    L[2] && l.ops.pop(), l.trys.pop();
                    continue;
                }
                de = i.call(g, l);
              } catch (Ee) {
                de = [6, Ee], M = 0;
              } finally {
                b = L = 0;
              }
              if (de[0] & 5) throw de[1];
              return { value: de[0] ? de[1] : void 0, done: !0 };
            }
          }, ne = function(g, i, l) {
            if (l || arguments.length === 2) for (var b = 0, M = i.length, L; b < M; b++)
              (L || !(b in i)) && (L || (L = Array.prototype.slice.call(i, 0, b)), L[b] = i[b]);
            return g.concat(L || Array.prototype.slice.call(i));
          }, Y = (
            /** @class */
            (function(g) {
              C(i, g);
              function i() {
                var l = g !== null && g.apply(this, arguments) || this;
                return l.isHandledError = !0, l;
              }
              return i;
            })(Error)
          ), F = function(g) {
            return g && g.isHandledError ? g.message : "Problem loading file; may be corrupt!";
          }, ie;
          (function(g) {
            g.Cover = "cover", g.Contain = "contain", g.Fill = "fill", g.FitWidth = "fitWidth", g.FitHeight = "fitHeight", g.None = "none", g.ScaleDown = "scaleDown", g.Layout = "layout";
          })(ie || (ie = {}));
          var V;
          (function(g) {
            g.Center = "center", g.TopLeft = "topLeft", g.TopCenter = "topCenter", g.TopRight = "topRight", g.CenterLeft = "centerLeft", g.CenterRight = "centerRight", g.BottomLeft = "bottomLeft", g.BottomCenter = "bottomCenter", g.BottomRight = "bottomRight";
          })(V || (V = {}));
          var T;
          (function(g) {
            g.AlwaysDraw = "alwaysDraw", g.DrawOnChanged = "drawOnChanged";
          })(T || (T = {}));
          var O = (
            /** @class */
            (function() {
              function g(i) {
                var l, b, M, L, $, ue, he;
                this.fit = (l = i == null ? void 0 : i.fit) !== null && l !== void 0 ? l : ie.Contain, this.alignment = (b = i == null ? void 0 : i.alignment) !== null && b !== void 0 ? b : V.Center, this.layoutScaleFactor = (M = i == null ? void 0 : i.layoutScaleFactor) !== null && M !== void 0 ? M : 1, this.minX = (L = i == null ? void 0 : i.minX) !== null && L !== void 0 ? L : 0, this.minY = ($ = i == null ? void 0 : i.minY) !== null && $ !== void 0 ? $ : 0, this.maxX = (ue = i == null ? void 0 : i.maxX) !== null && ue !== void 0 ? ue : 0, this.maxY = (he = i == null ? void 0 : i.maxY) !== null && he !== void 0 ? he : 0;
              }
              return g.new = function(i) {
                var l = i.fit, b = i.alignment, M = i.minX, L = i.minY, $ = i.maxX, ue = i.maxY;
                return J(x.legacyConstructors, "This function is deprecated: please use `new Layout({})` instead"), new g({ fit: l, alignment: b, minX: M, minY: L, maxX: $, maxY: ue });
              }, g.prototype.copyWith = function(i) {
                var l = i.fit, b = i.alignment, M = i.layoutScaleFactor, L = i.minX, $ = i.minY, ue = i.maxX, he = i.maxY;
                return new g({
                  fit: l ?? this.fit,
                  alignment: b ?? this.alignment,
                  layoutScaleFactor: M ?? this.layoutScaleFactor,
                  minX: L ?? this.minX,
                  minY: $ ?? this.minY,
                  maxX: ue ?? this.maxX,
                  maxY: he ?? this.maxY
                });
              }, g.prototype.runtimeFit = function(i) {
                if (this.cachedRuntimeFit)
                  return this.cachedRuntimeFit;
                var l;
                return this.fit === ie.Cover ? l = i.Fit.cover : this.fit === ie.Contain ? l = i.Fit.contain : this.fit === ie.Fill ? l = i.Fit.fill : this.fit === ie.FitWidth ? l = i.Fit.fitWidth : this.fit === ie.FitHeight ? l = i.Fit.fitHeight : this.fit === ie.ScaleDown ? l = i.Fit.scaleDown : this.fit === ie.Layout ? l = i.Fit.layout : l = i.Fit.none, this.cachedRuntimeFit = l, l;
              }, g.prototype.runtimeAlignment = function(i) {
                if (this.cachedRuntimeAlignment)
                  return this.cachedRuntimeAlignment;
                var l;
                return this.alignment === V.TopLeft ? l = i.Alignment.topLeft : this.alignment === V.TopCenter ? l = i.Alignment.topCenter : this.alignment === V.TopRight ? l = i.Alignment.topRight : this.alignment === V.CenterLeft ? l = i.Alignment.centerLeft : this.alignment === V.CenterRight ? l = i.Alignment.centerRight : this.alignment === V.BottomLeft ? l = i.Alignment.bottomLeft : this.alignment === V.BottomCenter ? l = i.Alignment.bottomCenter : this.alignment === V.BottomRight ? l = i.Alignment.bottomRight : l = i.Alignment.center, this.cachedRuntimeAlignment = l, l;
              }, g;
            })()
          ), G;
          (function(g) {
            g[g.Number = 56] = "Number", g[g.Trigger = 58] = "Trigger", g[g.Boolean = 59] = "Boolean";
          })(G || (G = {}));
          var le = (
            /** @class */
            (function() {
              function g(i, l) {
                this.type = i, this.runtimeInput = l;
              }
              return Object.defineProperty(g.prototype, "name", {
                /**
                 * Returns the name of the input
                 */
                get: function() {
                  return this.runtimeInput.name;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "value", {
                /**
                 * Returns the current value of the input
                 */
                get: function() {
                  return this.runtimeInput.value;
                },
                /**
                 * Sets the value of the input
                 */
                set: function(i) {
                  this.runtimeInput.value = i;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.fire = function() {
                this.type === G.Trigger && this.runtimeInput.fire();
              }, g.prototype.delete = function() {
                this.runtimeInput = null;
              }, g;
            })()
          ), me;
          (function(g) {
            g[g.General = 128] = "General", g[g.OpenUrl = 131] = "OpenUrl";
          })(me || (me = {}));
          var K = (
            /** @class */
            /* @__PURE__ */ (function() {
              function g(i) {
                this.isBindableArtboard = !1, this.isBindableArtboard = i;
              }
              return g;
            })()
          ), X = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                var M = g.call(this, !1) || this;
                return M.nativeArtboard = l, M.file = b, M;
              }
              return i;
            })(K)
          ), re = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l) {
                var b = g.call(this, !0) || this;
                return b.selfUnref = !1, b.nativeArtboard = l, b;
              }
              return Object.defineProperty(i.prototype, "viewModel", {
                set: function(l) {
                  this.nativeViewModel = l.nativeInstance;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.destroy = function() {
                var l;
                this.selfUnref && (this.nativeArtboard.unref(), (l = this.nativeViewModel) === null || l === void 0 || l.unref());
              }, i;
            })(K)
          ), Z = (
            /** @class */
            (function() {
              function g(i, l, b, M) {
                this.stateMachine = i, this.playing = b, this.artboard = M, this.inputs = [], this.instance = new l.StateMachineInstance(i, M), this.initInputs(l);
              }
              return Object.defineProperty(g.prototype, "hasFocusNodes", {
                /**
                 * Whether this state machine has focus nodes
                 */
                get: function() {
                  return this.instance.hasFocusNodes();
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "name", {
                get: function() {
                  return this.stateMachine.name;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "statesChanged", {
                /**
                 * Returns a list of state names that have changed on this frame
                 */
                get: function() {
                  for (var i = [], l = 0; l < this.instance.stateChangedCount(); l++)
                    i.push(this.instance.stateChangedNameByIndex(l));
                  return i;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.advance = function(i) {
                this.instance.advance(i);
              }, g.prototype.advanceAndApply = function(i) {
                this.instance.advanceAndApply(i);
              }, g.prototype.enableSemantics = function() {
                this.instance.enableSemantics();
              }, g.prototype.drainSemanticsDiff = function() {
                return this.instance.drainSemanticsDiff();
              }, g.prototype.fireSemanticAction = function(i, l) {
                this.instance.fireSemanticAction(i, l);
              }, g.prototype.focusSemanticNode = function(i) {
                return this.instance.focusSemanticNode(i);
              }, g.prototype.reportedEventCount = function() {
                return this.instance.reportedEventCount();
              }, g.prototype.reportedEventAt = function(i) {
                return this.instance.reportedEventAt(i);
              }, g.prototype.initInputs = function(i) {
                for (var l = 0; l < this.instance.inputCount(); l++) {
                  var b = this.instance.input(l);
                  this.inputs.push(this.mapRuntimeInput(b, i));
                }
              }, g.prototype.mapRuntimeInput = function(i, l) {
                if (i.type === l.SMIInput.bool)
                  return new le(G.Boolean, i.asBool());
                if (i.type === l.SMIInput.number)
                  return new le(G.Number, i.asNumber());
                if (i.type === l.SMIInput.trigger)
                  return new le(G.Trigger, i.asTrigger());
              }, g.prototype.cleanup = function() {
                this.inputs.forEach(function(i) {
                  i.delete();
                }), this.inputs.length = 0, this.instance.delete();
              }, g.prototype.bindViewModelInstance = function(i) {
                i.runtimeInstance != null && this.instance.bindViewModelInstance(i.runtimeInstance);
              }, g.prototype.focusState = function() {
                return this.instance.focusState();
              }, g.prototype.clearFocus = function() {
                this.instance.clearFocus();
              }, g;
            })()
          ), fe = (
            /** @class */
            (function() {
              function g(i, l, b, M, L) {
                M === void 0 && (M = []), L === void 0 && (L = []), this.runtime = i, this.artboard = l, this.eventManager = b, this.animations = M, this.stateMachines = L;
              }
              return g.prototype.add = function(i, l, b, M) {
                if (b === void 0 && (b = !0), M === void 0 && (M = !1), i = mt(i), i.length === 0)
                  this.animations.forEach(function(Ke) {
                    return Ke.playing = l;
                  }), this.stateMachines.forEach(function(Ke) {
                    return Ke.playing = l;
                  });
                else
                  for (var L = this.animations.map(function(Ke) {
                    return Ke.name;
                  }), $ = this.stateMachines.map(function(Ke) {
                    return Ke.name;
                  }), ue = 0; ue < i.length; ue++) {
                    var he = L.indexOf(i[ue]), de = $.indexOf(i[ue]);
                    if (he >= 0 || de >= 0)
                      he >= 0 ? this.animations[he].playing = l : this.stateMachines[de].playing = l;
                    else {
                      var Ee = this.artboard.animationByName(i[ue]);
                      if (Ee) {
                        var Pe = new Ce.Animation(Ee, this.artboard, this.runtime, l);
                        Pe.advance(0), Pe.apply(1), this.animations.push(Pe);
                      } else {
                        var Ve = this.artboard.stateMachineByName(i[ue]);
                        if (Ve) {
                          var ze = new Z(Ve, this.runtime, l, this.artboard);
                          M && ze.enableSemantics(), this.stateMachines.push(ze);
                        }
                      }
                    }
                  }
                return b && (l ? this.eventManager.fire({
                  type: q.Play,
                  data: this.playing
                }) : this.eventManager.fire({
                  type: q.Pause,
                  data: this.paused
                })), l ? this.playing : this.paused;
              }, g.prototype.initLinearAnimations = function(i, l, b) {
                b === void 0 && (b = !1);
                for (var M = this.animations.map(function(Ee) {
                  return Ee.name;
                }), L = 0; L < i.length; L++) {
                  var $ = M.indexOf(i[L]);
                  if ($ >= 0)
                    this.animations[$].playing = l;
                  else {
                    var ue = this.artboard.animationByName(i[L]);
                    if (ue) {
                      var he = new Ce.Animation(ue, this.artboard, this.runtime, l);
                      he.advance(0), he.apply(1), this.animations.push(he);
                    } else if (b) {
                      var de = "State Machine with name ".concat(i[L], " not found");
                      throw new Y(de);
                    } else
                      console.error("Animation with name ".concat(i[L], " not found."));
                  }
                }
              }, g.prototype.initStateMachines = function(i, l, b) {
                for (var M = this.stateMachines.map(function(de) {
                  return de.name;
                }), L = 0; L < i.length; L++) {
                  var $ = M.indexOf(i[L]);
                  if ($ >= 0)
                    this.stateMachines[$].playing = l;
                  else {
                    var ue = this.artboard.stateMachineByName(i[L]);
                    if (ue) {
                      var he = new Z(ue, this.runtime, l, this.artboard);
                      b && he.enableSemantics(), this.stateMachines.push(he);
                    } else
                      console.warn("State Machine with name ".concat(i[L], " not found. Falling back to find an animation with the same name.")), this.initLinearAnimations([i[L]], l, !0);
                  }
                }
              }, g.prototype.play = function(i) {
                return this.add(i, !0);
              }, g.prototype.advanceIfPaused = function() {
                this.stateMachines.forEach(function(i) {
                  i.playing || i.advanceAndApply(0);
                });
              }, g.prototype.pause = function(i) {
                return this.add(i, !1);
              }, g.prototype.scrub = function(i, l) {
                var b = this.animations.filter(function(M) {
                  return i.includes(M.name);
                });
                return b.forEach(function(M) {
                  return M.scrubTo = l;
                }), b.map(function(M) {
                  return M.name;
                });
              }, Object.defineProperty(g.prototype, "playing", {
                /**
                 * Returns a list of names of all animations and state machines currently
                 * playing
                 */
                get: function() {
                  return this.animations.filter(function(i) {
                    return i.playing;
                  }).map(function(i) {
                    return i.name;
                  }).concat(this.stateMachines.filter(function(i) {
                    return i.playing;
                  }).map(function(i) {
                    return i.name;
                  }));
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "paused", {
                /**
                 * Returns a list of names of all animations and state machines currently
                 * paused
                 */
                get: function() {
                  return this.animations.filter(function(i) {
                    return !i.playing;
                  }).map(function(i) {
                    return i.name;
                  }).concat(this.stateMachines.filter(function(i) {
                    return !i.playing;
                  }).map(function(i) {
                    return i.name;
                  }));
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.stop = function(i) {
                var l = this;
                i = mt(i);
                var b = [];
                if (i.length === 0)
                  b = this.animations.map(function($) {
                    return $.name;
                  }).concat(this.stateMachines.map(function($) {
                    return $.name;
                  })), this.animations.forEach(function($) {
                    return $.cleanup();
                  }), this.stateMachines.forEach(function($) {
                    return $.cleanup();
                  }), this.animations.splice(0, this.animations.length), this.stateMachines.splice(0, this.stateMachines.length);
                else {
                  var M = this.animations.filter(function($) {
                    return i.includes($.name);
                  });
                  M.forEach(function($) {
                    $.cleanup(), l.animations.splice(l.animations.indexOf($), 1);
                  });
                  var L = this.stateMachines.filter(function($) {
                    return i.includes($.name);
                  });
                  L.forEach(function($) {
                    $.cleanup(), l.stateMachines.splice(l.stateMachines.indexOf($), 1);
                  }), b = M.map(function($) {
                    return $.name;
                  }).concat(L.map(function($) {
                    return $.name;
                  }));
                }
                return this.eventManager.fire({
                  type: q.Stop,
                  data: b
                }), b;
              }, Object.defineProperty(g.prototype, "isPlaying", {
                /**
                 * Returns true if at least one animation is active
                 */
                get: function() {
                  return this.animations.reduce(function(i, l) {
                    return i || l.playing;
                  }, !1) || this.stateMachines.reduce(function(i, l) {
                    return i || l.playing;
                  }, !1);
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "isPaused", {
                /**
                 * Returns true if all animations are paused and there's at least one animation
                 */
                get: function() {
                  return !this.isPlaying && (this.animations.length > 0 || this.stateMachines.length > 0);
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "isStopped", {
                /**
                 * Returns true if there are no playing or paused animations/state machines
                 */
                get: function() {
                  return this.animations.length === 0 && this.stateMachines.length === 0;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.atLeastOne = function(i, l, b) {
                l === void 0 && (l = !0), b === void 0 && (b = !1);
                var M;
                return this.animations.length === 0 && this.stateMachines.length === 0 && (this.artboard.animationCount() > 0 ? (this.artboard.stateMachineCount() > 0 && J(x.defaultStateMachine, "No `stateMachine` was specified, so the artboard's first linear animation is playing by default. In the next major version, the artboard's state machine will be played by default instead when one exists. Pass the `stateMachine` parameter to adopt that behavior now."), this.add([M = this.artboard.animationByIndex(0).name], i, l)) : this.artboard.stateMachineCount() > 0 && this.add([M = this.artboard.stateMachineByIndex(0).name], i, l, b)), M;
              }, g.prototype.handleLooping = function() {
                for (var i = 0, l = this.animations.filter(function(M) {
                  return M.playing;
                }); i < l.length; i++) {
                  var b = l[i];
                  b.loopValue === 0 && b.loopCount ? (b.loopCount = 0, this.stop(b.name)) : b.loopValue === 1 && b.loopCount ? (this.eventManager.fire({
                    type: q.Loop,
                    data: { animation: b.name, type: we.Loop }
                  }), b.loopCount = 0) : b.loopValue === 2 && b.loopCount > 1 && (this.eventManager.fire({
                    type: q.Loop,
                    data: { animation: b.name, type: we.PingPong }
                  }), b.loopCount = 0);
                }
              }, g.prototype.handleStateChanges = function() {
                for (var i = [], l = 0, b = this.stateMachines.filter(function(L) {
                  return L.playing;
                }); l < b.length; l++) {
                  var M = b[l];
                  i.push.apply(i, M.statesChanged);
                }
                i.length > 0 && this.eventManager.fire({
                  type: q.StateChange,
                  data: i
                });
              }, g.prototype.handleAdvancing = function(i) {
                this.eventManager.fire({
                  type: q.Advance,
                  data: i
                });
              }, g;
            })()
          ), q;
          (function(g) {
            g.Load = "load", g.LoadError = "loaderror", g.Play = "play", g.Pause = "pause", g.Stop = "stop", g.Loop = "loop", g.Draw = "draw", g.Advance = "advance", g.StateChange = "statechange", g.RiveEvent = "riveevent", g.AudioStatusChange = "audiostatuschange";
          })(q || (q = {}));
          var Be = "Subscribing to Rive Events at runtime is deprecated and will be removed in a future major version: please use data binding instead. See https://rive.app/docs/runtimes/web/rive-events for how to migrate.", Ae = "State machine inputs are deprecated and will be removed in a future major version: please use data binding properties instead. See https://rive.app/docs/editor/data-binding/migration-guide#state-machine-inputs for how to migrate.", _e = "Text run APIs are deprecated and will be removed in a future major version: please use data binding instead. See https://rive.app/docs/editor/data-binding/migration-guide#updating-text-runs-at-runtime for how to migrate.", se = "Loop events are deprecated and will be removed in a future major version: they are only reported for linear animation playback, which is deprecated. Use a state machine to control playback and data binding to react to changes instead. See https://rive.app/docs/editor/data-binding/migration-guide for how to migrate.", A = "Subscribing to state change events at runtime is deprecated and will be removed in a future major version: use data binding (view model property observers) or state machine actions to react to changes from your graphic instead. See https://rive.app/docs/editor/state-machine/states#actions for how to migrate.", x = {
            animationNames: "animation-names",
            animationsParam: "animations-param",
            defaultStateMachine: "default-state-machine",
            legacyConstructors: "legacy-constructors",
            legacyUnsubscribe: "legacy-unsubscribe",
            loopEvents: "loop-events",
            namesArray: "names-array",
            riveEvents: "rive-events",
            scrub: "scrub",
            stateChangeEvents: "state-change-events",
            stateMachineInputs: "state-machine-inputs",
            stateMachinesParam: "state-machines-param",
            textRuns: "text-runs"
          }, H = new Set(Object.keys(x).map(function(g) {
            return x[g];
          })), Q = /* @__PURE__ */ new Set(), B = function(g) {
            if (Q.clear(), !Array.isArray(g)) {
              console.warn("[Rive] `suppressDeprecationWarnings` expects an array of deprecation ids, " + "received ".concat(typeof g, ". Nothing was suppressed."));
              return;
            }
            for (var i = 0, l = g; i < l.length; i++) {
              var b = l[i];
              H.has(b) && Q.add(b);
            }
          }, z = /* @__PURE__ */ new Set(), J = function(g, i) {
            if (!Q.has(g)) {
              var l = "".concat(g, ":").concat(i);
              z.has(l) || (z.add(l), console.warn("[Rive: ".concat(g, "] ").concat(i, `
`) + 'To suppress this warning, set Rive.suppressDeprecationWarnings = ["'.concat(g, '"]')));
            }
          }, ve = function(g, i) {
            Array.isArray(g) && J(x.namesArray, "Passing an array of names to `".concat(i, "()` is deprecated: in the next major version this parameter will be a single string, and playing multiple animations or state machines at once will not be supported."));
          }, Ie = function(g) {
            J(x.animationNames, "Passing linear animation names to `".concat(g, "()` is deprecated and will be removed in a future major version: ") + "Pass a single state machine name to control playback instead.");
          }, we;
          (function(g) {
            g.OneShot = "oneshot", g.Loop = "loop", g.PingPong = "pingpong";
          })(we || (we = {}));
          var be = (
            /** @class */
            (function() {
              function g(i) {
                i === void 0 && (i = []), this.listeners = i;
              }
              return g.prototype.getListeners = function(i) {
                return this.listeners.filter(function(l) {
                  return l.type === i;
                });
              }, g.prototype.add = function(i) {
                this.listeners.includes(i) || this.listeners.push(i);
              }, g.prototype.remove = function(i) {
                for (var l = 0; l < this.listeners.length; l++) {
                  var b = this.listeners[l];
                  if (b.type === i.type && b.callback === i.callback) {
                    this.listeners.splice(l, 1);
                    break;
                  }
                }
              }, g.prototype.removeAll = function(i) {
                var l = this;
                i ? this.listeners.filter(function(b) {
                  return b.type === i;
                }).forEach(function(b) {
                  return l.remove(b);
                }) : this.listeners.splice(0, this.listeners.length);
              }, g.prototype.fire = function(i) {
                var l = this.getListeners(i.type);
                l.forEach(function(b) {
                  return b.callback(i);
                });
              }, g;
            })()
          ), Se = (
            /** @class */
            (function() {
              function g(i) {
                this.eventManager = i, this.queue = [];
              }
              return g.prototype.add = function(i) {
                this.queue.push(i);
              }, g.prototype.process = function() {
                for (; this.queue.length > 0; ) {
                  var i = this.queue.shift();
                  i != null && i.action && i.action(), i != null && i.event && this.eventManager.fire(i.event);
                }
              }, g;
            })()
          ), ge;
          (function(g) {
            g[g.AVAILABLE = 0] = "AVAILABLE", g[g.UNAVAILABLE = 1] = "UNAVAILABLE";
          })(ge || (ge = {}));
          var Re = (
            /** @class */
            (function(g) {
              C(i, g);
              function i() {
                var l = g !== null && g.apply(this, arguments) || this;
                return l._started = !1, l._enabled = !1, l._status = ge.UNAVAILABLE, l;
              }
              return i.prototype.delay = function(l) {
                return te(this, void 0, void 0, function() {
                  return N(this, function(b) {
                    return [2, new Promise(function(M) {
                      return setTimeout(M, l);
                    })];
                  });
                });
              }, i.prototype.timeout = function() {
                return te(this, void 0, void 0, function() {
                  return N(this, function(l) {
                    return [2, new Promise(function(b, M) {
                      return setTimeout(M, 50);
                    })];
                  });
                });
              }, i.prototype.reportToListeners = function() {
                this.fire({ type: q.AudioStatusChange }), this.removeAll();
              }, i.prototype.enableAudio = function() {
                return te(this, void 0, void 0, function() {
                  return N(this, function(l) {
                    return this._enabled || (this._enabled = !0, this._status = ge.AVAILABLE, this.reportToListeners()), [
                      2
                      /*return*/
                    ];
                  });
                });
              }, i.prototype.testAudio = function() {
                return te(this, void 0, void 0, function() {
                  return N(this, function(l) {
                    switch (l.label) {
                      case 0:
                        if (!(this._status === ge.UNAVAILABLE && this._audioContext !== null)) return [3, 4];
                        l.label = 1;
                      case 1:
                        return l.trys.push([1, 3, , 4]), [4, Promise.race([this._audioContext.resume(), this.timeout()])];
                      case 2:
                        return l.sent(), this.enableAudio(), [3, 4];
                      case 3:
                        return l.sent(), [3, 4];
                      case 4:
                        return [
                          2
                          /*return*/
                        ];
                    }
                  });
                });
              }, i.prototype._establishAudio = function() {
                return te(this, void 0, void 0, function() {
                  return N(this, function(l) {
                    switch (l.label) {
                      case 0:
                        return this._started ? [3, 5] : (this._started = !0, typeof window > "u" ? (this.enableAudio(), [3, 5]) : [3, 1]);
                      case 1:
                        this._audioContext = new AudioContext(), this.listenForUserAction(), l.label = 2;
                      case 2:
                        return this._status !== ge.UNAVAILABLE ? [3, 5] : [4, this.testAudio()];
                      case 3:
                        return l.sent(), [4, this.delay(1e3)];
                      case 4:
                        return l.sent(), [3, 2];
                      case 5:
                        return [
                          2
                          /*return*/
                        ];
                    }
                  });
                });
              }, i.prototype.listenForUserAction = function() {
                var l = this, b = function() {
                  return te(l, void 0, void 0, function() {
                    return N(this, function(M) {
                      return this.enableAudio(), [
                        2
                        /*return*/
                      ];
                    });
                  });
                };
                document.addEventListener("pointerdown", b, {
                  once: !0
                });
              }, i.prototype.establishAudio = function() {
                return te(this, void 0, void 0, function() {
                  return N(this, function(l) {
                    return this._establishAudio(), [
                      2
                      /*return*/
                    ];
                  });
                });
              }, Object.defineProperty(i.prototype, "systemVolume", {
                get: function() {
                  return this._status === ge.UNAVAILABLE ? (this.testAudio(), 0) : 1;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(i.prototype, "status", {
                get: function() {
                  return this._status;
                },
                enumerable: !1,
                configurable: !0
              }), i;
            })(be)
          ), ke = new Re(), Fe = (
            /** @class */
            (function() {
              function g() {
              }
              return g.prototype.observe = function() {
              }, g.prototype.unobserve = function() {
              }, g.prototype.disconnect = function() {
              }, g;
            })()
          ), xe = globalThis.ResizeObserver || Fe, Ne = (
            /** @class */
            (function() {
              function g() {
                var i = this;
                this._elementsMap = /* @__PURE__ */ new Map(), this._onObservedEntry = function(l) {
                  var b = i._elementsMap.get(l.target);
                  b !== null ? b.onResize(l.target.clientWidth == 0 || l.target.clientHeight == 0) : i._resizeObserver.unobserve(l.target);
                }, this._onObserved = function(l) {
                  l.forEach(i._onObservedEntry);
                }, this._resizeObserver = new xe(this._onObserved);
              }
              return g.prototype.add = function(i, l) {
                var b = {
                  onResize: l,
                  element: i
                };
                return this._elementsMap.set(i, b), this._resizeObserver.observe(i), b;
              }, g.prototype.remove = function(i) {
                this._resizeObserver.unobserve(i.element), this._elementsMap.delete(i.element);
              }, g;
            })()
          ), Xe = new Ne(), Qe = 0, ot = function(g) {
            var i = g.stateMachine, l = g.animations, b = g.stateMachines;
            return l !== void 0 && J(x.animationsParam, "The `animations` parameter is deprecated and will be removed in a future major version: please use the `stateMachine` parameter to play a state machine instead."), b !== void 0 && J(x.stateMachinesParam, "The `stateMachines` parameter is deprecated: please use `stateMachine` with a single state machine name instead."), i ? {
              startingAnimationNames: [],
              startingStateMachineNames: [i]
            } : {
              startingAnimationNames: mt(l),
              startingStateMachineNames: mt(b)
            };
          }, Ue = (
            /** @class */
            (function() {
              function g(i) {
                this.enableRiveAssetCDN = !0, this.enablePerfMarks = !1, this.referenceCount = 0, this.destroyed = !1, this.selfUnref = !1, this.bindableArtboards = [], this.deferred = !1, this.session = null, this._sessionClaimed = !1, this.fileFinalizer = null, this.boundElsewhereWarned = !1, this.src = i.src, this.buffer = i.buffer, this.deferred = !!i.enableGPUCanvas, i.assetLoader && (this.assetLoader = i.assetLoader), this.enableRiveAssetCDN = typeof i.enableRiveAssetCDN == "boolean" ? i.enableRiveAssetCDN : !0, this.enablePerfMarks = !!i.enablePerfMarks, this.enablePerfMarks && (ce.RuntimeLoader.enablePerfMarks = !0), this.eventManager = new be(), i.onLoad && this.on(q.Load, i.onLoad), i.onLoadError && this.on(q.LoadError, i.onLoadError);
              }
              return g.prototype.releaseFile = function() {
                var i, l;
                (i = this.fileFinalizer) === null || i === void 0 || i.release(), (l = this.file) === null || l === void 0 || l.unref(), this.fileFinalizer = null, this.file = null;
              }, g.prototype.releaseSession = function() {
                var i;
                (i = this.session) === null || i === void 0 || i.delete(), this.session = null;
              }, g.prototype.releaseBindableArtboards = function() {
                this.bindableArtboards.forEach(function(i) {
                  return i.destroy();
                });
              }, g.prototype.initData = function() {
                return te(this, void 0, void 0, function() {
                  var i, l, b, M, L, $, ue;
                  return N(this, function(he) {
                    switch (he.label) {
                      case 0:
                        if (!(this.src && !this.buffer)) return [3, 4];
                        he.label = 1;
                      case 1:
                        return he.trys.push([1, 3, , 4]), i = this, [4, Lt(this.src)];
                      case 2:
                        return i.buffer = he.sent(), [3, 4];
                      case 3:
                        throw l = he.sent(), l instanceof Error ? l : new Y(g.fileLoadErrorMessage);
                      case 4:
                        if (this.destroyed)
                          return [
                            2
                            /*return*/
                          ];
                        this.deferred && this.session === null && (this.session = g.makeDeferredSession(this.runtime)), this.assetLoader && (M = new oe.CustomFileAssetLoaderWrapper(this.runtime, this.assetLoader, this.session), b = M.assetLoader), this.enablePerfMarks && performance.mark("rive:file-load:start"), he.label = 5;
                      case 5:
                        return he.trys.push([5, 7, , 8]), L = this, [4, this.runtime.load(new Uint8Array(this.buffer), b, this.enableRiveAssetCDN, this.session)];
                      case 6:
                        return L.file = he.sent(), [3, 8];
                      case 7:
                        throw $ = he.sent(), this.releaseSession(), $;
                      case 8:
                        return this.enablePerfMarks && (performance.mark("rive:file-load:end"), performance.measure("rive:file-load", "rive:file-load:start", "rive:file-load:end")), this.destroyed ? (this.releaseFile(), this.releaseSession(), [
                          2
                          /*return*/
                        ]) : this.file === null ? (this.releaseSession(), this.fireLoadError(g.fileLoadErrorMessage), [
                          2
                          /*return*/
                        ]) : (ue = new oe.FileFinalizer(this.file, this.session), this.fileFinalizer = ue, oe.finalizationRegistry.register(this, ue), this.eventManager.fire({
                          type: q.Load,
                          data: this
                        }), [
                          2
                          /*return*/
                        ]);
                    }
                  });
                });
              }, g.prototype.loadRiveFileBytes = function() {
                return te(this, void 0, void 0, function() {
                  var i;
                  return N(this, function(l) {
                    return this.enablePerfMarks && performance.mark("rive:fetch-riv:start"), i = this.src ? Lt(this.src) : Promise.resolve(this.buffer), this.enablePerfMarks && this.src && i.then(function() {
                      performance.mark("rive:fetch-riv:end"), performance.measure("rive:fetch-riv", "rive:fetch-riv:start", "rive:fetch-riv:end");
                    }), [2, i];
                  });
                });
              }, g.prototype.loadRuntime = function() {
                return te(this, void 0, void 0, function() {
                  var i;
                  return N(this, function(l) {
                    return this.enablePerfMarks && performance.mark("rive:await-wasm:start"), i = ce.RuntimeLoader.awaitInstance(), this.enablePerfMarks && i.then(function() {
                      performance.mark("rive:await-wasm:end"), performance.measure("rive:await-wasm", "rive:await-wasm:start", "rive:await-wasm:end");
                    }), [2, i];
                  });
                });
              }, g.prototype.init = function() {
                return te(this, void 0, void 0, function() {
                  var i, l, b, M;
                  return N(this, function(L) {
                    switch (L.label) {
                      case 0:
                        if (!this.src && !this.buffer)
                          return this.fireLoadError(g.missingErrorMessage), [
                            2
                            /*return*/
                          ];
                        L.label = 1;
                      case 1:
                        return L.trys.push([1, 4, , 5]), [4, Promise.all([this.loadRiveFileBytes(), this.loadRuntime()])];
                      case 2:
                        return i = L.sent(), l = i[0], b = i[1], this.destroyed ? [
                          2
                          /*return*/
                        ] : (this.buffer = l, this.runtime = b, this.enablePerfMarks && performance.mark("rive:init-data:start"), [4, this.initData()]);
                      case 3:
                        return L.sent(), this.enablePerfMarks && (performance.mark("rive:init-data:end"), performance.measure("rive:init-data", "rive:init-data:start", "rive:init-data:end")), [3, 5];
                      case 4:
                        return M = L.sent(), this.fireLoadError(M instanceof Error ? M.message : g.fileLoadErrorMessage), [3, 5];
                      case 5:
                        return [
                          2
                          /*return*/
                        ];
                    }
                  });
                });
              }, g.prototype.fireLoadError = function(i) {
                throw this.eventManager.fire({
                  type: q.LoadError,
                  data: i
                }), new Y(i);
              }, g.prototype.on = function(i, l) {
                this.eventManager.add({
                  type: i,
                  callback: l
                });
              }, g.prototype.off = function(i, l) {
                this.eventManager.remove({
                  type: i,
                  callback: l
                });
              }, g.prototype.cleanup = function() {
                this.referenceCount -= 1, this.referenceCount <= 0 && (this.removeAllRiveEventListeners(), this.releaseFile(), this.releaseBindableArtboards(), this.releaseSession(), this.destroyed = !0);
              }, g.makeDeferredSession = function(i) {
                var l, b, M = (b = (l = i.makeDeferredSession) === null || l === void 0 ? void 0 : l.call(i)) !== null && b !== void 0 ? b : null;
                return M === null && !g.deferredUnsupportedWarned && (g.deferredUnsupportedWarned = !0, console.warn("Rive: `enableGPUCanvas: true` was ignored because this runtime build has no GPU Canvas support; importing in immediate mode. Use a @rive-app/webgl2 or @rive-app/canvas build with deferred rendering compiled in.")), M;
              }, Object.defineProperty(g.prototype, "deferredSession", {
                /**
                 * @internal The deferred session this file imported through, or null if it
                 * was imported in immediate mode.
                 */
                get: function() {
                  return this.session;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "deferredRequested", {
                /**
                 * @internal Whether deferred was asked for, even when this build could not
                 * honor it and imported immediate.
                 */
                get: function() {
                  return this.deferred;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "sessionClaimed", {
                /**
                 * @internal Whether this file's session has ever been attached to a renderer.
                 * Attaching is once per session, so a claimed file re-imports for the next
                 * instance even after the renderer it was bound to is gone.
                 */
                get: function() {
                  return this._sessionClaimed;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.claimSession = function() {
                this._sessionClaimed = !0;
              }, g.prototype.warnBoundElsewhereOnce = function() {
                this.boundElsewhereWarned || (this.boundElsewhereWarned = !0, console.warn("Rive: this deferred RiveFile is already bound to another Rive instance's canvas, and a deferred session cannot span canvases. Re-importing the file for this instance (an extra parse of the retained buffer, no extra network request)."));
              }, g.prototype.reimport = function(i) {
                return te(this, void 0, void 0, function() {
                  var l;
                  return N(this, function(b) {
                    switch (b.label) {
                      case 0:
                        return l = new g({
                          buffer: this.buffer,
                          assetLoader: this.assetLoader,
                          enableRiveAssetCDN: this.enableRiveAssetCDN,
                          enablePerfMarks: this.enablePerfMarks,
                          enableGPUCanvas: i
                        }), [4, l.init()];
                      case 1:
                        return b.sent(), [2, l];
                    }
                  });
                });
              }, g.prototype.removeAllRiveEventListeners = function(i) {
                this.eventManager.removeAll(i);
              }, g.prototype.getInstance = function() {
                if (this.file !== null)
                  return this.referenceCount += 1, this.file;
              }, g.prototype.destroyIfUnused = function() {
                this.referenceCount <= 0 && this.cleanup();
              }, g.prototype.createBindableArtboard = function(i) {
                if (i != null) {
                  var l = new re(i);
                  return (0, oe.createFinalization)(l, l.nativeArtboard), this.bindableArtboards.push(l), l;
                }
                return null;
              }, g.prototype.getArtboard = function(i) {
                var l = this.file.artboardByName(i);
                if (l != null)
                  return new X(l, this);
              }, g.prototype.getBindableArtboard = function(i) {
                var l = this.file.bindableArtboardByName(i);
                return this.createBindableArtboard(l);
              }, g.prototype.getDefaultBindableArtboard = function() {
                var i = this.file.bindableArtboardDefault();
                return this.createBindableArtboard(i);
              }, g.prototype.internalBindableArtboardFromArtboard = function(i) {
                var l = this.file.internalBindableArtboardFromArtboard(i);
                return this.createBindableArtboard(l);
              }, g.prototype.viewModelByName = function(i) {
                var l = this.file.viewModelByName(i);
                return l !== null ? new st(l) : null;
              }, g.prototype.globalViewModelNames = function() {
                return this.file.globalViewModelNames();
              }, g.missingErrorMessage = "Rive source file or data buffer required", g.fileLoadErrorMessage = "The file failed to load", g.deferredUnsupportedWarned = !1, g;
            })()
          ), at = (
            /** @class */
            (function() {
              function g(i) {
                var l = this, b, M, L, $;
                this.loaded = !1, this.destroyed = !1, this._observed = null, this.readyForPlaying = !1, this.deferredRenderer = !1, this.ownsRiveFile = !1, this.artboard = null, this.eventCleanup = null, this._keyboardInteractions = null, this.shouldDisableRiveListeners = !1, this.automaticallyHandleEvents = !1, this.dispatchPointerExit = !0, this.enableMultiTouch = !1, this.enableRiveAssetCDN = !0, this.semanticsMode = ae.SemanticMode.Disabled, this.semanticsOptions = {
                  riveCanvasLabel: "Rive animation"
                }, this._semanticsActive = !1, this._volume = 1, this._artboardWidth = void 0, this._artboardHeight = void 0, this._devicePixelRatioUsed = 1, this._hasZeroSize = !1, this._needsRedraw = !1, this._currentCanvasWidth = 0, this._currentCanvasHeight = 0, this._audioEventListener = null, this._boundDraw = null, this._pageVisibilityHandler = null, this._explicitlyStoppedRendering = !1, this._viewModelInstance = null, this._globalViewModelInstances = /* @__PURE__ */ new Map(), this._dataEnums = null, this._tabIndex = null, this._prevHasFocus = !1, this._prevWantsTextInputSession = !1, this._inPointerDownDrain = !1, this._focusOptions = {
                  allowFocusInterrupt: !1
                }, this._semanticTree = null, this._accessibilityOverlay = null, this._overlayTransformDirty = !0, this._instanceId = "".concat(Qe++), this.drawOptimization = T.DrawOnChanged, this.enablePerfMarks = !1, this.durations = [], this.frameTimes = [], this.frameCount = 0, this.isTouchScrollEnabled = !1, this.onCanvasResize = function(ue) {
                  var he = l._hasZeroSize !== ue;
                  l._hasZeroSize = ue, ue ? (!l._layout.maxX || !l._layout.maxY) && l.resizeToCanvas() : he && l.resizeDrawingSurfaceToCanvas();
                }, this.isEditingHostFocused = function() {
                  var ue, he;
                  return (he = (ue = l._keyboardInteractions) === null || ue === void 0 ? void 0 : ue.isEditingHostFocused()) !== null && he !== void 0 ? he : !1;
                }, this.frameRequestId = null, this.renderSecondTimer = 0, this._boundDraw = this.draw.bind(this), typeof document < "u" && (this._pageVisibilityHandler = this._onPageVisibilityChange.bind(this), document.addEventListener("visibilitychange", this._pageVisibilityHandler)), this.canvas = i.canvas, i.canvas.constructor === HTMLCanvasElement && (this._observed = Xe.add(this.canvas, this.onCanvasResize)), this._currentCanvasWidth = this.canvas.width, this._currentCanvasHeight = this.canvas.height, this.src = i.src, this.buffer = i.buffer, this.riveFile = i.riveFile, this.layout = (b = i.layout) !== null && b !== void 0 ? b : new O(), this.shouldDisableRiveListeners = !!i.shouldDisableRiveListeners, this.isTouchScrollEnabled = !!i.isTouchScrollEnabled, i.automaticallyHandleEvents && J(x.riveEvents, "The `automaticallyHandleEvents` parameter is deprecated. " + Be), this.automaticallyHandleEvents = !!i.automaticallyHandleEvents, this.dispatchPointerExit = i.dispatchPointerExit === !1 ? i.dispatchPointerExit : this.dispatchPointerExit, this.enableMultiTouch = !!i.enableMultiTouch, this.drawOptimization = (M = i.drawingOptions) !== null && M !== void 0 ? M : this.drawOptimization, this.enableRiveAssetCDN = i.enableRiveAssetCDN === void 0 ? !0 : i.enableRiveAssetCDN, this.enablePerfMarks = !!i.enablePerfMarks, this.enablePerfMarks && (ce.RuntimeLoader.enablePerfMarks = !0), this._focusOptions = (L = i.focusOptions) !== null && L !== void 0 ? L : this._focusOptions, this._tabIndex = ($ = i.tabIndex) !== null && $ !== void 0 ? $ : null, this.deferredRenderer = !!i.enableGPUCanvas, this.eventManager = new be(), i.onLoad && this.on(q.Load, i.onLoad), i.onLoadError && this.on(q.LoadError, i.onLoadError), i.onPlay && this.on(q.Play, i.onPlay), i.onPause && this.on(q.Pause, i.onPause), i.onStop && this.on(q.Stop, i.onStop), i.onLoop && this.on(q.Loop, i.onLoop), i.onStateChange && this.on(q.StateChange, i.onStateChange), i.onAdvance && this.on(q.Advance, i.onAdvance), i.onload && !i.onLoad && this.on(q.Load, i.onload), i.onloaderror && !i.onLoadError && this.on(q.LoadError, i.onloaderror), i.onplay && !i.onPlay && this.on(q.Play, i.onplay), i.onpause && !i.onPause && this.on(q.Pause, i.onpause), i.onstop && !i.onStop && this.on(q.Stop, i.onstop), i.onloop && !i.onLoop && this.on(q.Loop, i.onloop), i.onstatechange && !i.onStateChange && this.on(q.StateChange, i.onstatechange), i.assetLoader && (this.assetLoader = i.assetLoader), this.taskQueue = new Se(this.eventManager), this.init({
                  src: this.src,
                  buffer: this.buffer,
                  riveFile: this.riveFile,
                  autoplay: i.autoplay,
                  autoBind: i.autoBind,
                  stateMachine: i.stateMachine,
                  animations: i.animations,
                  stateMachines: i.stateMachines,
                  artboard: i.artboard,
                  useOffscreenRenderer: i.useOffscreenRenderer,
                  tabIndex: i.tabIndex,
                  semanticsMode: i.semanticsMode,
                  semanticsOptions: i.semanticsOptions,
                  enableGPUCanvas: this.deferredRenderer
                });
              }
              return Object.defineProperty(g, "suppressDeprecationWarnings", {
                /**
                 * Deprecation warnings to silence, by {@link DeprecationId}. Each warning
                 * prints the id needed to silence it, so you can copy it out of the console.
                 *
                 * ```ts
                 * Rive.suppressDeprecationWarnings = ["rive-events", "text-runs"];
                 * ```
                 *
                 * Assigning replaces the whole list.
                 * There is no option to silence everything
                 */
                get: function() {
                  return Object.freeze(Array.from(Q));
                },
                set: function(i) {
                  B(i);
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "viewModelCount", {
                get: function() {
                  return this.file.viewModelCount();
                },
                enumerable: !1,
                configurable: !0
              }), g.new = function(i) {
                return J(x.legacyConstructors, "This function is deprecated: please use `new Rive({})` instead"), new g(i);
              }, g.prototype.enableSemantics = function() {
                this.semanticsMode = ae.SemanticMode.Enabled, this.activateSemantics();
              }, g.prototype.activateSemantics = function() {
                this._semanticsActive || this.semanticsMode === ae.SemanticMode.Disabled || (this._semanticsActive = !0, this.syncSemanticsOnStateMachines());
              }, g.prototype.syncSemanticsOnStateMachines = function() {
                if (!(!this._semanticsActive || !this.animator))
                  for (var i = 0, l = this.animator.stateMachines; i < l.length; i++) {
                    var b = l[i];
                    b.enableSemantics();
                  }
              }, g.prototype.cleanupSemantics = function() {
                this._semanticTree = null, this._accessibilityOverlay && (this._accessibilityOverlay.destroy(), this._accessibilityOverlay = null);
              }, g.prototype.onSystemAudioChanged = function() {
                this.volume = this._volume;
              }, g.prototype.init = function(i) {
                var l = this, b, M, L, $, ue, he = i.src, de = i.buffer, Ee = i.riveFile, Pe = i.stateMachine, Ve = i.animations, ze = i.stateMachines, Ke = i.artboard, tt = i.autoplay, wt = tt === void 0 ? !1 : tt, _t = i.useOffscreenRenderer, bt = _t === void 0 ? !1 : _t, St = i.autoBind, ht = St === void 0 ? !1 : St, ut = i.tabIndex, dt = i.semanticsMode, He = i.semanticsOptions, ft = i.enableGPUCanvas;
                if (!this.destroyed) {
                  if (!he && !de && !Ee)
                    throw new Y(g.missingErrorMessage);
                  this.artboard && ((M = (b = this.renderer) === null || b === void 0 ? void 0 : b.bindContext) === null || M === void 0 || M.call(b), (L = this.animator) === null || L === void 0 || L.stop(), this.artboard.delete(), this.artboard = null), this.renderer && ((ue = ($ = this.renderer).detachSession) === null || ue === void 0 || ue.call($)), this.releaseCurrentRiveFile(
                    /* isTeardown */
                    !1
                  ), this.src = he, this.buffer = de, this.riveFile = Ee, this.ownsRiveFile = !1, this.deferredRenderer = ft ?? this.deferredRenderer, this._tabIndex = ut ?? null, this.semanticsMode = dt ?? ae.SemanticMode.Disabled, this.semanticsOptions = He ?? this.semanticsOptions;
                  var je = ot({
                    stateMachine: Pe,
                    animations: Ve,
                    stateMachines: ze
                  }), Je = je.startingAnimationNames, nt = je.startingStateMachineNames;
                  this.loaded = !1, this.readyForPlaying = !1, ce.RuntimeLoader.awaitInstance().then(function(ct) {
                    if (!l.destroyed) {
                      l.runtime = ct, l.removeRiveListeners(), l.cleanupSemantics(), l.deleteRiveRenderer(), l.enablePerfMarks && performance.mark("rive:make-renderer:start");
                      try {
                        if (l.renderer = l.runtime.makeRenderer(l.canvas, bt), !l.renderer)
                          throw new Error("Renderer is null, cannot render Rive on the canvas.");
                      } catch (Bt) {
                        throw console.error(Bt), new Y("Unable to create the renderer, your environment may not support WebGL. Try the @rive-app/canvas runtime as an alternative.");
                      }
                      l.enablePerfMarks && (performance.mark("rive:make-renderer:end"), performance.measure("rive:make-renderer", "rive:make-renderer:start", "rive:make-renderer:end")), l.canvas.width || l.canvas.height || l.resizeDrawingSurfaceToCanvas(), l.initData(Ke, Je, nt, wt, ht).then(function(Bt) {
                        if (Bt)
                          return l.setupRiveListeners();
                      }).catch(function(Bt) {
                        console.error(Bt);
                      });
                    }
                  }).catch(function(ct) {
                    l.eventManager.fire({ type: q.LoadError, data: ct.message });
                  });
                }
              }, g.prototype.setupRiveListeners = function(i) {
                var l = this;
                if (this.eventCleanup && this.eventCleanup(), this.cleanupKeyboardInteractions(), !this.shouldDisableRiveListeners) {
                  var b = this.animator.stateMachines.filter(function(he) {
                    return he.playing;
                  }), M = b.filter(function(he) {
                    return l.runtime.hasListeners(he.instance);
                  }).map(function(he) {
                    return he.instance;
                  }), L = this.isTouchScrollEnabled, $ = this.dispatchPointerExit, ue = this.enableMultiTouch;
                  i && "isTouchScrollEnabled" in i && (L = i.isTouchScrollEnabled), this.eventCleanup = (0, oe.registerTouchInteractions)({
                    canvas: this.canvas,
                    artboard: this.artboard,
                    stateMachines: M,
                    renderer: this.renderer,
                    rive: this.runtime,
                    fit: this._layout.runtimeFit(this.runtime),
                    alignment: this._layout.runtimeAlignment(this.runtime),
                    isTouchScrollEnabled: L,
                    dispatchPointerExit: $,
                    enableMultiTouch: ue,
                    layoutScaleFactor: this._layout.layoutScaleFactor,
                    advanceAndDrain: this.advanceAndDrainForPointer.bind(this),
                    summonKeyboard: this.summonKeyboardForGesture.bind(this),
                    isTextProxyFocused: this.isEditingHostFocused
                  }), this.ensureKeyboardInteractions();
                }
              }, Object.defineProperty(g.prototype, "focusStateMachine", {
                // Assumes a single state machine drives focus.
                get: function() {
                  return this.animator.stateMachines.find(function(i) {
                    return i.playing && i.hasFocusNodes;
                  });
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.ensureKeyboardInteractions = function() {
                var i = this;
                if (!(this._keyboardInteractions || this.shouldDisableRiveListeners || typeof window > "u" || !(this.canvas instanceof HTMLCanvasElement))) {
                  var l = this.focusStateMachine;
                  if (l) {
                    var b = this.canvas.tabIndex;
                    (b === -1 || isNaN(b)) && (this.canvas.tabIndex = this._tabIndex !== null ? this._tabIndex : 0), this._keyboardInteractions = new oe.KeyboardInteractions({
                      canvas: this.canvas,
                      stateMachine: l.instance,
                      hasFocusNodes: !0,
                      getOverlayElement: function() {
                        var M, L;
                        return (L = (M = i._accessibilityOverlay) === null || M === void 0 ? void 0 : M.getSemanticOverlayContainer()) !== null && L !== void 0 ? L : null;
                      }
                    });
                  }
                }
              }, g.prototype.summonKeyboardForGesture = function() {
                if (this._keyboardInteractions) {
                  var i = this.focusStateMachine;
                  i && this.wantsTextInputSession(i.focusState().expectsKeyboardInput) && this._keyboardInteractions.summonForPointer();
                }
              }, g.prototype.wantsTextInputSession = function(i) {
                var l;
                if (!i)
                  return !1;
                var b = (l = this._semanticTree) === null || l === void 0 ? void 0 : l.focusedNode();
                return b === void 0 || b.role === ae.SemanticRole.textField;
              }, g.prototype.advanceAndDrainForPointer = function(i, l) {
                if (!(l != null && l.pointerDown)) {
                  this.advanceAndReportChanges(i);
                  return;
                }
                this._inPointerDownDrain = !0;
                try {
                  this.advanceAndReportChanges(i);
                } finally {
                  this._inPointerDownDrain = !1;
                }
              }, g.prototype.cleanupKeyboardInteractions = function() {
                var i;
                this._keyboardInteractions && (this._keyboardInteractions.cleanup(), this._keyboardInteractions = null), this._prevWantsTextInputSession = !1, (i = this._accessibilityOverlay) === null || i === void 0 || i.releaseEditingHost(null, null);
              }, g.prototype.removeRiveListeners = function() {
                this.eventCleanup && (this.eventCleanup(), this.eventCleanup = null), this.cleanupKeyboardInteractions();
              }, g.prototype.initializeAudio = function() {
                var i = this, l;
                ke.status == ge.UNAVAILABLE && (this.file.hasAudio || !((l = this.artboard) === null || l === void 0) && l.hasAudio && this._audioEventListener === null) && (this._audioEventListener = {
                  type: q.AudioStatusChange,
                  callback: function() {
                    return i.onSystemAudioChanged();
                  }
                }, ke.add(this._audioEventListener), ke.establishAudio());
              }, g.prototype.initArtboardSize = function() {
                this.artboard && (this._artboardWidth = this.artboard.width = this._artboardWidth || this.artboard.width, this._artboardHeight = this.artboard.height = this._artboardHeight || this.artboard.height);
              }, g.prototype.initData = function(i, l, b, M, L) {
                return te(this, void 0, void 0, function() {
                  var $, ue, he, de, Ee;
                  return N(this, function(Pe) {
                    switch (Pe.label) {
                      case 0:
                        return Pe.trys.push([0, 5, , 6]), this.ownsRiveFile = this.riveFile == null, this.ownsRiveFile ? ($ = new Ue({
                          src: this.src,
                          buffer: this.buffer,
                          enableRiveAssetCDN: this.enableRiveAssetCDN,
                          assetLoader: this.assetLoader,
                          enablePerfMarks: this.enablePerfMarks,
                          // The instance owns this file, so its flag is the file's flag.
                          enableGPUCanvas: this.deferredRenderer
                        }), this.riveFile = $, [4, $.init()]) : [3, 2];
                      case 1:
                        if (Pe.sent(), this.destroyed)
                          return $.destroyIfUnused(), [2, !1];
                        Pe.label = 2;
                      case 2:
                        return this.riveFile.deferredSession !== null || this.deferredRenderer ? [4, this.resolveDeferredRendering()] : [3, 4];
                      case 3:
                        if (Pe.sent(), this.destroyed)
                          return this.ownsRiveFile && ((de = this.riveFile) === null || de === void 0 || de.destroyIfUnused()), [2, !1];
                        Pe.label = 4;
                      case 4:
                        this.file = this.riveFile.getInstance(), this.reportDisplayScale(), this.initArtboard(i, l, b, M, L), this.initArtboardSize(), this.initializeAudio(), this.semanticsMode === ae.SemanticMode.Enabled ? this.activateSemantics() : this._semanticsActive && this.syncSemanticsOnStateMachines();
                        try {
                          this.loaded = !0, this.eventManager.fire({
                            type: q.Load,
                            data: (Ee = this.src) !== null && Ee !== void 0 ? Ee : "buffer"
                          });
                        } catch (Ve) {
                          console.error(Ve);
                        }
                        return this.animator.advanceIfPaused(), this.readyForPlaying = !0, this.taskQueue.process(), this.drawFrame(), [2, !0];
                      case 5:
                        return ue = Pe.sent(), he = F(ue), this.eventManager.fire({ type: q.LoadError, data: he }), [2, Promise.reject(he)];
                      case 6:
                        return [
                          2
                          /*return*/
                        ];
                    }
                  });
                });
              }, g.prototype.resolveDeferredRendering = function() {
                return te(this, void 0, void 0, function() {
                  var i, l, b, M, L, $, ue, he, de, Ee;
                  return N(this, function(Pe) {
                    switch (Pe.label) {
                      case 0:
                        return i = this.riveFile, l = this.ownsRiveFile, b = this.renderer, M = i.deferredSession, M === null ? (this.deferredRenderer && !i.deferredRequested && console.warn("Rive: `enableGPUCanvas: true` was ignored because this RiveFile was imported without it. The mode is fixed at import: construct the RiveFile with `enableGPUCanvas: true` to opt in."), [
                          2
                          /*return*/
                        ]) : (this.deferredRenderer || console.warn("Rive: this RiveFile was imported with `enableGPUCanvas: true`, so this instance renders deferred even though `enableGPUCanvas` is false on the instance. An immediate renderer would drop the file's deferred resources and draw nothing."), L = b == null ? void 0 : b.attachSession, typeof L == "function" ? [3, 2] : (console.warn("Rive: this renderer cannot replay a deferred session (`useOffscreenRenderer` is not supported with deferred rendering). Re-importing the file in immediate mode for this instance."), [4, i.reimport(!1)]));
                      case 1:
                        return $ = Pe.sent(), this.destroyed ? ($.destroyIfUnused(), [
                          2
                          /*return*/
                        ]) : (this.riveFile = $, this.ownsRiveFile = !0, l && i.destroyIfUnused(), [
                          2
                          /*return*/
                        ]);
                      case 2:
                        return !i.sessionClaimed && L.call(b, M) ? (i.claimSession(), [
                          2
                          /*return*/
                        ]) : (i.warnBoundElsewhereOnce(), [4, i.reimport(!0)]);
                      case 3:
                        return ue = Pe.sent(), this.destroyed ? (ue.destroyIfUnused(), [
                          2
                          /*return*/
                        ]) : (this.riveFile = ue, this.ownsRiveFile = !0, he = ue.deferredSession, he !== null && L.call(b, he) ? (ue.claimSession(), [
                          2
                          /*return*/
                        ]) : (console.warn("Rive: could not attach the re-imported file's deferred session to this canvas; falling back to immediate rendering for this instance."), (Ee = b.detachSession) === null || Ee === void 0 || Ee.call(b), [4, i.reimport(!1)]));
                      case 4:
                        return de = Pe.sent(), ue.destroyIfUnused(), this.destroyed ? (de.destroyIfUnused(), [
                          2
                          /*return*/
                        ]) : (this.riveFile = de, this.ownsRiveFile = !0, l && i.destroyIfUnused(), [
                          2
                          /*return*/
                        ]);
                    }
                  });
                });
              }, g.prototype.initArtboard = function(i, l, b, M, L) {
                if (this.file) {
                  var $ = i ? this.file.artboardByName(i) : this.file.defaultArtboard();
                  if (!$)
                    throw new Y("Invalid artboard name or no default artboard");
                  this.artboard = $, $.volume = this._volume * ke.systemVolume, this.animator = new fe(this.runtime, this.artboard, this.eventManager);
                  var ue;
                  if (l.length > 0 || b.length > 0 ? (ue = l.concat(b), this.animator.initLinearAnimations(l, M), this.animator.initStateMachines(b, M, this._semanticsActive)) : ue = [this.animator.atLeastOne(M, !1, this._semanticsActive)], this.taskQueue.add({
                    event: {
                      type: M ? q.Play : q.Pause,
                      data: ue
                    }
                  }), L) {
                    var he = this.file.defaultArtboardViewModel($);
                    if (he !== null) {
                      var de = he.defaultInstance();
                      if (de !== null) {
                        var Ee = new it(de, null);
                        (0, oe.createFinalization)(Ee, Ee.runtimeInstance), this.setViewModelInstance(Ee);
                      }
                    }
                    for (var Pe = 0, Ve = this.file.globalViewModelNames(); Pe < Ve.length; Pe++) {
                      var ze = Ve[Pe], Ke = this.file.viewModelByName(ze);
                      if (Ke !== null) {
                        var tt = new st(Ke).defaultInstance();
                        tt !== null && this.setGlobalViewModelInstance(ze, tt);
                      }
                    }
                    this.bind();
                  }
                }
              }, g.prototype.drawFrame = function() {
                var i, l;
                !((i = document == null ? void 0 : document.timeline) === null || i === void 0) && i.currentTime ? this.loaded && this.artboard && !this.frameRequestId && (this._boundDraw(document.timeline.currentTime), (l = this.runtime) === null || l === void 0 || l.resolveAnimationFrame()) : this.scheduleRendering();
              }, g.prototype._canvasSizeChanged = function() {
                var i = !1;
                return this.canvas && (this.canvas.width !== this._currentCanvasWidth && (this._currentCanvasWidth = this.canvas.width, i = !0), this.canvas.height !== this._currentCanvasHeight && (this._currentCanvasHeight = this.canvas.height, i = !0)), i;
              }, g.prototype._deferredWorkPending = function() {
                var i, l, b;
                return (b = (l = (i = this.riveFile) === null || i === void 0 ? void 0 : i.deferredSession) === null || l === void 0 ? void 0 : l.recordedThisFrame()) !== null && b !== void 0 ? b : !1;
              }, g.prototype.pollFocusState = function() {
                this.ensureKeyboardInteractions();
                var i = this._keyboardInteractions, l = i ? this.focusStateMachine : void 0;
                if (!i || !l || !(this.canvas instanceof HTMLCanvasElement)) {
                  this._prevHasFocus = !1, this._prevWantsTextInputSession = !1;
                  return;
                }
                var b = l.focusState(), M = b.hasFocus, L = b.expectsKeyboardInput;
                this.syncTextInputSession(i, this.wantsTextInputSession(L)), this.syncRiveFocus(i, this.canvas, M);
              }, g.prototype.syncTextInputSession = function(i, l) {
                var b = i.editingHost, M = this._accessibilityOverlay;
                if (l) {
                  var L = !this._prevWantsTextInputSession;
                  if (L) {
                    var $ = !this._inPointerDownDrain && (i.isInFocusDomain(document.activeElement) || !!this._focusOptions.allowFocusInterrupt);
                    i.beginTextInputSession($);
                  }
                  M && this._semanticTree && (b.hasDomFocus() ? M.syncEditingHost(this._semanticTree, b, L || !M.hasEditingHost()) : M.hasEditingHost() && M.releaseEditingHost(this._semanticTree, b));
                } else this._prevWantsTextInputSession && (M == null || M.releaseEditingHost(this._semanticTree, b), i.endTextInputSession());
                this._prevWantsTextInputSession = l;
              }, g.prototype.syncRiveFocus = function(i, l, b) {
                b ? (i.notifyRiveFocused(), this._prevHasFocus || (!i.isInFocusDomain(document.activeElement) && this._focusOptions.allowFocusInterrupt && l.focus(), this._prevHasFocus = !0)) : (this._prevHasFocus = !1, i.focusSessionState === oe.FocusSessionState.RiveFocused && i.setFocusSessionState(oe.FocusSessionState.NotFocused));
              }, g.prototype.advanceAndReportChanges = function(i) {
                for (var l, b, M = this.animator.animations.filter(function(nt) {
                  return nt.playing || nt.needsScrub;
                }).sort(function(nt) {
                  return nt.needsScrub ? -1 : 1;
                }), L = 0, $ = M; L < $.length; L++) {
                  var ue = $[L];
                  ue.advance(i), ue.instance.didLoop && (ue.loopCount += 1), ue.apply(1);
                }
                for (var he = this.animator.stateMachines.filter(function(nt) {
                  return nt.playing;
                }), de = this.enablePerfMarks && this.frameCount < 3 ? this.frameCount : -1, Ee = 0, Pe = he; Ee < Pe.length; Ee++) {
                  var Ve = Pe[Ee], ze = Ve.reportedEventCount();
                  if (ze)
                    for (var Ke = 0; Ke < ze; Ke++) {
                      var tt = Ve.reportedEventAt(Ke);
                      if (tt)
                        if (tt.type === me.OpenUrl) {
                          if (this.eventManager.fire({
                            type: q.RiveEvent,
                            data: tt
                          }), this.automaticallyHandleEvents) {
                            var wt = document.createElement("a"), _t = tt, bt = _t.url, St = _t.target, ht = (0, oe.sanitizeUrl)(bt);
                            bt && wt.setAttribute("href", ht), St && wt.setAttribute("target", St), ht && ht !== oe.BLANK_URL && wt.click();
                          }
                        } else
                          this.eventManager.fire({
                            type: q.RiveEvent,
                            data: tt
                          });
                    }
                  if (de >= 0 && performance.mark("rive:sm-advance:start:f".concat(de)), Ve.advanceAndApply(i), de >= 0 && (performance.mark("rive:sm-advance:end:f".concat(de)), performance.measure("rive:sm-advance:f".concat(de), "rive:sm-advance:start:f".concat(de), "rive:sm-advance:end:f".concat(de))), this._semanticsActive) {
                    var ut = Ve.drainSemanticsDiff();
                    ut && (this._semanticTree || (this._semanticTree = new ae.SemanticTreeModel()), this._semanticTree.applyDiff(ut));
                  }
                }
                if (this._semanticsActive && this._semanticTree && he.length > 0 && this.canvas instanceof HTMLCanvasElement) {
                  if (!this._accessibilityOverlay) {
                    var dt = he[0];
                    this._accessibilityOverlay = new ae.AccessibilityOverlay({
                      canvas: this.canvas,
                      instanceId: this._instanceId,
                      semanticsOptions: this.semanticsOptions,
                      allowFocusInterrupt: this._focusOptions.allowFocusInterrupt,
                      isEditingHostFocused: this.isEditingHostFocused,
                      fireAction: function(nt, ct) {
                        dt.fireSemanticAction(nt, ct);
                      },
                      requestFocus: function(nt) {
                        return dt.focusSemanticNode(nt);
                      },
                      clearFocus: function() {
                        return dt.instance.clearFocus();
                      }
                    });
                  }
                  var He = (l = this._accessibilityOverlay) === null || l === void 0 ? void 0 : l.needsUpdate(this._semanticTree);
                  if (He || this._overlayTransformDirty) {
                    var ft = null;
                    if (He != null && He.layoutChanged || this._overlayTransformDirty) {
                      var je = this._layout.runtimeFit(this.runtime), Je = this._layout.runtimeAlignment(this.runtime);
                      ft = this.runtime.computeAlignment(je, Je, {
                        minX: this._layout.minX,
                        minY: this._layout.minY,
                        maxX: this._layout.maxX,
                        maxY: this._layout.maxY
                      }, this.artboard.bounds, this._devicePixelRatioUsed * this._layout.layoutScaleFactor), this._overlayTransformDirty = !1;
                    }
                    this._accessibilityOverlay.update(this._semanticTree, ft, this._devicePixelRatioUsed, this.artboard.bounds, He), ft == null || ft.delete();
                  }
                }
                this.animator.stateMachines.length == 0 && this.artboard.advance(i), this.animator.handleLooping(), this.animator.handleStateChanges(), this.animator.handleAdvancing(i), this.pollFocusState(), (b = this._viewModelInstance) === null || b === void 0 || b.handleCallbacks(), this._globalViewModelInstances.forEach(function(nt) {
                  nt && nt.handleCallbacks();
                });
              }, g.prototype.draw = function(i, l) {
                if (this.frameRequestId = null, !!this.artboard) {
                  var b = performance.now(), M = this.enablePerfMarks && this.frameCount < 3 ? this.frameCount : -1;
                  this.lastRenderTime || (this.lastRenderTime = i), this.renderSecondTimer += i - this.lastRenderTime, this.renderSecondTimer > 5e3 && (this.renderSecondTimer = 0, l == null || l());
                  var L = (i - this.lastRenderTime) / 1e3;
                  this.lastRenderTime = i, this.advanceAndReportChanges(L);
                  var $ = this.renderer;
                  this._hasZeroSize || (this.drawOptimization == T.AlwaysDraw || this.artboard.didChange() || this._deferredWorkPending() || this._needsRedraw || this._canvasSizeChanged()) && ($.clear(), $.save(), M >= 0 && performance.mark("rive:align-renderer:start:f".concat(M)), this.alignRenderer(), M >= 0 && (performance.mark("rive:align-renderer:end:f".concat(M)), performance.measure("rive:align-renderer:f".concat(M), "rive:align-renderer:start:f".concat(M), "rive:align-renderer:end:f".concat(M))), M >= 0 && performance.mark("rive:artboard-draw:start:f".concat(M)), this.artboard.draw($), M >= 0 && (performance.mark("rive:artboard-draw:end:f".concat(M)), performance.measure("rive:artboard-draw:f".concat(M), "rive:artboard-draw:start:f".concat(M), "rive:artboard-draw:end:f".concat(M))), $.restore(), M >= 0 && performance.mark("rive:renderer-flush:start:f".concat(M)), $.flush(), M >= 0 && (performance.mark("rive:renderer-flush:end:f".concat(M)), performance.measure("rive:renderer-flush:f".concat(M), "rive:renderer-flush:start:f".concat(M), "rive:renderer-flush:end:f".concat(M))), this._needsRedraw = !1), this.frameCount++;
                  var ue = performance.now();
                  for (this.frameTimes.push(ue), this.durations.push(ue - b); this.frameTimes[0] <= ue - 1e3; )
                    this.frameTimes.shift(), this.durations.shift();
                  this.animator.isPlaying ? this.scheduleRendering() : this.animator.isPaused ? this.lastRenderTime = 0 : this.animator.isStopped && (this.lastRenderTime = 0);
                }
              }, g.prototype.alignRenderer = function() {
                var i = this, l = i.renderer, b = i.runtime, M = i._layout, L = i.artboard;
                l.align(M.runtimeFit(b), M.runtimeAlignment(b), {
                  minX: M.minX,
                  minY: M.minY,
                  maxX: M.maxX,
                  maxY: M.maxY
                }, L.bounds, this._devicePixelRatioUsed * M.layoutScaleFactor);
              }, Object.defineProperty(g.prototype, "fps", {
                get: function() {
                  return this.durations.length;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "frameTime", {
                get: function() {
                  return this.durations.length === 0 ? 0 : (this.durations.reduce(function(i, l) {
                    return i + l;
                  }, 0) / this.durations.length).toFixed(4);
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.cleanup = function() {
                var i, l, b, M, L;
                this.destroyed = !0, this.stopRendering(), (l = (i = this.renderer) === null || i === void 0 ? void 0 : i.bindContext) === null || l === void 0 || l.call(i), this.cleanupInstances(), this._observed !== null && Xe.remove(this._observed), this.removeRiveListeners(), this.renderer && ((M = (b = this.renderer).detachSession) === null || M === void 0 || M.call(b)), this.releaseCurrentRiveFile(
                  /* isTeardown */
                  !0
                ), this.riveFile = null, this.deleteRiveRenderer(), this._audioEventListener !== null && (ke.remove(this._audioEventListener), this._audioEventListener = null), this._pageVisibilityHandler && (document.removeEventListener("visibilitychange", this._pageVisibilityHandler), this._pageVisibilityHandler = null), (L = this._viewModelInstance) === null || L === void 0 || L.cleanup(), this._viewModelInstance = null, this._globalViewModelInstances.forEach(function($) {
                  return $.cleanup();
                }), this._globalViewModelInstances.clear(), this._dataEnums = null;
              }, g.prototype.releaseCurrentRiveFile = function(i) {
                var l, b;
                this.file ? ((i || this.ownsRiveFile) && ((l = this.riveFile) === null || l === void 0 || l.cleanup()), this.file = null) : this.ownsRiveFile && ((b = this.riveFile) === null || b === void 0 || b.destroyIfUnused());
              }, g.prototype.deleteRiveRenderer = function() {
                var i, l;
                this.renderer && ((l = (i = this.renderer).detachSession) === null || l === void 0 || l.call(i), this.renderer.delete()), this.renderer = null;
              }, Object.defineProperty(g.prototype, "deferredRendererActive", {
                /**
                 * @experimental This API is early and may encounter breaking behavior change without a major version bump
                 *
                 * Whether this instance is rendering through a deferred session. False whenever
                 * a fallback ran, whatever was requested.
                 */
                get: function() {
                  var i, l, b;
                  return (b = (l = (i = this.renderer) === null || i === void 0 ? void 0 : i.deferredActive) === null || l === void 0 ? void 0 : l.call(i)) !== null && b !== void 0 ? b : !1;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.cleanupInstances = function() {
                var i;
                this.eventCleanup !== null && this.eventCleanup(), this.cleanupKeyboardInteractions(), this.cleanupSemantics(), (i = this.animator) === null || i === void 0 || i.stop(), this.artboard && (this.artboard.delete(), this.artboard = null);
              }, g.prototype.retrieveTextRun = function(i) {
                var l;
                if (!i) {
                  console.warn("No text run name provided");
                  return;
                }
                if (!this.artboard) {
                  console.warn("Tried to access text run, but the Artboard is null");
                  return;
                }
                var b = this.artboard.textRun(i);
                if (!b) {
                  console.warn("Could not access a text run with name '".concat(i, "' in the '").concat((l = this.artboard) === null || l === void 0 ? void 0 : l.name, "' Artboard. Note that you must rename a text run node in the Rive editor to make it queryable at runtime."));
                  return;
                }
                return b;
              }, g.prototype.getTextRunValue = function(i) {
                J(x.textRuns, _e);
                var l = this.retrieveTextRun(i);
                return l ? l.text : void 0;
              }, g.prototype.setTextRunValue = function(i, l) {
                J(x.textRuns, _e);
                var b = this.retrieveTextRun(i);
                b && (b.text = l);
              }, g.prototype.warnIfLinearAnimationNames = function(i, l) {
                this.animator && this.animator.animations.some(function(b) {
                  return i.includes(b.name);
                }) && Ie(l);
              }, g.prototype.play = function(i, l) {
                var b = this;
                ve(i, "play");
                var M = mt(i);
                if (!this.readyForPlaying) {
                  this.taskQueue.add({
                    action: function() {
                      return b.play(i, l);
                    }
                  });
                  return;
                }
                this.animator.play(M), this.warnIfLinearAnimationNames(M, "play"), this.syncSemanticsOnStateMachines(), this.eventCleanup && this.eventCleanup(), this.cleanupKeyboardInteractions(), this.setupRiveListeners(), this.startRendering();
              }, g.prototype.pause = function(i) {
                var l = this;
                ve(i, "pause");
                var b = mt(i);
                if (!this.readyForPlaying) {
                  this.taskQueue.add({
                    action: function() {
                      return l.pause(i);
                    }
                  });
                  return;
                }
                this.eventCleanup && this.eventCleanup(), this.cleanupKeyboardInteractions(), this.animator.pause(b), this.warnIfLinearAnimationNames(b, "pause");
              }, g.prototype.scrub = function(i, l) {
                var b = this;
                J(x.scrub, "`scrub()` is deprecated and will be removed in a future major version: use a state machine to control playback instead.");
                var M = mt(i);
                if (!this.readyForPlaying) {
                  this.taskQueue.add({
                    action: function() {
                      return b.scrub(i, l);
                    }
                  });
                  return;
                }
                this.animator.scrub(M, l || 0), this.drawFrame();
              }, g.prototype.stop = function(i) {
                var l = this;
                ve(i, "stop");
                var b = mt(i);
                if (!this.readyForPlaying) {
                  this.taskQueue.add({
                    action: function() {
                      return l.stop(i);
                    }
                  });
                  return;
                }
                this.warnIfLinearAnimationNames(b, "stop"), this.animator && this.animator.stop(b), this.eventCleanup && this.eventCleanup(), this.cleanupKeyboardInteractions(), this.cleanupSemantics();
              }, g.prototype.reset = function(i) {
                var l, b, M = i == null ? void 0 : i.artboard, L = ot({
                  stateMachine: i == null ? void 0 : i.stateMachine,
                  animations: i == null ? void 0 : i.animations,
                  stateMachines: i == null ? void 0 : i.stateMachines
                }), $ = L.startingAnimationNames, ue = L.startingStateMachineNames, he = (l = i == null ? void 0 : i.autoplay) !== null && l !== void 0 ? l : !1, de = (b = i == null ? void 0 : i.autoBind) !== null && b !== void 0 ? b : !1;
                this.cleanupInstances(), this.initArtboard(M, $, ue, he, de), this.readyForPlaying && this.taskQueue.process();
              }, g.prototype.load = function(i) {
                if (!i.src && !i.buffer && !i.riveFile)
                  throw new Y(g.missingErrorMessage);
                this.stop(), this.init(i);
              }, Object.defineProperty(g.prototype, "layout", {
                /**
                 * Returns the current layout. Note that layout should be treated as
                 * immutable. If you want to change the layout, create a new one use the
                 * layout setter
                 */
                get: function() {
                  return this._layout;
                },
                // Sets a new layout
                set: function(i) {
                  this._layout = i, this.reportDisplayScale(), this._overlayTransformDirty = !0, (!i.maxX || !i.maxY) && this.resizeToCanvas(), this.loaded && !this.animator.isPlaying && this.drawFrame();
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.resizeToCanvas = function() {
                this._layout = this.layout.copyWith({
                  minX: 0,
                  minY: 0,
                  maxX: this.canvas.width,
                  maxY: this.canvas.height
                }), this._overlayTransformDirty = !0;
              }, g.prototype.resizeDrawingSurfaceToCanvas = function(i) {
                if (this.canvas instanceof HTMLCanvasElement && window) {
                  var l = this.canvas.getBoundingClientRect(), b = l.width, M = l.height, L = i || window.devicePixelRatio || 1;
                  if (this.devicePixelRatioUsed = L, this.canvas.width = L * b, this.canvas.height = L * M, this._needsRedraw = !0, this.resizeToCanvas(), this.layout.fit === ie.Layout && this.artboard) {
                    var $ = this._layout.layoutScaleFactor;
                    this.artboard.width = b / $, this.artboard.height = M / $;
                  }
                  this.drawFrame();
                }
              }, Object.defineProperty(g.prototype, "source", {
                // Returns the animation source, which may be undefined
                get: function() {
                  return this.src;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "activeArtboard", {
                /**
                 * Returns the name of the active artboard
                 */
                get: function() {
                  return this.artboard ? this.artboard.name : "";
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "semanticTree", {
                /**
                 * Returns the semantic tree model when semantics are enabled, or null.
                 * The overlay and external consumers use this to inspect the
                 * current state of the semantic tree.
                 */
                get: function() {
                  return this._semanticTree;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "accessibilityOverlay", {
                /**
                 * Returns the accessibility overlay when semantics are enabled, or null.
                 * External consumers can use this to inspect the
                 * current state of the accessibility overlay for this instance.
                 */
                get: function() {
                  return this._accessibilityOverlay;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "animationNames", {
                // Returns a list of animation names on the chosen artboard
                get: function() {
                  if (!this.loaded || !this.artboard)
                    return [];
                  for (var i = [], l = 0; l < this.artboard.animationCount(); l++)
                    i.push(this.artboard.animationByIndex(l).name);
                  return i;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "stateMachineNames", {
                /**
                 * Returns a list of state machine names from the current artboard
                 */
                get: function() {
                  if (!this.loaded || !this.artboard)
                    return [];
                  for (var i = [], l = 0; l < this.artboard.stateMachineCount(); l++)
                    i.push(this.artboard.stateMachineByIndex(l).name);
                  return i;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.stateMachineInputs = function(i) {
                if (J(x.stateMachineInputs, Ae), !!this.loaded) {
                  var l = this.animator.stateMachines.find(function(b) {
                    return b.name === i;
                  });
                  return l == null ? void 0 : l.inputs;
                }
              }, g.prototype.retrieveInputAtPath = function(i, l) {
                if (!i) {
                  console.warn("No input name provided for path '".concat(l, "'"));
                  return;
                }
                if (!this.artboard) {
                  console.warn("Tried to access input: '".concat(i, "', at path: '").concat(l, "', but the Artboard is null"));
                  return;
                }
                var b = this.artboard.inputByPath(i, l);
                if (!b) {
                  console.warn("Could not access an input with name: '".concat(i, "', at path:'").concat(l, "'"));
                  return;
                }
                return b;
              }, g.prototype.setBooleanStateAtPath = function(i, l, b) {
                J(x.stateMachineInputs, Ae);
                var M = this.retrieveInputAtPath(i, b);
                M && (M.type === G.Boolean ? M.asBool().value = l : console.warn("Input with name: '".concat(i, "', at path:'").concat(b, "' is not a boolean")));
              }, g.prototype.setNumberStateAtPath = function(i, l, b) {
                J(x.stateMachineInputs, Ae);
                var M = this.retrieveInputAtPath(i, b);
                M && (M.type === G.Number ? M.asNumber().value = l : console.warn("Input with name: '".concat(i, "', at path:'").concat(b, "' is not a number")));
              }, g.prototype.fireStateAtPath = function(i, l) {
                J(x.stateMachineInputs, Ae);
                var b = this.retrieveInputAtPath(i, l);
                b && (b.type === G.Trigger ? b.asTrigger().fire() : console.warn("Input with name: '".concat(i, "', at path:'").concat(l, "' is not a trigger")));
              }, g.prototype.retrieveTextAtPath = function(i, l) {
                if (!i) {
                  console.warn("No text name provided for path '".concat(l, "'"));
                  return;
                }
                if (!l) {
                  console.warn("No path provided for text '".concat(i, "'"));
                  return;
                }
                if (!this.artboard) {
                  console.warn("Tried to access text: '".concat(i, "', at path: '").concat(l, "', but the Artboard is null"));
                  return;
                }
                var b = this.artboard.textByPath(i, l);
                if (!b) {
                  console.warn("Could not access text with name: '".concat(i, "', at path:'").concat(l, "'"));
                  return;
                }
                return b;
              }, g.prototype.getTextRunValueAtPath = function(i, l) {
                J(x.textRuns, _e);
                var b = this.retrieveTextAtPath(i, l);
                if (!b) {
                  console.warn("Could not get text with name: '".concat(i, "', at path:'").concat(l, "'"));
                  return;
                }
                return b.text;
              }, g.prototype.setTextRunValueAtPath = function(i, l, b) {
                J(x.textRuns, _e);
                var M = this.retrieveTextAtPath(i, b);
                if (!M) {
                  console.warn("Could not set text with name: '".concat(i, "', at path:'").concat(b, "'"));
                  return;
                }
                M.text = l;
              }, Object.defineProperty(g.prototype, "playingStateMachineNames", {
                // Returns a list of playing machine names
                get: function() {
                  return this.loaded ? this.animator.stateMachines.filter(function(i) {
                    return i.playing;
                  }).map(function(i) {
                    return i.name;
                  }) : [];
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "playingAnimationNames", {
                // Returns a list of playing animation names
                get: function() {
                  return this.loaded ? this.animator.animations.filter(function(i) {
                    return i.playing;
                  }).map(function(i) {
                    return i.name;
                  }) : [];
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "pausedAnimationNames", {
                // Returns a list of paused animation names
                get: function() {
                  return this.loaded ? this.animator.animations.filter(function(i) {
                    return !i.playing;
                  }).map(function(i) {
                    return i.name;
                  }) : [];
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "pausedStateMachineNames", {
                /**
                 *  Returns a list of paused machine names
                 * @returns a list of state machine names that are paused
                 */
                get: function() {
                  return this.loaded ? this.animator.stateMachines.filter(function(i) {
                    return !i.playing;
                  }).map(function(i) {
                    return i.name;
                  }) : [];
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "isPlaying", {
                /**
                 * @returns true if any animation is playing
                 */
                get: function() {
                  return this.animator.isPlaying;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "isPaused", {
                /**
                 * @returns true if all instanced animations are paused
                 */
                get: function() {
                  return this.animator.isPaused;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "isStopped", {
                /**
                 * @returns true if no animations are playing or paused
                 */
                get: function() {
                  var i, l;
                  return (l = (i = this.animator) === null || i === void 0 ? void 0 : i.isStopped) !== null && l !== void 0 ? l : !0;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "bounds", {
                /**
                 * @returns the bounds of the current artboard, or undefined if the artboard
                 * isn't loaded yet.
                 */
                get: function() {
                  return this.artboard ? this.artboard.bounds : void 0;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.on = function(i, l) {
                i === q.RiveEvent ? J(x.riveEvents, Be) : i === q.StateChange ? J(x.stateChangeEvents, A) : i === q.Loop && J(x.loopEvents, se), this.eventManager.add({
                  type: i,
                  callback: l
                });
              }, g.prototype.off = function(i, l) {
                this.eventManager.remove({
                  type: i,
                  callback: l
                });
              }, g.prototype.unsubscribe = function(i, l) {
                J(x.legacyUnsubscribe, "This function is deprecated: please use `off()` instead."), this.off(i, l);
              }, g.prototype.removeAllRiveEventListeners = function(i) {
                this.eventManager.removeAll(i);
              }, g.prototype.unsubscribeAll = function(i) {
                J(x.legacyUnsubscribe, "This function is deprecated: please use `removeAllRiveEventListeners()` instead."), this.removeAllRiveEventListeners(i);
              }, g.prototype.stopRendering = function() {
                this._explicitlyStoppedRendering = !0, this.loaded && this.frameRequestId && (this.runtime.cancelAnimationFrame ? this.runtime.cancelAnimationFrame(this.frameRequestId) : cancelAnimationFrame(this.frameRequestId), this.frameRequestId = null);
              }, g.prototype.startRendering = function() {
                this._explicitlyStoppedRendering = !1, this.drawFrame();
              }, g.prototype.scheduleRendering = function() {
                this.loaded && this.artboard && !this.frameRequestId && (this.runtime.requestAnimationFrame ? this.frameRequestId = this.runtime.requestAnimationFrame(this._boundDraw) : this.frameRequestId = requestAnimationFrame(this._boundDraw));
              }, g.prototype._onPageVisibilityChange = function() {
                var i, l;
                document.hidden ? (this.frameRequestId !== null && (!((i = this.runtime) === null || i === void 0) && i.cancelAnimationFrame ? this.runtime.cancelAnimationFrame(this.frameRequestId) : cancelAnimationFrame(this.frameRequestId), this.frameRequestId = null), this.lastRenderTime = 0) : !((l = this.animator) === null || l === void 0) && l.isPlaying && !this._explicitlyStoppedRendering && this.scheduleRendering();
              }, g.prototype.enableFPSCounter = function(i) {
                this.runtime.enableFPSCounter(i);
              }, g.prototype.disableFPSCounter = function() {
                this.runtime.disableFPSCounter();
              }, Object.defineProperty(g.prototype, "contents", {
                /**
                 * Returns the contents of a Rive file: the artboards, animations, and state machines
                 */
                get: function() {
                  if (this.loaded) {
                    for (var i = {
                      artboards: []
                    }, l = 0; l < this.file.artboardCount(); l++) {
                      for (var b = this.file.artboardByIndex(l), M = {
                        name: b.name,
                        animations: [],
                        stateMachines: []
                      }, L = 0; L < b.animationCount(); L++) {
                        var $ = b.animationByIndex(L);
                        M.animations.push($.name);
                      }
                      for (var ue = 0; ue < b.stateMachineCount(); ue++) {
                        for (var he = b.stateMachineByIndex(ue), de = he.name, Ee = new this.runtime.StateMachineInstance(he, b), Pe = [], Ve = 0; Ve < Ee.inputCount(); Ve++) {
                          var ze = Ee.input(Ve);
                          Pe.push({ name: ze.name, type: ze.type });
                        }
                        M.stateMachines.push({
                          name: de,
                          inputs: Pe
                        });
                      }
                      i.artboards.push(M);
                    }
                    return i;
                  }
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "volume", {
                /**
                 * Getter / Setter for the volume of the artboard
                 */
                get: function() {
                  return this.artboard && this.artboard.volume !== this._volume && (this._volume = this.artboard.volume), this._volume;
                },
                set: function(i) {
                  this._volume = i, this.artboard && (this.artboard.volume = i * ke.systemVolume);
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "artboardWidth", {
                /**
                 * The width of the artboard.
                 *
                 * This will return 0 if the artboard is not loaded yet and a custom
                 * width has not been set.
                 *
                 * Do not set this value manually when using {@link resizeDrawingSurfaceToCanvas}
                 * with a {@link Layout.fit} of {@link Fit.Layout}, as the artboard width is
                 * automatically set.
                 */
                get: function() {
                  var i;
                  return this.artboard ? this.artboard.width : (i = this._artboardWidth) !== null && i !== void 0 ? i : 0;
                },
                set: function(i) {
                  this._artboardWidth = i, this.artboard && (this.artboard.width = i);
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "artboardHeight", {
                /**
                 * The height of the artboard.
                 *
                 * This will return 0 if the artboard is not loaded yet and a custom
                 * height has not been set.
                 *
                 * Do not set this value manually when using {@link resizeDrawingSurfaceToCanvas}
                 * with a {@link Layout.fit} of {@link Fit.Layout}, as the artboard height is
                 * automatically set.
                 */
                get: function() {
                  var i;
                  return this.artboard ? this.artboard.height : (i = this._artboardHeight) !== null && i !== void 0 ? i : 0;
                },
                set: function(i) {
                  this._artboardHeight = i, this.artboard && (this.artboard.height = i);
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.resetArtboardSize = function() {
                this.artboard ? (this.artboard.resetArtboardSize(), this._artboardWidth = this.artboard.width, this._artboardHeight = this.artboard.height) : (this._artboardWidth = void 0, this._artboardHeight = void 0);
              }, Object.defineProperty(g.prototype, "devicePixelRatioUsed", {
                /**
                 * The device pixel ratio used in rendering and canvas/artboard resizing.
                 *
                 * This value will be overidden by the device pixel ratio used in
                 * {@link resizeDrawingSurfaceToCanvas}. If you use that method, do not set this value.
                 */
                get: function() {
                  return this._devicePixelRatioUsed;
                },
                set: function(i) {
                  i !== this._devicePixelRatioUsed && (this._overlayTransformDirty = !0), this._devicePixelRatioUsed = i, this.reportDisplayScale();
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.reportDisplayScale = function() {
                var i;
                (i = this.file) === null || i === void 0 || i.displayScale(this._devicePixelRatioUsed * this._layout.layoutScaleFactor);
              }, g.prototype.bindViewModelInstance = function(i) {
                i && (this.setViewModelInstance(i), this.bind());
              }, g.prototype.setViewModelInstance = function(i) {
                var l, b = i == null ? void 0 : i.runtimeInstance;
                !this.artboard || this.destroyed || !i || !b || (i.internalIncrementReferenceCount(), (l = this._viewModelInstance) === null || l === void 0 || l.cleanup(), this._viewModelInstance = i, this.animator.stateMachines.length > 0 ? this.animator.stateMachines.forEach(function(M) {
                  return M.instance.setViewModelInstance(b);
                }) : this.artboard.setViewModelInstance(b));
              }, g.prototype.bind = function() {
                !this.artboard || this.destroyed || (this.animator.stateMachines.length > 0 ? this.animator.stateMachines.forEach(function(i) {
                  return i.instance.bind();
                }) : this.artboard.bind());
              }, Object.defineProperty(g.prototype, "viewModelInstance", {
                get: function() {
                  return this._viewModelInstance;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.setGlobalViewModelInstance = function(i, l) {
                var b, M = l == null ? void 0 : l.runtimeInstance;
                if (!this.artboard || this.destroyed || !M)
                  return !1;
                var L = !1;
                return this.animator.stateMachines.length > 0 ? this.animator.stateMachines.forEach(function($) {
                  $.instance.setGlobalViewModelInstance(i, M) && (L = !0);
                }) : L = this.artboard.setGlobalViewModelInstance(i, M), L && (l.internalIncrementReferenceCount(), (b = this._globalViewModelInstances.get(i)) === null || b === void 0 || b.cleanup(), this._globalViewModelInstances.set(i, l)), L;
              }, g.prototype.globalViewModelInstance = function(i) {
                var l = this._globalViewModelInstances.get(i);
                if (l)
                  return l;
                if (!this.artboard || this.destroyed)
                  return null;
                var b = this.animator.stateMachines.length > 0 ? this.animator.stateMachines[0].instance.globalViewModelInstance(i) : this.artboard.globalViewModelInstance(i);
                if (b === null)
                  return null;
                var M = new it(b, null);
                return (0, oe.createFinalization)(M, b), M.internalIncrementReferenceCount(), this._globalViewModelInstances.set(i, M), M;
              }, g.prototype.globalViewModelNames = function() {
                var i, l;
                return (l = (i = this.file) === null || i === void 0 ? void 0 : i.globalViewModelNames()) !== null && l !== void 0 ? l : [];
              }, g.prototype.viewModelByIndex = function(i) {
                var l = this.file.viewModelByIndex(i);
                return l !== null ? new st(l) : null;
              }, g.prototype.viewModelByName = function(i) {
                var l;
                return (l = this.riveFile) === null || l === void 0 ? void 0 : l.viewModelByName(i);
              }, g.prototype.enums = function() {
                if (this._dataEnums === null) {
                  var i = this.file.enums();
                  this._dataEnums = i.map(function(l) {
                    return new lt(l);
                  });
                }
                return this._dataEnums;
              }, g.prototype.defaultViewModel = function() {
                if (this.artboard) {
                  var i = this.file.defaultArtboardViewModel(this.artboard);
                  if (i)
                    return new st(i);
                }
                return null;
              }, g.prototype.getArtboard = function(i) {
                var l, b;
                return (b = (l = this.riveFile) === null || l === void 0 ? void 0 : l.getArtboard(i)) !== null && b !== void 0 ? b : null;
              }, g.prototype.getBindableArtboard = function(i) {
                var l, b;
                return (b = (l = this.riveFile) === null || l === void 0 ? void 0 : l.getBindableArtboard(i)) !== null && b !== void 0 ? b : null;
              }, g.prototype.getDefaultBindableArtboard = function() {
                var i, l;
                return (l = (i = this.riveFile) === null || i === void 0 ? void 0 : i.getDefaultBindableArtboard()) !== null && l !== void 0 ? l : null;
              }, g.prototype.clearFocus = function() {
                var i = this.animator.stateMachines.filter(function(l) {
                  return l.playing && l.hasFocusNodes;
                });
                i.forEach(function(l) {
                  return l.clearFocus();
                });
              }, g.missingErrorMessage = "Rive source file or data buffer required", g.cleanupErrorMessage = "Attempt to use file after calling cleanup.", g;
            })()
          ), qe;
          (function(g) {
            g.none = "none", g.string = "string", g.number = "number", g.boolean = "boolean", g.color = "color", g.list = "list", g.enumType = "enumType", g.trigger = "trigger", g.viewModel = "viewModel", g.integer = "integer", g.listIndex = "listIndex", g.image = "image", g.artboard = "artboard";
          })(qe || (qe = {}));
          var st = (
            /** @class */
            (function() {
              function g(i) {
                this._viewModel = i;
              }
              return Object.defineProperty(g.prototype, "instanceCount", {
                get: function() {
                  return this._viewModel.instanceCount;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "name", {
                get: function() {
                  return this._viewModel.name;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.instanceByIndex = function(i) {
                var l = this._viewModel.instanceByIndex(i);
                if (l !== null) {
                  var b = new it(l, null);
                  return (0, oe.createFinalization)(b, l), b;
                }
                return null;
              }, g.prototype.instanceByName = function(i) {
                var l = this._viewModel.instanceByName(i);
                if (l !== null) {
                  var b = new it(l, null);
                  return (0, oe.createFinalization)(b, l), b;
                }
                return null;
              }, g.prototype.defaultInstance = function() {
                var i = this._viewModel.defaultInstance();
                if (i !== null) {
                  var l = new it(i, null);
                  return (0, oe.createFinalization)(l, i), l;
                }
                return null;
              }, g.prototype.instance = function() {
                var i = this._viewModel.instance();
                if (i !== null) {
                  var l = new it(i, null);
                  return (0, oe.createFinalization)(l, i), l;
                }
                return null;
              }, Object.defineProperty(g.prototype, "properties", {
                get: function() {
                  return this._viewModel.getProperties();
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "instanceNames", {
                get: function() {
                  return this._viewModel.getInstanceNames();
                },
                enumerable: !1,
                configurable: !0
              }), g;
            })()
          ), lt = (
            /** @class */
            (function() {
              function g(i) {
                this._dataEnum = i;
              }
              return Object.defineProperty(g.prototype, "name", {
                get: function() {
                  return this._dataEnum.name;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "values", {
                get: function() {
                  return this._dataEnum.values;
                },
                enumerable: !1,
                configurable: !0
              }), g;
            })()
          ), Te;
          (function(g) {
            g.Number = "number", g.String = "string", g.Boolean = "boolean", g.Color = "color", g.Trigger = "trigger", g.Enum = "enum", g.List = "list", g.Image = "image", g.Font = "font", g.Artboard = "artboard";
          })(Te || (Te = {}));
          var it = (
            /** @class */
            (function() {
              function g(i, l) {
                this._parents = [], this._children = [], this._viewModelInstances = /* @__PURE__ */ new Map(), this._propertiesWithCallbacks = [], this._referenceCount = 0, this.selfUnref = !1, this._runtimeInstance = i, l !== null && this._parents.push(l);
              }
              return Object.defineProperty(g.prototype, "runtimeInstance", {
                get: function() {
                  return this._runtimeInstance;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "nativeInstance", {
                get: function() {
                  return this._runtimeInstance;
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.handleCallbacks = function() {
                this._propertiesWithCallbacks.length !== 0 && (this._propertiesWithCallbacks.forEach(function(i) {
                  i.handleCallbacks();
                }), this._propertiesWithCallbacks.forEach(function(i) {
                  i.clearChanges();
                })), this._children.forEach(function(i) {
                  return i.handleCallbacks();
                });
              }, g.prototype.addParent = function(i) {
                this._parents.includes(i) || (this._parents.push(i), (this._propertiesWithCallbacks.length > 0 || this._children.length > 0) && i.addToViewModelCallbacks(this));
              }, g.prototype.removeParent = function(i) {
                var l = this._parents.indexOf(i);
                if (l !== -1) {
                  var b = this._parents[l];
                  b.removeFromViewModelCallbacks(this), this._parents.splice(l, 1);
                }
              }, g.prototype.addToPropertyCallbacks = function(i) {
                var l = this;
                this._propertiesWithCallbacks.includes(i) || (this._propertiesWithCallbacks.push(i), this._propertiesWithCallbacks.length > 0 && this._parents.forEach(function(b) {
                  b.addToViewModelCallbacks(l);
                }));
              }, g.prototype.removeFromPropertyCallbacks = function(i) {
                var l = this;
                this._propertiesWithCallbacks.includes(i) && (this._propertiesWithCallbacks = this._propertiesWithCallbacks.filter(function(b) {
                  return b !== i;
                }), this._children.length === 0 && this._propertiesWithCallbacks.length === 0 && this._parents.forEach(function(b) {
                  b.removeFromViewModelCallbacks(l);
                }));
              }, g.prototype.addToViewModelCallbacks = function(i) {
                var l = this;
                this._children.includes(i) || (this._children.push(i), this._parents.forEach(function(b) {
                  b.addToViewModelCallbacks(l);
                }));
              }, g.prototype.removeFromViewModelCallbacks = function(i) {
                var l = this;
                this._children.includes(i) && (this._children = this._children.filter(function(b) {
                  return b !== i;
                }), this._children.length === 0 && this._propertiesWithCallbacks.length === 0 && this._parents.forEach(function(b) {
                  b.removeFromViewModelCallbacks(l);
                }));
              }, g.prototype.clearCallbacks = function() {
                this._propertiesWithCallbacks.forEach(function(i) {
                  i.clearCallbacks();
                });
              }, g.prototype.propertyFromPath = function(i, l) {
                var b = i.split("/");
                return this.propertyFromPathSegments(b, 0, l);
              }, g.prototype.viewModelFromPathSegments = function(i, l) {
                var b = this.internalViewModelInstance(i[l]);
                return b !== null ? l == i.length - 1 ? b : b.viewModelFromPathSegments(i, l++) : null;
              }, g.prototype.propertyFromPathSegments = function(i, l, b) {
                var M, L, $, ue, he, de, Ee, Pe, Ve, ze, Ke, tt, wt, _t, bt, St, ht, ut, dt, He;
                if (l < i.length - 1) {
                  var ft = this.internalViewModelInstance(i[l]);
                  return ft !== null ? ft.propertyFromPathSegments(i, l + 1, b) : null;
                }
                var je = null;
                switch (b) {
                  case Te.Number:
                    if (je = (L = (M = this._runtimeInstance) === null || M === void 0 ? void 0 : M.number(i[l])) !== null && L !== void 0 ? L : null, je !== null)
                      return new et(je, this);
                    break;
                  case Te.String:
                    if (je = (ue = ($ = this._runtimeInstance) === null || $ === void 0 ? void 0 : $.string(i[l])) !== null && ue !== void 0 ? ue : null, je !== null)
                      return new ye(je, this);
                    break;
                  case Te.Boolean:
                    if (je = (de = (he = this._runtimeInstance) === null || he === void 0 ? void 0 : he.boolean(i[l])) !== null && de !== void 0 ? de : null, je !== null)
                      return new pt(je, this);
                    break;
                  case Te.Color:
                    if (je = (Pe = (Ee = this._runtimeInstance) === null || Ee === void 0 ? void 0 : Ee.color(i[l])) !== null && Pe !== void 0 ? Pe : null, je !== null)
                      return new Le(je, this);
                    break;
                  case Te.Trigger:
                    if (je = (ze = (Ve = this._runtimeInstance) === null || Ve === void 0 ? void 0 : Ve.trigger(i[l])) !== null && ze !== void 0 ? ze : null, je !== null)
                      return new Rt(je, this);
                    break;
                  case Te.Enum:
                    if (je = (tt = (Ke = this._runtimeInstance) === null || Ke === void 0 ? void 0 : Ke.enum(i[l])) !== null && tt !== void 0 ? tt : null, je !== null)
                      return new We(je, this);
                    break;
                  case Te.List:
                    if (je = (_t = (wt = this._runtimeInstance) === null || wt === void 0 ? void 0 : wt.list(i[l])) !== null && _t !== void 0 ? _t : null, je !== null)
                      return new De(je, this);
                    break;
                  case Te.Image:
                    if (je = (St = (bt = this._runtimeInstance) === null || bt === void 0 ? void 0 : bt.image(i[l])) !== null && St !== void 0 ? St : null, je !== null)
                      return new Mt(je, this);
                    break;
                  case Te.Font:
                    if (je = (ut = (ht = this._runtimeInstance) === null || ht === void 0 ? void 0 : ht.font(i[l])) !== null && ut !== void 0 ? ut : null, je !== null)
                      return new Xt(je, this);
                    break;
                  case Te.Artboard:
                    if (je = (He = (dt = this._runtimeInstance) === null || dt === void 0 ? void 0 : dt.artboard(i[l])) !== null && He !== void 0 ? He : null, je !== null)
                      return new Wt(je, this);
                    break;
                }
                return null;
              }, g.prototype.internalViewModelInstance = function(i) {
                var l;
                if (this._viewModelInstances.has(i))
                  return this._viewModelInstances.get(i);
                var b = (l = this._runtimeInstance) === null || l === void 0 ? void 0 : l.viewModel(i);
                if (b !== null) {
                  var M = new g(b, this);
                  return (0, oe.createFinalization)(M, b), M.internalIncrementReferenceCount(), this._viewModelInstances.set(i, M), M;
                }
                return null;
              }, g.prototype.number = function(i) {
                var l = this.propertyFromPath(i, Te.Number);
                return l;
              }, g.prototype.string = function(i) {
                var l = this.propertyFromPath(i, Te.String);
                return l;
              }, g.prototype.boolean = function(i) {
                var l = this.propertyFromPath(i, Te.Boolean);
                return l;
              }, g.prototype.color = function(i) {
                var l = this.propertyFromPath(i, Te.Color);
                return l;
              }, g.prototype.trigger = function(i) {
                var l = this.propertyFromPath(i, Te.Trigger);
                return l;
              }, g.prototype.enum = function(i) {
                var l = this.propertyFromPath(i, Te.Enum);
                return l;
              }, g.prototype.list = function(i) {
                var l = this.propertyFromPath(i, Te.List);
                return l;
              }, g.prototype.image = function(i) {
                var l = this.propertyFromPath(i, Te.Image);
                return l;
              }, g.prototype.font = function(i) {
                var l = this.propertyFromPath(i, Te.Font);
                return l;
              }, g.prototype.artboard = function(i) {
                var l = this.propertyFromPath(i, Te.Artboard);
                return l;
              }, g.prototype.viewModel = function(i) {
                var l = i.split("/"), b = l.length > 1 ? this.viewModelFromPathSegments(l.slice(0, l.length - 1), 0) : this;
                return b != null ? b.internalViewModelInstance(l[l.length - 1]) : null;
              }, g.prototype.internalReplaceViewModel = function(i, l) {
                var b;
                if (l.runtimeInstance !== null) {
                  var M = ((b = this._runtimeInstance) === null || b === void 0 ? void 0 : b.replaceViewModel(i, l.runtimeInstance)) || !1;
                  if (M) {
                    l.internalIncrementReferenceCount();
                    var L = this.internalViewModelInstance(i);
                    L !== null && (L.removeParent(this), this._children.includes(L) && (this._children = this._children.filter(function($) {
                      return $ !== L;
                    })), L.cleanup()), this._viewModelInstances.set(i, l), l.addParent(this);
                  }
                  return M;
                }
                return !1;
              }, g.prototype.replaceViewModel = function(i, l) {
                var b, M = i.split("/"), L = M.length > 1 ? this.viewModelFromPathSegments(M.slice(0, M.length - 1), 0) : this;
                return (b = L == null ? void 0 : L.internalReplaceViewModel(M[M.length - 1], l)) !== null && b !== void 0 ? b : !1;
              }, g.prototype.incrementReferenceCount = function() {
                var i;
                this._referenceCount++, (i = this._runtimeInstance) === null || i === void 0 || i.incrementReferenceCount();
              }, g.prototype.decrementReferenceCount = function() {
                var i;
                this._referenceCount--, (i = this._runtimeInstance) === null || i === void 0 || i.decrementReferenceCount();
              }, Object.defineProperty(g.prototype, "properties", {
                get: function() {
                  var i;
                  return ((i = this._runtimeInstance) === null || i === void 0 ? void 0 : i.getProperties().map(function(l) {
                    return I({}, l);
                  })) || [];
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(g.prototype, "viewModelName", {
                /**
                 * Get the name of the ViewModel definition this instance was created from.
                 */
                get: function() {
                  var i, l;
                  return (l = (i = this._runtimeInstance) === null || i === void 0 ? void 0 : i.getViewModelName()) !== null && l !== void 0 ? l : "";
                },
                enumerable: !1,
                configurable: !0
              }), g.prototype.internalIncrementReferenceCount = function() {
                this._referenceCount++;
              }, g.prototype.cleanup = function() {
                var i = this, l;
                if (this._referenceCount--, this._referenceCount <= 0) {
                  this.selfUnref && ((l = this._runtimeInstance) === null || l === void 0 || l.unref()), this._runtimeInstance = null, this.clearCallbacks(), this._propertiesWithCallbacks = [], this._viewModelInstances.forEach(function(L) {
                    L.cleanup();
                  }), this._viewModelInstances.clear();
                  var b = ne([], this._children, !0);
                  this._children.length = 0;
                  var M = ne([], this._parents, !0);
                  this._parents.length = 0, b.forEach(function(L) {
                    L.removeParent(i);
                  }), M.forEach(function(L) {
                    L.removeFromViewModelCallbacks(i);
                  });
                }
              }, g;
            })()
          ), Ye = (
            /** @class */
            (function() {
              function g(i, l) {
                this.callbacks = [], this._viewModelInstanceValue = i, this._parentViewModel = l;
              }
              return g.prototype.on = function(i) {
                this.callbacks.length === 0 && this._viewModelInstanceValue.clearChanges(), this.callbacks.includes(i) || (this.callbacks.push(i), this._parentViewModel.addToPropertyCallbacks(this));
              }, g.prototype.off = function(i) {
                i ? this.callbacks = this.callbacks.filter(function(l) {
                  return l !== i;
                }) : this.callbacks.length = 0, this.callbacks.length === 0 && this._parentViewModel.removeFromPropertyCallbacks(this);
              }, g.prototype.internalHandleCallback = function(i) {
              }, g.prototype.handleCallbacks = function() {
                var i = this;
                this._viewModelInstanceValue.hasChanged && this.callbacks.forEach(function(l) {
                  i.internalHandleCallback(l);
                });
              }, g.prototype.clearChanges = function() {
                this._viewModelInstanceValue.clearChanges();
              }, g.prototype.clearCallbacks = function() {
                this.callbacks.length = 0;
              }, Object.defineProperty(g.prototype, "name", {
                get: function() {
                  return this._viewModelInstanceValue.name;
                },
                enumerable: !1,
                configurable: !0
              }), g;
            })()
          ), ye = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                get: function() {
                  return this._viewModelInstanceValue.value;
                },
                set: function(l) {
                  this._viewModelInstanceValue.value = l;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l(this.value);
              }, i;
            })(Ye)
          ), et = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                get: function() {
                  return this._viewModelInstanceValue.value;
                },
                set: function(l) {
                  this._viewModelInstanceValue.value = l;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l(this.value);
              }, i;
            })(Ye)
          ), pt = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                get: function() {
                  return this._viewModelInstanceValue.value;
                },
                set: function(l) {
                  this._viewModelInstanceValue.value = l;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l(this.value);
              }, i;
            })(Ye)
          ), Rt = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return i.prototype.trigger = function() {
                return this._viewModelInstanceValue.trigger();
              }, i.prototype.internalHandleCallback = function(l) {
                l();
              }, i;
            })(Ye)
          ), We = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                get: function() {
                  return this._viewModelInstanceValue.value;
                },
                set: function(l) {
                  this._viewModelInstanceValue.value = l;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(i.prototype, "valueIndex", {
                get: function() {
                  return this._viewModelInstanceValue.valueIndex;
                },
                set: function(l) {
                  this._viewModelInstanceValue.valueIndex = l;
                },
                enumerable: !1,
                configurable: !0
              }), Object.defineProperty(i.prototype, "values", {
                get: function() {
                  return this._viewModelInstanceValue.values;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l(this.value);
              }, i;
            })(Ye)
          ), De = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "length", {
                get: function() {
                  return this._viewModelInstanceValue.size;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.addInstance = function(l) {
                l.runtimeInstance != null && (this._viewModelInstanceValue.addInstance(l.runtimeInstance), l.addParent(this._parentViewModel));
              }, i.prototype.addInstanceAt = function(l, b) {
                return l.runtimeInstance != null && this._viewModelInstanceValue.addInstanceAt(l.runtimeInstance, b) ? (l.addParent(this._parentViewModel), !0) : !1;
              }, i.prototype.removeInstance = function(l) {
                l.runtimeInstance != null && (this._viewModelInstanceValue.removeInstance(l.runtimeInstance), l.removeParent(this._parentViewModel));
              }, i.prototype.removeInstanceAt = function(l) {
                this._viewModelInstanceValue.removeInstanceAt(l);
              }, i.prototype.instanceAt = function(l) {
                var b = this._viewModelInstanceValue.instanceAt(l);
                if (b != null) {
                  var M = new it(b, this._parentViewModel);
                  return (0, oe.createFinalization)(M, b), M;
                }
                return null;
              }, i.prototype.swap = function(l, b) {
                this._viewModelInstanceValue.swap(l, b);
              }, i.prototype.internalHandleCallback = function(l) {
                l();
              }, i;
            })(Ye)
          ), Le = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                get: function() {
                  return this._viewModelInstanceValue.value;
                },
                set: function(l) {
                  this._viewModelInstanceValue.value = l;
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.rgb = function(l, b, M) {
                this._viewModelInstanceValue.rgb(l, b, M);
              }, i.prototype.rgba = function(l, b, M, L) {
                this._viewModelInstanceValue.argb(L, l, b, M);
              }, i.prototype.argb = function(l, b, M, L) {
                this._viewModelInstanceValue.argb(l, b, M, L);
              }, i.prototype.alpha = function(l) {
                this._viewModelInstanceValue.alpha(l);
              }, i.prototype.opacity = function(l) {
                this._viewModelInstanceValue.alpha(Math.round(Math.max(0, Math.min(1, l)) * 255));
              }, i.prototype.internalHandleCallback = function(l) {
                l(this.value);
              }, i;
            })(Ye)
          ), Mt = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                set: function(l) {
                  var b;
                  this._viewModelInstanceValue.value((b = l == null ? void 0 : l.nativeImage) !== null && b !== void 0 ? b : null);
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l();
              }, i;
            })(Ye)
          ), Xt = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                set: function(l) {
                  var b;
                  this._viewModelInstanceValue.value((b = l == null ? void 0 : l.nativeFont) !== null && b !== void 0 ? b : null);
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l();
              }, i;
            })(Ye)
          ), Wt = (
            /** @class */
            (function(g) {
              C(i, g);
              function i(l, b) {
                return g.call(this, l, b) || this;
              }
              return Object.defineProperty(i.prototype, "value", {
                set: function(l) {
                  var b, M, L;
                  l.isBindableArtboard ? L = l : L = l.file.internalBindableArtboardFromArtboard(l.nativeArtboard), this._viewModelInstanceValue.value((b = L == null ? void 0 : L.nativeArtboard) !== null && b !== void 0 ? b : null), L != null && L.nativeViewModel && this._viewModelInstanceValue.viewModelInstance((M = L == null ? void 0 : L.nativeViewModel) !== null && M !== void 0 ? M : null);
                },
                enumerable: !1,
                configurable: !0
              }), i.prototype.internalHandleCallback = function(l) {
                l();
              }, i;
            })(Ye)
          ), Lt = function(g) {
            return te(void 0, void 0, void 0, function() {
              var i, l, b;
              return N(this, function(M) {
                switch (M.label) {
                  case 0:
                    return i = new Request(g), [4, fetch(i)];
                  case 1:
                    if (l = M.sent(), !l.ok)
                      throw new Error("Failed to fetch the Rive file: HTTP ".concat(l.status));
                    return [4, l.arrayBuffer()];
                  case 2:
                    return b = M.sent(), [2, b];
                }
              });
            });
          }, mt = function(g) {
            return typeof g == "string" ? [g] : g instanceof Array ? g : [];
          }, xt = {
            EventManager: be,
            TaskQueueManager: Se
          }, Nt = function(g) {
            return te(void 0, void 0, void 0, function() {
              var i, l, b;
              return N(this, function(M) {
                switch (M.label) {
                  case 0:
                    return i = new Promise(function(L) {
                      return ce.RuntimeLoader.getInstance(function($) {
                        $.decodeAudio(g, L, null);
                      });
                    }), [4, i];
                  case 1:
                    return l = M.sent(), b = new oe.AudioWrapper(l), oe.finalizationRegistry.register(b, l), [2, b];
                }
              });
            });
          }, Tt = function(g) {
            return te(void 0, void 0, void 0, function() {
              var i, l, b;
              return N(this, function(M) {
                switch (M.label) {
                  case 0:
                    return i = new Promise(function(L) {
                      return ce.RuntimeLoader.getInstance(function($) {
                        $.decodeImage(g, L, null);
                      });
                    }), [4, i];
                  case 1:
                    return l = M.sent(), b = new oe.ImageWrapper(l), oe.finalizationRegistry.register(b, l), [2, b];
                }
              });
            });
          }, Ot = function(g) {
            return te(void 0, void 0, void 0, function() {
              var i, l, b;
              return N(this, function(M) {
                switch (M.label) {
                  case 0:
                    return i = new Promise(function(L) {
                      return ce.RuntimeLoader.getInstance(function($) {
                        $.decodeFont(g, L, null);
                      });
                    }), [4, i];
                  case 1:
                    return l = M.sent(), b = new oe.FontWrapper(l), oe.finalizationRegistry.register(b, l), [2, b];
                }
              });
            });
          };
        })(), jt;
      })()
    ));
  })(an)), an.exports;
}
var Gt = fr();
const Ge = "https://public.rive.app/community/runtime-files/", vr = [
  // visemes
  { name: "Lion", file: "28789-54540-lion-lip-sync-system.riv", download: Ge + "28789-54540-lion-lip-sync-system.riv", by: "stvfunm", machine: "State Machine 1", kind: "vm-number", path: "visemeId", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], speaking: { kind: "vm-boolean", path: "isSpeaking" }, group: "visemes" },
  { name: "Custom Talking Avatar", file: "21097-39950-custom-talking-avatar-real-time-lip-sync-for-your-app.riv", download: Ge + "21097-39950-custom-talking-avatar-real-time-lip-sync-for-your-app.riv", by: "stvfunm", machine: "State Machine 1", kind: "sm-number", path: "Number 1", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], group: "visemes" },
  { name: "Lip Sync/Visemes (monster)", file: "28687-54254-lip-syncvisemes.riv", download: Ge + "28687-54254-lip-syncvisemes.riv", by: "ElmerVergara", machine: "State Machine 1", kind: "vm-enum", path: "visemes", closed: "idle", shapes: ["B, M, P", "F, V", "Ee", "R", "L", "U", "O", "Th", "C, D, G, K, N, S, T, X, Y, Z", "Ch, J, Sh", "Q, W, Oo", "A, E, I"], speaking: { kind: "vm-boolean", path: "talkPoseBool" }, group: "visemes" },
  { name: "Gargoyle", file: "25582-47749-gargoyle-avatar.riv", download: Ge + "25582-47749-gargoyle-avatar.riv", by: "malchemist", artboard: "MAIN", machine: "SM_Main", kind: "vm-enum", path: "viseme/visemes", closed: "none", shapes: ["mmm", "sss", "neutral", "wh", "ch", "oh", "hey", "ahh"], speaking: { kind: "vm-boolean", path: "viseme/isSpeaking" }, group: "visemes" },
  { name: "Bald woman", file: "24791-46343-lip-syncing-bald-female-character.riv", download: Ge + "24791-46343-lip-syncing-bald-female-character.riv", by: "stvfunm", artboard: "Android Medium - 1", machine: "State Machine 1", kind: "vm-number", path: "MouthNumber", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], group: "visemes" },
  { name: "Talk for video call", file: "26373-49354-talk-for-video-call.riv", download: Ge + "26373-49354-talk-for-video-call.riv", by: "saurs_", machine: "State Machine_call", kind: "sm-number", path: "Lipsync", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], speaking: { kind: "sm-trigger", path: "talk" }, group: "visemes" },
  { name: "Character Talking", file: "27757-52432-character-talking.riv", download: Ge + "27757-52432-character-talking.riv", by: "interactiver", machine: "State Machine_call", kind: "sm-number", path: "Lipsync", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], speaking: { kind: "sm-trigger", path: "talk" }, group: "visemes" },
  { name: "Bone-based coach", file: "20725-39009-bone-based-lipsync-character-animation.riv", download: Ge + "20725-39009-bone-based-lipsync-character-animation.riv", by: "HaiDo", artboard: "Coach model", machine: "State Machine 1", kind: "sm-number", path: "lips sync id", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], group: "visemes" },
  { name: "Dim Sum (face)", file: "28218-53312-dim-sum-talking.riv", download: Ge + "28218-53312-dim-sum-talking.riv", by: "Julia.fer.surrealm", artboard: "FACE", machine: "State Machine 1", kind: "sm-number", path: "Number_mouth", closed: 0, shapes: [3, 4, 5, 6, 7, 8, 1, 2, 9, 10], group: "visemes" },
  { name: "Expression Grid (mouth)", file: "24941-46557-expression-grid.riv", download: Ge + "24941-46557-expression-grid.riv", by: "erdemediz", artboard: "Mouth", machine: "Mouth State", kind: "sm-number", path: "Viseme", closed: 0, shapes: [1, 2, 3, 4, 5, 6, 7, 8, 9], group: "visemes" },
  { name: "Old man", file: "28375-53657-old-man-character-animation-or-rive-interactive-v02.riv", download: Ge + "28375-53657-old-man-character-animation-or-rive-interactive-v02.riv", by: "ar.akash", artboard: "iPhone 16 Pro Max - 1", machine: "State Machine 1", kind: "vm-enum", path: "mouth", closed: "Default", shapes: ["OO", "AAA"], group: "visemes" },
  // open/shut or talk loop
  { name: "Sobo", file: "28761-54484-sobo.riv", download: Ge + "28761-54484-sobo.riv", by: "Patgrivet", artboard: "SOBO-Motion-V02", machine: "State Machine", kind: "vm-number", path: "mouthOpen", closed: 0, shapes: [1], group: "switch" },
  { name: "Cursor-following head", file: "19679-37036-cursor-following-head.riv", download: Ge + "19679-37036-cursor-following-head.riv", by: "info-WP6YK", machine: "State Machine 1", kind: "sm-boolean", path: "mouth", group: "switch" },
  { name: "Voice activation girl", file: "13204-24955-voice-activation-maybe.riv", download: Ge + "13204-24955-voice-activation-maybe.riv", by: "zentrie101", machine: "State Machine 1", kind: "sm-boolean", path: "talk", group: "switch" },
  { name: "Wave, hear and talk (bear)", file: "5628-11215-wave-hear-and-talk.riv", download: Ge + "5628-11215-wave-hear-and-talk.riv", by: "japarj", machine: "State Machine 1", kind: "sm-boolean", path: "Talk", group: "switch" },
  { name: "Female bear", file: "18971-35688-female-wave-hear-and-talk.riv", download: Ge + "18971-35688-female-wave-hear-and-talk.riv", by: "nelsons", machine: "State Machine 1", kind: "sm-boolean", path: "Talk", group: "switch" },
  { name: "Talking bear", file: "23033-43063-talking-bear.riv", download: Ge + "23033-43063-talking-bear.riv", by: "majid.entysquare", machine: "State Machine 1", kind: "sm-boolean", path: "Talk", group: "switch" },
  { name: "Speaking bear", file: "9940-18945-speaking-bear.riv", download: Ge + "9940-18945-speaking-bear.riv", by: "xiaoshayu1001", machine: "State Machine 1", kind: "sm-boolean", path: "Speaking", group: "switch" },
  { name: "Teddy (Login Machine)", file: "6408-12409-speaking.riv", download: Ge + "6408-12409-speaking.riv", by: "develophasan", artboard: "Teddy", machine: "Login Machine", kind: "sm-boolean", path: "isSpeaking", group: "switch" },
  { name: "Bearded face", file: "4532-9211-character-face-animation.riv", download: Ge + "4532-9211-character-face-animation.riv", by: "ak2665622", artboard: "Character ", machine: "State Machine 1", kind: "sm-trigger", path: "speak", group: "switch" },
  { name: "Face speak/mute", file: "8078-15527-face-speakmute.riv", download: Ge + "8078-15527-face-speakmute.riv", by: "krdsabdllh53", artboard: "Character ", machine: "State Machine 1", kind: "sm-trigger", path: "speak", group: "switch" },
  { name: "Floating rig", file: "25311-47232-expressive-floating-character-rig-old-work-share.riv", download: Ge + "25311-47232-expressive-floating-character-rig-old-work-share.riv", by: "kouidero", machine: "State Machine 1", kind: "sm-boolean", path: "isTalking", group: "switch" },
  { name: "Mouth movement (lips)", file: "5023-10162-mouth-movement.riv", download: Ge + "5023-10162-mouth-movement.riv", by: "alexiusnwala", artboard: "Mouth", machine: "Talk", kind: "sm-boolean", path: "talk", group: "switch" },
  { name: "WufWuf", file: "12148-23106-wufwuf.riv", download: Ge + "12148-23106-wufwuf.riv", by: "shabrinashaliha95", machine: "State Machine 1", kind: "sm-boolean", path: "Talking", group: "switch", note: "barely moves" }
];
Gt.RuntimeLoader.setWasmUrl(new URL("./vendor/rive-2.44.2.wasm", import.meta.url).href);
Gt.RuntimeLoader.setWasmFallbackUrl(null);
const pr = (At) => "./rive/" + At, Ht = vr.map((At) => ({ ...At, url: new URL(pr(At.file), import.meta.url).href }));
function gr(At, { initial: sn = 0 } = {}) {
  const Ft = document.createElement("canvas");
  Ft.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
  const vt = document.createElement("select");
  vt.style.cssText = "position:absolute;top:6px;right:8px;z-index:4;font:12px system-ui;border-radius:999px;padding:2px 8px;background:#1f2633;color:#dde;border:1px solid #3a4456", vt.append(Object.assign(document.createElement("option"), { textContent: "Looking in rive/…", value: "", disabled: !0, selected: !0 })), At.append(Ft, vt);
  const Me = { rive: null, ctl: null, speak: null, spec: null, flip: 0, lastShape: null, lastFire: 0, wasSpeaking: !1 };
  let jt = 0, Ce = 0;
  const ce = () => {
    var N;
    const C = Ft.clientWidth, I = Ft.clientHeight;
    if (!C || !I) return;
    const te = window.devicePixelRatio || 1;
    Ft.width = Math.round(C * te), Ft.height = Math.round(I * te);
    try {
      (N = Me.rive) == null || N.resizeDrawingSurfaceToCanvas(te);
    } catch {
    }
  };
  new ResizeObserver(ce).observe(At), ce(), setInterval(() => {
    var Y;
    Ce += (jt - Ce) * (jt > Ce ? 0.8 : 0.4);
    const C = Ce, I = Me.spec;
    if (!I || !Me.ctl) return;
    const te = Math.min(1, C * 1.6), N = te > 0.04, ne = performance.now();
    try {
      if (I.kind.endsWith("number") || I.kind.endsWith("enum")) {
        let F = I.closed;
        if (N && ((Y = I.shapes) != null && Y.length)) {
          Me.flip = (Me.flip + 1) % 3;
          const ie = I.shapes.length;
          let V = Math.min(ie - 1, Math.floor(te * ie));
          Me.flip === 0 && V > 0 && (V -= 1), F = I.shapes[V];
        }
        F !== Me.lastShape && (Me.ctl.value = F, Me.lastShape = F);
      } else I.kind.endsWith("boolean") ? N !== Me.lastShape && (Me.ctl.value = N, Me.lastShape = N) : I.kind.endsWith("trigger") && N && ne - Me.lastFire > 1500 && (Me.ctl.fire(), Me.lastFire = ne);
      Me.speak && (I.speaking.kind.endsWith("boolean") ? Me.speak.value !== N && (Me.speak.value = N) : I.speaking.kind.endsWith("trigger") && N && !Me.wasSpeaking && Me.speak.fire()), Me.wasSpeaking = N;
    } catch (F) {
      console.warn("rive drive", F);
    }
  }, 1e3 / 30);
  const oe = (C) => {
    var N;
    ce();
    try {
      (N = Me.rive) == null || N.cleanup();
    } catch {
    }
    Me.ctl = null, Me.speak = null, Me.spec = C, Me.lastShape = null;
    const I = (ne) => {
      const Y = C.machine, F = Y ? ne.stateMachineInputs(Y) || [] : [], ie = (G) => F.find((le) => le.name === G) || null, V = ne.viewModelInstance || (() => {
        var me, K, X, re, Z, fe, q;
        const G = C.vm && ((me = ne.viewModelByName) == null ? void 0 : me.call(ne, C.vm)) || ((K = ne.defaultViewModel) == null ? void 0 : K.call(ne)) || ((X = ne.viewModelByIndex) == null ? void 0 : X.call(ne, 0)), le = ((re = G == null ? void 0 : G.defaultInstance) == null ? void 0 : re.call(G)) || ((Z = G == null ? void 0 : G.instanceByIndex) == null ? void 0 : Z.call(G, 0)) || ((fe = G == null ? void 0 : G.instance) == null ? void 0 : fe.call(G));
        return le && ((q = ne.bindViewModelInstance) == null || q.call(ne, le)), le;
      })(), T = (G, le) => {
        var K;
        if (!V) return null;
        const me = G.endsWith("number") ? "number" : G.endsWith("enum") ? "enum" : G.endsWith("boolean") ? "boolean" : "trigger";
        try {
          return ((K = V[me]) == null ? void 0 : K.call(V, le)) || null;
        } catch {
          return null;
        }
      }, O = (G, le) => G.startsWith("sm-") ? ie(le) : T(G, le);
      return { ctl: O(C.kind, C.path), speak: C.speaking ? O(C.speaking.kind, C.speaking.path) : null };
    }, te = new Gt.Rive({
      src: C.url,
      canvas: Ft,
      autoplay: !0,
      autoBind: !0,
      artboard: C.artboard || void 0,
      stateMachines: C.machine || void 0,
      layout: new Gt.Layout({ fit: Gt.Fit.Contain, alignment: Gt.Alignment.Center }),
      onLoad: () => {
        ce();
        const ne = I(te);
        Me.ctl = ne.ctl, Me.speak = ne.speak, Me.rive = te;
      }
    });
    Me.rive = te;
  };
  return vt.onchange = () => {
    vt.value !== "" && oe(Ht[+vt.value]);
  }, Promise.all(Ht.map((C) => fetch(C.url, { method: "HEAD" }).then((I) => I.ok, () => !1))).then((C) => {
    const I = Ht.map((N, ne) => ne).filter((N) => C[N]);
    vt.options[0].textContent = I.length ? "Select character" : "No characters in rive/: see README.md", I.length || At.insertAdjacentHTML("beforeend", '<div style="position:absolute;inset:0;display:grid;place-items:center;font:600 16px system-ui;color:#a33">No character: download one, see README.md</div>'), I.forEach((N) => vt.append(Object.assign(document.createElement("option"), { textContent: Ht[N].name, value: String(N), title: Ht[N].by })));
    const te = I.includes(sn) ? sn : I[0];
    te !== void 0 && (vt.value = String(te), oe(Ht[te]));
  }), { level: (C) => {
    jt = C;
  } };
}
export {
  Ht as RIVE_MODELS,
  gr as mountRive
};
