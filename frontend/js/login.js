// Login & Registration Controller

document.addEventListener('DOMContentLoaded', () => {
  const formLogin = document.getElementById('form-login');
  const formRegister = document.getElementById('form-register');
  const alertError = document.getElementById('alert-error');
  const alertSuccess = document.getElementById('alert-success');

  const btnToggleRegister = document.getElementById('btn-toggle-register');
  const btnToggleLogin = document.getElementById('btn-toggle-login');

  const btnLoginSubmit = document.getElementById('btn-login-submit');
  const btnRegisterSubmit = document.getElementById('btn-register-submit');

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

  // Toggle forms
  btnToggleRegister.addEventListener('click', () => {
    clearAlerts();
    formLogin.style.display = 'none';
    formRegister.style.display = 'block';
  });

  btnToggleLogin.addEventListener('click', () => {
    clearAlerts();
    formRegister.style.display = 'none';
    formLogin.style.display = 'block';
  });

  // Handle Login submission
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlerts();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
      showError('Username and password are required.');
      return;
    }

    btnLoginSubmit.disabled = true;
    btnLoginSubmit.textContent = 'Authenticating...';

    try {
      const res = await window.api.login(username, password);

      if (res && res.challenge_id) {
        // MFA challenge initiated: store challenge metadata only
        sessionStorage.setItem('mfa_challenge_id', res.challenge_id);
        if (res.email_masked) {
          sessionStorage.setItem('mfa_email_masked', res.email_masked);
        }
        if (res.expires_in_seconds) {
          sessionStorage.setItem('mfa_expires_in_seconds', res.expires_in_seconds);
        }

        const urlParams = new URLSearchParams(window.location.search);
        const redirectParam = urlParams.get('redirect');
        const mfaUrl = redirectParam ? `mfa.html?redirect=${encodeURIComponent(redirectParam)}` : 'mfa.html';
        window.location.href = mfaUrl;
        return;
      }

      // Direct login fallback if access_token returned
      if (res && res.access_token) {
        window.auth.setToken(res.access_token);
        window.auth.setUser(res.user);
        const urlParams = new URLSearchParams(window.location.search);
        const redirectTarget = urlParams.get('redirect') || 'soc.html';
        window.location.href = redirectTarget;
      }
    } catch (err) {
      showError(err.message || 'Incorrect username/email or password.');
    } finally {
      btnLoginSubmit.disabled = false;
      btnLoginSubmit.textContent = 'Sign In to SOC';
    }
  });

  // Handle Registration submission
  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlerts();

    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;

    if (!username || !email || !password) {
      showError('All fields are required for registration.');
      return;
    }

    btnRegisterSubmit.disabled = true;
    btnRegisterSubmit.textContent = 'Registering...';

    try {
      await window.api.register(username, email, password);
      showSuccess('Analyst account created successfully. You may now log in.');
      formRegister.style.display = 'none';
      formLogin.style.display = 'block';
      document.getElementById('login-username').value = username;
      document.getElementById('login-password').value = '';
    } catch (err) {
      showError(err.message || 'Registration failed.');
    } finally {
      btnRegisterSubmit.disabled = false;
      btnRegisterSubmit.textContent = 'Create Analyst Account';
    }
  });
});
