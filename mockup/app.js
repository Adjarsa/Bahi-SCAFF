const INVENTORY_ITEMS = [
  { id: "plateau_3", label: "Plateaux 3 m", defaultStock: 60 },
  { id: "plateau_2", label: "Plateaux 2 m", defaultStock: 34 },
  { id: "plateau_1_5", label: "Plateaux 1.5 m", defaultStock: 18 },
  { id: "plateau_1", label: "Plateaux 1 m", defaultStock: 12 },
  { id: "plateau_0_75", label: "Plateaux 0.75 m", defaultStock: 20 },
  { id: "poteau_2", label: "Poteaux 2 m", defaultStock: 120 },
  { id: "poteau_3", label: "Poteaux 3 m", defaultStock: 20 },
  { id: "moise_3", label: "Moises 3 m", defaultStock: 180 },
  { id: "moise_2", label: "Moises 2 m", defaultStock: 80 },
  { id: "moise_1_5", label: "Moises 1.5 m", defaultStock: 124 },
  { id: "garde_corps", label: "Garde-corps", defaultStock: 140 },
  { id: "diagonale", label: "Diagonales", defaultStock: 90 },
  { id: "verin", label: "Verins de pied", defaultStock: 80 },
  { id: "ancrage", label: "Ancrages", defaultStock: 120 },
  { id: "plinthe", label: "Plinthes", defaultStock: 70 },
  { id: "filet", label: "Filets", defaultStock: 45 },
  { id: "signal", label: "Signalisation nuit", defaultStock: 30 },
];

const TRAME_PRESETS = {
  mixte: [3, 2, 1.5, 0.75],
  standard: [3, 2, 1.5],
  urbaine: [2, 1.5, 0.75],
  serree: [1.5, 1, 0.75],
};

const ACCESS_CAPACITY = {
  minimal: (width) => 1,
  standard: (width) => Math.max(1, Math.ceil(width / 20)),
  renforce: (width) => Math.max(1, Math.ceil(width / 12)),
};

const state = {
  calibration: null,
  result: null,
  imageObject: null,
  objectUrls: [],
};

const els = {
  projectName: document.getElementById("projectName"),
  facadeWidth: document.getElementById("facadeWidth"),
  facadeHeight: document.getElementById("facadeHeight"),
  levelHeight: document.getElementById("levelHeight"),
  facadeFiles: document.getElementById("facadeFiles"),
  referenceMeters: document.getElementById("referenceMeters"),
  referencePixels: document.getElementById("referencePixels"),
  calibrationResult: document.getElementById("calibrationResult"),
  applyCalibration: document.getElementById("applyCalibration"),
  gallery: document.getElementById("gallery"),
  tramePreset: document.getElementById("tramePreset"),
  scaffoldType: document.getElementById("scaffoldType"),
  accessStrategy: document.getElementById("accessStrategy"),
  addToeBoards: document.getElementById("addToeBoards"),
  addNets: document.getElementById("addNets"),
  nightShift: document.getElementById("nightShift"),
  generatePlan: document.getElementById("generatePlan"),
  computeQuantities: document.getElementById("computeQuantities"),
  r408Checks: document.getElementById("r408Checks"),
  inventoryBody: document.getElementById("inventoryBody"),
  resultBody: document.getElementById("resultBody"),
  materialSummary: document.getElementById("materialSummary"),
  metricSurface: document.getElementById("metricSurface"),
  metricBays: document.getElementById("metricBays"),
  metricLevels: document.getElementById("metricLevels"),
  metricCoverage: document.getElementById("metricCoverage"),
  planCanvas: document.getElementById("planCanvas"),
  downloadCsv: document.getElementById("downloadCsv"),
  exportPng: document.getElementById("exportPng"),
};

const ITEM_BY_ID = Object.fromEntries(INVENTORY_ITEMS.map((item) => [item.id, item]));

