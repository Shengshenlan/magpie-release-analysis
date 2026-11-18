/* Shared chart renderer for the magpie release cards. */
const NS = "http://www.w3.org/2000/svg";
const E = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };

const DATA = {
  days: ["09-23","09-24","09-25","09-26","09-27","09-28","09-29","09-30","10-01","10-02","10-03","10-04","10-05","10-06","10-07","10-08","10-09","10-10","10-11","10-12","10-13","10-14","10-15","10-16","10-17","10-18","10-19","10-20","10-21","10-22","10-23","10-24","10-25","10-26","10-27","10-28","10-29","10-30","10-31","11-01","11-02","11-03","11-04","11-05","11-06","11-07","11-08","11-09","11-10","11-11","11-12","11-13","11-14","11-15","11-16","11-17"],
  rel: [3,41,48,60,67,120,83,115,62,78,104,127,140,24,10,21,21,27,26,15,8,15,19,14,7,5,4,11,13,9,36,96,81,92,121,178,140,164,201,155,106,119,95,77,128,84,57,118,157,146,144,124,116,56,61,9],
  files: [20,12,11.5,8.3,6.7,6.6,10.8,10.6,22.9,16.3,10.5,13.5,9.9,36.4,26.7,35.3,24.7,50.5,37.1,56.7,87.0,80.1,41.8,26.6,73.0,10.4,76.5,36.9,19.0,25.6,10.5,7.0,7.1,7.9,6.9,6.8,7.2,9.6,8.1,8.3,6.6,7.7,7.9,7.4,8.7,6.3,8.4,11.9,12.9,12.4,9.1,9.0,9.0,10.0,7.4,10.6],
  mods: [4.33,3.51,3.52,2.67,2.45,1.98,2.63,2.81,4.47,3.71,2.72,2.63,2.55,6.83,5.30,7.38,5.81,9.07,6.58,7.20,10.75,10.93,7.32,5.71,8.71,2.80,9.50,7.00,5.15,6.56,3.22,2.29,2.19,2.61,2.61,2.32,2.41,2.51,2.31,2.54,2.36,2.55,2.40,2.57,2.57,2.26,2.30,2.64,3.75,3.14,2.51,2.66,2.85,3.20,2.80,3.89]
};
const N = DATA.days.length;

function frame(id, opt) {
  const svg = document.getElementById(id);
  if (!svg) return null;
  const W = 960, H = opt.h, m = { l: 52, r: 16, t: 16, b: 32 };
  const iw = W - m.l - m.r, ih = H - m.t - m.b;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  if (opt.band !== false) {
    const bx = m.l + (13 / N) * iw, bwd = (12 / N) * iw;
    svg.appendChild(E("rect", { x: bx, y: m.t, width: bwd, height: ih, fill: "#fde68a", opacity: .28 }));
    svg.appendChild(E("line", { x1: bx, x2: bx, y1: m.t, y2: m.t + ih, stroke: "#f59e0b", "stroke-width": 1.2, "stroke-dasharray": "3 3", opacity: .7 }));
    svg.appendChild(E("line", { x1: bx + bwd, x2: bx + bwd, y1: m.t, y2: m.t + ih, stroke: "#f59e0b", "stroke-width": 1.2, "stroke-dasharray": "3 3", opacity: .7 }));
  }
  const ymax = opt.ymax, yOf = v => m.t + ih - (v / ymax) * ih;
  for (let i = 0; i <= 4; i++) {
    const y = yOf(ymax * i / 4);
    svg.appendChild(E("line", { x1: m.l, x2: W - m.r, y1: y, y2: y, class: "gridline" }));
    const t = E("text", { x: m.l - 8, y: y + 4, "text-anchor": "end", class: "tick" });
    t.textContent = opt.fmtY ? opt.fmtY(ymax * i / 4) : Math.round(ymax * i / 4);
    svg.appendChild(t);
  }
  for (let i = 0; i < N; i += 7) {
    const t = E("text", { x: m.l + ((i + 0.5) / N) * iw, y: H - 8, "text-anchor": "middle", class: "tick" });
    t.textContent = DATA.days[i];
    svg.appendChild(t);
  }
  return { svg, m, iw, ih, yOf, W, H, xOf: i => m.l + ((i + 0.5) / N) * iw, bw: iw / N };
}

/* ── chart: daily release counts (bars) ── */
function drawBars(id) {
  const f = frame(id, { ymax: 210, h: 250 });
  if (!f) return;
  const bw = f.bw * 0.7;
  DATA.rel.forEach((v, i) => {
    const x = f.xOf(i) - bw / 2, y = f.yOf(v);
    f.svg.appendChild(E("rect", { x, y, width: bw, height: Math.max(f.m.t + f.ih - y, 1), rx: 2,
      fill: (i >= 13 && i <= 24) ? "#fbbf24" : "#93c5fd" }));
  });
  const pi = DATA.rel.indexOf(201);
  const t = E("text", { x: f.xOf(pi), y: f.yOf(201) - 7, "text-anchor": "middle", class: "lbl" });
  t.textContent = "201"; f.svg.appendChild(t);
  const bl = E("text", { x: f.m.l + (19 / N) * f.iw, y: f.m.t + 16, "text-anchor": "middle", class: "lbl" });
  bl.textContent = "规范建设期"; bl.style.fill = "#b45309"; bl.style.fontSize = "12px";
  f.svg.appendChild(bl);
}

