import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx

from app.core.config import settings
from app.schemas.ai import AIAnalysisOutput
from app.services.ai.knowledge_loader import (
    knowledge_loader,
    ATTACK_TECHNIQUE_MAP,
)

logger = logging.getLogger(__name__)

MANDATORY_DISCLAIMER = "AI Suggested — Human Review Required"


def build_system_prompt() -> str:
    return (
        "You are an elite Tier-3 Incident Response AI Specialist following NIST SP 800-61 Rev. 2 "
        "and MITRE ATT&CK framework guidelines.\n"
        "Your task is to analyze security incidents based strictly on provided telemetry, indicators, and authorized knowledge context.\n\n"
        "CRITICAL POLICY CONSTRAINTS:\n"
        "1. Every suggestion is ADVISORY ONLY. Human review is strictly authoritative.\n"
        "2. You MUST NOT make final regulatory determinations, breach determinations, containment decisions, or reporting decisions.\n"
        "3. Severity and Priority are COMPLETELY INDEPENDENT. Severity must be one of: 'Low', 'Medium', 'High', 'Critical', 'Not Determined'. Do not mention or map priority (P1-P4).\n"
        "4. Your response MUST be valid JSON adhering strictly to the requested schema.\n"
        "5. The disclaimer MUST be exactly 'AI Suggested — Human Review Required'.\n"
    )


def build_incident_prompt(
    incident_data: Dict[str, Any],
    indicators: List[Dict[str, Any]],
    knowledge_context: str,
) -> str:
    prompt = f"""
{build_system_prompt()}

--- AUTHORITATIVE REFERENCE KNOWLEDGE ---
{knowledge_context}

--- INCIDENT TELEMETRY ---
Incident ID: {incident_data.get("id")}
Title: {incident_data.get("title")}
Reported Attack Type: {incident_data.get("attack_type")}
Current Status: {incident_data.get("status")}
Current NIST Phase: {incident_data.get("current_nist_phase")}
Description: {incident_data.get("description")}

Indicators of Compromise:
{json.dumps(indicators, indent=2)}

--- RESPONSE SCHEMA REQUIREMENTS ---
Return a JSON object with EXACTLY the following keys:
- "incident_type": string (e.g., "Brute Force", "Phishing", "PowerShell Execution", "DDoS")
- "suggested_nist_phase": string (one of: "Preparation", "Detection & Analysis", "Containment, Eradication & Recovery", "Post-Incident Activity")
- "suggested_severity": string (one of: "Low", "Medium", "High", "Critical", "Not Determined")
- "attack_technique": string (e.g., "T1110", "T1566", "T1059.001", "T1498")
- "attack_technique_name": string (MITRE ATT&CK technique name)
- "reason": string (comprehensive analytical justification referencing observed indicators)
- "recommended_actions": list of strings (concrete next actions for human analysts)
- "confidence": float (between 0.0 and 1.0)
- "disclaimer": "AI Suggested — Human Review Required"
"""
    return prompt.strip()


