const elements = {
  connectorBadge: document.getElementById("connectorBadge"),
  rankingRefreshButton: document.getElementById("rankingRefreshButton"),
  rankingMessage: document.getElementById("rankingMessage"),
  dataSourceStatus: document.getElementById("dataSourceStatus"),
  mapCoordinate: document.getElementById("mapCoordinate"),
  lastUpdated: document.getElementById("lastUpdated"),
  provinceFilter: document.getElementById("provinceFilter"),
  severityFilter: document.getElementById("severityFilter"),
  hotspotOnlyFilter: document.getElementById("hotspotOnlyFilter"),
  summaryTotalAreas: document.getElementById("summaryTotalAreas"),
  summaryHotspotAreas: document.getElementById("summaryHotspotAreas"),
  summaryHighAreas: document.getElementById("summaryHighAreas"),
  summaryMediumAreas: document.getElementById("summaryMediumAreas"),
  summaryTotalHotspots: document.getElementById("summaryTotalHotspots"),
  briefingRefreshButton: document.getElementById("briefingRefreshButton"),
  briefingMessage: document.getElementById("briefingMessage"),
  briefingExecutiveSummary: document.getElementById("briefingExecutiveSummary"),
  briefingTotalAreas: document.getElementById("briefingTotalAreas"),
  briefingHotspotAreas: document.getElementById("briefingHotspotAreas"),
  briefingTotalHotspots: document.getElementById("briefingTotalHotspots"),
  briefingUrgentQueue: document.getElementById("briefingUrgentQueue"),
  briefingFieldQueue: document.getElementById("briefingFieldQueue"),
  briefingTopAreas: document.getElementById("briefingTopAreas"),
  briefingNextActions: document.getElementById("briefingNextActions"),
  provinceSummaryBody: document.getElementById("provinceSummaryBody"),
  urgentCoordinationQueue: document.getElementById("urgentCoordinationQueue"),
  fieldVerificationQueue: document.getElementById("fieldVerificationQueue"),
  closeMonitoringQueue: document.getElementById("closeMonitoringQueue"),
  routineMonitoringQueue: document.getElementById("routineMonitoringQueue"),
  changeSummaryMessage: document.getElementById("changeSummaryMessage"),
  newHotspotChanges: document.getElementById("newHotspotChanges"),
  increasedHotspotChanges: document.getElementById("increasedHotspotChanges"),
  severityIncreasedChanges: document.getElementById("severityIncreasedChanges"),
  rankImprovedChanges: document.getElementById("rankImprovedChanges"),
  unchangedHighPriorityChanges: document.getElementById("unchangedHighPriorityChanges"),
  selectedSeverityBadge: document.getElementById("selectedSeverityBadge"),
  selectedAreaTitle: document.getElementById("selectedAreaTitle"),
  selectedRank: document.getElementById("selectedRank"),
  selectedAreaName: document.getElementById("selectedAreaName"),
  selectedProvince: document.getElementById("selectedProvince"),
  selectedDistrict: document.getElementById("selectedDistrict"),
  selectedScore: document.getElementById("selectedScore"),
  selectedSeverity: document.getElementById("selectedSeverity"),
  selectedResponsePriority: document.getElementById("selectedResponsePriority"),
  selectedHotspots: document.getElementById("selectedHotspots"),
  selectedLanduse: document.getElementById("selectedLanduse"),
  selectedDistance: document.getElementById("selectedDistance"),
  selectedAction: document.getElementById("selectedAction"),
  selectedOperatorSummary: document.getElementById("selectedOperatorSummary"),
  selectedExplainableRanking: document.getElementById("selectedExplainableRanking"),
  selectedChangeStatus: document.getElementById("selectedChangeStatus"),
  selectedRecurrenceStatus: document.getElementById("selectedRecurrenceStatus"),
  selectedRecurrenceSource: document.getElementById("selectedRecurrenceSource"),
  selectedRecurrenceCounts: document.getElementById("selectedRecurrenceCounts"),
  selectedHotspotRecurrence: document.getElementById("selectedHotspotRecurrence"),
  selectedFloodRecurrence: document.getElementById("selectedFloodRecurrence"),
  selectedDroughtRecurrence: document.getElementById("selectedDroughtRecurrence"),
  selectedRecurrenceScore: document.getElementById("selectedRecurrenceScore"),
  selectedRecurrenceSummary: document.getElementById("selectedRecurrenceSummary"),
  selectedRiskDrivers: document.getElementById("selectedRiskDrivers"),
  selectedPatterns: document.getElementById("selectedPatterns"),
  rankingTableBody: document.getElementById("rankingTableBody"),
  topAreasList: document.getElementById("topAreasList"),
  patternCounts: document.getElementById("patternCounts"),
  recurrenceOverview: document.getElementById("recurrenceOverview"),
};

