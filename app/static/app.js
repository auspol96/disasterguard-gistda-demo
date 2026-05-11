const scenarios = {
  wildfire: {
    label: "Chiang Mai wildfire/haze",
    area_id: "NTH-CHIANGMAI-001",
    incident_type: "wildfire_haze",
    hazard_score: 0.82,
    exposure_score: 0.74,
    urgency_score: 0.79,
    confidence: 0.76,
    risk_drivers: ["recent hotspot cluster", "vegetation stress", "low humidity", "wind spread potential", "nearby community exposure"],
  },
  flood: {
    label: "Chiang Rai rapid flood",
    area_id: "NTH-CHIANGRAI-002",
    incident_type: "rapid_flood",
    hazard_score: 0.88,
    exposure_score: 0.81,
    urgency_score: 0.86,
    confidence: 0.73,
    risk_drivers: ["heavy rainfall accumulation", "river proximity", "low-lying terrain", "surface water expansion signal", "nearby road and community exposure"],
  },
  landslide: {
    label: "Mae Hong Son landslide",
    area_id: "NTH-MAEHONGSON-003",
    incident_type: "landslide",
    hazard_score: 0.68,
    exposure_score: 0.72,
    urgency_score: 0.61,
    confidence: 0.70,
    risk_drivers: ["heavy rainfall accumulation", "steep slope", "soil saturation proxy", "forest cover disturbance", "nearby transport route exposure"],
  },
};

const readinessByIncidentType = {
  wildfire_haze: [
    ["Fire Hotspot", "Available now"],
    ["Crop Drought / vegetation stress", "Partner integration"],
    ["Humidity / Temperature / Wind", "Partner integration"],
    ["Community Exposure", "Future calibration"],
    ["Road / Infrastructure Exposure", "Future calibration"],
  ],
  rapid_flood: [
    ["Rainfall", "Partner integration"],
    ["SAR surface water", "Partner integration"],
    ["Terrain / Slope", "Available now"],
    ["Community Exposure", "Future calibration"],
    ["Road / Infrastructure Exposure", "Future calibration"],
  ],
  landslide: [
    ["Rainfall", "Partner integration"],
    ["Terrain / Slope", "Available now"],
    ["Crop Drought / vegetation stress", "Future calibration"],
    ["Community Exposure", "Future calibration"],
    ["Road / Infrastructure Exposure", "Future calibration"],
  ],
};

const elements = {
  scenario: document.getElementById("scenario"),
  priorityScore: document.getElementById("priorityScore"),
  severity: document.getElementById("severity"),
  recommendedAction: document.getElementById("recommendedAction"),
  areaId: document.getElementById("areaId"),
  incidentType: document.getElementById("incidentType"),
  operatorSummary: document.getElementById("operatorSummary"),
  riskDrivers: document.getElementById("riskDrivers"),
  activeMapLabel: document.getElementById("activeMapLabel"),
  markers: document.querySelectorAll(".incident-marker"),
  totalIncidents: document.getElementById("totalIncidents"),
  highIncidents: document.getElementById("highIncidents"),
  mediumIncidents: document.getElementById("mediumIncidents"),
  criticalIncidents: document.getElementById("criticalIncidents"),
  topConcern: document.getElementById("topConcern"),
  priorityQueue: document.getElementById("priorityQueue"),
  queueStatus: document.getElementById("queueStatus"),
  readinessIncident: document.getElementById("readinessIncident"),
  readinessLayers: document.getElementById("readinessLayers"),
  gistdaContextStatus: document.getElementById("gistdaContextStatus"),
  gistdaHotspotCount: document.getElementById("gistdaHotspotCount"),
  gistdaDates: document.getElementById("gistdaDates"),
  gistdaNearestDistance: document.getElementById("gistdaNearestDistance"),
  gistdaProvinces: document.getElementById("gistdaProvinces"),
  gistdaLanduse: document.getElementById("gistdaLanduse"),
};

const queueResults = new Map();

function apiPayload(scenario) {
  const {label, ...payload} = scenario;
  return payload;
}

function formatLabel(value) {
  return value.replaceAll("_", " ");
}

function severityClass(severity) {
  return severity.toLowerCase();
}

async function scoreScenario(scenarioKey) {
  const response = await fetch("/api/incident/score", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(apiPayload(scenarios[scenarioKey])),
  });
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  return response.json();
}

function updateActiveMarker(scenarioKey, severity) {
  const level = severityClass(severity);
  elements.markers.forEach((marker) => {
    const isActive = marker.dataset.scenario === scenarioKey;
    marker.classList.toggle("active", isActive);
    marker.dataset.severity = marker.dataset.scenario === scenarioKey ? level : marker.dataset.severity || "watch";
    marker.setAttribute("aria-pressed", String(isActive));
  });
  elements.activeMapLabel.textContent = `${scenarios[scenarioKey].label} · ${severity}`;
  elements.activeMapLabel.dataset.severity = level;
}

function renderOverview(results) {
  const highCount = results.filter((item) => item.severity === "HIGH").length;
  const mediumCount = results.filter((item) => item.severity === "MEDIUM").length;
  const criticalCount = results.filter((item) => item.severity === "CRITICAL").length;
  const top = results[0];

  elements.totalIncidents.textContent = results.length;
  elements.highIncidents.textContent = highCount;
  elements.mediumIncidents.textContent = mediumCount;
  elements.criticalIncidents.textContent = criticalCount;
  elements.topConcern.textContent = `${top.area_id} · ${formatLabel(top.incident_type)} · ${top.priority_score.toFixed(2)}`;
}