class GeminiService:
    """
    Primary AI Service integrating Google Gemini API with timeout, exponential retry,
    safe error sanitization, Pydantic response validation, and controlled manual fallback.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout = timeout if timeout is not None else settings.GEMINI_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.GEMINI_MAX_RETRIES

    def _is_api_key_valid(self) -> bool:
        if not self.api_key:
            return False
        clean = self.api_key.strip()
        if not clean or clean.lower() in ("replace_me", "your_gemini_api_key", "none"):
            return False
        return True

    def _invoke_gemini_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Executes HTTP call to Gemini API with retries and safe error handling.
        NEVER logs or exposes the API key in exceptions or messages.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        }

        attempts = 0
        while attempts <= self.max_retries:
            attempts += 1
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, headers=headers, json=payload)

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        logger.warning("Gemini API returned no candidates in response.")
                        return None
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    cleaned = text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    return json.loads(cleaned.strip())
                elif resp.status_code in (429, 500, 502, 503, 504):
                    logger.warning("Gemini API transient status %d on attempt %d/%d.", resp.status_code, attempts, self.max_retries + 1)
                    if attempts <= self.max_retries:
                        time.sleep(0.5 * attempts)
                        continue
                    return None
                else:
                    logger.warning("Gemini API returned non-retryable status %d.", resp.status_code)
                    return None
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                logger.warning("Gemini network error (%s) on attempt %d/%d.", exc.__class__.__name__, attempts, self.max_retries + 1)
                if attempts <= self.max_retries:
                    time.sleep(0.5 * attempts)
                    continue
                return None
            except Exception as exc:
                logger.warning("Gemini invocation failed with exception (%s).", exc.__class__.__name__)
                return None

        return None

    def execute_controlled_fallback(
        self,
        incident_data: Dict[str, Any],
        indicators: List[Dict[str, Any]],
    ) -> AIAnalysisOutput:
        """
        Deterministic, rule-based fallback aligning strictly with the
        verified knowledge base (T1110, T1566, T1059.001, T1498).
        """
        attack_type = str(incident_data.get("attack_type", "")).lower()
        title = str(incident_data.get("title", "")).lower()
        desc = str(incident_data.get("description", "")).lower()
        combined_text = f"{attack_type} {title} {desc}"

        # 1. Brute Force Scenario (T1110)
        if "brute" in combined_text or any("ssh" in str(ind.get("indicator_value", "")).lower() for ind in indicators):
            return AIAnalysisOutput(
                incident_type="Brute Force",
                suggested_nist_phase="Detection & Analysis",
                suggested_severity="High",
                attack_technique="T1110",
                attack_technique_name="Brute Force",
                reason=(
                    "High-frequency failed authentication attempts detected against perimeter access points. "
                    "Indicator patterns align with MITRE ATT&CK T1110 (Brute Force). Review of source IP and failed login "
                    "threshold indicates active credential guessing."
                ),
                recommended_actions=[
                    "Inspect authentication logs for targeted accounts and source IP",
                    "Verify threshold lockouts on perimeter identity endpoints",
                    "Prepare perimeter firewall drop rule for analyst approval",
                    "Confirm whether any credential guessing attempts succeeded",
                ],
                confidence=0.90,
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 2. Phishing Scenario (T1566)
        if "phish" in combined_text or any("mail" in str(ind.get("indicator_type", "")).lower() for ind in indicators):
            return AIAnalysisOutput(
                incident_type="Phishing",
                suggested_nist_phase="Containment, Eradication & Recovery",
                suggested_severity="High",
                attack_technique="T1566",
                attack_technique_name="Phishing",
                reason=(
                    "Observed message telemetry (suspicious sender domain, credential harvesting URL, and header spoofing) "
                    "aligns with MITRE ATT&CK T1566 (Phishing). Target user interaction requires containment verification."
                ),
                recommended_actions=[
                    "Quarantine malicious email across mail server and recipient mailboxes",
                    "Block reported phishing domain and link at secure web gateway / DNS resolver",
                    "Trigger password reset and session revocation for affected users",
                    "Audit tenant mail logs for additional recipients of the same message",
                ],
                confidence=0.92,
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 3. PowerShell Scenario (T1059.001)
        if "powershell" in combined_text:
            return AIAnalysisOutput(
                incident_type="PowerShell Execution",
                suggested_nist_phase="Containment, Eradication & Recovery",
                suggested_severity="Critical",
                attack_technique="T1059.001",
                attack_technique_name="Command and Scripting Interpreter: PowerShell",
                reason=(
                    "Endpoint process telemetry captured obfuscated PowerShell execution with execution policy bypass flags. "
                    "Observed behavioral indicators match MITRE ATT&CK T1059.001. High risk of secondary payload retrieval."
                ),
                recommended_actions=[
                    "Isolate affected endpoint host from the corporate network",
                    "Terminate rogue PowerShell parent and child processes",
                    "Extract script block logs (Event ID 4104) and memory capture for forensic preservation",
                    "Inspect outbound socket connections for command-and-control beacons",
                ],
                confidence=0.94,
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 4. DDoS Scenario (T1498)
        if "ddos" in combined_text or "denial" in combined_text:
            return AIAnalysisOutput(
                incident_type="DDoS",
                suggested_nist_phase="Containment, Eradication & Recovery",
                suggested_severity="High",
                attack_technique="T1498",
                attack_technique_name="Network Denial of Service",
                reason=(
                    "Anomalous ingress volumetric traffic and connection exhaustion detected against edge interfaces. "
                    "Telemetry signatures match MITRE ATT&CK T1498 (Network Denial of Service)."
                ),
                recommended_actions=[
                    "Activate upstream ISP / CDN scrubbing center mitigation rules",
                    "Enforce edge rate limiting and stateful TCP connection ceilings",
                    "Monitor infrastructure CPU, memory, and application queue saturation",
                    "Preserve perimeter NetFlow / pcap evidence for post-incident review",
                ],
                confidence=0.89,
                disclaimer=MANDATORY_DISCLAIMER,
            )

        # 5. Default Generic Scenario
        current_phase = incident_data.get("current_nist_phase") or "Detection & Analysis"
        return AIAnalysisOutput(
            incident_type=incident_data.get("attack_type", "Security Incident"),
            suggested_nist_phase=current_phase,
            suggested_severity="Medium",
            attack_technique="T1110",
            attack_technique_name="General Incident Analysis",
            reason=(
                f"Controlled fallback engine evaluated incident #{incident_data.get('id', 'N/A')}. "
                "Initial indicators logged. SOC analyst triage required."
            ),
            recommended_actions=[
                "Review recorded indicators and alert fidelity",
                "Correlate events with central SIEM telemetry",
                "Assign designated analyst for triage and containment",
            ],
            confidence=0.75,
            disclaimer=MANDATORY_DISCLAIMER,
        )

    def analyze(
        self,
        incident_data: Dict[str, Any],
        indicators: List[Dict[str, Any]],
    ) -> Tuple[AIAnalysisOutput, str]:
        """
        Coordinates AI analysis:
        Attempts Gemini -> retries -> executes controlled fallback if Gemini fails or is unconfigured.
        Returns (validated_output, provider_name).
        """
        # 1. Check if Gemini is enabled and configured
        if self._is_api_key_valid():
            knowledge_context = knowledge_loader.get_context_for_incident(
                attack_type=incident_data.get("attack_type"),
                current_phase=incident_data.get("current_nist_phase"),
            )
            prompt = build_incident_prompt(incident_data, indicators, knowledge_context)
            raw_response = self._invoke_gemini_api(prompt)

            if raw_response:
                try:
                    # Validate structured JSON using Pydantic
                    parsed = AIAnalysisOutput(**raw_response)
                    # Force mandatory disclaimer
                    parsed.disclaimer = MANDATORY_DISCLAIMER
                    return parsed, "gemini"
                except Exception as val_err:
                    logger.warning("Gemini output failed Pydantic validation: %s. Engaging fallback.", val_err.__class__.__name__)

        # 2. Controlled fallback
        fallback_output = self.execute_controlled_fallback(incident_data, indicators)
        return fallback_output, "fallback"


gemini_service = GeminiService()
