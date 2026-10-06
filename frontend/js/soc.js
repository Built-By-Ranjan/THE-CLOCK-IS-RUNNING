// SOC Dashboard Operations Controller

document.addEventListener('DOMContentLoaded', async () => {
  // Enforce SOC authentication
  const authenticated = await window.auth.requireAuth();
  if (!authenticated) return;

  window.auth.renderHeaderUser('header-user-info');

  const btnRefresh = document.getElementById('btn-refresh');
  const inputSearch = document.getElementById('input-search');
  const filterStatus = document.getElementById('filter-status');
  const filterAttack = document.getElementById('filter-attack');

  const socError = document.getElementById('soc-error');
  const tableLoading = document.getElementById('table-loading');
  const tableEmpty = document.getElementById('table-empty');
  const tableWrapper = document.getElementById('table-wrapper');
  const incidentRows = document.getElementById('incident-rows');
  const labelTableCount = document.getElementById('label-table-count');

  const statTotal = document.getElementById('stat-total');
  const statP1 = document.getElementById('stat-p1');
  const statP2 = document.getElementById('stat-p2');
  const statOpen = document.getElementById('stat-open');
  const statContained = document.getElementById('stat-contained');

  let allIncidents = [];

  function renderPriorityBadge(priority) {
    const map = {
      P1: 'badge-p1',
      P2: 'badge-p2',
      P3: 'badge-p3',
      P4: 'badge-p4',
    };
    return `<span class="badge ${map[priority] || 'badge-default'}">${priority}</span>`;
  }

  function renderStatusBadge(status) {
    return `<span class="badge badge-status">${escapeHtml(status)}</span>`;
  }

  function renderTableRows(items) {
    if (items.length === 0) {
      incidentRows.innerHTML = '';
      tableWrapper.style.display = 'none';
      tableEmpty.style.display = 'block';
      labelTableCount.textContent = '0 incidents match criteria';
      return;
    }

    tableEmpty.style.display = 'none';
    tableWrapper.style.display = 'block';
    labelTableCount.textContent = `Showing ${items.length} incident${items.length === 1 ? '' : 's'}`;

    incidentRows.innerHTML = '';
    items.forEach((inc) => {
      const detected = new Date(inc.detected_at).toLocaleString();
      const deadline = new Date(inc.deadline_at).toLocaleTimeString();
      const isPastDeadline = new Date(inc.deadline_at).getTime() < Date.now();

      const tr = document.createElement('tr');
      tr.style.cursor = 'pointer';
      tr.innerHTML = `
        <td class="mono" style="font-weight: 600;">#${inc.id}</td>
        <td style="font-weight: 500;">${escapeHtml(inc.title)}</td>
        <td>
          <span class="mono" style="font-size: 12px; background: var(--bg-secondary); padding: 2px 6px; border: 1px solid var(--border-color); border-radius: 3px;">
            ${escapeHtml(inc.attack_type)}
          </span>
        </td>
        <td>${renderStatusBadge(inc.status)}</td>
        <td>${renderPriorityBadge(inc.priority)}</td>
        <td style="font-size: 12px; color: var(--text-secondary);">${escapeHtml(inc.current_nist_phase)}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${detected}</td>
        <td style="font-size: 12px;">
          <span class="${isPastDeadline ? 'badge badge-overdue' : ''}">
            ${deadline}
          </span>
        </td>
        <td style="text-align: right;">
          <button class="btn btn-secondary btn-sm btn-inspect" data-id="${inc.id}">
            Inspect
          </button>
        </td>
      `;

      tr.addEventListener('click', () => {
        window.location.href = `incident.html?id=${inc.id}`;
      });

      const btnInspect = tr.querySelector('.btn-inspect');
      if (btnInspect) {
        btnInspect.addEventListener('click', (e) => {
          e.stopPropagation();
          window.location.href = `incident.html?id=${inc.id}`;
        });
      }

      incidentRows.appendChild(tr);
    });
  }

  function applySearchFilter() {
    const q = (inputSearch ? inputSearch.value : '').trim().toLowerCase();
    if (!q) {
      renderTableRows(allIncidents);
      return;
    }
    const filtered = allIncidents.filter((inc) => {
      const idMatch = String(inc.id).includes(q);
      const titleMatch = (inc.title || '').toLowerCase().includes(q);
      const attackMatch = (inc.attack_type || '').toLowerCase().includes(q);
      const descMatch = (inc.description || '').toLowerCase().includes(q);
      return idMatch || titleMatch || attackMatch || descMatch;
    });
    renderTableRows(filtered);
  }

  async function loadIncidents() {
    socError.style.display = 'none';
    tableLoading.style.display = 'block';
    tableEmpty.style.display = 'none';
    tableWrapper.style.display = 'none';
    labelTableCount.textContent = 'Loading incidents...';

    const statusVal = filterStatus.value || undefined;
    const attackVal = filterAttack.value || undefined;

    try {
      const res = await window.api.getIncidents(0, 100, statusVal, attackVal);
      allIncidents = res.items || [];

      // Update metrics based on currently fetched items
      statTotal.textContent = allIncidents.length;
      statP1.textContent = allIncidents.filter((i) => i.priority === 'P1').length;
      statP2.textContent = allIncidents.filter((i) => i.priority === 'P2').length;
      statOpen.textContent = allIncidents.filter((i) => i.status === 'Open' || i.status === 'Under Investigation').length;
      statContained.textContent = allIncidents.filter((i) => i.status === 'Contained' || i.status === 'Eradicated').length;

      tableLoading.style.display = 'none';
      applySearchFilter();
    } catch (err) {
      tableLoading.style.display = 'none';
      socError.textContent = err.message || 'Failed to load incidents from backend.';
      socError.style.display = 'block';
    }
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

  btnRefresh.addEventListener('click', loadIncidents);
  filterStatus.addEventListener('change', loadIncidents);
  filterAttack.addEventListener('change', loadIncidents);
  if (inputSearch) {
    inputSearch.addEventListener('input', applySearchFilter);
  }

  loadIncidents();
});