function renderPriorityQueue(results) {
  elements.priorityQueue.innerHTML = "";
  results.forEach((item, index) => {
    const row = document.createElement("tr");
    row.dataset.scenario = item.scenarioKey;
    row.tabIndex = 0;
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${item.area_id}</td>
      <td>${formatLabel(item.incident_type)}</td>
      <td>${item.priority_score.toFixed(2)}</td>
      <td><span class="severity-pill" data-severity="${severityClass(item.severity)}">${item.severity}</span></td>
      <td>${formatLabel(item.recommended_action)}</td>
    `;
    row.addEventListener("click", () => selectScenario(item.scenarioKey));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectScenario(item.scenarioKey);
      }
    });
    elements.priorityQueue.appendChild(row);
  });
}

function renderReadinessPanel(data) {
  const layers = readinessByIncidentType[data.incident_type] || [];
  elements.readinessIncident.textContent = formatLabel(data.incident_type);
  elements.readinessLayers.innerHTML = "";
  layers.forEach(([name, status]) => {
    const layer = document.createElement("article");
    layer.className = "readiness-item";
    layer.innerHTML = `<span>${name}</span><strong>${status}</strong>`;
    elements.readinessLayers.appendChild(layer);
  });
}

function renderGistdaContext(context) {
  const summary = context.summary || {};
  elements.gistdaContextStatus.textContent = context.status || summary.status || "unknown";
  elements.gistdaContextStatus.dataset.status = context.status || summary.status || "unknown";
  elements.gistdaHotspotCount.textContent = summary.hotspot_count ?? "—";
  elements.gistdaDates.textContent = (summary.dates_available || []).join(", ") || "—";
  elements.gistdaNearestDistance.textContent =
    summary.nearest_hotspot_distance_km === null || summary.nearest_hotspot_distance_km === undefined
      ? "—"
      : `${Number(summary.nearest_hotspot_distance_km).toFixed(2)} km`;
  elements.gistdaProvinces.textContent = (summary.provinces_detected || []).join(", ") || "—";
  elements.gistdaLanduse.textContent = (summary.landuse_types || []).join(", ") || "—";
}

async function loadGistdaContext() {
  try {
    const response = await fetch("/live_context/gistda_hotspot_context.json", {cache: "no-store"});
    if (response.status === 404) {
      elements.gistdaContextStatus.textContent = "Not loaded yet";
      elements.gistdaContextStatus.dataset.status = "not_loaded";
      return;
    }
    if (!response.ok) throw new Error(`Context returned ${response.status}`);
    renderGistdaContext(await response.json());
  } catch (error) {
    elements.gistdaContextStatus.textContent = "error";
    elements.gistdaContextStatus.dataset.status = "error";
  }
}

function setActiveQueueRow(scenarioKey) {
  elements.priorityQueue.querySelectorAll("tr").forEach((row) => {
    row.classList.toggle("active", row.dataset.scenario === scenarioKey);
  });
}

function renderDetail(data, scenarioKey) {
  elements.priorityScore.textContent = data.priority_score.toFixed(2);
  elements.severity.textContent = data.severity;
  elements.severity.dataset.level = severityClass(data.severity);
  elements.recommendedAction.textContent = formatLabel(data.recommended_action);
  elements.areaId.textContent = data.area_id;
  elements.incidentType.textContent = formatLabel(data.incident_type);
  elements.operatorSummary.textContent = data.operator_summary;
  elements.riskDrivers.innerHTML = "";
  data.risk_drivers.forEach((driver) => {
    const chip = document.createElement("span");
    chip.className = "driver-chip";
    chip.textContent = driver;
    elements.riskDrivers.appendChild(chip);
  });
  renderReadinessPanel(data);
  updateActiveMarker(scenarioKey, data.severity);
  setActiveQueueRow(scenarioKey);
}

function selectScenario(scenarioKey) {
  const data = queueResults.get(scenarioKey);
  if (!data) return;
  elements.scenario.value = scenarioKey;
  renderDetail(data, scenarioKey);
}

async function buildPilotDemo() {
  try {
    const results = await Promise.all(Object.keys(scenarios).map(async (scenarioKey) => {
      const data = await scoreScenario(scenarioKey);
      return {...data, scenarioKey};
    }));
    results.sort((a, b) => b.priority_score - a.priority_score);
    results.forEach((item) => {
      queueResults.set(item.scenarioKey, item);
      const marker = document.querySelector(`[data-scenario="${item.scenarioKey}"]`);
      if (marker) marker.dataset.severity = severityClass(item.severity);
    });
    renderOverview(results);
    renderPriorityQueue(results);
    elements.queueStatus.textContent = `${results.length} incidents ranked`;
    selectScenario(results[0].scenarioKey);
  } catch (error) {
    elements.queueStatus.textContent = "Queue unavailable";
    elements.operatorSummary.textContent = `Unable to build Pilot Demo v1 queue: ${error.message}`;
    elements.priorityQueue.innerHTML = `<tr><td colspan="6">Unable to build queue: ${error.message}</td></tr>`;
  }
}

elements.scenario.addEventListener("change", () => selectScenario(elements.scenario.value));
elements.markers.forEach((marker) => marker.addEventListener("click", () => selectScenario(marker.dataset.scenario)));

buildPilotDemo();
loadGistdaContext();