/* ── chart: files per release, log scale ── */
function drawFiles(id) {
  const MAX = 100, lg = Math.log10(MAX);
  const f = frame(id, { ymax: lg, h: 300, fmtY: v => Math.round(Math.pow(10, v)) });
  if (!f) return;
  const yl = v => f.m.t + f.ih - (Math.log10(Math.max(v, 1)) / lg) * f.ih;
  let d = "";
  DATA.files.forEach((v, i) => { d += (i ? "L" : "M") + f.xOf(i) + "," + yl(v); });
  f.svg.appendChild(E("path", { d: d + `L${f.xOf(N - 1)},${f.m.t + f.ih}L${f.xOf(0)},${f.m.t + f.ih}Z`, fill: "#fee2e2", opacity: .55 }));
  f.svg.appendChild(E("path", { d, fill: "none", stroke: "#ef4444", "stroke-width": 2.8, "stroke-linejoin": "round" }));
  DATA.files.forEach((v, i) => f.svg.appendChild(E("circle", { cx: f.xOf(i), cy: yl(v), r: 2.6, fill: "#ef4444" })));
  const pi = DATA.files.indexOf(87);
  const t = E("text", { x: f.xOf(pi), y: yl(87) - 12, "text-anchor": "middle", class: "lbl" });
  t.textContent = "87"; f.svg.appendChild(t);
  const xm = f.xOf(30);
  f.svg.appendChild(E("line", { x1: xm, x2: xm, y1: f.m.t, y2: f.m.t + f.ih, stroke: "#0f172a", "stroke-width": 1.5, "stroke-dasharray": "4 4", opacity: .45 }));
  const mt = E("text", { x: xm + 7, y: f.m.t + 16, class: "lbl" });
  mt.textContent = "10-23 起锁定 7~9"; mt.style.fontSize = "12.5px";
  f.svg.appendChild(mt);
}

/* ── chart: modules per release ── */
function drawMods(id) {
  const f = frame(id, { ymax: 12, h: 290 });
  if (!f) return;
  let d = "";
  DATA.mods.forEach((v, i) => { d += (i ? "L" : "M") + f.xOf(i) + "," + f.yOf(v); });
  f.svg.appendChild(E("path", { d: d + `L${f.xOf(N - 1)},${f.m.t + f.ih}L${f.xOf(0)},${f.m.t + f.ih}Z`, fill: "#ede9fe" }));
  f.svg.appendChild(E("path", { d, fill: "none", stroke: "#8b5cf6", "stroke-width": 2.8, "stroke-linejoin": "round" }));
  DATA.mods.forEach((v, i) => f.svg.appendChild(E("circle", { cx: f.xOf(i), cy: f.yOf(v), r: 2.6, fill: "#8b5cf6" })));
  const pi = DATA.mods.indexOf(10.93);
  const t = E("text", { x: f.xOf(pi), y: f.yOf(10.93) - 12, "text-anchor": "middle", class: "lbl" });
  t.textContent = "10.9"; f.svg.appendChild(t);
}

/* ── chart: module frequency bars ── */
function drawModuleBars(id) {
  const svg = document.getElementById(id);
  if (!svg) return;
  const W = 960, H = 340, m = { l: 200, r: 78, t: 10, b: 10 };
  const iw = W - m.l - m.r;
  const rows = [["internal/gui", 2272], ["internal/gateway", 1628], ["docs", 1625],
    ["internal/provider", 1487], ["internal/agent", 779], ["(root)", 537],
    ["site", 442], ["internal/cli", 329], ["internal/library", 323], ["internal/usage", 310]];
  const ymax = 2272, rh = (H - m.t - m.b) / rows.length;
  rows.forEach(([n, v], i) => {
    const y = m.t + i * rh + rh * 0.16, h = rh * 0.66, w = (v / ymax) * iw;
    const isD = n === "docs";
    svg.appendChild(E("rect", { x: m.l, y, width: w, height: h, rx: 3, fill: isD ? "#34d399" : "#bfdbfe" }));
    const ln = E("text", { x: m.l - 12, y: y + h / 2 + 5, "text-anchor": "end", class: "tick" });
    ln.textContent = n; ln.style.fontSize = "17px"; ln.style.fill = isD ? "#059669" : "#475569";
    if (isD) ln.style.fontWeight = "750";
    svg.appendChild(ln);
    const vn = E("text", { x: m.l + w + 10, y: y + h / 2 + 5, class: "tick" });
    vn.textContent = v; vn.style.fontSize = "16px"; vn.style.fill = isD ? "#059669" : "#64748b";
    if (isD) vn.style.fontWeight = "750";
    svg.appendChild(vn);
  });
}
