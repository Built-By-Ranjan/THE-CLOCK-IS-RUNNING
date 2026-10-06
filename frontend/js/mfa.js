// MFA Verification Controller — Email OTP Flow

document.addEventListener('DOMContentLoaded', () => {
  const formMfa = document.getElementById('form-mfa');
  const alertError = document.getElementById('alert-error');
  const alertInfo = document.getElementById('alert-info');
  const btnMfaSubmit = document.getElementById('btn-mfa-submit');
  const btnMfaResend = document.getElementById('btn-mfa-resend');
  const resendCountdownSpan = document.getElementById('resend-countdown');
  const mfaOtp = document.getElementById('mfa-otp');
  const targetEmailDiv = document.getElementById('mfa-target-email');
  const expiryTimerSpan = document.getElementById('mfa-expiry-timer');

  const challengeId = sessionStorage.getItem('mfa_challenge_id');
  const emailMasked = sessionStorage.getItem('mfa_email_masked');

  // If no active challenge exists, redirect back to login
  if (!challengeId) {
    window.location.href = 'login.html';
    return;
  }

  if (emailMasked && targetEmailDiv) {
    targetEmailDiv.textContent = `Code sent to: ${emailMasked}`;
    targetEmailDiv.style.display = 'block';
  }

  function showError(msg) {
    alertError.textContent = msg;
    alertError.style.display = 'block';
    alertInfo.style.display = 'none';
  }

  function showInfo(msg) {
    alertInfo.textContent = msg;
    alertInfo.style.display = 'block';
    alertError.style.display = 'none';
  }

  function clearAlerts() {
    alertError.style.display = 'none';
    alertInfo.style.display = 'none';
  }

  // Cooldown timer state
  let cooldownRemaining = 60;
  let cooldownInterval = null;

  function startCooldown(seconds = 60) {
    cooldownRemaining = seconds;
    btnMfaResend.disabled = true;
    if (resendCountdownSpan) {
      resendCountdownSpan.textContent = cooldownRemaining;
    }
    btnMfaResend.textContent = `Resend Code (${cooldownRemaining}s)`;

    if (cooldownInterval) clearInterval(cooldownInterval);

    cooldownInterval = setInterval(() => {
      cooldownRemaining--;
      if (cooldownRemaining <= 0) {
        clearInterval(cooldownInterval);
        btnMfaResend.disabled = false;
        btnMfaResend.textContent = 'Resend Code';
      } else {
        btnMfaResend.textContent = `Resend Code (${cooldownRemaining}s)`;
      }
    }, 1000);
  }

  // Expiry timer state (5 minutes = 300 seconds)
  let expiryRemaining = parseInt(sessionStorage.getItem('mfa_expires_in_seconds') || '300', 10);
  let expiryInterval = null;

  function startExpiryTimer(seconds = 300) {
    expiryRemaining = seconds;
    if (expiryInterval) clearInterval(expiryInterval);

    function updateDisplay() {
      const mins = Math.floor(expiryRemaining / 60);
      const secs = expiryRemaining % 60;
      const formatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
      if (expiryTimerSpan) {
        expiryTimerSpan.textContent = `Expires in: ${formatted}`;
      }
    }

    updateDisplay();

    expiryInterval = setInterval(() => {
      expiryRemaining--;
      if (expiryRemaining <= 0) {
        clearInterval(expiryInterval);
        if (expiryTimerSpan) {
          expiryTimerSpan.textContent = 'Code expired';
        }
        showError('Verification code has expired. Please click "Resend Code" or log in again.');
      } else {
        updateDisplay();
      }
    }, 1000);
  }

  // Start initial timers on page load
  startCooldown(60);
  startExpiryTimer(expiryRemaining);

  // Restrict OTP input to numbers only
  mfaOtp.addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '');
  });

  // Handle MFA Verification
  formMfa.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlerts();

    const otpCode = mfaOtp.value.trim();

    if (otpCode.length !== 6) {
      showError('Verification code must be exactly 6 digits.');
      return;
    }

    btnMfaSubmit.disabled = true;
    btnMfaSubmit.textContent = 'Verifying Code...';

    try {
      const res = await window.api.verifyMfa(challengeId, otpCode);

      // Successful MFA authentication: store token & user
      window.auth.setToken(res.access_token);
      window.auth.setUser(res.user);

      // Clean up sensitive session challenge metadata
      sessionStorage.removeItem('mfa_challenge_id');
      sessionStorage.removeItem('mfa_email_masked');
      sessionStorage.removeItem('mfa_expires_in_seconds');

      const urlParams = new URLSearchParams(window.location.search);
      const redirectTarget = urlParams.get('redirect') || 'soc.html';
      window.location.href = redirectTarget;
    } catch (err) {
      showError(err.message || 'Invalid or expired verification code.');
    } finally {
      btnMfaSubmit.disabled = false;
      btnMfaSubmit.textContent = 'Verify & Open SOC Dashboard';
    }
  });

  // Handle Resend Code
  btnMfaResend.addEventListener('click', async () => {
    clearAlerts();
    btnMfaResend.disabled = true;

    try {
      const res = await window.api.resendMfa(challengeId);
      showInfo(res.message || 'A new verification code has been sent to your email.');
      startCooldown(res.cooldown_seconds || 60);
      startExpiryTimer(res.expires_in_seconds || 300);
      mfaOtp.value = '';
      mfaOtp.focus();
    } catch (err) {
      showError(err.message || 'Failed to resend verification code. Please wait and try again.');
      btnMfaResend.disabled = false;
    }
  });
});
