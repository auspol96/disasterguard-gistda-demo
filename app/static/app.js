const scenarios = {
  wildfire: {
    area_id: "NTH-CHIANGMAI-001",
    incident_type: "wildfire_haze",
    hazard_score: 0.82,
    exposure_score: 0.74,
    urgency_score: 0.79,
    confidence: 0.76,
    risk_drivers: [
      "recent hotspot cluster",
      "vegetation stress",
      "low humidity",
      "wind spread potential",
      "nearby community exposure",
    ],
  },
  flood: {
    area_id: "NTH-CHIANGRAI-014",
    incident_type: "rapid_flood",
    hazard_score: 0.91,
    exposure_score: 0.86,
    urgency_score: 0.92,
    confidence: 0.82,
    risk_drivers: [
      "heavy rainfall accumulation",
      "rapid rainfall intensity increase",
      "river proximity",
      "low-lying terrain",
      "nearby road and bridge exposure",
    ],
  },
  landslide: {
    area_id: "NTH-MAEHONGSON-008",
    incident_type: "landslide",
    hazard_score: 0.68,
    exposure_score: 0.63,
    urgency_score: 0.71,
    confidence: 0.69,
    risk_drivers: [
      "heavy rainfall accumulation",
      "steep slope",
      "soil moisture proxy",
      "land-cover change",
      "nearby transport route exposure",
    ],
  },
};

const elements = {
  serviceStatus: document.querySelector("#serviceStatus"),
  scenarioSelect: document.querySelector("#scenarioSelect"),
  scoreButton: document.querySelector("#scoreButton"),
  priorityScore: document.querySelector("#priorityScore"),
  severity: document.querySelector("#severity"),
  recommendedAction: document.querySelector("#recommendedAction"),
  areaId: document.querySelector("#areaId"),
  incidentType: document.querySelector("#incidentType"),
  operatorSummary: document.querySelector("#operatorSummary"),
  riskDrivers: document.querySelector("#riskDrivers"),
};

function formatLabel(value) {
  return value.replaceAll("_", " ");
}

function setLoading(isLoading) {
  elements.scoreButton.disabled = isLoading;
  elements.scoreButton.textContent = isLoading ? "Scoring..." : "Score selected scenario";
}

function renderResult(result) {
  elements.priorityScore.textContent = result.priority_score.toFixed(2);
  elements.severity.textContent = result.severity;
  elements.severity.dataset.level = result.severity.toLowerCase();
  elements.recommendedAction.textContent = formatLabel(result.recommended_action);
  elements.areaId.textContent = result.area_id;
  elements.incidentType.textContent = formatLabel(result.incident_type);
  elements.operatorSummary.textContent = result.operator_summary;
  elements.riskDrivers.innerHTML = "";

  result.risk_drivers.forEach((driver) => {
    const item = document.createElement("li");
    item.textContent = driver;
    elements.riskDrivers.appendChild(item);
  });
}

async function scoreSelectedScenario() {
  const selectedScenario = scenarios[elements.scenarioSelect.value];
  setLoading(true);

  try {
    const response = await fetch("/api/incident/score", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(selectedScenario),
    });

    if (!response.ok) {
      throw new Error(`Scoring request failed with status ${response.status}`);
    }

    renderResult(await response.json());
  } catch (error) {
    elements.operatorSummary.textContent = error.message;
  } finally {
    setLoading(false);
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    elements.serviceStatus.textContent = data.status === "ok" ? "API online" : "API unavailable";
  } catch {
    elements.serviceStatus.textContent = "API unavailable";
  }
}

elements.scoreButton.addEventListener("click", scoreSelectedScenario);
elements.scenarioSelect.addEventListener("change", scoreSelectedScenario);

checkHealth();
scoreSelectedScenario();