let map;
let forestAreaLayer;
const forestAreaMarkers = new Map();
let allRankedAreas = [];
let selectedAreaId = null;

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

function formatJoined(values) {
  return Array.isArray(values) && values.length ? values.join(", ") : "--";
}

function formatDistance(distance) {
  return distance === null || distance === undefined ? "--" : `${Number(distance).toFixed(2)} กม.`;
}

function formatScore(score) {
  return score === null || score === undefined ? "--" : Number(score).toFixed(2);
}

function formatAction(value) {
  return value ? value.replaceAll("_", " ") : "--";
}

function responsePriorityLabel(value) {
  if (value === "ROUTINE_MONITORING") return "ติดตามตามรอบปกติ";
  if (value === "WATCHLIST") return "เฝ้าระวังใกล้ชิด";
  if (value === "FIELD_VERIFICATION") return "ตรวจสอบภาคสนาม";
  if (value === "URGENT_COORDINATION") return "ประสานงานเร่งด่วน";
  return value || "--";
}

function severityClass(value) {
  return value ? String(value).toLowerCase() : "unknown";
}

function severityLabel(value) {
  const normalized = severityClass(value);
  if (normalized === "low" || normalized === "monitor") return "ต่ำ";
  if (normalized === "medium" || normalized === "watch") return "ปานกลาง";
  if (normalized === "high") return "สูง";
  if (normalized === "critical") return "วิกฤต";
  return value || "--";
}

function severityColor(severity) {
  const normalized = severityClass(severity);
  if (normalized === "low" || normalized === "monitor") return "#2fbf71";
  if (normalized === "medium" || normalized === "watch") return "#f2b45f";
  if (normalized === "high") return "#ef4444";
  if (normalized === "critical") return "#7f1d1d";
  return "#7cc7ff";
}

function markerTextColor(severity) {
  const normalized = severityClass(severity);
  return normalized === "medium" || normalized === "watch" ? "#081117" : "#ffffff";
}

function markerRadius(area) {
  const score = Number(area.priority_score);
  const baseRadius = Number.isFinite(score) ? 15 + Math.max(0, Math.min(1, score)) * 11 : 16;
  return Number(area.rank) === 1 ? baseRadius + 4 : baseRadius;
}

function rankedAreaPosition(area) {
  const latitude = Number(area.lat);
  const longitude = Number(area.lon);
  return Number.isFinite(latitude) && Number.isFinite(longitude)
    ? { latitude, longitude }
    : null;
}

function showRankingMessage(message, status = "neutral") {
  elements.rankingMessage.textContent = message;
  elements.rankingMessage.dataset.status = status;
}

function updateMapTimestamp(prefix = "อัปเดตล่าสุด") {
  if (elements.lastUpdated) {
    elements.lastUpdated.textContent = `${prefix}: ${new Date().toLocaleString()}`;
  }
}

function ensureBaseMap(position, zoom = 7) {
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
  }

  return map;
}

function buildForestAreaPopup(area) {
  const detailRows = [
    ["ลำดับ", area.rank],
    ["ชื่อพื้นที่", area.area_name],
    ["จังหวัด", area.province],
    ["อำเภอ", area.district],
    ["จำนวนจุดความร้อน", area.hotspot_count],
    ["คะแนนความเสี่ยง", formatScore(area.priority_score)],
    ["ระดับความรุนแรง", severityLabel(area.severity)],
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

    ensureBaseMap(position, 7);
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
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
    elements.mapCoordinate.textContent = `แสดง ${bounds.length} พื้นที่`;
  } else if (elements.mapCoordinate) {
    elements.mapCoordinate.textContent = "ไม่พบพื้นที่ตามตัวกรอง";
  }
}

