import json
from unittest.mock import MagicMock, patch
import httpx
import pytest
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.ai import AIAnalysisOutput
from app.services.ai.gemini_service import (
    GeminiService,
    gemini_service,
    MANDATORY_DISCLAIMER,
)


def test_gemini_configuration():
    """Verify Gemini configuration reads from settings and has expected defaults."""
    svc = GeminiService()
    assert svc.model == settings.GEMINI_MODEL
    assert svc.timeout == settings.GEMINI_TIMEOUT_SECONDS
    assert svc.max_retries == settings.GEMINI_MAX_RETRIES
    # Verify API key comes strictly from config/env
    assert svc.api_key == settings.GEMINI_API_KEY


def test_structured_ai_response_validation():
    """Verify structured response validation against Pydantic schema."""
    valid_data = {
        "incident_type": "Brute Force",
        "suggested_nist_phase": "Detection & Analysis",
        "suggested_severity": "High",
        "attack_technique": "T1110",
        "attack_technique_name": "Brute Force",
        "reason": "Observed rapid authentication failures from IP 198.51.100.42.",
        "recommended_actions": ["Block source IP", "Audit accounts"],
        "confidence": 0.90,
        "disclaimer": MANDATORY_DISCLAIMER,
    }
    parsed = AIAnalysisOutput(**valid_data)
    assert parsed.incident_type == "Brute Force"
    assert parsed.suggested_severity == "High"
    assert parsed.attack_technique == "T1110"
    assert parsed.disclaimer == "AI Suggested — Human Review Required"


def test_structured_ai_response_rejects_invalid_severity():
    """Verify that invalid severity levels (such as P1, P2) are rejected by schema."""
    invalid_data = {
        "incident_type": "Brute Force",
        "suggested_nist_phase": "Detection & Analysis",
        "suggested_severity": "P1",  # P1 is priority, NOT severity!
        "attack_technique": "T1110",
        "reason": "Test reason",
        "recommended_actions": [],
        "confidence": 0.85,
    }
    with pytest.raises(ValidationError):
        AIAnalysisOutput(**invalid_data)


def test_gemini_api_success_with_mock():
    """Verify successful Gemini invocation parses JSON candidates and returns 'gemini' provider."""
    mock_response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "incident_type": "Brute Force",
                                "suggested_nist_phase": "Detection & Analysis",
                                "suggested_severity": "High",
                                "attack_technique": "T1110",
                                "attack_technique_name": "Brute Force",
                                "reason": "Multiple authentication failures detected.",
                                "recommended_actions": ["Block IP 198.51.100.42"],
                                "confidence": 0.92,
                                "disclaimer": MANDATORY_DISCLAIMER,
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data

    svc = GeminiService(api_key="valid-mock-key")
    with patch("httpx.Client.post", return_value=mock_resp):
        output, provider = svc.analyze(
            incident_data={"id": 1, "title": "SSH Attack", "attack_type": "Brute Force"},
            indicators=[],
        )

    assert provider == "gemini"
    assert output.incident_type == "Brute Force"
    assert output.attack_technique == "T1110"
    assert output.suggested_severity == "High"
    assert output.disclaimer == MANDATORY_DISCLAIMER


def test_gemini_retry_on_transient_error():
    """Verify that transient 503 or network errors trigger retries before failing."""
    mock_503 = MagicMock()
    mock_503.status_code = 503

    svc = GeminiService(api_key="valid-mock-key", max_retries=2)
    with patch("httpx.Client.post", side_effect=[mock_503, httpx.ConnectError("timeout"), mock_503]) as mock_post:
        with patch("time.sleep"):  # Avoid slowing down tests
            output, provider = svc.analyze(
                incident_data={"id": 1, "title": "SSH Attack", "attack_type": "Brute Force"},
                indicators=[],
            )

    # All retries failed -> successfully switched to controlled fallback
    assert mock_post.call_count == 3
    assert provider == "fallback"
    assert output.attack_technique == "T1110"


def test_controlled_fallback_scenarios():
    """Verify that fallback produces accurate ATT&CK mappings and advisory recommendations."""
    svc = GeminiService(api_key="replace_me")

    # 1. Brute Force -> T1110
    out_bf, prov_bf = svc.analyze(
        incident_data={"id": 10, "title": "SSH Brute Force", "attack_type": "Brute Force"},
        indicators=[],
    )
    assert prov_bf == "fallback"
    assert out_bf.attack_technique == "T1110"
    assert out_bf.incident_type == "Brute Force"
    assert out_bf.suggested_severity == "High"
    assert out_bf.suggested_nist_phase == "Detection & Analysis"
    assert out_bf.disclaimer == MANDATORY_DISCLAIMER

    # 2. Phishing -> T1566
    out_ph, prov_ph = svc.analyze(
        incident_data={"id": 11, "title": "Suspicious Email", "attack_type": "Phishing"},
        indicators=[],
    )
    assert prov_ph == "fallback"
    assert out_ph.attack_technique == "T1566"
    assert out_ph.incident_type == "Phishing"
    assert out_ph.suggested_severity == "High"
    assert out_ph.disclaimer == MANDATORY_DISCLAIMER

    # 3. PowerShell -> T1059.001
    out_ps, prov_ps = svc.analyze(
        incident_data={"id": 12, "title": "Encoded Script", "attack_type": "PowerShell Execution"},
        indicators=[],
    )
    assert prov_ps == "fallback"
    assert out_ps.attack_technique == "T1059.001"
    assert out_ps.suggested_severity == "Critical"
    assert out_ps.disclaimer == MANDATORY_DISCLAIMER

    # 4. DDoS -> T1498
    out_ddos, prov_ddos = svc.analyze(
        incident_data={"id": 13, "title": "SYN Flood", "attack_type": "DDoS"},
        indicators=[],
    )
    assert prov_ddos == "fallback"
    assert out_ddos.attack_technique == "T1498"
    assert out_ddos.suggested_severity == "High"
    assert out_ddos.disclaimer == MANDATORY_DISCLAIMER


def test_api_key_not_exposed_on_failure():
    """Verify that exceptions or failures never expose the API key in output."""
    secret_key = "secret-super-sensitive-gemini-key-999"
    svc = GeminiService(api_key=secret_key)

    with patch("httpx.Client.post", side_effect=Exception(f"Failed with key {secret_key}")):
        output, provider = svc.analyze(
            incident_data={"id": 1, "attack_type": "Brute Force"},
            indicators=[],
        )

    assert provider == "fallback"
    assert secret_key not in output.reason
    assert secret_key not in output.disclaimer
    for act in output.recommended_actions:
        assert secret_key not in act