function formatNumber(value, decimals = 0) {
  return value.toLocaleString("fr-FR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function setText(node, text) {
  node.textContent = text;
}

function buildInventoryRows() {
  els.inventoryBody.innerHTML = "";
  INVENTORY_ITEMS.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.label}</td>
      <td><input type="number" min="0" step="1" value="${item.defaultStock}" data-item-id="${item.id}" /></td>
    `;
    els.inventoryBody.appendChild(row);
  });
}

function getInventoryStock() {
  const values = {};
  els.inventoryBody.querySelectorAll("input[data-item-id]").forEach((input) => {
    const itemId = input.getAttribute("data-item-id");
    values[itemId] = Math.max(0, Number(input.value) || 0);
  });
  return values;
}

function revokeObjectUrls() {
  state.objectUrls.forEach((url) => URL.revokeObjectURL(url));
  state.objectUrls = [];
}

function onFilesSelected(event) {
  revokeObjectUrls();
  els.gallery.innerHTML = "";

  const files = Array.from(event.target.files || []);
  if (files.length === 0) {
    state.imageObject = null;
    drawPlan();
    return;
  }

  let firstImageUrl = null;

  files.forEach((file) => {
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      state.objectUrls.push(url);
      const thumb = document.createElement("img");
      thumb.src = url;
      thumb.alt = file.name;
      thumb.className = "thumb";
      els.gallery.appendChild(thumb);
      if (!firstImageUrl) {
        firstImageUrl = url;
      }
      return;
    }

    const badge = document.createElement("span");
    badge.className = "hint";
    badge.textContent = `${file.name} (plan)`;
    els.gallery.appendChild(badge);
  });

  if (!firstImageUrl) {
    state.imageObject = null;
    drawPlan();
    return;
  }

  const img = new Image();
  img.onload = () => {
    state.imageObject = img;
    drawPlan();
  };
  img.onerror = () => {
    state.imageObject = null;
    drawPlan();
  };
  img.src = firstImageUrl;
}

function applyCalibration() {
  const meters = Number(els.referenceMeters.value);
  const pixels = Number(els.referencePixels.value);

  if (meters > 0 && pixels > 0) {
    state.calibration = {
      metersPerPixel: meters / pixels,
      meters,
      pixels,
    };
    setText(
      els.calibrationResult,
      `Calibration active: 1 px = ${formatNumber(state.calibration.metersPerPixel, 4)} m`
    );
  } else {
    state.calibration = null;
    setText(els.calibrationResult, "Calibration non appliquee.");
  }

  drawPlan();
}

function decomposeWidth(width, presetKey) {
  const modules = [...new Set(TRAME_PRESETS[presetKey] || TRAME_PRESETS.mixte)].sort(
    (a, b) => b - a
  );
  const factor = 4;
  const moduleUnits = modules.map((module) => Math.round(module * factor));
  const target = Math.max(1, Math.round(width * factor));
  const maxUnits = target + Math.max(...moduleUnits) * 16;

  const inf = Number.POSITIVE_INFINITY;
  const dp = new Array(maxUnits + 1).fill(inf);
  const prev = new Array(maxUnits + 1).fill(null);
  dp[0] = 0;

  for (let unit = 0; unit <= maxUnits; unit += 1) {
    if (!Number.isFinite(dp[unit])) {
      continue;
    }
    moduleUnits.forEach((moduleUnit, index) => {
      const next = unit + moduleUnit;
      if (next > maxUnits) {
        return;
      }
      if (dp[unit] + 1 < dp[next]) {
        dp[next] = dp[unit] + 1;
        prev[next] = { from: unit, module: modules[index] };
      }
    });
  }

  let bestUnit = -1;
  for (let unit = target; unit <= maxUnits; unit += 1) {
    if (!Number.isFinite(dp[unit])) {
      continue;
    }
    if (bestUnit < 0) {
      bestUnit = unit;
      continue;
    }
    const overshoot = unit - target;
    const bestOvershoot = bestUnit - target;
    if (overshoot < bestOvershoot || (overshoot === bestOvershoot && dp[unit] < dp[bestUnit])) {
      bestUnit = unit;
    }
  }

  if (bestUnit < 0) {
    const fallback = modules[modules.length - 1];
    return {
      sequence: [fallback],
      counts: { [fallback]: 1 },
      coveredWidth: fallback,
      totalBays: 1,
    };
  }

  const sequence = [];
  let cursor = bestUnit;
  while (cursor > 0) {
    const step = prev[cursor];
    if (!step) {
      break;
    }
    sequence.push(step.module);
    cursor = step.from;
  }

  sequence.reverse();
  sequence.sort((a, b) => b - a);

  const counts = {};
  modules.forEach((module) => {
    counts[module] = 0;
  });
  sequence.forEach((module) => {
    counts[module] = (counts[module] || 0) + 1;
  });

  return {
    sequence,
    counts,
    coveredWidth: bestUnit / factor,
    totalBays: sequence.length,
  };
}

function addQuantity(quantities, key, value) {
  quantities[key] = (quantities[key] || 0) + value;
}

function buildPlanResult() {
  const width = Number(els.facadeWidth.value);
  const height = Number(els.facadeHeight.value);
  const levelHeight = Number(els.levelHeight.value);

  if (width <= 0 || height <= 0 || levelHeight <= 0) {
    return { error: "Veuillez saisir largeur, hauteur et hauteur niveau valides." };
  }

  const trame = decomposeWidth(width, els.tramePreset.value);
  const levels = Math.max(1, Math.ceil(height / levelHeight));
  const verticalLines = trame.totalBays + 1;
  const quantities = {};

  const moduleToDeck = {
    3: "plateau_3",
    2: "plateau_2",
    1.5: "plateau_1_5",
    1: "plateau_1",
    0.75: "plateau_0_75",
  };
  const moduleToMoise = {
    3: "moise_3",
    2: "moise_2",
    1.5: "moise_1_5",
  };

  Object.entries(trame.counts).forEach(([moduleStr, count]) => {
    if (!count) {
      return;
    }
    const module = Number(moduleStr);
    const deckKey = moduleToDeck[module];
    if (deckKey) {
      addQuantity(quantities, deckKey, count * levels);
    }
    const moiseKey = moduleToMoise[module];
    if (moiseKey) {
      addQuantity(quantities, moiseKey, count * (levels + 1) * 2);
    }
  });

  const postTotal = verticalLines * levels;
  const ratioPoteau3 = levelHeight > 2.2 ? 0.32 : 0.16;
  const poteau3 = Math.ceil(postTotal * ratioPoteau3);
  const poteau2 = Math.max(0, postTotal - poteau3);

  quantities.poteau_2 = poteau2;
  quantities.poteau_3 = poteau3;
  quantities.garde_corps = trame.totalBays * levels * 2;
  quantities.diagonale = Math.ceil(trame.totalBays / 3) * Math.max(1, levels - 1);
  quantities.verin = verticalLines;
  quantities.ancrage = Math.ceil(trame.coveredWidth / 4) * Math.ceil(height / 4);

  if (els.addToeBoards.checked) {
    quantities.plinthe = trame.totalBays * Math.max(1, levels - 1);
  }
  if (els.addNets.checked) {
    quantities.filet = Math.ceil((trame.coveredWidth * height) / 10);
  }
  if (els.nightShift.checked) {
    quantities.signal = Math.ceil(trame.coveredWidth / 6);
  }

  const maxBay = trame.sequence.length ? Math.max(...trame.sequence) : 0;
  const accessRequired = Math.max(1, Math.ceil(trame.coveredWidth / 20));
  const accessPlanned = ACCESS_CAPACITY[els.accessStrategy.value](trame.coveredWidth);
  const anchorArea = (trame.coveredWidth * height) / Math.max(1, quantities.ancrage);

  const checks = [
    {
      label: "Travees inferieures ou egales a 3 m",
      status: maxBay <= 3 ? "ok" : "bad",
      detail: `max ${formatNumber(maxBay, 2)} m`,
    },
    {
      label: "Ancrages <= 24 m2 par point",
      status: anchorArea <= 24 ? "ok" : "bad",
      detail: `${formatNumber(anchorArea, 2)} m2/point`,
    },
    {
      label: "Acces verticaux suffisants",
      status: accessPlanned >= accessRequired ? "ok" : "warn",
      detail: `${accessPlanned} prevus / ${accessRequired} requis`,
    },
    {
      label: "Protection plinthe active",
      status: els.addToeBoards.checked ? "ok" : "warn",
      detail: els.addToeBoards.checked ? "activee" : "desactivee",
    },
    {
      label: "Protection filet active",
      status: els.addNets.checked ? "ok" : "warn",
      detail: els.addNets.checked ? "activee" : "desactivee",
    },
  ];

  if (height > 24 && els.scaffoldType.value !== "renforce") {
    checks.push({
      label: "Facade haute: mode renforce recommande",
      status: "warn",
      detail: "hauteur > 24 m",
    });
  } else {
    checks.push({
      label: "Type echafaudage coherent avec hauteur",
      status: "ok",
      detail: els.scaffoldType.value,
    });
  }

  return {
    width,
    height,
    levelHeight,
    levels,
    trame,
    quantities,
    checks,
    accessRequired,
    accessPlanned,
  };
}

function renderChecks(checks) {
  els.r408Checks.innerHTML = "";
  checks.forEach((check) => {
    const li = document.createElement("li");
    const statusLabel = check.status === "ok" ? "OK" : check.status === "warn" ? "A verifier" : "Critique";
    li.innerHTML = `
      <div>
        <strong>${check.label}</strong>
        <div class="hint">${check.detail}</div>
      </div>
      <span class="badge ${check.status}">${statusLabel}</span>
    `;
    els.r408Checks.appendChild(li);
  });
}

function renderSummary(result) {
  const entries = Object.entries(result.quantities)
    .filter(([, qty]) => qty > 0)
    .sort((a, b) => b[1] - a[1]);
  els.materialSummary.innerHTML = "";

  if (entries.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Aucune quantite calculee.";
    els.materialSummary.appendChild(li);
    return;
  }

  entries.forEach(([id, qty]) => {
    const li = document.createElement("li");
    const label = ITEM_BY_ID[id] ? ITEM_BY_ID[id].label : id;
    li.textContent = `${formatNumber(Math.ceil(qty))} ${label}`;
    els.materialSummary.appendChild(li);
  });
}

function renderMetrics(result) {
  setText(els.metricSurface, `${formatNumber(result.width * result.height, 1)} m2`);
  setText(els.metricBays, `${result.trame.totalBays} (${formatNumber(result.trame.coveredWidth, 2)} m)`);
  setText(els.metricLevels, `${result.levels}`);
}

function renderQuantitiesTable(result) {
  const stock = getInventoryStock();
  els.resultBody.innerHTML = "";
  let totalNeed = 0;
  let totalCovered = 0;

  INVENTORY_ITEMS.forEach((item) => {
    const need = Math.ceil(result.quantities[item.id] || 0);
    const currentStock = Math.ceil(stock[item.id] || 0);
    const toOrder = Math.max(0, need - currentStock);
    totalNeed += need;
    totalCovered += Math.min(need, currentStock);

    if (need === 0 && currentStock === 0) {
      return;
    }

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.label}</td>
      <td>${formatNumber(need)}</td>
      <td>${formatNumber(currentStock)}</td>
      <td>${formatNumber(toOrder)}</td>
    `;
    els.resultBody.appendChild(row);
  });

  const coverage = totalNeed > 0 ? (totalCovered / totalNeed) * 100 : 100;
  setText(els.metricCoverage, `${formatNumber(coverage, 1)} %`);
}

