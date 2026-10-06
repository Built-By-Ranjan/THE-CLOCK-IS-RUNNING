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
    alertError.textContent = msg;
    alertError.style.display = 'block';
    alertSuccess.style.display = 'none';
  }

  function showSuccess(msg) {
    alertSuccess.textContent = msg;
    alertSuccess.style.display = 'block';
    alertError.style.display = 'none';
  }

  function clearAlerts() {
    alertError.style.display = 'none';
    alertSuccess.style.display = 'none';
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
  let clockTimerInterval = null;

  // Badge render helpers
  function renderPriorityBadge(priority) {
    const map = { P1: 'badge-p1', P2: 'badge-p2', P3: 'badge-p3', P4: 'badge-p4' };
    return `<span class="badge ${map[priority] || 'badge-default'}">${priority}</span>`;
  }

  function renderStatusBadge(status) {
    return `<span class="badge badge-status">${status}</span>`;
  }

  function renderSeverityBadge(severity) {
    if (!severity) return '<span class="badge badge-default">Not Determined</span>';
    let c = 'badge-default';
    if (severity === 'Critical') c = 'badge-p1';
    else if (severity === 'High') c = 'badge-p2';
    else if (severity === 'Medium') c = 'badge-p3';
    else if (severity === 'Low') c = 'badge-p4';
    return `<span class="badge ${c}">${severity}</span>`;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
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
    if (!container || !clockData) return;

    if (clockTimerInterval) clearInterval(clockTimerInterval);

    let secondsLeft = clockData.time_remaining_seconds;

    function updateDisplay() {
      const hours = Math.floor(secondsLeft / 3600);
      const minutes = Math.floor((secondsLeft % 3600) / 60);
      const seconds = secondsLeft % 60;
      const isOverdue = clockData.is_overdue || secondsLeft <= 0;

      const timerText = isOverdue
        ? '<span style="color: #b91c1c;">OVERDUE</span>'
        : `<span>${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</span>`;

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
            <div>Status: <strong style="color: ${isOverdue ? '#b91c1c' : '#166534'};">${clockData.compliance_status}</strong></div>
            <div style="color: var(--text-muted);">Deadline: ${new Date(clockData.deadline_at).toLocaleTimeString()}</div>
          </div>
        </div>
      `;
    }

    updateDisplay();
    clockTimerInterval = setInterval(() => {
      if (secondsLeft > 0) {
        secondsLeft -= 1;
        updateDisplay();
      }
    }, 1000);
  }

  // Load All Incident Data
  async function loadAllData() {
    clearAlerts();
    try {
      const [inc, clk, tl, ev, nist, ind, ai] = await Promise.all([
        window.api.getIncident(incidentId),
        window.api.getClock(incidentId).catch(() => null),
        window.api.getTimeline(incidentId).catch(() => []),
        window.api.getEvidence(incidentId).catch(() => []),
        window.api.getNistHistory(incidentId).catch(() => []),
        window.api.getIndicators(incidentId).catch(() => []),
        window.api.getAiAnalyses(incidentId).catch(() => []),
      ]);

      incident = inc;
      clock = clk;
      timeline = tl;
      evidenceList = ev;
      nistHistory = nist;
      indicators = ind;
      aiAnalyses = ai;

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
    document.getElementById('label-incident-id').textContent = `#${incident.id}`;
    document.getElementById('label-incident-title').textContent = incident.title;
    document.getElementById('badge-status-container').innerHTML = renderStatusBadge(incident.status);
    document.getElementById('badge-priority-container').innerHTML = renderPriorityBadge(incident.priority);
    document.getElementById('label-attack-type').textContent = incident.attack_type;
    document.getElementById('label-detected-at').textContent = `Detected: ${new Date(incident.detected_at).toLocaleString()}`;

    if (clock) {
      renderClockWidget('clock-widget-container', clock);
    }
  }

  // 2. Overview Tab
  function populateOverviewTab() {
    document.getElementById('label-source').textContent = `Source: ${incident.source}`;
    document.getElementById('label-description').textContent = incident.description;

    document.getElementById('select-status').value = incident.status;
    document.getElementById('select-priority').value = incident.priority;

    // Assets
    const listAssets = document.getElementById('list-assets');
    if (incident.affected_assets && incident.affected_assets.length > 0) {
      listAssets.innerHTML = incident.affected_assets
        .map((a) => `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(a.asset_name)} (${escapeHtml(a.asset_type)})</span>`)
        .join('');
    } else {
      listAssets.innerHTML = '<span style="font-size: 12px; color: var(--text-muted);">None recorded</span>';
    }

    // Users
    const listUsers = document.getElementById('list-users');
    if (incident.affected_users && incident.affected_users.length > 0) {
      listUsers.innerHTML = incident.affected_users
        .map((u) => `<span class="badge badge-default mono" style="font-size: 12px;">${escapeHtml(u.username)} &lt;${escapeHtml(u.email)}&gt;</span>`)
        .join('');
    } else {
      listUsers.innerHTML = '<span style="font-size: 12px; color: var(--text-muted);">None recorded</span>';
    }

    // Indicators
    const iocRows = document.getElementById('ioc-rows');
    if (indicators.length === 0) {
      iocRows.innerHTML = '<tr><td colspan="3" style="color: var(--text-muted); text-align: center;">No IoCs recorded</td></tr>';
    } else {
      iocRows.innerHTML = indicators
        .map((ind) => `
          <tr>
            <td style="width: 80px; font-weight: 600;">${ind.type.toUpperCase()}</td>
            <td class="mono">${escapeHtml(ind.value)}</td>
            <td style="color: var(--text-muted);">${escapeHtml(ind.description || '—')}</td>
          </tr>
        `)
        .join('');
    }
  }

  // Overview Action Listeners
  document.getElementById('btn-apply-status').addEventListener('click', async () => {
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

  document.getElementById('btn-apply-priority').addEventListener('click', async () => {
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

  // Toggle Add IoC
  const btnToggleAddIoc = document.getElementById('btn-toggle-add-ioc');
  const formAddIoc = document.getElementById('form-add-ioc');
  const btnCancelIoc = document.getElementById('btn-cancel-ioc');

  btnToggleAddIoc.addEventListener('click', () => {
    formAddIoc.style.display = formAddIoc.style.display === 'none' ? 'block' : 'none';
  });
  btnCancelIoc.addEventListener('click', () => {
    formAddIoc.style.display = 'none';
  });

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

  // 3. Timeline Tab
  function populateTimelineTab() {
    document.getElementById('count-timeline').textContent = timeline.length;
    const tlRows = document.getElementById('timeline-rows');
    const tlEmpty = document.getElementById('timeline-empty');
    const tlWrapper = document.getElementById('timeline-table-wrapper');

    if (timeline.length === 0) {
      tlEmpty.style.display = 'block';
      tlWrapper.style.display = 'none';
      return;
    }

    tlEmpty.style.display = 'none';
    tlWrapper.style.display = 'block';

    tlRows.innerHTML = timeline
      .map((ev) => {
        const trans = ev.previous_value && ev.new_value
          ? `<span>${escapeHtml(ev.previous_value)} &rarr; <strong>${escapeHtml(ev.new_value)}</strong></span>`
          : ev.new_value ? `<span><strong>${escapeHtml(ev.new_value)}</strong></span>` : '—';

        return `
          <tr>
            <td class="mono" style="font-size: 12px; color: var(--text-muted);">${new Date(ev.timestamp).toLocaleString()}</td>
            <td style="font-weight: 600;">${escapeHtml(ev.event)}</td>
            <td class="mono" style="font-size: 12px;">${escapeHtml(ev.actor)}</td>
            <td><span class="badge badge-default" style="font-size: 10px;">${escapeHtml(ev.source)}</span></td>
            <td style="color: var(--text-secondary);">${escapeHtml(ev.description)}</td>
            <td class="mono" style="font-size: 11px; color: var(--text-muted);">${trans}</td>
          </tr>
        `;
      })
      .join('');
  }

  // 4. Evidence Tab
  function populateEvidenceTab() {
    document.getElementById('count-evidence').textContent = evidenceList.length;
    const evRows = document.getElementById('evidence-rows');
    const evEmpty = document.getElementById('evidence-empty');
    const evWrapper = document.getElementById('evidence-table-wrapper');

    if (evidenceList.length === 0) {
      evEmpty.style.display = 'block';
      evWrapper.style.display = 'none';
      return;
    }

    evEmpty.style.display = 'none';
    evWrapper.style.display = 'block';

    evRows.innerHTML = evidenceList
      .map((item) => `
        <tr>
          <td class="mono">#${item.id}</td>
          <td style="font-weight: 600;">${escapeHtml(item.evidence_type)}</td>
          <td>${escapeHtml(item.source)}</td>
          <td class="mono">${escapeHtml(item.collector)}</td>
          <td class="mono" style="font-size: 11px; color: var(--text-secondary);">${escapeHtml(item.sha256_hash)}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${new Date(item.collected_at).toLocaleString()}</td>
          <td style="font-size: 12px;">${escapeHtml(item.description || '—')}</td>
        </tr>
      `)
      .join('');
  }

  const btnToggleAddEv = document.getElementById('btn-toggle-add-evidence');
  const formAddEv = document.getElementById('form-add-evidence');
  const btnCancelEv = document.getElementById('btn-cancel-evidence');

  btnToggleAddEv.addEventListener('click', () => {
    formAddEv.style.display = formAddEv.style.display === 'none' ? 'block' : 'none';
  });
  btnCancelEv.addEventListener('click', () => {
    formAddEv.style.display = 'none';
  });

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

  // 5. NIST & ATT&CK Tab
  function populateNistTab() {
    document.getElementById('badge-nist-current').textContent = incident.current_nist_phase;
    document.getElementById('select-nist-phase').value = incident.current_nist_phase;
    document.getElementById('label-attack-vector').textContent = incident.attack_type;
    document.getElementById('label-mitre-active').textContent = incident.attack_type;
    document.getElementById('label-mitre-source').textContent = `Source: ${incident.source}`;

    // History
    const historyContainer = document.getElementById('nist-history-container');
    if (nistHistory.length === 0) {
      historyContainer.innerHTML = '<div style="font-size: 12px; color: var(--text-muted);">No phase transitions recorded yet.</div>';
    } else {
      historyContainer.innerHTML = nistHistory
        .map((h) => `
          <div style="padding: 8px 10px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 3px; font-size: 12px;">
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
              <span>${escapeHtml(h.phase)}</span>
              <span class="mono" style="color: var(--text-muted); font-weight: 400;">${new Date(h.timestamp).toLocaleTimeString()}</span>
            </div>
            <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px;">
              Actor: ${escapeHtml(h.actor)} ${h.rationale ? `| Rationale: ${escapeHtml(h.rationale)}` : ''}
            </div>
          </div>
        `)
        .join('');
    }

    // AI suggestion card inside ATT&CK
    const aiBox = document.getElementById('mitre-ai-suggestion-box');
    if (selectedAnalysis) {
      aiBox.style.display = 'block';
      document.getElementById('badge-ai-technique').textContent = selectedAnalysis.attack_technique;
      document.getElementById('label-ai-technique-name').textContent = selectedAnalysis.attack_technique_name || selectedAnalysis.incident_type;
      document.getElementById('label-ai-technique-status').textContent = selectedAnalysis.status.toUpperCase();
    } else {
      aiBox.style.display = 'none';
    }
  }

  document.getElementById('btn-execute-nist').addEventListener('click', async () => {
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

  // 6. AI Analysis Tab
  function populateAiTab() {
    const countAi = document.getElementById('count-ai');
    countAi.textContent = aiAnalyses.length > 0 ? `(${aiAnalyses.length})` : '';

    const selectHistory = document.getElementById('select-ai-history');
    const aiEmpty = document.getElementById('ai-empty');
    const aiPanel = document.getElementById('ai-panel');

    if (aiAnalyses.length === 0) {
      aiEmpty.style.display = 'block';
      aiPanel.style.display = 'none';
      selectHistory.innerHTML = '<option value="">No analyses generated yet</option>';
      return;
    }

    aiEmpty.style.display = 'none';
    aiPanel.style.display = 'block';

    selectHistory.innerHTML = aiAnalyses
      .map((a) => `
        <option value="${a.id}">
          #${a.id} — ${escapeHtml(a.incident_type)} (${escapeHtml(a.attack_technique)}) [${a.status.toUpperCase()}]
        </option>
      `)
      .join('');

    if (!selectedAnalysis && aiAnalyses.length > 0) {
      selectedAnalysis = aiAnalyses[0];
    }
    if (selectedAnalysis) {
      selectHistory.value = selectedAnalysis.id;
      renderAiRecord(selectedAnalysis);
    }
  }

  function renderAiRecord(record) {
    document.getElementById('ai-record-title').textContent = `Analysis Record #${record.id}`;
    document.getElementById('ai-status-badge').textContent = record.status.toUpperCase();
    document.getElementById('ai-status-badge').className = `badge ${
      record.status === 'accepted' ? 'badge-ok' : record.status === 'rejected' ? 'badge-p1' : record.status === 'overridden' ? 'badge-p2' : 'badge-default'
    }`;
    document.getElementById('ai-provider-badge').textContent = `Provider: ${record.provider}`;

    let meta = `Generated: ${new Date(record.created_at).toLocaleString()}`;
    if (record.reviewed_by) {
      meta += ` | Reviewed by: ${escapeHtml(record.reviewed_by)} at ${new Date(record.reviewed_at).toLocaleTimeString()}`;
    }
    document.getElementById('ai-metadata-line').textContent = meta;

    document.getElementById('ai-suggested-type').textContent = record.incident_type;
    document.getElementById('ai-suggested-technique').textContent = `${record.attack_technique} (${record.attack_technique_name || 'Scenario'})`;

    document.getElementById('ai-severity-badge-container').innerHTML = renderSeverityBadge(record.suggested_severity);
    document.getElementById('ai-suggested-phase').textContent = record.suggested_nist_phase;

    document.getElementById('ai-reason').textContent = record.reason;

    const listActions = document.getElementById('ai-actions-list');
    listActions.innerHTML = (record.recommended_actions || [])
      .map((act) => `<li>${escapeHtml(act)}</li>`)
      .join('');

    // Pre-fill override form defaults
    document.getElementById('override-type').value = record.incident_type;
    document.getElementById('override-technique').value = record.attack_technique;
    document.getElementById('override-phase').value = record.suggested_nist_phase;
    document.getElementById('override-severity').value = record.suggested_severity;

    // Disable Accept if already accepted
    document.getElementById('btn-ai-accept').disabled = record.status === 'accepted';
  }

  // Switch Selected AI History
  document.getElementById('select-ai-history').addEventListener('change', (e) => {
    const targetId = Number(e.target.value);
    const rec = aiAnalyses.find((a) => a.id === targetId);
    if (rec) {
      selectedAnalysis = rec;
      renderAiRecord(rec);
      populateNistTab();
    }
  });

  // Run / Re-Analyze AI
  async function triggerAiRun(isReanalysis = false) {
    clearAlerts();
    const btn = isReanalysis ? document.getElementById('btn-reanalyze-ai') : document.getElementById('btn-run-ai');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';

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
      btn.disabled = false;
      btn.textContent = isReanalysis ? 'Re-Analyze Incident' : 'Run Analysis';
    }
  }

  document.getElementById('btn-run-ai').addEventListener('click', () => triggerAiRun(false));
  document.getElementById('btn-init-ai').addEventListener('click', () => triggerAiRun(false));
  document.getElementById('btn-reanalyze-ai').addEventListener('click', () => triggerAiRun(true));

  // AI Human Review: Accept
  document.getElementById('btn-ai-accept').addEventListener('click', async () => {
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

  // AI Human Review: Reject
  const btnAiRejectToggle = document.getElementById('btn-ai-reject-toggle');
  const aiRejectBox = document.getElementById('ai-reject-box');
  const btnAiCancelReject = document.getElementById('btn-ai-cancel-reject');
  const btnAiConfirmReject = document.getElementById('btn-ai-confirm-reject');

  btnAiRejectToggle.addEventListener('click', () => {
    aiRejectBox.style.display = aiRejectBox.style.display === 'none' ? 'block' : 'none';
    document.getElementById('ai-override-box').style.display = 'none';
  });
  btnAiCancelReject.addEventListener('click', () => {
    aiRejectBox.style.display = 'none';
  });

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
      aiRejectBox.style.display = 'none';
      document.getElementById('ai-reject-reason').value = '';
      showSuccess('AI suggestion rejected.');
      loadAllData();
    } catch (err) {
      showError(err.message || 'Failed to reject suggestion.');
    }
  });

  // AI Human Review: Override
  const btnAiOverrideToggle = document.getElementById('btn-ai-override-toggle');
  const aiOverrideBox = document.getElementById('ai-override-box');
  const btnAiCancelOverride = document.getElementById('btn-ai-cancel-override');
  const btnAiConfirmOverride = document.getElementById('btn-ai-confirm-override');

  btnAiOverrideToggle.addEventListener('click', () => {
    aiOverrideBox.style.display = aiOverrideBox.style.display === 'none' ? 'block' : 'none';
    document.getElementById('ai-reject-box').style.display = 'none';
  });
  btnAiCancelOverride.addEventListener('click', () => {
    aiOverrideBox.style.display = 'none';
  });

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
      aiOverrideBox.style.display = 'none';
      showSuccess('Custom analyst override applied.');
      loadAllData();
    } catch (err) {
      showError(err.message || 'Failed to apply override.');
    }
  });

  // 7. Clock Tab
  function populateClockTab() {
    if (!clock) return;
    document.getElementById('clock-compliance-badge').textContent = clock.compliance_status;
    document.getElementById('clock-compliance-badge').className = `badge ${clock.is_overdue ? 'badge-overdue' : 'badge-ok'}`;

    renderClockWidget('clock-full-widget', clock);

    document.getElementById('clock-full-detected').textContent = new Date(clock.detected_at).toUTCString();
    document.getElementById('clock-full-elapsed').textContent = `Elapsed Time: ${clock.hours_elapsed.toFixed(1)} hours`;

    document.getElementById('clock-full-deadline').textContent = new Date(clock.deadline_at).toUTCString();
    document.getElementById('clock-full-deadline').style.color = clock.is_overdue ? '#b91c1c' : 'inherit';
    document.getElementById('clock-full-compliance').innerHTML = `Compliance Flag: <strong>${clock.compliance_status}</strong>`;
  }

  // Initial Load
  loadAllData();
});
