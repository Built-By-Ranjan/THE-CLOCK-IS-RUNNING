// Centralized API Client for THE-CLOCK-IS-RUNNING
// Connects directly to the existing FastAPI backend without frameworks.

const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE}${endpoint}`;
  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new ApiError(`Network connection to ${API_BASE} failed: ${err.message}`, 0);
  }

  if (response.status === 204) {
    return {};
  }

  let data;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorDetail =
      (data && typeof data === 'object' && (data.detail || data.error || data.message)) ||
      (typeof data === 'string' && data) ||
      `HTTP Error ${response.status}`;
    throw new ApiError(
      typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail),
      response.status,
      data
    );
  }

  return data;
}

const api = {
  // Authentication & Email OTP MFA
  async login(username, password) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },

  async verifyMfa(challenge_id, otp) {
    return request('/auth/mfa/verify', {
      method: 'POST',
      body: JSON.stringify({ challenge_id, otp }),
    });
  },

  async resendMfa(challenge_id) {
    return request('/auth/mfa/resend', {
      method: 'POST',
      body: JSON.stringify({ challenge_id }),
    });
  },

  async getMe() {
    return request('/auth/me');
  },

  async register(username, email, password) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  },

  // Incidents
  async getIncidents(skip = 0, limit = 50, status, attack_type) {
    const params = new URLSearchParams();
    params.set('skip', skip.toString());
    params.set('limit', limit.toString());
    if (status) params.set('status', status);
    if (attack_type) params.set('attack_type', attack_type);
    return request(`/incidents?${params.toString()}`);
  },

  async getIncident(id) {
    return request(`/incidents/${id}`);
  },

  async updateIncident(id, data) {
    return request(`/incidents/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async getClock(id) {
    return request(`/incidents/${id}/clock`);
  },

  async getTimeline(id) {
    return request(`/incidents/${id}/timeline`);
  },

  async getIndicators(id) {
    return request(`/incidents/${id}/indicators`);
  },

  async addIndicator(id, indicator) {
    return request(`/incidents/${id}/indicators`, {
      method: 'POST',
      body: JSON.stringify(indicator),
    });
  },

  async getEvidence(id) {
    return request(`/incidents/${id}/evidence`);
  },

  async addEvidence(id, evidence) {
    return request(`/incidents/${id}/evidence`, {
      method: 'POST',
      body: JSON.stringify(evidence),
    });
  },

  async getNistHistory(id) {
    return request(`/incidents/${id}/nist-history`);
  },

  async updateNistPhase(id, phase, rationale) {
    return request(`/incidents/${id}/nist-phase`, {
      method: 'POST',
      body: JSON.stringify({ phase, rationale }),
    });
  },

  // AI Intelligence
  async analyzeIncident(id) {
    return request(`/incidents/${id}/ai/analyze`, { method: 'POST' });
  },

  async getAiAnalyses(id) {
    return request(`/incidents/${id}/ai/analyses`);
  },

  async getAiAnalysis(id, analysisId) {
    return request(`/incidents/${id}/ai/analysis/${analysisId}`);
  },

  async reanalyzeIncident(id) {
    return request(`/incidents/${id}/ai/reanalyze`, { method: 'POST' });
  },

  async reviewAiAnalysis(id, reviewData) {
    return request(`/incidents/${id}/ai/review`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  },

  // Attack Simulations
  async triggerSimulation(scenario) {
    return request(`/simulations/${scenario}`, { method: 'POST' });
  },
};

window.api = api;
window.ApiError = ApiError;
