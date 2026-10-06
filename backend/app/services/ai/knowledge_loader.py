import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

ATTACK_TECHNIQUE_MAP: Dict[str, Dict[str, str]] = {
    "brute-force": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "incident_type": "Brute Force",
    },
    "phishing": {
        "technique_id": "T1566",
        "technique_name": "Phishing",
        "incident_type": "Phishing",
    },
    "powershell": {
        "technique_id": "T1059.001",
        "technique_name": "Command and Scripting Interpreter: PowerShell",
        "incident_type": "PowerShell Execution",
    },
    "ddos": {
        "technique_id": "T1498",
        "technique_name": "Network Denial of Service",
        "incident_type": "DDoS",
    },
}

NIST_PHASE_FILE_MAP: Dict[str, str] = {
    "preparation": "Preparation",
    "detection-analysis": "Detection & Analysis",
    "containment-eradication-recovery": "Containment, Eradication & Recovery",
    "post-incident": "Post-Incident Activity",
}


def resolve_knowledge_dir(start_path: Optional[Path] = None) -> Path:
    """
    Safely locates the authoritative knowledge/ root directory.
    Operates correctly regardless of whether the working directory is the
    project root or the backend/ directory.
    """
    search_roots = []
    if start_path:
        search_roots.append(start_path)
    search_roots.append(Path.cwd())
    search_roots.append(Path(__file__).resolve().parent)

    for root in search_roots:
        current = root.resolve()
        for _ in range(6):
            candidate = current / "knowledge"
            if candidate.is_dir() and (candidate / "attacks").is_dir() and (candidate / "nist").is_dir():
                return candidate
            if current.parent == current:
                break
            current = current.parent

    raise FileNotFoundError("Could not safely locate the knowledge/ base directory.")


class KnowledgeLoader:
    """
    Strictly read-only knowledge loader service.
    Loads human-authored, authoritative Markdown guidance for NIST IR and MITRE ATT&CK.
    Under no circumstances writes to or mutates the knowledge base directory.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self._base_dir = (base_dir.resolve() if base_dir else resolve_knowledge_dir())

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    def get_attack_document(self, attack_key: str) -> Optional[str]:
        """
        Reads attack vector guidance safely.
        Returns document content string or None if missing.
        """
        file_path = self._base_dir / "attacks" / f"{attack_key}.md"
        if not file_path.is_file():
            logger.warning("Knowledge attack document not found: %s", file_path)
            return None
        with open(file_path, mode="r", encoding="utf-8") as f:
            return f.read()

    def get_nist_document(self, nist_key: str) -> Optional[str]:
        """
        Reads NIST phase guidelines safely.
        Returns document content string or None if missing.
        """
        file_path = self._base_dir / "nist" / f"{nist_key}.md"
        if not file_path.is_file():
            logger.warning("Knowledge NIST document not found: %s", file_path)
            return None
        with open(file_path, mode="r", encoding="utf-8") as f:
            return f.read()

    def load_all_attack_docs(self) -> Dict[str, str]:
        """Loads all available attack documents."""
        docs: Dict[str, str] = {}
        for key in ATTACK_TECHNIQUE_MAP.keys():
            content = self.get_attack_document(key)
            if content is not None:
                docs[key] = content
        return docs

    def load_all_nist_docs(self) -> Dict[str, str]:
        """Loads all available NIST phase guidance documents."""
        docs: Dict[str, str] = {}
        for key in NIST_PHASE_FILE_MAP.keys():
            content = self.get_nist_document(key)
            if content is not None:
                docs[key] = content
        return docs

    def get_context_for_incident(self, attack_type: Optional[str] = None, current_phase: Optional[str] = None) -> str:
        """
        Generates focused reference context for AI prompts combining
        relevant attack vector guidance and current NIST phase guidelines.
        """
        sections = ["### RELEVANT KNOWLEDGE BASE CONTEXT (READ-ONLY) ###"]
        
        # Match attack document
        attack_key = None
        if attack_type:
            lowered = attack_type.lower()
            if "brute" in lowered:
                attack_key = "brute-force"
            elif "phish" in lowered:
                attack_key = "phishing"
            elif "powershell" in lowered:
                attack_key = "powershell"
            elif "ddos" in lowered or "denial" in lowered:
                attack_key = "ddos"

        if attack_key:
            doc = self.get_attack_document(attack_key)
            if doc:
                info = ATTACK_TECHNIQUE_MAP[attack_key]
                sections.append(f"\n#### Threat Scenario & MITRE ATT&CK: {info['incident_type']} ({info['technique_id']})\n{doc[:2500]}")

        # Match NIST phase document
        nist_key = None
        if current_phase:
            phase_lower = current_phase.lower()
            if "prep" in phase_lower:
                nist_key = "preparation"
            elif "detect" in phase_lower or "analys" in phase_lower:
                nist_key = "detection-analysis"
            elif "contain" in phase_lower or "eradicat" in phase_lower or "recover" in phase_lower:
                nist_key = "containment-eradication-recovery"
            elif "post" in phase_lower:
                nist_key = "post-incident"

        if nist_key:
            doc = self.get_nist_document(nist_key)
            if doc:
                sections.append(f"\n#### NIST Phase Guidance: {NIST_PHASE_FILE_MAP[nist_key]}\n{doc[:2500]}")

        return "\n".join(sections)


# Default singleton instance
knowledge_loader = KnowledgeLoader()
