document.getElementById("btnMenu")?.addEventListener("click", () => {
  document.querySelector(".sidebar")?.classList.toggle("open");
});

function toggleAutre(select, wrap, value) {
  if (!select || !wrap) return;
  wrap.style.display = select.value === value ? "" : "none";
}

function initAutreFields() {
  const typeSel = document.getElementById("id_type");
  toggleAutre(typeSel, document.querySelector(".js-type-autre"), "autre");
  typeSel?.addEventListener("change", () =>
    toggleAutre(typeSel, document.querySelector(".js-type-autre"), "autre")
  );
  const lieuSel = document.getElementById("id_lieu");
  toggleAutre(lieuSel, document.querySelector(".js-lieu-autre"), "autre");
  lieuSel?.addEventListener("change", () =>
    toggleAutre(lieuSel, document.querySelector(".js-lieu-autre"), "autre")
  );
  document.querySelectorAll(".js-volet").forEach((sel) => {
    const wrap = sel.closest(".row, .point-block, form")?.querySelector(".js-volet-wrap");
    toggleAutre(sel, wrap, "autre");
    sel.addEventListener("change", () => toggleAutre(sel, wrap, "autre"));
  });
}
initAutreFields();

const PALETTE = ["#0b2545", "#1d4e89", "#c9a227", "#c0392b", "#1e7a46", "#3d7ea6", "#6c7a89"];

function drawPie(id, labels, data) {
  const c = document.getElementById(id);
  if (!c) return;
  const ctx = c.getContext("2d");
  const total = data.reduce((a, b) => a + b, 0) || 1;
  const w = c.width, h = c.height, r = Math.min(w, h) / 2 - 10;
  let a0 = -Math.PI / 2;
  ctx.clearRect(0, 0, w, h);
  data.forEach((v, i) => {
    const a1 = a0 + (v / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, h / 2);
    ctx.arc(w / 2, h / 2, r, a0, a1);
    ctx.closePath();
    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.fill();
    a0 = a1;
  });
  ctx.fillStyle = "#1a2332";
  ctx.font = "12px Segoe UI, sans-serif";
  labels.forEach((lab, i) => {
    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.fillRect(8, 8 + i * 16, 10, 10);
    ctx.fillStyle = "#1a2332";
    ctx.fillText(`${lab} (${data[i] || 0})`, 22, 17 + i * 16);
  });
}

function drawBars(id, labels, data) {
  const c = document.getElementById(id);
  if (!c) return;
  const ctx = c.getContext("2d");
  const w = c.width, h = c.height, max = Math.max(1, ...data);
  ctx.clearRect(0, 0, w, h);
  const barW = Math.max(12, (w - 40) / Math.max(labels.length, 1) - 8);
  labels.forEach((lab, i) => {
    const bh = (data[i] / max) * (h - 40);
    const x = 20 + i * (barW + 8);
    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.fillRect(x, h - 20 - bh, barW, bh);
    ctx.fillStyle = "#1a2332";
    ctx.font = "11px Segoe UI, sans-serif";
    ctx.fillText(String(lab), x, h - 6);
  });
}
