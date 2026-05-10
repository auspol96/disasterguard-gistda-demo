const scenarios = {
  wildfire: {
    area_id: "NTH-CHIANGMAI-001",
    incident_type: "wildfire_haze",
    hazard_score: 0.82,
    exposure_score: 0.74,
    urgency_score: 0.79,
    confidence: 0.76,
    risk_drivers: ["recent hotspot cluster", "vegetation stress", "low humidity", "wind spread potential", "nearby community exposure"]
  },
  flood: {
    area_id: "NTH-CHIANGRAI-002",
    incident_type: "rapid_flood",
    hazard_score: 0.88,
    exposure_score: 0.81,
    urgency_score: 0.86,
    confidence: 0.73,
    risk_drivers: ["heavy rainfall accumulation", "river proximity", "low-lying terrain", "surface water expansion signal", "nearby road and community exposure"]
  },
  landslide: {
    area_id: "NTH-MAEHONGSON-003",
    incident_type: "landslide",
    hazard_score: 0.68,
    exposure_score: 0.72,
    urgency_score: 0.61,
    confidence: 0.70,
    risk_drivers: ["heavy rainfall accumulation", "steep slope", "soil saturation proxy", "forest cover disturbance", "nearby transport route exposure"]
  }
};

const el = {
  scenario: document.getElementById("scenario"),
  scoreBtn: document.getElementById("scoreBtn"),
  priorityScore: document.getElementById("priorityScore"),
  severity: document.getElementById("severity"),
  recommendedAction: document.getElementById("recommendedAction"),
  areaId: document.getElementById("areaId"),
  incidentType: document.getElementById("incidentType"),
  operatorSummary: document.getElementById("operatorSummary"),
  riskDrivers: document.getElementById("riskDrivers")
};

function renderResult(data) {
  el.priorityScore.textContent = data.priority_score.toFixed(2);
  el.severity.textContent = data.severity;
  el.recommendedAction.textContent = data.recommended_action.replaceAll("_", " ");
  el.areaId.textContent = data.area_id;
  el.incidentType.textContent = data.incident_type.replaceAll("_", " ");
  el.operatorSummary.textContent = data.operator_summary;
  el.riskDrivers.innerHTML = "";
  data.risk_drivers.forEach((driver) => {
    const chip = document.createElement("span");
    chip.className = "driver-chip";
    chip.textContent = driver;
    el.riskDrivers.appendChild(chip);
  });
}

async function scoreSelectedScenario() {
  const payload = scenarios[el.scenario.value];
  el.scoreBtn.disabled = true;
  el.scoreBtn.textContent = "Scoring...";
  try {
    const response = await fetch("/api/incident/score", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    renderResult(await response.json());
  } catch (error) {
    el.operatorSummary.textContent = `Unable to score scenario: ${error.message}`;
  } finally {
    el.scoreBtn.disabled = false;
    el.scoreBtn.textContent = "Score selected scenario";
  }
}

el.scoreBtn.addEventListener("click", scoreSelectedScenario);
scoreSelectedScenario();
