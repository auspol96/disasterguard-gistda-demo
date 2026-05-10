const scenarios = {
  wildfire: {label: "Chiang Mai wildfire/haze", area_id: "NTH-CHIANGMAI-001", incident_type: "wildfire_haze", hazard_score: 0.82, exposure_score: 0.74, urgency_score: 0.79, confidence: 0.76, risk_drivers: ["recent hotspot cluster", "vegetation stress", "low humidity", "wind spread potential", "nearby community exposure"]},
  flood: {label: "Chiang Rai rapid flood", area_id: "NTH-CHIANGRAI-002", incident_type: "rapid_flood", hazard_score: 0.88, exposure_score: 0.81, urgency_score: 0.86, confidence: 0.73, risk_drivers: ["heavy rainfall accumulation", "river proximity", "low-lying terrain", "surface water expansion signal", "nearby road and community exposure"]},
  landslide: {label: "Mae Hong Son landslide", area_id: "NTH-MAEHONGSON-003", incident_type: "landslide", hazard_score: 0.68, exposure_score: 0.72, urgency_score: 0.61, confidence: 0.70, risk_drivers: ["heavy rainfall accumulation", "steep slope", "soil saturation proxy", "forest cover disturbance", "nearby transport route exposure"]}
};

const elements = {
  scenario: document.getElementById("scenario"),
  scoreBtn: document.getElementById("scoreBtn"),
  priorityScore: document.getElementById("priorityScore"),
  severity: document.getElementById("severity"),
  recommendedAction: document.getElementById("recommendedAction"),
  areaId: document.getElementById("areaId"),
  incidentType: document.getElementById("incidentType"),
  operatorSummary: document.getElementById("operatorSummary"),
  riskDrivers: document.getElementById("riskDrivers"),
  activeMapLabel: document.getElementById("activeMapLabel"),
  markers: document.querySelectorAll(".incident-marker")
};

function updateActiveMarker(scenarioKey, severity) {
  elements.markers.forEach((marker) => {
    const isActive = marker.dataset.scenario === scenarioKey;
    marker.classList.toggle("active", isActive);
    marker.setAttribute("aria-pressed", String(isActive));
  });
  elements.activeMapLabel.textContent = `${scenarios[scenarioKey].label} · ${severity}`;
  elements.activeMapLabel.dataset.severity = severity.toLowerCase();
}

function renderResult(data) {
  const scenarioKey = elements.scenario.value;
  elements.priorityScore.textContent = data.priority_score.toFixed(2);
  elements.severity.textContent = data.severity;
  elements.recommendedAction.textContent = data.recommended_action.replaceAll("_", " ");
  elements.areaId.textContent = data.area_id;
  elements.incidentType.textContent = data.incident_type.replaceAll("_", " ");
  elements.operatorSummary.textContent = data.operator_summary;
  elements.riskDrivers.innerHTML = "";
  data.risk_drivers.forEach((driver) => {
    const chip = document.createElement("span");
    chip.className = "driver-chip";
    chip.textContent = driver;
    elements.riskDrivers.appendChild(chip);
  });
  updateActiveMarker(scenarioKey, data.severity);
}

async function scoreSelectedScenario() {
  const payload = scenarios[elements.scenario.value];
  elements.scoreBtn.disabled = true;
  elements.scoreBtn.textContent = "Scoring...";
  try {
    const response = await fetch("/api/incident/score", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    renderResult(await response.json());
  } catch (error) {
    elements.operatorSummary.textContent = `Unable to score scenario: ${error.message}`;
  } finally {
    elements.scoreBtn.disabled = false;
    elements.scoreBtn.textContent = "Score selected scenario";
  }
}

elements.scoreBtn.addEventListener("click", scoreSelectedScenario);
elements.scenario.addEventListener("change", scoreSelectedScenario);
elements.markers.forEach((marker) => marker.addEventListener("click", () => {
  elements.scenario.value = marker.dataset.scenario;
  scoreSelectedScenario();
}));
scoreSelectedScenario();