function drawDimensionLine(ctx, x1, y1, x2, y2, label) {
  ctx.strokeStyle = "#f5f9ff";
  ctx.fillStyle = "#f5f9ff";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();

  const angle = Math.atan2(y2 - y1, x2 - x1);
  const arrowSize = 7;
  [[x1, y1, angle + Math.PI], [x2, y2, angle]].forEach(([x, y, baseAngle]) => {
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(
      x + Math.cos(baseAngle - 0.4) * arrowSize,
      y + Math.sin(baseAngle - 0.4) * arrowSize
    );
    ctx.lineTo(
      x + Math.cos(baseAngle + 0.4) * arrowSize,
      y + Math.sin(baseAngle + 0.4) * arrowSize
    );
    ctx.closePath();
    ctx.fill();
  });

  const textX = (x1 + x2) / 2;
  const textY = (y1 + y2) / 2 - 10;
  ctx.font = "12px Inter, sans-serif";
  ctx.fillText(label, textX - ctx.measureText(label).width / 2, textY);
}

function drawPlan() {
  const canvas = els.planCanvas;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, "#1f2b44");
  gradient.addColorStop(1, "#0d1424");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  if (state.imageObject) {
    const imageRatio = state.imageObject.width / state.imageObject.height;
    const canvasRatio = width / height;
    let drawWidth = width;
    let drawHeight = height;
    if (imageRatio > canvasRatio) {
      drawHeight = width / imageRatio;
    } else {
      drawWidth = height * imageRatio;
    }
    const dx = (width - drawWidth) / 2;
    const dy = (height - drawHeight) / 2;
    ctx.globalAlpha = 0.58;
    ctx.drawImage(state.imageObject, dx, dy, drawWidth, drawHeight);
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(10, 16, 27, 0.35)";
    ctx.fillRect(dx, dy, drawWidth, drawHeight);
  }

  if (!state.result) {
    ctx.fillStyle = "#f7fbff";
    ctx.font = "600 20px Inter, sans-serif";
    const title = "Apercu implantation facade";
    ctx.fillText(title, width / 2 - ctx.measureText(title).width / 2, height / 2 - 12);
    ctx.font = "14px Inter, sans-serif";
    const text = "Cliquez sur Generer implantation pour dessiner le plan cote.";
    ctx.fillText(text, width / 2 - ctx.measureText(text).width / 2, height / 2 + 16);
    return;
  }

  const result = state.result;
  const marginX = 90;
  const marginY = 85;
  const maxDrawW = width - marginX * 2;
  const maxDrawH = height - marginY * 2;
  const pxPerMeter = Math.min(maxDrawW / result.trame.coveredWidth, maxDrawH / result.height);
  const realDrawW = result.trame.coveredWidth * pxPerMeter;
  const realDrawH = result.height * pxPerMeter;
  const originX = (width - realDrawW) / 2;
  const originY = (height - realDrawH) / 2 + 10;
  const levelPx = realDrawH / result.levels;

  ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
  ctx.lineWidth = 1.4;
  ctx.strokeRect(originX, originY, realDrawW, realDrawH);

  let cursorX = originX;
  result.trame.sequence.forEach((bay, bayIndex) => {
    const bayW = bay * pxPerMeter;
    for (let levelIndex = 0; levelIndex < result.levels; levelIndex += 1) {
      const y = originY + realDrawH - (levelIndex + 1) * levelPx;
      ctx.fillStyle =
        (bayIndex + levelIndex) % 2 === 0 ? "rgba(84, 173, 255, 0.28)" : "rgba(35, 130, 255, 0.22)";
      ctx.fillRect(cursorX, y, bayW, levelPx);
      ctx.strokeStyle = "rgba(214, 234, 255, 0.62)";
      ctx.strokeRect(cursorX, y, bayW, levelPx);
    }

    ctx.fillStyle = "#f4f9ff";
    const label = `${formatNumber(bay, 2)} m`;
    ctx.font = "11px Inter, sans-serif";
    ctx.fillText(label, cursorX + bayW / 2 - ctx.measureText(label).width / 2, originY + realDrawH + 16);
    cursorX += bayW;
  });

  drawDimensionLine(
    ctx,
    originX,
    originY - 26,
    originX + realDrawW,
    originY - 26,
    `${formatNumber(result.trame.coveredWidth, 2)} m`
  );
  drawDimensionLine(
    ctx,
    originX - 30,
    originY + realDrawH,
    originX - 30,
    originY,
    `${formatNumber(result.height, 2)} m`
  );

  ctx.fillStyle = "#f4f9ff";
  ctx.font = "600 12px Inter, sans-serif";
  ctx.fillText(
    `Niveaux: ${result.levels} | Type: ${els.scaffoldType.value}`,
    originX,
    originY - 44
  );
  if (state.calibration) {
    ctx.font = "12px Inter, sans-serif";
    ctx.fillText(
      `Calibration: 1 px = ${formatNumber(state.calibration.metersPerPixel, 4)} m`,
      originX,
      originY + realDrawH + 34
    );
  }
}