function renderChips(container, values) {
  container.innerHTML = "";
  if (!values.length) {
    const empty = document.createElement("span");
    empty.className = "info-chip";
    empty.textContent = "--";
    container.appendChild(empty);
    return;
  }

  values.forEach((value) => {
    const chip = document.createElement("span");
    chip.className = "info-chip";
    chip.textContent = value;
    container.appendChild(chip);
  });
}

function renderPatternCards(container, patterns) {
  container.innerHTML = "";
  if (!patterns.length) {
    const empty = document.createElement("article");
    empty.className = "pattern-card";
    empty.textContent = "--";
    container.appendChild(empty);
    return;
  }

  patterns.forEach((pattern) => {
    const card = document.createElement("article");
    card.className = "pattern-card";
    card.innerHTML = `
      <strong>${escapeHtml(pattern.pattern_name || pattern.pattern_code)}</strong>
      <span>${escapeHtml(pattern.pattern_code)}</span>
      <p>${escapeHtml(pattern.explanation || "--")}</p>
    `;
    container.appendChild(card);
  });
}

function recurrenceStatusLabel(status) {
  if (status === "ok") return "พบข้อมูลจาก GISTDA";
  if (status === "not_found") return "ไม่พบข้อมูล";
  if (status === "not_configured") return "ยังไม่ได้ตั้งค่า";
  if (status === "error") return "ดึงข้อมูลไม่สำเร็จ";
  return status || "--";
}

function recurrenceSourceLabel(source) {
  if (source === "gistda_recurring_v2_api") return "แหล่งข้อมูล: GISTDA Recurring Disaster API v2";
  if (source === "gistda_recurring_api") return "แหล่งข้อมูล: GISTDA Recurring Disaster API";
  return source || "--";
}

function renderSelectedArea(area) {
  if (!area) {
    selectedAreaId = null;
    elements.selectedAreaTitle.textContent = "ยังไม่มีพื้นที่ที่เลือก";
    elements.selectedSeverityBadge.textContent = "--";
    elements.selectedSeverityBadge.dataset.severity = "unknown";
    [
      "selectedRank",
      "selectedAreaName",
      "selectedProvince",
      "selectedDistrict",
      "selectedScore",
      "selectedSeverity",
      "selectedResponsePriority",
      "selectedHotspots",
      "selectedLanduse",
      "selectedDistance",
    ].forEach((id) => {
      elements[id].textContent = "--";
    });
    elements.selectedAction.textContent = "--";
    elements.selectedOperatorSummary.textContent = "--";
    elements.selectedExplainableRanking.textContent = "--";
    elements.selectedChangeStatus.textContent = "--";
    elements.selectedRecurrenceStatus.textContent = "--";
    elements.selectedRecurrenceSource.textContent = "--";
    elements.selectedRecurrenceCounts.hidden = true;
    elements.selectedHotspotRecurrence.textContent = "--";
    elements.selectedFloodRecurrence.textContent = "--";
    elements.selectedDroughtRecurrence.textContent = "--";
    elements.selectedRecurrenceScore.textContent = "--";
    elements.selectedRecurrenceSummary.textContent = "--";
    renderChips(elements.selectedRiskDrivers, []);
    renderPatternCards(elements.selectedPatterns, []);
    return;
  }

  selectedAreaId = area.area_id;
  elements.selectedAreaTitle.textContent = `${area.rank}. ${area.area_name}`;
  elements.selectedSeverityBadge.textContent = severityLabel(area.severity);
  elements.selectedSeverityBadge.dataset.severity = severityClass(area.severity);
  elements.selectedRank.textContent = area.rank ?? "--";
  elements.selectedAreaName.textContent = area.area_name || "--";
  elements.selectedProvince.textContent = area.province || "--";
  elements.selectedDistrict.textContent = area.district || "--";
  elements.selectedScore.textContent = formatScore(area.priority_score);
  elements.selectedSeverity.textContent = severityLabel(area.severity);
  elements.selectedResponsePriority.textContent = responsePriorityLabel(area.response_priority);
  elements.selectedHotspots.textContent = area.hotspot_count ?? "--";
  elements.selectedLanduse.textContent = formatJoined(area.landuse_types);
  elements.selectedDistance.textContent = formatDistance(area.nearest_hotspot_distance_km);
  elements.selectedAction.textContent = formatAction(area.recommended_action);
  elements.selectedOperatorSummary.textContent = area.operator_summary || "--";
  elements.selectedExplainableRanking.textContent = area.explainable_ranking_th || "--";
  elements.selectedChangeStatus.textContent = area.change_status_th || "ยังไม่มีข้อมูลรอบก่อนหน้า";

  const recurrence = area.recurrence_context || {};
  const recurrenceOk = recurrence.status === "ok";
  elements.selectedRecurrenceStatus.textContent = recurrenceStatusLabel(recurrence.status);
  elements.selectedRecurrenceSource.textContent = recurrenceSourceLabel(recurrence.source);
  elements.selectedRecurrenceCounts.hidden = !recurrenceOk;
  elements.selectedHotspotRecurrence.textContent = recurrenceOk ? recurrence.hotspot_recurrence_count ?? "--" : "--";
  elements.selectedFloodRecurrence.textContent = recurrenceOk ? recurrence.flood_recurrence_count ?? "--" : "--";
  elements.selectedDroughtRecurrence.textContent = recurrenceOk ? recurrence.drought_recurrence_count ?? "--" : "--";
  elements.selectedRecurrenceScore.textContent = recurrenceOk ? formatScore(recurrence.recurrence_score) : "--";
  elements.selectedRecurrenceSummary.textContent = recurrence.recurrence_summary_th || "--";

  renderChips(elements.selectedRiskDrivers, area.risk_drivers || []);
  renderPatternCards(elements.selectedPatterns, area.matched_patterns || []);
}

