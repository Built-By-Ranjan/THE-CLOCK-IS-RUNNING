// Authentication and Session Handling for SOC Dashboard

const auth = {
  getToken() {
    return localStorage.getItem('token');
  },

  setToken(token) {
    localStorage.setItem('token', token);
  },

  getUser() {
    try {
      const u = localStorage.getItem('user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  async requireAuth() {
    const token = this.getToken();
    if (!token) {
      const current = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `login.html?redirect=${current}`;
      return false;
    }

    try {
      const user = await window.api.getMe();
      this.setUser(user);
      return true;
    } catch (err) {
      console.warn('Session verification failed:', err);
      this.logout();
      return false;
    }
  },

  renderHeaderUser(targetElementId = 'header-user-info') {
    const container = document.getElementById(targetElementId);
    if (!container) return;

    const user = this.getUser();
    const username = user ? user.username : 'Analyst';

    container.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px; font-size: 13px;">
        <span style="color: var(--text-secondary);">
          Analyst: <strong>${username}</strong>
        </span>
        <button id="btn-logout" class="btn btn-secondary btn-sm">
          Sign Out
        </button>
      </div>
    `;

    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => this.logout());
    }
  },
};

window.auth = auth;