function computePlan(renderTable) {
  const result = buildPlanResult();
  if (result.error) {
    window.alert(result.error);
    return;
  }

  state.result = result;
  renderChecks(result.checks);
  renderMetrics(result);
  renderSummary(result);
  drawPlan();

  if (renderTable) {
    renderQuantitiesTable(result);
  }
}

function sanitizeFileName(value) {
  return (value || "chantier")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 50);
}

function downloadCsv() {
  if (!state.result) {
    computePlan(true);
    if (!state.result) {
      return;
    }
  } else {
    renderQuantitiesTable(state.result);
  }

  const stock = getInventoryStock();
  const rows = [["Element", "Besoin", "Stock", "A commander"]];
  INVENTORY_ITEMS.forEach((item) => {
    const need = Math.ceil(state.result.quantities[item.id] || 0);
    const currentStock = Math.ceil(stock[item.id] || 0);
    const toOrder = Math.max(0, need - currentStock);
    if (need === 0 && currentStock === 0) {
      return;
    }
    rows.push([item.label, `${need}`, `${currentStock}`, `${toOrder}`]);
  });

  const csv = rows.map((row) => row.join(";")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const project = sanitizeFileName(els.projectName.value);
  link.download = `quantitatif-${project}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function exportPng() {
  if (!state.result) {
    computePlan(false);
    if (!state.result) {
      return;
    }
  }
  const url = els.planCanvas.toDataURL("image/png");
  const link = document.createElement("a");
  link.href = url;
  const project = sanitizeFileName(els.projectName.value);
  link.download = `plan-facade-${project}.png`;
  link.click();
}

function initEvents() {
  els.facadeFiles.addEventListener("change", onFilesSelected);
  els.applyCalibration.addEventListener("click", applyCalibration);
  els.generatePlan.addEventListener("click", () => computePlan(false));
  els.computeQuantities.addEventListener("click", () => computePlan(true));
  els.downloadCsv.addEventListener("click", downloadCsv);
  els.exportPng.addEventListener("click", exportPng);
  els.inventoryBody.addEventListener("input", () => {
    if (state.result) {
      renderQuantitiesTable(state.result);
    }
  });
}

function bootstrap() {
  buildInventoryRows();
  initEvents();
  drawPlan();
  computePlan(true);
  applyCalibration();
}

bootstrap();