function selectRankedArea(area, focusMarker = false) {
  renderSelectedArea(area);
  updateSelectedMarkerStyles();
  if (focusMarker) {
    openForestAreaMarker(area);
  }
}

function populateProvinceFilter(areas) {
  const selectedProvince = elements.provinceFilter.value;
  const provinces = [...new Set(areas.map((area) => area.province).filter(Boolean))].sort();
  elements.provinceFilter.innerHTML = '<option value="">ทุกจังหวัด</option>';
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
  const selectedProvince = elements.provinceFilter.value;
  const selectedSeverity = elements.severityFilter.value;
  const hotspotOnly = elements.hotspotOnlyFilter.checked;

  return allRankedAreas.filter((area) => {
    if (selectedProvince && area.province !== selectedProvince) return false;
    if (selectedSeverity && area.severity !== selectedSeverity) return false;
    if (hotspotOnly && Number(area.hotspot_count || 0) <= 0) return false;
    return true;
  });
}

function renderSituationSummary(areas) {
  const highSeverities = new Set(["HIGH", "CRITICAL"]);
  elements.summaryTotalAreas.textContent = areas.length;
  elements.summaryHotspotAreas.textContent = areas.filter((area) => Number(area.hotspot_count || 0) > 0).length;
  elements.summaryHighAreas.textContent = areas.filter((area) => highSeverities.has(area.severity)).length;
  elements.summaryMediumAreas.textContent = areas.filter((area) => area.severity === "MEDIUM").length;
  elements.summaryTotalHotspots.textContent = areas.reduce((total, area) => total + Number(area.hotspot_count || 0), 0);
}

function renderBriefingList(container, items, formatter) {
  container.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("li");
    empty.textContent = "ยังไม่มีรายการ";
    container.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = formatter(item);
    container.appendChild(row);
  });
}

