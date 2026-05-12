const fallbackScorePayload = {
  area_id: "NTH-CHIANGMAI-GISTDA-001",
  incident_type: "wildfire_haze",
  hazard_score: 0.51,
  exposure_score: 0.75,
  urgency_score: 0.73,
  confidence: 0.62,
  risk_drivers: [
    "GISTDA hotspot API context",
    "1 hotspot record(s) returned",
    "landuse: ป่าอนุรักษ์",
    "nearest hotspot distance 5.83 km",
  ],
};

const elements = {
  refreshButton: document.getElementById("refreshButton"),
  refreshMessage: document.getElementById("refreshMessage"),
  connectorBadge: document.getElementById("connectorBadge"),
  connectorStatus: document.getElementById("connectorStatus"),
  mapCoordinate: document.getElementById("mapCoordinate"),
  lastUpdated: document.getElementById("lastUpdated"),
  hotspotCount: document.getElementById("hotspotCount"),
  locality: document.getElementById("locality"),
  landuse: document.getElementById("landuse"),
  nearestDistance: document.getElementById("nearestDistance"),
  satellitesChecked: document.getElementById("satellitesChecked"),
  datesAvailable: document.getElementById("datesAvailable"),
  severityBadge: document.getElementById("severityBadge"),
  priorityScore: document.getElementById("priorityScore"),
  recommendedAction: document.getElementById("recommendedAction"),
  operatorSummary: document.getElementById("operatorSummary"),
  riskDrivers: document.getElementById("riskDrivers"),
  rankingRefreshButton: document.getElementById("rankingRefreshButton"),
  rankingMessage: document.getElementById("rankingMessage"),
  rankingTableBody: document.getElementById("rankingTableBody"),
  patternAreaName: document.getElementById("patternAreaName"),
  patternCodes: document.getElementById("patternCodes"),
  patternExplanation: document.getElementById("patternExplanation"),
  patternFocus: document.getElementById("patternFocus"),
};

let map;
let hotspotMarker;

function formatJoined(values) {
  return Array.isArray(values) && values.length ? values.join(", ") : "--";
}

function formatDistance(distance) {
  return distance === null || distance === undefined ? "--" : `${Number(distance).toFixed(5)} km`;
}

function formatAction(value) {
  return value ? value.replaceAll("_", " ") : "--";
}

function clampScore(value) {
  return Math.max(0, Math.min(1, Number(value.toFixed(2))));
}

function severityClass(value) {
  return value ? value.toLowerCase() : "unknown";
}

function setConnectorStatus(status) {
  const resolvedStatus = status || "unknown";
  elements.connectorStatus.textContent = resolvedStatus.replaceAll("_", " ");
  elements.connectorStatus.dataset.status = resolvedStatus;
  elements.connectorBadge.hidden = resolvedStatus !== "ok";
}

function sampleRecordFromContext(context) {
  return context?.summary?.raw_limited_sample?.[0] || {};
}

function positionFromContext(context) {
  const sample = sampleRecordFromContext(context);
  const latitude = Number(sample.lat ?? context?.request?.lat);
  const longitude = Number(sample.lon ?? context?.request?.lon);
  return Number.isFinite(latitude) && Number.isFinite(longitude)
    ? { latitude, longitude }
    : null;
}

function formatPopupValue(value) {
  return value === null || value === undefined || value === "" ? "--" : value;
}

