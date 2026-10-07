// Incident Details Controller (Vanilla JS)

document.addEventListener('DOMContentLoaded', async () => {
  const authenticated = await window.auth.requireAuth();
  if (!authenticated) return;

  window.auth.renderHeaderUser('header-user-info');

  const urlParams = new URLSearchParams(window.location.search);
  const incidentId = Number(urlParams.get('id'));

  const alertError = document.getElementById('alert-error');
  const alertSuccess = document.getElementById('alert-success');

  function showError(msg) {
    if (alertError) {
      alertError.textContent = msg;
      alertError.style.display = 'block';
    }
    if (alertSuccess) alertSuccess.style.display = 'none';
  }

  function showSuccess(msg) {
    if (alertSuccess) {
      alertSuccess.textContent = msg;
      alertSuccess.style.display = 'block';
    }
    if (alertError) alertError.style.display = 'none';
  }

  function clearAlerts() {
    if (alertError) alertError.style.display = 'none';
    if (alertSuccess) alertSuccess.style.display = 'none';
  }

  if (isNaN(incidentId) || incidentId <= 0) {
    showError('Invalid Incident ID in URL parameter.');
    return;
  }

  // State
  let incident = null;
  let clock = null;
  let timeline = [];
  let evidenceList = [];
  let nistHistory = [];
  let indicators = [];
  let aiAnalyses = [];
  let selectedAnalysis = null;
  const clockIntervals = {};

  function clearClockInterval(containerId) {
    if (clockIntervals[containerId]) {
      clearInterval(clockIntervals[containerId]);
      delete clockIntervals[containerId];
    }
  }

  function clearAllClockIntervals() {
    Object.keys(clockIntervals).forEach((id) => {
      clearInterval(clockIntervals[id]);
      delete clockIntervals[id];
    });
  }

  // Safe formatting helpers
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function safeToFixed(value, decimals = 1, fallback = '0.0') {
    if (value === null || value === undefined) return fallback;
    const num = Number(value);
    return Number.isFinite(num) ? num.toFixed(decimals) : fallback;
  }

  function safeDateString(val, formatter = 'toLocaleString', fallback = '—') {
    if (!val) return fallback;
    const d = new Date(val);
    if (isNaN(d.getTime())) return fallback;
    return typeof d[formatter] === 'function' ? d[formatter]() : d.toLocaleString();
  }

  // Badge render helpers
  function renderPriorityBadge(priority) {
    if (!priority) return '<span class="badge badge-default">—</span>';
    const map = { P1: 'badge-p1', P2: 'badge-p2', P3: 'badge-p3', P4: 'badge-p4' };
    return `<span class="badge ${map[priority] || 'badge-default'}">${escapeHtml(priority)}</span>`;
  }

  function renderStatusBadge(status) {
    if (!status) return '<span class="badge badge-status">—</span>';
    return `<span class="badge badge-status">${escapeHtml(status)}</span>`;
  }

  function renderSeverityBadge(severity) {
    if (!severity || severity === 'Not Determined') return '<span class="badge badge-default">Not Determined</span>';
    let c = 'badge-default';
    if (severity === 'Critical') c = 'badge-p1';
    else if (severity === 'High') c = 'badge-p2';
    else if (severity === 'Medium') c = 'badge-p3';
    else if (severity === 'Low') c = 'badge-p4';
    return `<span class="badge ${c}">${escapeHtml(severity)}</span>`;
  }

  // Tab switching
  const tabButtons = document.querySelectorAll('.tab');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      tabButtons.forEach((b) => b.classList.remove('active'));
      tabPanels.forEach((p) => (p.style.display = 'none'));

      btn.classList.add('active');
      const activePanel = document.getElementById(`tab-content-${targetTab}`);
      if (activePanel) activePanel.style.display = 'block';
    });
  });

  // Render Clock Widget with Live Countdown Ticker
  function renderClockWidget(containerId, clockData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    clearClockInterval(containerId);

    if (!clockData) {
      container.innerHTML = `
        <div class="clock-display">
          <div>
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
              72-Hour Clock
            </div>
            <div class="clock-timer" style="font-size: 13px; color: var(--text-muted); font-family: sans-serif;">
              Clock data unavailable
            </div>
          </div>
        </div>
      `;
      return;
    }

    // Backend fields: remaining_seconds, elapsed_seconds, is_expired, deadline_at, detected_at
    let secondsLeft = null;
    if (typeof clockData.remaining_seconds === 'number' && Number.isFinite(clockData.remaining_seconds)) {
      secondsLeft = clockData.remaining_seconds;
    } else if (typeof clockData.time_remaining_seconds === 'number' && Number.isFinite(clockData.time_remaining_seconds)) {
      secondsLeft = clockData.time_remaining_seconds;
    } else if (clockData.deadline_at) {
      const dl = new Date(clockData.deadline_at).getTime();
      if (Number.isFinite(dl)) {
        secondsLeft = Math.max(0, (dl - Date.now()) / 1000);
      }
    }

    if (secondsLeft === null || !Number.isFinite(secondsLeft)) {
      secondsLeft = 0;
    }

    const isExpired = Boolean(
      clockData.is_expired ??
      clockData.is_overdue ??
      (secondsLeft <= 0)
    );

    const clockStatus = clockData.status || clockData.compliance_status || (isExpired ? 'EXPIRED' : 'ACTIVE');

    function updateDisplay() {
      const isOverdue = isExpired || secondsLeft <= 0;
      const totalSec = Math.max(0, Math.floor(secondsLeft));
      const hours = Math.floor(totalSec / 3600);
      const minutes = Math.floor((totalSec % 3600) / 60);
      const seconds = totalSec % 60;

      const timerText = isOverdue
        ? '<span style="color: #b91c1c;">OVERDUE</span>'
        : `<span>${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</span>`;

      const deadlineStr = safeDateString(clockData.deadline_at, 'toLocaleTimeString', '—');

      container.innerHTML = `
        <div class="clock-display">
          <div>
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
              72-Hour Clock
            </div>
            <div class="clock-timer ${isOverdue ? 'badge-overdue' : ''}">
              ${timerText}
            </div>
          </div>
          <div style="margin-left: auto; text-align: right; font-size: 12px;">
            <div>Status: <strong style="color: ${isOverdue ? '#b91c1c' : '#166534'};">${escapeHtml(clockStatus)}</strong></div>
            <div style="color: var(--text-muted);">Deadline: ${deadlineStr}</div>
          </div>
        </div>
      `;
    }

    updateDisplay();

    if (!isExpired && secondsLeft > 0) {
      clockIntervals[containerId] = setInterval(() => {
        if (secondsLeft > 0) {
          secondsLeft -= 1;
          updateDisplay();
        } else {
          clearClockInterval(containerId);
          updateDisplay();
        }
      }, 1000);
    }
  }

  // Load All Incident Data
  async function loadAllData() {
    clearAlerts();
    clearAllClockIntervals();
    try {
      const [inc, clk, tl, ev, nist, ind, ai] = await Promise.all([
        window.api.getIncident(incidentId),
        window.api.getClock(incidentId).catch((err) => {
          console.warn('Clock fetch notice:', err);
          return null;
        }),
        window.api.getTimeline(incidentId).catch(() => []),
        window.api.getEvidence(incidentId).catch(() => []),
        window.api.getNistHistory(incidentId).catch(() => []),
        window.api.getIndicators(incidentId).catch(() => []),
        window.api.getAiAnalyses(incidentId).catch(() => []),
      ]);

      if (!inc) {
        showError(`Incident #${incidentId} could not be loaded.`);
        return;
      }

      incident = inc;
      clock = clk;
      timeline = Array.isArray(tl) && tl.length > 0 ? tl : (inc.timeline_events || []);
      evidenceList = Array.isArray(ev) && ev.length > 0 ? ev : (inc.evidence || []);
      nistHistory = Array.isArray(nist) && nist.length > 0 ? nist : (inc.nist_history || []);
      indicators = Array.isArray(ind) && ind.length > 0 ? ind : (inc.indicators || []);
      aiAnalyses = Array.isArray(ai) ? ai : [];

      populateHeader();
      populateOverviewTab();
      populateTimelineTab();
      populateEvidenceTab();
      populateNistTab();
      populateAiTab();
      populateClockTab();
    } catch (err) {
      showError(err.message || 'Failed to fetch incident telemetry.');
    }
  }

  // 1. Populate Header
  function populateHeader() {
    if (!incident) return;
    const idEl = document.getElementById('label-incident-id');
    if (idEl) idEl.textContent = `#${incident.id}`;

    const titleEl = document.getElementById('label-incident-title');
    if (titleEl) titleEl.textContent = incident.title || 'Untitled Incident';

    const statusCont = document.getElementById('badge-status-container');
    if (statusCont) statusCont.innerHTML = renderStatusBadge(incident.status);

    const prioCont = document.getElementById('badge-priority-container');
    if (prioCont) prioCont.innerHTML = renderPriorityBadge(incident.priority);

    const attackEl = document.getElementById('label-attack-type');
    if (attackEl) attackEl.textContent = incident.attack_type || '—';

    const detectedEl = document.getElementById('label-detected-at');
    if (detectedEl) {
      detectedEl.textContent = `Detected: ${safeDateString(incident.detected_at, 'toLocaleString', '—')}`;
    }

    renderClockWidget('clock-widget-container', clock);
  }

  // 2. Overview Tab
  function populateOverviewTab() {
    if (!incident) return;
    const srcEl = document.getElementById('label-source');
    if (srcEl) srcEl.textContent = `Source: ${incident.source || '—'}`;

    const descEl = document.getElementById('label-description');
    if (descEl) descEl.textContent = incident.description || 'No description provided.';

    const selStatus = document.getElementById('select-status');
    if (selStatus && incident.status) selStatus.value = incident.status;

    const selPrio = document.getElementById('select-priority');
    if (selPrio && incident.priority) selPrio.value = incident.priority;

    // Assets
    const listAssets = document.getElementById('list-assets');
    if (listAssets) {
      if (Array.isArray(incident.affected_assets) && incident.affected_assets.length > 0) {
        listAssets.innerHTML = incident.affected_assets
          .map((a) => {
            if (typeof a === 'string') {
              return `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(a)}</span>`;
            }
            const name = a.asset_name || a.name || 'Unknown Asset';
            const type = a.asset_type || a.type;
            const label = type ? `${name} (${type})` : name;
            return `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(label)}</span>`;
          })
          .join('');
      } else {
        listAssets.innerHTML = '<span style="font-size: 12px; color: var(--text-muted);">None recorded</span>';
      }
    }

    // Users
    const listUsers = document.getElementById('list-users');
    if (listUsers) {
      if (Array.isArray(incident.affected_users) && incident.affected_users.length > 0) {
        listUsers.innerHTML = incident.affected_users
          .map((u) => {
            if (typeof u === 'string') {
              return `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(u)}</span>`;
            }
            const uname = u.username || 'Unknown User';
            const email = u.email ? ` &lt;${escapeHtml(u.email)}&gt;` : '';
            return `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(uname)}${email}</span>`;
          })
          .join('');
      } else {
        listUsers.innerHTML = '<span style="font-size: 12px; color: var(--text-muted);">None recorded</span>';
      }
    }

    // Indicators
    const iocRows = document.getElementById('ioc-rows');
    if (iocRows) {
      if (!Array.isArray(indicators) || indicators.length === 0) {
        iocRows.innerHTML = '<tr><td colspan="3" style="color: var(--text-muted); text-align: center;">No IoCs recorded</td></tr>';
      } else {
        iocRows.innerHTML = indicators
          .map((ind) => `
            <tr>
              <td style="width: 80px; font-weight: 600;">${escapeHtml((ind.type || 'IoC').toUpperCase())}</td>
              <td class="mono">${escapeHtml(ind.value || '—')}</td>
              <td style="color: var(--text-muted);">${escapeHtml(ind.description || '—')}</td>
            </tr>
          `)
          .join('');
      }
    }
  }

  // Overview Action Listeners
  const btnApplyStatus = document.getElementById('btn-apply-status');
  if (btnApplyStatus) {
    btnApplyStatus.addEventListener('click', async () => {
      clearAlerts();
      const st = document.getElementById('select-status').value;
      try {
        await window.api.updateIncident(incidentId, { status: st });
        showSuccess(`Incident status updated to '${st}'.`);
        loadAllData();
      } catch (err) {
        showError(err.message || 'Status transition failed.');
      }
    });
  }

  const btnApplyPriority = document.getElementById('btn-apply-priority');
  if (btnApplyPriority) {
    btnApplyPriority.addEventListener('click', async () => {
      clearAlerts();
      const pr = document.getElementById('select-priority').value;
      try {
        await window.api.updateIncident(incidentId, { priority: pr });
        showSuccess(`Priority updated to '${pr}'.`);
        loadAllData();
      } catch (err) {
        showError(err.message || 'Priority update failed.');
      }
    });
  }

  // Toggle Add IoC
  const btnToggleAddIoc = document.getElementById('btn-toggle-add-ioc');
  const formAddIoc = document.getElementById('form-add-ioc');
  const btnCancelIoc = document.getElementById('btn-cancel-ioc');

  if (btnToggleAddIoc && formAddIoc) {
    btnToggleAddIoc.addEventListener('click', () => {
      formAddIoc.style.display = formAddIoc.style.display === 'none' ? 'block' : 'none';
    });
  }
  if (btnCancelIoc && formAddIoc) {
    btnCancelIoc.addEventListener('click', () => {
      formAddIoc.style.display = 'none';
    });
  }

  if (formAddIoc) {
    formAddIoc.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlerts();
      const t = document.getElementById('new-ioc-type').value;
      const v = document.getElementById('new-ioc-value').value.trim();
      const d = document.getElementById('new-ioc-desc').value.trim();

      try {
        await window.api.addIndicator(incidentId, { type: t, value: v, description: d || undefined });
        showSuccess('Indicator of Compromise added.');
        formAddIoc.style.display = 'none';
        document.getElementById('new-ioc-value').value = '';
        document.getElementById('new-ioc-desc').value = '';
        loadAllData();
      } catch (err) {
        showError(err.message || 'Failed to add indicator.');
      }
    });
  }

  // 3. Timeline Tab
  function populateTimelineTab() {
    const countEl = document.getElementById('count-timeline');
    if (countEl) countEl.textContent = Array.isArray(timeline) ? timeline.length : 0;

    const tlRows = document.getElementById('timeline-rows');
    const tlEmpty = document.getElementById('timeline-empty');
    const tlWrapper = document.getElementById('timeline-table-wrapper');

    if (!Array.isArray(timeline) || timeline.length === 0) {
      if (tlEmpty) tlEmpty.style.display = 'block';
      if (tlWrapper) tlWrapper.style.display = 'none';
      return;
    }

    if (tlEmpty) tlEmpty.style.display = 'none';
    if (tlWrapper) tlWrapper.style.display = 'block';

    if (tlRows) {
      tlRows.innerHTML = timeline
        .map((ev) => {
          const trans = (ev.previous_value && ev.new_value)
            ? `<span>${escapeHtml(ev.previous_value)} &rarr; <strong>${escapeHtml(ev.new_value)}</strong></span>`
            : ev.new_value ? `<span><strong>${escapeHtml(ev.new_value)}</strong></span>` : '—';

          const timeStr = safeDateString(ev.timestamp, 'toLocaleString', '—');

          return `
            <tr>
              <td class="mono" style="font-size: 12px; color: var(--text-muted);">${timeStr}</td>
              <td style="font-weight: 600;">${escapeHtml(ev.event || 'Event')}</td>
              <td class="mono" style="font-size: 12px;">${escapeHtml(ev.actor || 'system')}</td>
              <td><span class="badge badge-default" style="font-size: 10px;">${escapeHtml(ev.source || 'system')}</span></td>
              <td style="color: var(--text-secondary);">${escapeHtml(ev.description || '—')}</td>
              <td class="mono" style="font-size: 11px; color: var(--text-muted);">${trans}</td>
            </tr>
          `;
        })
        .join('');
    }
  }

  // 4. Evidence Tab
  function populateEvidenceTab() {
    const countEl = document.getElementById('count-evidence');
    if (countEl) countEl.textContent = Array.isArray(evidenceList) ? evidenceList.length : 0;

    const evRows = document.getElementById('evidence-rows');
    const evEmpty = document.getElementById('evidence-empty');
    const evWrapper = document.getElementById('evidence-table-wrapper');

    if (!Array.isArray(evidenceList) || evidenceList.length === 0) {
      if (evEmpty) evEmpty.style.display = 'block';
      if (evWrapper) evWrapper.style.display = 'none';
      return;
    }

    if (evEmpty) evEmpty.style.display = 'none';
    if (evWrapper) evWrapper.style.display = 'block';

    if (evRows) {
      evRows.innerHTML = evidenceList
        .map((item) => `
          <tr>
            <td class="mono">#${item.id}</td>
            <td style="font-weight: 600;">${escapeHtml(item.evidence_type || 'Evidence')}</td>
            <td>${escapeHtml(item.source || '—')}</td>
            <td class="mono">${escapeHtml(item.collector || '—')}</td>
            <td class="mono" style="font-size: 11px; color: var(--text-secondary);">${escapeHtml(item.sha256_hash || '—')}</td>
            <td style="font-size: 12px; color: var(--text-muted);">${safeDateString(item.collected_at, 'toLocaleString', '—')}</td>
            <td style="font-size: 12px;">${escapeHtml(item.description || '—')}</td>
          </tr>
        `)
        .join('');
    }
  }

  const btnToggleAddEv = document.getElementById('btn-toggle-add-evidence');
  const formAddEv = document.getElementById('form-add-evidence');
  const btnCancelEv = document.getElementById('btn-cancel-evidence');

  if (btnToggleAddEv && formAddEv) {
    btnToggleAddEv.addEventListener('click', () => {
      formAddEv.style.display = formAddEv.style.display === 'none' ? 'block' : 'none';
    });
  }
  if (btnCancelEv && formAddEv) {
    btnCancelEv.addEventListener('click', () => {
      formAddEv.style.display = 'none';
    });
  }

  if (formAddEv) {
    formAddEv.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlerts();
      const t = document.getElementById('new-ev-type').value;
      const s = document.getElementById('new-ev-source').value;
      const c = document.getElementById('new-ev-collector').value;
      const h = document.getElementById('new-ev-hash').value.trim() || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
      const d = document.getElementById('new-ev-desc').value.trim();

      try {
        await window.api.addEvidence(incidentId, {
          evidence_type: t,
          source: s,
          collector: c,
          sha256_hash: h,
          description: d || undefined,
        });
        showSuccess('Evidence item logged with SHA-256 integrity hash.');
        formAddEv.style.display = 'none';
        document.getElementById('new-ev-hash').value = '';
        document.getElementById('new-ev-desc').value = '';
        loadAllData();
      } catch (err) {
        showError(err.message || 'Failed to add evidence.');
      }
    });
  }

  // 5. NIST & ATT&CK Tab
  function populateNistTab() {
    if (!incident) return;
    const currentPhase = incident.current_nist_phase || 'Detection & Analysis';
    const badgeNist = document.getElementById('badge-nist-current');
    if (badgeNist) badgeNist.textContent = currentPhase;

    const selNist = document.getElementById('select-nist-phase');
    if (selNist) selNist.value = currentPhase;

    const labelVector = document.getElementById('label-attack-vector');
    if (labelVector) labelVector.textContent = incident.attack_type || '—';

    const labelMitre = document.getElementById('label-mitre-active');
    if (labelMitre) labelMitre.textContent = incident.attack_type || '—';

    const labelMitreSrc = document.getElementById('label-mitre-source');
    if (labelMitreSrc) labelMitreSrc.textContent = `Source: ${incident.source || '—'}`;

    // History
    const historyContainer = document.getElementById('nist-history-container');
    if (historyContainer) {
      if (!Array.isArray(nistHistory) || nistHistory.length === 0) {
        historyContainer.innerHTML = '<div style="font-size: 12px; color: var(--text-muted);">No phase transitions recorded yet.</div>';
      } else {
        historyContainer.innerHTML = nistHistory
          .map((h) => `
            <div style="padding: 8px 10px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 3px; font-size: 12px;">
              <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <span>${escapeHtml(h.phase || '—')}</span>
                <span class="mono" style="color: var(--text-muted); font-weight: 400;">${safeDateString(h.timestamp, 'toLocaleTimeString', '—')}</span>
              </div>
              <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px;">
                Actor: ${escapeHtml(h.actor || 'system')} ${h.rationale ? `| Rationale: ${escapeHtml(h.rationale)}` : ''}
              </div>
            </div>
          `)
          .join('');
      }
    }

    // AI suggestion card inside ATT&CK
    const aiBox = document.getElementById('mitre-ai-suggestion-box');
    if (aiBox) {
      if (selectedAnalysis) {
        aiBox.style.display = 'block';
        const techniqueBadge = document.getElementById('badge-ai-technique');
        if (techniqueBadge) techniqueBadge.textContent = selectedAnalysis.attack_technique || '—';

        const techniqueName = document.getElementById('label-ai-technique-name');
        if (techniqueName) techniqueName.textContent = selectedAnalysis.attack_technique_name || selectedAnalysis.incident_type || '—';

        const techniqueStatus = document.getElementById('label-ai-technique-status');
        if (techniqueStatus) techniqueStatus.textContent = (selectedAnalysis.status || 'pending').toUpperCase();
      } else {
        aiBox.style.display = 'none';
      }
    }
  }

  const btnExecNist = document.getElementById('btn-execute-nist');
  if (btnExecNist) {
    btnExecNist.addEventListener('click', async () => {
      clearAlerts();
      const ph = document.getElementById('select-nist-phase').value;
      const rat = document.getElementById('text-nist-rationale').value.trim();

      try {
        await window.api.updateNistPhase(incidentId, ph, rat || undefined);
        showSuccess(`Transitioned to NIST phase '${ph}'.`);
        document.getElementById('text-nist-rationale').value = '';
        loadAllData();
      } catch (err) {
        showError(err.message || 'NIST phase transition failed.');
      }
    });
  }

  // 6. AI Analysis Tab
  function populateAiTab() {
    const countAi = document.getElementById('count-ai');
    if (countAi) countAi.textContent = (Array.isArray(aiAnalyses) && aiAnalyses.length > 0) ? `(${aiAnalyses.length})` : '';

    const selectHistory = document.getElementById('select-ai-history');
    const aiEmpty = document.getElementById('ai-empty');
    const aiPanel = document.getElementById('ai-panel');

    if (!Array.isArray(aiAnalyses) || aiAnalyses.length === 0) {
      if (aiEmpty) aiEmpty.style.display = 'block';
      if (aiPanel) aiPanel.style.display = 'none';
      if (selectHistory) selectHistory.innerHTML = '<option value="">No analyses generated yet</option>';
      return;
    }

    if (aiEmpty) aiEmpty.style.display = 'none';
    if (aiPanel) aiPanel.style.display = 'block';

    if (selectHistory) {
      selectHistory.innerHTML = aiAnalyses
        .map((a) => `
          <option value="${a.id}">
            #${a.id} — ${escapeHtml(a.incident_type || 'Unknown')} (${escapeHtml(a.attack_technique || '—')}) [${escapeHtml((a.status || 'pending').toUpperCase())}]
          </option>
        `)
        .join('');
    }

    if (!selectedAnalysis && aiAnalyses.length > 0) {
      selectedAnalysis = aiAnalyses[0];
    }
    if (selectedAnalysis) {
      if (selectHistory) selectHistory.value = selectedAnalysis.id;
      renderAiRecord(selectedAnalysis);
    }
  }

  function renderAiRecord(record) {
    if (!record) return;

    const titleEl = document.getElementById('ai-record-title');
    if (titleEl) titleEl.textContent = `Analysis Record #${record.id}`;

    const statusBadge = document.getElementById('ai-status-badge');
    const statusVal = (record.status || 'pending').toLowerCase();
    if (statusBadge) {
      statusBadge.textContent = statusVal.toUpperCase();
      statusBadge.className = `badge ${
        statusVal === 'accepted' ? 'badge-ok' : statusVal === 'rejected' ? 'badge-p1' : statusVal === 'overridden' ? 'badge-p2' : 'badge-default'
      }`;
    }

    const providerBadge = document.getElementById('ai-provider-badge');
    if (providerBadge) providerBadge.textContent = `Provider: ${escapeHtml(record.provider || 'gemini')}`;

    const metaLine = document.getElementById('ai-metadata-line');
    if (metaLine) {
      let meta = `Generated: ${safeDateString(record.created_at, 'toLocaleString', '—')}`;
      if (record.reviewed_by) {
        meta += ` | Reviewed by: ${escapeHtml(record.reviewed_by)} at ${safeDateString(record.reviewed_at, 'toLocaleTimeString', '—')}`;
      }
      metaLine.textContent = meta;
    }

    const typeEl = document.getElementById('ai-suggested-type');
    if (typeEl) typeEl.textContent = record.incident_type || '—';

    const techEl = document.getElementById('ai-suggested-technique');
    if (techEl) {
      techEl.textContent = `${record.attack_technique || '—'} (${record.attack_technique_name || record.incident_type || 'Scenario'})`;
    }

    const sevCont = document.getElementById('ai-severity-badge-container');
    if (sevCont) sevCont.innerHTML = renderSeverityBadge(record.suggested_severity);

    const phaseEl = document.getElementById('ai-suggested-phase');
    if (phaseEl) phaseEl.textContent = record.suggested_nist_phase || '—';

    const reasonEl = document.getElementById('ai-reason');
    if (reasonEl) reasonEl.textContent = record.reason || '—';

    const listActions = document.getElementById('ai-actions-list');
    if (listActions) {
      const actions = Array.isArray(record.recommended_actions) ? record.recommended_actions : [];
      listActions.innerHTML = actions.length > 0
        ? actions.map((act) => `<li>${escapeHtml(act)}</li>`).join('')
        : '<li>No specific actions recommended.</li>';
    }

    // Pre-fill override form defaults
    const ovType = document.getElementById('override-type');
    if (ovType) ovType.value = record.incident_type || '';

    const ovTech = document.getElementById('override-technique');
    if (ovTech) ovTech.value = record.attack_technique || '';

    const ovPhase = document.getElementById('override-phase');
    if (ovPhase) ovPhase.value = record.suggested_nist_phase || 'Detection & Analysis';

    const ovSev = document.getElementById('override-severity');
    if (ovSev) ovSev.value = record.suggested_severity || 'Medium';

    // Disable Accept if already accepted
    const btnAccept = document.getElementById('btn-ai-accept');
    if (btnAccept) btnAccept.disabled = (record.status === 'accepted');
  }

  // Switch Selected AI History
  const selAiHistory = document.getElementById('select-ai-history');
  if (selAiHistory) {
    selAiHistory.addEventListener('change', (e) => {
      const targetId = Number(e.target.value);
      const rec = aiAnalyses.find((a) => a.id === targetId);
      if (rec) {
        selectedAnalysis = rec;
        renderAiRecord(rec);
        populateNistTab();
      }
    });
  }

  // Run / Re-Analyze AI
  async function triggerAiRun(isReanalysis = false) {
    clearAlerts();
    const btn = isReanalysis ? document.getElementById('btn-reanalyze-ai') : document.getElementById('btn-run-ai');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Analyzing...';
    }

    try {
      const res = isReanalysis
        ? await window.api.reanalyzeIncident(incidentId)
        : await window.api.analyzeIncident(incidentId);

      showSuccess(isReanalysis ? 'Re-analysis executed. Previous records preserved.' : 'AI analysis generated.');
      selectedAnalysis = res;
      loadAllData();
    } catch (err) {
      showError(err.message || 'AI analysis failed.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = isReanalysis ? 'Re-Analyze Incident' : 'Run Analysis';
      }
    }
  }

  const btnRunAi = document.getElementById('btn-run-ai');
  if (btnRunAi) btnRunAi.addEventListener('click', () => triggerAiRun(false));

  const btnInitAi = document.getElementById('btn-init-ai');
  if (btnInitAi) btnInitAi.addEventListener('click', () => triggerAiRun(false));

  const btnReanalyzeAi = document.getElementById('btn-reanalyze-ai');
  if (btnReanalyzeAi) btnReanalyzeAi.addEventListener('click', () => triggerAiRun(true));

  // AI Human Review: Accept
  const btnAiAccept = document.getElementById('btn-ai-accept');
  if (btnAiAccept) {
    btnAiAccept.addEventListener('click', async () => {
      if (!selectedAnalysis) return;
      clearAlerts();

      try {
        const res = await window.api.reviewAiAnalysis(incidentId, {
          analysis_id: selectedAnalysis.id,
          decision: 'accept',
          apply_to_incident: true,
        });
        selectedAnalysis = res;
        showSuccess('AI suggestion accepted. NIST phase updated.');
        loadAllData();
      } catch (err) {
        showError(err.message || 'Failed to accept suggestion.');
      }
    });
  }

  // AI Human Review: Reject
  const btnAiRejectToggle = document.getElementById('btn-ai-reject-toggle');
  const aiRejectBox = document.getElementById('ai-reject-box');
  const btnAiCancelReject = document.getElementById('btn-ai-cancel-reject');
  const btnAiConfirmReject = document.getElementById('btn-ai-confirm-reject');
  const aiOverrideBox = document.getElementById('ai-override-box');

  if (btnAiRejectToggle && aiRejectBox) {
    btnAiRejectToggle.addEventListener('click', () => {
      aiRejectBox.style.display = aiRejectBox.style.display === 'none' ? 'block' : 'none';
      if (aiOverrideBox) aiOverrideBox.style.display = 'none';
    });
  }
  if (btnAiCancelReject && aiRejectBox) {
    btnAiCancelReject.addEventListener('click', () => {
      aiRejectBox.style.display = 'none';
    });
  }

  if (btnAiConfirmReject) {
    btnAiConfirmReject.addEventListener('click', async () => {
      if (!selectedAnalysis) return;
      clearAlerts();
      const reason = document.getElementById('ai-reject-reason').value.trim();

      try {
        const res = await window.api.reviewAiAnalysis(incidentId, {
          analysis_id: selectedAnalysis.id,
          decision: 'reject',
          rejection_reason: reason || undefined,
          apply_to_incident: true,
        });
        selectedAnalysis = res;
        if (aiRejectBox) aiRejectBox.style.display = 'none';
        const rejectInput = document.getElementById('ai-reject-reason');
        if (rejectInput) rejectInput.value = '';
        showSuccess('AI suggestion rejected.');
        loadAllData();
      } catch (err) {
        showError(err.message || 'Failed to reject suggestion.');
      }
    });
  }

  // AI Human Review: Override
  const btnAiOverrideToggle = document.getElementById('btn-ai-override-toggle');
  const btnAiCancelOverride = document.getElementById('btn-ai-cancel-override');
  const btnAiConfirmOverride = document.getElementById('btn-ai-confirm-override');

  if (btnAiOverrideToggle && aiOverrideBox) {
    btnAiOverrideToggle.addEventListener('click', () => {
      aiOverrideBox.style.display = aiOverrideBox.style.display === 'none' ? 'block' : 'none';
      if (aiRejectBox) aiRejectBox.style.display = 'none';
    });
  }
  if (btnAiCancelOverride && aiOverrideBox) {
    btnAiCancelOverride.addEventListener('click', () => {
      aiOverrideBox.style.display = 'none';
    });
  }

  if (btnAiConfirmOverride) {
    btnAiConfirmOverride.addEventListener('click', async () => {
      if (!selectedAnalysis) return;
      clearAlerts();

      const override_values = {
        incident_type: document.getElementById('override-type').value.trim(),
        attack_technique: document.getElementById('override-technique').value.trim(),
        suggested_nist_phase: document.getElementById('override-phase').value,
        suggested_severity: document.getElementById('override-severity').value,
      };

      try {
        const res = await window.api.reviewAiAnalysis(incidentId, {
          analysis_id: selectedAnalysis.id,
          decision: 'override',
          override_values,
          apply_to_incident: true,
        });
        selectedAnalysis = res;
        if (aiOverrideBox) aiOverrideBox.style.display = 'none';
        showSuccess('Custom analyst override applied.');
        loadAllData();
      } catch (err) {
        showError(err.message || 'Failed to apply override.');
      }
    });
  }

  // 7. Clock Tab
  function populateClockTab() {
    const badge = document.getElementById('clock-compliance-badge');
    const detectedElem = document.getElementById('clock-full-detected');
    const elapsedElem = document.getElementById('clock-full-elapsed');
    const deadlineElem = document.getElementById('clock-full-deadline');
    const complianceElem = document.getElementById('clock-full-compliance');

    if (!clock) {
      if (badge) {
        badge.textContent = 'Unavailable';
        badge.className = 'badge badge-default';
      }
      renderClockWidget('clock-full-widget', null);
      if (detectedElem) detectedElem.textContent = '—';
      if (elapsedElem) elapsedElem.textContent = 'Elapsed Time: —';
      if (deadlineElem) deadlineElem.textContent = '—';
      if (complianceElem) complianceElem.innerHTML = 'Compliance Flag: <strong>Unavailable</strong>';
      return;
    }

    const isExpired = Boolean(
      clock.is_expired ??
      clock.is_overdue ??
      ((clock.remaining_seconds != null ? clock.remaining_seconds : clock.time_remaining_seconds) <= 0)
    );
    const complianceStatus = clock.compliance_status || clock.status || (isExpired ? 'EXPIRED' : 'COMPLIANT');

    if (badge) {
      badge.textContent = complianceStatus;
      badge.className = `badge ${isExpired ? 'badge-overdue' : 'badge-ok'}`;
    }

    renderClockWidget('clock-full-widget', clock);

    if (detectedElem) {
      detectedElem.textContent = safeDateString(clock.detected_at, 'toUTCString', '—');
    }

    let elapsedHours = null;
    if (typeof clock.elapsed_seconds === 'number' && Number.isFinite(clock.elapsed_seconds)) {
      elapsedHours = clock.elapsed_seconds / 3600;
    } else if (typeof clock.hours_elapsed === 'number' && Number.isFinite(clock.hours_elapsed)) {
      elapsedHours = clock.hours_elapsed;
    } else if (clock.detected_at) {
      const dt = new Date(clock.detected_at).getTime();
      if (Number.isFinite(dt)) {
        elapsedHours = Math.max(0, (Date.now() - dt) / (1000 * 3600));
      }
    }

    if (elapsedElem) {
      const formattedElapsed = elapsedHours !== null ? `${safeToFixed(elapsedHours, 1, '0.0')} hours` : '—';
      elapsedElem.textContent = `Elapsed Time: ${formattedElapsed}`;
    }

    if (deadlineElem) {
      deadlineElem.textContent = safeDateString(clock.deadline_at, 'toUTCString', '—');
      deadlineElem.style.color = isExpired ? '#b91c1c' : 'inherit';
    }

    if (complianceElem) {
      complianceElem.innerHTML = `Compliance Flag: <strong>${escapeHtml(complianceStatus)}</strong>`;
    }
  }

  // Initial Load
  loadAllData();
});
