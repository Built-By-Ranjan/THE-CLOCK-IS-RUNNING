// Attack Simulator Controller (Vanilla JS)

document.addEventListener('DOMContentLoaded', () => {
  const simError = document.getElementById('sim-error');
  const simStatus = document.getElementById('sim-status');
  const simResultBox = document.getElementById('sim-result-box');
  const resIncidentId = document.getElementById('res-incident-id');
  const resIncidentTitle = document.getElementById('res-incident-title');
  const resIncidentDesc = document.getElementById('res-incident-desc');
  const btnOpenIncident = document.getElementById('btn-open-incident');

  const btnBruteforce = document.getElementById('btn-sim-bruteforce');
  const btnPhishing = document.getElementById('btn-sim-phishing');
  const btnPowershell = document.getElementById('btn-sim-powershell');
  const btnDdos = document.getElementById('btn-sim-ddos');

  function showError(msg) {
    simError.textContent = msg;
    simError.style.display = 'block';
    simStatus.style.display = 'none';
  }

  function showStatus(msg) {
    simStatus.textContent = msg;
    simStatus.style.display = 'block';
    simError.style.display = 'none';
  }

  function clearAlerts() {
    simError.style.display = 'none';
    simStatus.style.display = 'none';
    if (simResultBox) simResultBox.style.display = 'none';
  }

  async function launchSimulation(scenario, scenarioName) {
    clearAlerts();

    // PowerShell and DDoS do not currently have backend simulation endpoints
    if (scenario === 'powershell' || scenario === 'ddos') {
      showError(`Coming Soon: Backend simulation endpoint is currently unavailable for ${scenarioName}. Available endpoints: Brute Force, Phishing.`);
      return;
    }

    const btn = scenario === 'brute-force' ? btnBruteforce : btnPhishing;
    btn.disabled = true;
    btn.textContent = 'Launching...';

    showStatus(`Initiating controlled ${scenarioName} simulation on backend...`);

    try {
      const res = await window.api.triggerSimulation(scenario);

      if (res && res.incident_id) {
        simStatus.style.display = 'none';
        if (resIncidentId) resIncidentId.textContent = `#${res.incident_id}`;
        if (resIncidentTitle) resIncidentTitle.textContent = res.title || scenarioName;
        if (resIncidentDesc) {
          resIncidentDesc.textContent = `Attack Vector: ${res.attack_type || scenarioName}. Priority: ${res.priority || 'P1'}. 72h clock activated.`;
        }
        if (btnOpenIncident) {
          btnOpenIncident.href = `incident.html?id=${res.incident_id}`;
        }
        if (simResultBox) {
          simResultBox.style.display = 'block';
        }
      } else {
        showError('Simulation executed but incident ID was not returned.');
      }
    } catch (err) {
      if (err.status === 404) {
        showError(`Simulation endpoint /simulations/${scenario} is not available on backend.`);
      } else {
        showError(err.message || `Failed to run ${scenarioName} simulation.`);
      }
    } finally {
      btn.disabled = false;
      btn.textContent = 'Run Simulation';
    }
  }

  btnBruteforce.addEventListener('click', () => launchSimulation('brute-force', 'Brute Force'));
  btnPhishing.addEventListener('click', () => launchSimulation('phishing', 'Phishing'));
  btnPowershell.addEventListener('click', () => launchSimulation('powershell', 'PowerShell Execution'));
  btnDdos.addEventListener('click', () => launchSimulation('ddos', 'DDoS'));
});