function renderDailyBriefing(briefing) {
  const keyNumbers = briefing.key_numbers || {};
  elements.briefingMessage.textContent = briefing.title_th || "รายงานสถานการณ์ประจำวัน";
  elements.briefingExecutiveSummary.textContent = briefing.executive_summary_th || "--";
  elements.briefingTotalAreas.textContent = keyNumbers.total_areas ?? "--";
  elements.briefingHotspotAreas.textContent = keyNumbers.hotspot_area_count ?? "--";
  elements.briefingTotalHotspots.textContent = keyNumbers.total_hotspots ?? "--";
  elements.briefingUrgentQueue.textContent = keyNumbers.urgent_queue_count ?? "--";
  elements.briefingFieldQueue.textContent = keyNumbers.field_verification_count ?? "--";
  renderBriefingList(
    elements.briefingTopAreas,
    briefing.top_priority_areas || [],
    (area) => `#${area.rank} ${area.area_name} / ${area.province} / จุดความร้อน ${area.hotspot_count} / คะแนน ${formatScore(area.priority_score)}`
  );
  renderBriefingList(
    elements.briefingNextActions,
    briefing.recommended_next_actions || [],
    (action) => action
  );
}

async function fetchDailyBriefing() {
  const response = await fetch("/api/briefing/daily", { cache: "no-store" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || `Daily briefing returned ${response.status}`);
  return payload;
}

async function loadDailyBriefing() {
  try {
    const briefing = await fetchDailyBriefing();
    renderDailyBriefing(briefing);
  } catch (error) {
    elements.briefingMessage.textContent = `โหลดรายงานไม่สำเร็จ: ${error.message}`;
    elements.briefingExecutiveSummary.textContent = "--";
  }
}

async function refreshDailyBriefing() {
  elements.briefingRefreshButton.disabled = true;
  elements.briefingRefreshButton.textContent = "กำลังรีเฟรช...";
  try {
    await loadDailyBriefing();
  } finally {
    elements.briefingRefreshButton.disabled = false;
    elements.briefingRefreshButton.textContent = "รีเฟรชรายงานสถานการณ์";
  }
}

function renderProvinceSummary(provinceSummary) {
  elements.provinceSummaryBody.innerHTML = "";
  if (!provinceSummary.length) {
    elements.provinceSummaryBody.innerHTML = '<tr><td colspan="6">ยังไม่มีข้อมูลรายจังหวัด</td></tr>';
    return;
  }

  provinceSummary.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(item.province)}</td>
      <td>${escapeHtml(item.total_areas)}</td>
      <td>${escapeHtml(item.total_hotspots)}</td>
      <td>${escapeHtml(item.high_count)}</td>
      <td>${escapeHtml(item.medium_count)}</td>
      <td>${escapeHtml(item.highest_rank_area?.area_name || "--")}</td>
    `;
    elements.provinceSummaryBody.appendChild(row);
  });
}

function renderActionQueueList(container, items) {
  container.innerHTML = "";
  if (!items.length) {
    container.innerHTML = "<p>ยังไม่มีรายการ</p>";
    return;
  }

  items.slice(0, 8).forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "action-queue-item";
    card.innerHTML = `
      <strong>#${escapeHtml(item.rank)} ${escapeHtml(item.area_name)}</strong>
      <span>${escapeHtml(item.province)} / ${escapeHtml(item.district)}</span>
      <span>จุดความร้อน ${escapeHtml(item.hotspot_count)} | ระดับ ${escapeHtml(severityLabel(item.severity))}</span>
      <p>${escapeHtml(item.short_reason_th || item.reason_th)}</p>
    `;
    card.addEventListener("click", () => {
      const area = allRankedAreas.find((rankedArea) => rankedArea.area_id === item.area_id);
      if (area) selectRankedArea(area, true);
    });
    container.appendChild(card);
  });
}

function renderActionQueue(actionQueue) {
  renderActionQueueList(elements.urgentCoordinationQueue, actionQueue?.urgent_coordination || []);
  renderActionQueueList(elements.fieldVerificationQueue, actionQueue?.field_verification || []);
  renderActionQueueList(elements.closeMonitoringQueue, actionQueue?.close_monitoring || []);
  renderActionQueueList(elements.routineMonitoringQueue, actionQueue?.routine_monitoring || []);
}

function renderChangeSummaryList(container, items) {
  container.innerHTML = "";
  if (!items.length) {
    container.innerHTML = "<p>ยังไม่มีรายการ</p>";
    return;
  }

  items.slice(0, 8).forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "change-summary-item";
    card.innerHTML = `
      <strong>#${escapeHtml(item.previous_rank)} → #${escapeHtml(item.current_rank)} ${escapeHtml(item.area_name)}</strong>
      <span>${escapeHtml(item.province)} / ${escapeHtml(item.district)}</span>
      <span>จุดความร้อน ${escapeHtml(item.previous_hotspot_count)} → ${escapeHtml(item.current_hotspot_count)}</span>
      <span>ระดับ ${escapeHtml(severityLabel(item.previous_severity))} → ${escapeHtml(severityLabel(item.current_severity))}</span>
      <p>${escapeHtml(item.change_reason_th)}</p>
    `;
    card.addEventListener("click", () => {
      const area = allRankedAreas.find((rankedArea) => rankedArea.area_id === item.area_id);
      if (area) selectRankedArea(area, true);
    });
    container.appendChild(card);
  });
}

function renderChangeSummary(changeSummary) {
  if (elements.changeSummaryMessage) {
    elements.changeSummaryMessage.textContent = changeSummary?.message || "ยังไม่มีข้อมูลรอบก่อนหน้าเพื่อเปรียบเทียบ";
  }
  renderChangeSummaryList(elements.newHotspotChanges, changeSummary?.new_hotspot_areas || []);
  renderChangeSummaryList(elements.increasedHotspotChanges, changeSummary?.increased_hotspot_areas || []);
  renderChangeSummaryList(elements.severityIncreasedChanges, changeSummary?.severity_increased_areas || []);
  renderChangeSummaryList(elements.rankImprovedChanges, changeSummary?.rank_improved_areas || []);
  renderChangeSummaryList(elements.unchangedHighPriorityChanges, changeSummary?.unchanged_high_priority_areas || []);
}

function renderRankingTable(areas) {
  elements.rankingTableBody.innerHTML = "";
  if (!areas.length) {
    elements.rankingTableBody.innerHTML = '<tr><td colspan="10">ไม่พบพื้นที่ตามตัวกรอง</td></tr>';
    return;
  }

  areas.forEach((area) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(area.rank)}</td>
      <td>${escapeHtml(area.area_name)}</td>
      <td>${escapeHtml(area.province)}</td>
      <td>${escapeHtml(area.district)}</td>
      <td>${escapeHtml(area.hotspot_count)}</td>
      <td>${escapeHtml(formatScore(area.recurrence_context?.recurrence_score))}</td>
      <td>${escapeHtml(formatScore(area.priority_score))}</td>
      <td><span class="table-severity" data-severity="${severityClass(area.severity)}">${escapeHtml(severityLabel(area.severity))}</span></td>
      <td>${escapeHtml(responsePriorityLabel(area.response_priority))}</td>
      <td>${escapeHtml(formatAction(area.recommended_action))}</td>
    `;
    row.addEventListener("click", () => selectRankedArea(area, true));
    elements.rankingTableBody.appendChild(row);
  });
}