function escapeHtml(value) {
  return String(formatPopupValue(value))
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function buildHotspotPopup(sample, summary) {
  const detailRows = [
    ["Province", sample.province],
    ["District", sample.district],
    ["Subdistrict", sample.subdistrict],
    ["Village", sample.village],
    ["Landuse", sample.landuse || summary.landuse_types?.[0]],
    ["Date", sample.date || summary.dates_available?.[0]],
    ["Satellite", sample.satellite],
    ["Distance", sample.distance === undefined ? null : `${Number(sample.distance).toFixed(5)} km`],
  ];

  return `
    <div class="hotspot-popup">
      <strong>Forest hotspot context</strong>
      ${detailRows.map(([label, value]) => `<span><b>${escapeHtml(label)}</b>${escapeHtml(value)}</span>`).join("")}
    </div>
  `;
}

function ensureMap(position, sample, summary) {
  if (!position || typeof L === "undefined") return;

  if (!map) {
    map = L.map("hotspotMap", {
      zoomControl: true,
      scrollWheelZoom: false,
    }).setView([position.latitude, position.longitude], 11);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);
  } else {
    map.setView([position.latitude, position.longitude], 11);
  }

  if (hotspotMarker) {
    hotspotMarker.remove();
  }

  hotspotMarker = L.marker([position.latitude, position.longitude])
    .addTo(map)
    .bindPopup(buildHotspotPopup(sample, summary))
    .openPopup();

  elements.mapCoordinate.textContent = `${position.latitude.toFixed(5)}, ${position.longitude.toFixed(5)}`;
}

function renderContext(context) {
  const summary = context.summary || {};
  const sample = sampleRecordFromContext(context);
  const localityParts = [sample.province, sample.district, sample.subdistrict, sample.village].filter(Boolean);

  setConnectorStatus(context.status || summary.status);
  elements.hotspotCount.textContent = summary.hotspot_count ?? "--";
  elements.locality.textContent = localityParts.length ? localityParts.join(" / ") : "--";
  elements.landuse.textContent = formatJoined(summary.landuse_types);
  elements.nearestDistance.textContent = formatDistance(summary.nearest_hotspot_distance_km);
  elements.satellitesChecked.textContent = formatJoined(summary.source_satellites_checked);
  elements.datesAvailable.textContent = formatJoined(summary.dates_available);
  ensureMap(positionFromContext(context), sample, summary);
}

function buildScorePayloadFromContext(context) {
  const summary = context.summary || {};
  const hotspotCount = Number(summary.hotspot_count || 0);
  const rawNearestDistance = summary.nearest_hotspot_distance_km;
  const hasNearestDistance = rawNearestDistance !== null && rawNearestDistance !== undefined;
  const nearestDistance = hasNearestDistance ? Number(rawNearestDistance) : null;
  const landuseTypes = summary.landuse_types || [];
  const rawSample = summary.raw_limited_sample || [];
  const maxFrequency = Math.max(0, ...rawSample.map((item) => Number(item.frequency || 0)));

  if ((context.status || summary.status) !== "ok") {
    return fallbackScorePayload;
  }

  const confirmedClearRadius = hotspotCount === 0 && !landuseTypes.length && !hasNearestDistance;
  if (confirmedClearRadius) {
    return {
      area_id: "NTH-CHIANGMAI-GISTDA-001",
      incident_type: "wildfire_haze",
      hazard_score: 0.10,
      exposure_score: 0.20,
      urgency_score: 0.10,
      confidence: 0.25,
      risk_drivers: [
        "GISTDA hotspot API context",
        "GISTDA checked, no hotspot detected in monitored radius",
      ],
      hotspot_count: hotspotCount,
      landuse_types: landuseTypes,
      nearest_hotspot_distance_km: null,
    };
  }

  const hotspotSignal = clampScore(Math.min(hotspotCount, 10) / 10);
  const frequencySignal = clampScore(Math.min(maxFrequency, 5) / 5);
  const distanceSignal = hasNearestDistance && Number.isFinite(nearestDistance)
    ? clampScore(1 - Math.min(nearestDistance, 25) / 25)
    : 0;
  const landuseSignal = landuseTypes.length ? 0.2 : 0;

  const riskDrivers = ["GISTDA hotspot API context"];
  if (hotspotCount) riskDrivers.push(`${hotspotCount} hotspot record(s) returned`);
  if (landuseTypes.length) riskDrivers.push(`landuse: ${landuseTypes.slice(0, 3).join(", ")}`);
  if (hasNearestDistance && Number.isFinite(nearestDistance)) riskDrivers.push(`nearest hotspot distance ${nearestDistance.toFixed(2)} km`);

  return {
    area_id: "NTH-CHIANGMAI-GISTDA-001",
    incident_type: "wildfire_haze",
    hazard_score: clampScore(0.45 + hotspotSignal * 0.3 + frequencySignal * 0.15),
    exposure_score: clampScore(0.55 + landuseSignal),
    urgency_score: clampScore(0.45 + distanceSignal * 0.35 + hotspotSignal * 0.1),
    confidence: clampScore(0.55 + Math.min(hotspotCount, 3) * 0.07),
    risk_drivers: riskDrivers,
    hotspot_count: hotspotCount,
    landuse_types: landuseTypes,
    nearest_hotspot_distance_km: hasNearestDistance ? nearestDistance : null,
  };
}

