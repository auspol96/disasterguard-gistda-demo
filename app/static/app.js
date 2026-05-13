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
  provinceFilter: document.getElementById("provinceFilter"),
  rankingTableBody: document.getElementById("rankingTableBody"),
  patternAreaName: document.getElementById("patternAreaName"),
  patternCodes: document.getElementById("patternCodes"),
  patternExplanation: document.getElementById("patternExplanation"),
  patternFocus: document.getElementById("patternFocus"),
  envSource: document.getElementById("envSource"),
  envTemperature: document.getElementById("envTemperature"),
  envHumidity: document.getElementById("envHumidity"),
  envWind: document.getElementById("envWind"),
  envRain: document.getElementById("envRain"),
  envPm25: document.getElementById("envPm25"),
  envFireRisk: document.getElementById("envFireRisk"),
  envHazeRisk: document.getElementById("envHazeRisk"),
  envEscalation: document.getElementById("envEscalation"),
  envRiskSummary: document.getElementById("envRiskSummary"),
};

let map;
let forestAreaLayer;
const forestAreaMarkers = new Map();
let selectedAreaId = null;
let allRankedAreas = [];

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

function ensureBaseMap(position, zoom = 9) {
  if (!position || typeof L === "undefined") return null;

  if (!map) {
    map = L.map("hotspotMap", {
      zoomControl: true,
      scrollWheelZoom: false,
    }).setView([position.latitude, position.longitude], zoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);
  } else {
    map.setView([position.latitude, position.longitude], zoom);
  }

  return map;
}

function ensureMap(position, sample, summary) {
  if (!position || typeof L === "undefined") return;

  if (!map) {
    ensureBaseMap(position, 11);
  } else if (!forestAreaMarkers.size) {
    map.setView([position.latitude, position.longitude], 11);
  }
  if (!map) return;

  elements.mapCoordinate.textContent = `${position.latitude.toFixed(5)}, ${position.longitude.toFixed(5)}`;
}

function severityColor(severity) {
  const normalized = severityClass(severity);
  if (normalized === "low" || normalized === "monitor") return "#2fbf71";
  if (normalized === "medium" || normalized === "watch") return "#f2b45f";
  if (normalized === "high") return "#ef4444";
  if (normalized === "critical") return "#7f1d1d";
  return "#7cc7ff";
}

function markerRadius(area) {
  const score = Number(area.priority_score);
  const baseRadius = Number.isFinite(score) ? 15 + Math.max(0, Math.min(1, score)) * 11 : 16;
  return Number(area.rank) === 1 ? baseRadius + 4 : baseRadius;
}

function markerTextColor(severity) {
  const normalized = severityClass(severity);
  return normalized === "medium" || normalized === "watch" ? "#081117" : "#ffffff";
}

function rankedAreaPosition(area) {
  const latitude = Number(area.lat);
  const longitude = Number(area.lon);
  return Number.isFinite(latitude) && Number.isFinite(longitude)
    ? { latitude, longitude }
    : null;
}

function buildForestAreaPopup(area) {
  const detailRows = [
    ["ลำดับ", area.rank],
    ["ชื่อพื้นที่", area.area_name],
    ["จังหวัด", area.province],
    ["อำเภอ", area.district],
    ["จำนวนจุดความร้อน", area.hotspot_count],
    ["คะแนนความเสี่ยง", area.priority_score === undefined ? null : Number(area.priority_score).toFixed(2)],
    ["ระดับความรุนแรง", area.severity],
    ["ข้อเสนอแนะ", formatAction(area.recommended_action)],
  ];

  return `
    <div class="hotspot-popup forest-area-popup">
      <strong>พื้นที่เฝ้าระวังป่า</strong>
      ${detailRows.map(([label, value]) => `<span><b>${escapeHtml(label)}</b>${escapeHtml(value)}</span>`).join("")}
    </div>
  `;
}