function renderTopAreasInsight(areas) {
  elements.topAreasList.innerHTML = "";
  areas.slice(0, 5).forEach((area) => {
    const item = document.createElement("li");
    item.textContent = `${area.area_name} / ${area.province} / คะแนน ${formatScore(area.priority_score)}`;
    elements.topAreasList.appendChild(item);
  });
}

function renderPatternCountsInsight(areas) {
  const counts = new Map();
  areas.forEach((area) => {
    (area.matched_patterns || []).forEach((pattern) => {
      counts.set(pattern.pattern_code, (counts.get(pattern.pattern_code) || 0) + 1);
    });
  });

  elements.patternCounts.innerHTML = "";
  if (!counts.size) {
    elements.patternCounts.innerHTML = "<p>ยังไม่พบรูปแบบเหตุการณ์</p>";
    return;
  }

  [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .forEach(([patternCode, count]) => {
      const row = document.createElement("p");
      row.textContent = `${patternCode}: ${count} พื้นที่`;
      elements.patternCounts.appendChild(row);
    });
}

function renderRecurrenceOverview(areas) {
  const okCount = areas.filter((area) => area.recurrence_context?.status === "ok").length;
  const notFoundCount = areas.filter((area) => area.recurrence_context?.status === "not_found").length;
  const unavailableCount = areas.filter((area) => {
    const status = area.recurrence_context?.status;
    return status === "not_configured" || status === "error";
  }).length;

  elements.recurrenceOverview.innerHTML = `
    <p>พื้นที่ที่พบข้อมูลประวัติซ้ำซากจาก GISTDA: ${okCount}</p>
    <p>พื้นที่ที่ GISTDA ยังไม่พบประวัติซ้ำซาก: ${notFoundCount}</p>
    <p>พื้นที่ที่ยังดึงข้อมูลประวัติซ้ำซากไม่ได้: ${unavailableCount}</p>
  `;
}

function renderInsights(areas) {
  renderTopAreasInsight(areas);
  renderPatternCountsInsight(areas);
  renderRecurrenceOverview(areas);
}

function applyFilters() {
  const filteredAreas = filteredRankedAreas();
  const selectedAreaStillVisible = filteredAreas.some((area) => area.area_id === selectedAreaId);
  const areaToSelect = selectedAreaStillVisible
    ? filteredAreas.find((area) => area.area_id === selectedAreaId)
    : filteredAreas[0];

  renderForestPriorityMarkers(filteredAreas);
  renderRankingTable(filteredAreas);
  selectRankedArea(areaToSelect || null);
}

function renderRanking(ranking) {
  allRankedAreas = ranking.areas || [];
  allRankedAreas.sort((a, b) => Number(a.rank || 0) - Number(b.rank || 0));
  elements.connectorBadge.hidden = ranking.status !== "ok";
  if (elements.dataSourceStatus) {
    elements.dataSourceStatus.textContent = `สถานะข้อมูล: ${ranking.status || "--"}`;
  }
  populateProvinceFilter(allRankedAreas);
  renderSituationSummary(allRankedAreas);
  renderProvinceSummary(ranking.province_summary || []);
  renderActionQueue(ranking.action_queue || {});
  renderChangeSummary(ranking.change_summary || {});
  renderInsights(allRankedAreas);
  applyFilters();
}

async function fetchRanking() {
  const response = await fetch("/api/forest-priority/ranking", { cache: "no-store" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || `Ranking returned ${response.status}`);
  return payload;
}

async function refreshRanking() {
  elements.rankingRefreshButton.disabled = true;
  elements.rankingRefreshButton.textContent = "กำลังรีเฟรช...";
  showRankingMessage("กำลังรีเฟรชข้อมูลลำดับความเสี่ยงพื้นที่ป่า", "working");

  try {
    const refreshResponse = await fetch("/api/forest-priority/refresh-ranking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const refreshPayload = await refreshResponse.json();
    if (!refreshResponse.ok) throw new Error(refreshPayload.message || `Ranking refresh returned ${refreshResponse.status}`);

    const ranking = await fetchRanking();
    renderRanking(ranking);
    await loadDailyBriefing();
    updateMapTimestamp("รีเฟรชล่าสุด");
    showRankingMessage(`รีเฟรชข้อมูลสำเร็จ ${new Date().toLocaleString()}`, "success");
  } catch (error) {
    showRankingMessage(`รีเฟรชข้อมูลไม่สำเร็จ: ${error.message}`, "error");
  } finally {
    elements.rankingRefreshButton.disabled = false;
    elements.rankingRefreshButton.textContent = "รีเฟรชลำดับความเสี่ยง";
  }
}

async function loadRanking() {
  try {
    const ranking = await fetchRanking();
    renderRanking(ranking);
    await loadDailyBriefing();
    updateMapTimestamp();
    showRankingMessage("โหลดข้อมูลลำดับความเสี่ยงล่าสุดแล้ว", "success");
  } catch (error) {
    showRankingMessage(error.message, "neutral");
  }
}

elements.rankingRefreshButton.addEventListener("click", refreshRanking);
elements.briefingRefreshButton.addEventListener("click", refreshDailyBriefing);
elements.provinceFilter.addEventListener("change", applyFilters);
elements.severityFilter.addEventListener("change", applyFilters);
elements.hotspotOnlyFilter.addEventListener("change", applyFilters);
loadRanking();
