from app.services.ai.knowledge_loader import (
    KnowledgeLoader,
    knowledge_loader,
    resolve_knowledge_dir,
    ATTACK_TECHNIQUE_MAP,
    NIST_PHASE_FILE_MAP,
)

# For backward compatibility
find_knowledge_base_dir = resolve_knowledge_dir

__all__ = [
    "KnowledgeLoader",
    "knowledge_loader",
    "resolve_knowledge_dir",
    "find_knowledge_base_dir",
    "ATTACK_TECHNIQUE_MAP",
    "NIST_PHASE_FILE_MAP",
]