function buildRankMarkerIcon(area, isSelected = false) {
  const radius = markerRadius(area);
  const size = Math.round(radius * 2);
  const isTopRank = Number(area.rank) === 1;
  const classes = [
    "forest-rank-marker",
    isTopRank ? "is-top-rank" : "",
    isSelected ? "is-selected" : "",
  ].filter(Boolean).join(" ");

  return L.divIcon({
    className: "forest-rank-marker-icon",
    html: `
      <div
        class="${classes}"
        style="
          --marker-size:${size}px;
          --marker-bg:${severityColor(area.severity)};
          --marker-text:${markerTextColor(area.severity)};
        "
      >${escapeHtml(area.rank)}</div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

function updateSelectedMarkerStyles() {
  forestAreaMarkers.forEach((marker, areaId) => {
    marker.setIcon(buildRankMarkerIcon(marker.options.area, areaId === selectedAreaId));
  });
}

function openForestAreaMarker(area) {
  const marker = forestAreaMarkers.get(area.area_id);
  if (!marker || !map) return;

  const position = rankedAreaPosition(area);
  if (position) {
    map.setView([position.latitude, position.longitude], Math.max(map.getZoom(), 10));
  }
  marker.openPopup();
}

function selectRankedArea(area, focusMarker = false) {
  selectedAreaId = area?.area_id || null;
  renderPatternDetail(area);
  updateSelectedMarkerStyles();
  if (focusMarker) {
    openForestAreaMarker(area);
  }
}

function renderForestPriorityMarkers(areas) {
  if (typeof L === "undefined") return;

  if (!forestAreaLayer) {
    forestAreaLayer = L.layerGroup();
  }
  forestAreaLayer.clearLayers();
  forestAreaMarkers.clear();

  const bounds = [];
  areas.forEach((area) => {
    const position = rankedAreaPosition(area);
    if (!position) return;

    ensureBaseMap(position, 8);
    const marker = L.marker([position.latitude, position.longitude], {
      area,
      icon: buildRankMarkerIcon(area, area.area_id === selectedAreaId),
    })
      .bindPopup(buildForestAreaPopup(area))
      .on("click", () => selectRankedArea(area));

    marker.addTo(forestAreaLayer);
    forestAreaMarkers.set(area.area_id, marker);
    bounds.push([position.latitude, position.longitude]);
  });

  if (map && !map.hasLayer(forestAreaLayer)) {
    forestAreaLayer.addTo(map);
  }

  if (map && bounds.length) {
    map.fitBounds(bounds, { padding: [42, 42], maxZoom: 10 });
    elements.mapCoordinate.textContent = `แสดงพื้นที่จัดอันดับ ${bounds.length} จุด`;
  }
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

function populateProvinceFilter(areas) {
  if (!elements.provinceFilter) return;

  const selectedProvince = elements.provinceFilter.value;
  const provinces = [...new Set(areas.map((area) => area.province).filter(Boolean))].sort();
  elements.provinceFilter.innerHTML = '<option value="">All provinces</option>';
  provinces.forEach((province) => {
    const option = document.createElement("option");
    option.value = province;
    option.textContent = province;
    elements.provinceFilter.appendChild(option);
  });

  if (provinces.includes(selectedProvince)) {
    elements.provinceFilter.value = selectedProvince;
  }
}

function filteredRankedAreas() {
  const selectedProvince = elements.provinceFilter?.value || "";
  return selectedProvince
    ? allRankedAreas.filter((area) => area.province === selectedProvince)
    : allRankedAreas;
}

function renderRankingAreas(areas) {
  elements.rankingTableBody.innerHTML = "";

  if (!areas.length) {
    elements.rankingTableBody.innerHTML = '<tr><td colspan="10">No ranked areas available.</td></tr>';
    renderForestPriorityMarkers([]);
    renderPatternDetail(null);
    return;
  }

  renderForestPriorityMarkers(areas);

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
    row.addEventListener("click", () => selectRankedArea(area, true));
    elements.rankingTableBody.appendChild(row);
  });

  selectRankedArea(areas[0]);
}

function renderRanking(ranking) {
  allRankedAreas = ranking.areas || [];
  populateProvinceFilter(allRankedAreas);
  renderRankingAreas(filteredRankedAreas());
}

function renderPatternDetail(area) {
  if (!area) {
    elements.patternAreaName.textContent = "No ranked area selected";
    elements.patternCodes.textContent = "--";
    elements.patternExplanation.textContent = "Refresh the ranking to load pattern guidance.";
    elements.patternFocus.textContent = "--";
    renderEnvironmentalContext({});
    renderEnvironmentalRiskSummary({});
    return;
  }

  const patterns = area.matched_patterns || [];
  const primaryPattern = patterns[0];
  elements.patternAreaName.textContent = `${area.area_name} · ${area.province}`;
  elements.patternCodes.textContent = patterns.map((pattern) => pattern.pattern_code).join(", ") || "--";
  elements.patternExplanation.textContent = primaryPattern?.explanation || "No incident pattern matched this area.";
  elements.patternFocus.textContent = primaryPattern?.recommended_operational_focus || "--";
  renderEnvironmentalContext(area.environmental_context || {});
  renderEnvironmentalRiskSummary(area.environmental_risk_summary || {});
}

function renderEnvironmentalContext(context) {
  elements.envSource.textContent = context.source === "open-meteo"
    ? "Live Open-Meteo"
    : context.source === "sample"
      ? "Sample fallback"
      : "--";
  elements.envTemperature.textContent = context.temperature_c === undefined ? "--" : `${context.temperature_c} C`;
  elements.envHumidity.textContent = context.humidity_percent === undefined ? "--" : `${context.humidity_percent}%`;
  elements.envWind.textContent = context.wind_speed_kph === undefined ? "--" : `${context.wind_speed_kph} kph ${context.wind_direction || ""}`.trim();
  elements.envRain.textContent = context.rain_probability_percent === undefined ? "--" : `${context.rain_probability_percent}%`;
  elements.envPm25.textContent = context.pm25_ugm3 === undefined ? "--" : `${context.pm25_ugm3} ug/m3`;
}

function renderEnvironmentalRiskSummary(summary) {
  elements.envFireRisk.textContent = summary.fire_spread_risk || "--";
  elements.envHazeRisk.textContent = summary.haze_health_risk || "--";
  elements.envEscalation.textContent = summary.weather_supports_escalation === undefined
    ? "--"
    : summary.weather_supports_escalation
      ? "Yes"
      : "No";
  elements.envRiskSummary.textContent = summary.summary || "--";
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
elements.provinceFilter?.addEventListener("change", () => renderRankingAreas(filteredRankedAreas()));
loadDashboard();
loadRanking();