function renderScore(score) {
  elements.severityBadge.textContent = score.severity || "--";
  elements.severityBadge.dataset.severity = severityClass(score.severity);
  elements.priorityScore.textContent = Number(score.priority_score).toFixed(2);
  elements.recommendedAction.textContent = formatAction(score.recommended_action);
  elements.operatorSummary.textContent = score.operator_summary || "--";
  elements.riskDrivers.innerHTML = "";

  (score.risk_drivers || []).forEach((driver) => {
    const chip = document.createElement("span");
    chip.className = "risk-chip";
    chip.textContent = driver;
    elements.riskDrivers.appendChild(chip);
  });
}

async function fetchHotspotContext() {
  const response = await fetch("/api/gistda/hotspot-context", { cache: "no-store" });
  if (!response.ok) throw new Error(`Hotspot context returned ${response.status}`);
  return response.json();
}

async function refreshLiveHotspotContext() {
  const response = await fetch("/api/gistda/refresh-hotspot-context", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || `Refresh returned ${response.status}`);
  return payload;
}

async function fetchPriorityScore(payload) {
  const response = await fetch("/api/incident/score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Priority score returned ${response.status}`);
  return response.json();
}

function formatRefreshTimestamp() {
  return new Date().toLocaleString();
}

function showRefreshMessage(message, status = "neutral") {
  elements.refreshMessage.textContent = message;
  elements.refreshMessage.dataset.status = status;
}

function showRankingMessage(message, status = "neutral") {
  elements.rankingMessage.textContent = message;
  elements.rankingMessage.dataset.status = status;
}

function renderRefreshTimestamp(timestamp = formatRefreshTimestamp()) {
  elements.lastUpdated.textContent = `Refreshed ${timestamp}`;
}

async function refreshDashboard() {
  elements.refreshButton.disabled = true;
  elements.refreshButton.textContent = "Refreshing...";
  showRefreshMessage("Refreshing live GISTDA hotspot context...", "working");

  try {
    await refreshLiveHotspotContext();
    const context = await fetchHotspotContext();
    const score = await fetchPriorityScore(buildScorePayloadFromContext(context));
    renderContext(context);
    renderScore(score);
    const refreshedAt = formatRefreshTimestamp();
    renderRefreshTimestamp(refreshedAt);
    showRefreshMessage(`Live GISTDA data refreshed successfully at ${refreshedAt}.`, "success");
  } catch (error) {
    setConnectorStatus("error");
    elements.operatorSummary.textContent = error.message;
    showRefreshMessage(`Live refresh failed: ${error.message}`, "error");
  } finally {
    elements.refreshButton.disabled = false;
    elements.refreshButton.textContent = "Refresh Live GISTDA Data";
  }
}

async function loadDashboard() {
  try {
    const context = await fetchHotspotContext();
    const score = await fetchPriorityScore(buildScorePayloadFromContext(context));
    renderContext(context);
    renderScore(score);
    renderRefreshTimestamp();
  } catch (error) {
    setConnectorStatus("error");
    elements.operatorSummary.textContent = error.message;
  }
}

function renderRanking(ranking) {
  const areas = ranking.areas || [];
  elements.rankingTableBody.innerHTML = "";

  if (!areas.length) {
    elements.rankingTableBody.innerHTML = '<tr><td colspan="10">No ranked areas available.</td></tr>';
    renderPatternDetail(null);
    return;
  }

  areas.forEach((area) => {
    const patternCodes = (area.matched_patterns || []).map((pattern) => pattern.pattern_code);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(area.rank)}</td>
      <td>${escapeHtml(area.province)}</td>
      <td>${escapeHtml(area.district)}</td>
      <td>${escapeHtml(area.hotspot_count)}</td>
      <td>${escapeHtml(formatJoined(area.landuse_types))}</td>
      <td>${escapeHtml(formatDistance(area.nearest_hotspot_distance_km))}</td>
      <td>${escapeHtml(Number(area.priority_score).toFixed(2))}</td>
      <td><span class="table-severity" data-severity="${severityClass(area.severity)}">${escapeHtml(area.severity)}</span></td>
      <td>${escapeHtml(formatAction(area.recommended_action))}</td>
      <td>${escapeHtml(patternCodes.join(", ") || "--")}</td>
    `;
    row.addEventListener("click", () => renderPatternDetail(area));
    elements.rankingTableBody.appendChild(row);
  });

  renderPatternDetail(areas[0]);
}

function renderPatternDetail(area) {
  if (!area) {
    elements.patternAreaName.textContent = "No ranked area selected";
    elements.patternCodes.textContent = "--";
    elements.patternExplanation.textContent = "Refresh the ranking to load pattern guidance.";
    elements.patternFocus.textContent = "--";
    return;
  }

  const patterns = area.matched_patterns || [];
  const primaryPattern = patterns[0];
  elements.patternAreaName.textContent = `${area.area_name} · ${area.province}`;
  elements.patternCodes.textContent = patterns.map((pattern) => pattern.pattern_code).join(", ") || "--";
  elements.patternExplanation.textContent = primaryPattern?.explanation || "No incident pattern matched this area.";
  elements.patternFocus.textContent = primaryPattern?.recommended_operational_focus || "--";
}

async function fetchRanking() {
  const response = await fetch("/api/forest-priority/ranking", { cache: "no-store" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || `Ranking returned ${response.status}`);
  return payload;
}

async function refreshRanking() {
  elements.rankingRefreshButton.disabled = true;
  elements.rankingRefreshButton.textContent = "Refreshing...";
  showRankingMessage("Refreshing multi-area forest priority ranking...", "working");

  try {
    const refreshResponse = await fetch("/api/forest-priority/refresh-ranking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const refreshPayload = await refreshResponse.json();
    if (!refreshResponse.ok) throw new Error(refreshPayload.message || `Ranking refresh returned ${refreshResponse.status}`);

    const ranking = await fetchRanking();
    renderRanking(ranking);
    showRankingMessage(`Multi-area ranking refreshed successfully at ${formatRefreshTimestamp()}.`, "success");
  } catch (error) {
    showRankingMessage(`Ranking refresh failed: ${error.message}`, "error");
  } finally {
    elements.rankingRefreshButton.disabled = false;
    elements.rankingRefreshButton.textContent = "Refresh Multi-area Ranking";
  }
}

async function loadRanking() {
  try {
    const ranking = await fetchRanking();
    renderRanking(ranking);
    showRankingMessage("Loaded the latest saved multi-area ranking.", "success");
  } catch (error) {
    showRankingMessage(error.message, "neutral");
  }
}

elements.refreshButton.addEventListener("click", refreshDashboard);
elements.rankingRefreshButton.addEventListener("click", refreshRanking);
loadDashboard();
loadRanking();
