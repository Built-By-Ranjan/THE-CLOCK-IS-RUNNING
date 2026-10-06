import os
from pathlib import Path
import pytest

from app.services.ai.knowledge_loader import (
    KnowledgeLoader,
    resolve_knowledge_dir,
    knowledge_loader,
    ATTACK_TECHNIQUE_MAP,
    NIST_PHASE_FILE_MAP,
)


def test_knowledge_root_resolution():
    """Verify that knowledge root directory resolves correctly and contains required folders."""
    knowledge_dir = resolve_knowledge_dir()
    assert knowledge_dir.is_dir()
    assert (knowledge_dir / "attacks").is_dir()
    assert (knowledge_dir / "nist").is_dir()


def test_knowledge_root_resolution_from_backend_directory():
    """Verify that knowledge loader resolves root directory even when given backend path."""
    backend_dir = Path(__file__).resolve().parent.parent
    knowledge_dir = resolve_knowledge_dir(start_path=backend_dir)
    assert knowledge_dir.is_dir()
    assert (knowledge_dir / "attacks").is_dir()
    assert (knowledge_dir / "nist").is_dir()


def test_brute_force_knowledge_loads():
    """Verify that Brute Force attack guidance loads successfully."""
    doc = knowledge_loader.get_attack_document("brute-force")
    assert doc is not None
    assert len(doc) > 100
    assert "Brute Force" in doc


def test_phishing_knowledge_loads():
    """Verify that Phishing attack guidance loads successfully."""
    doc = knowledge_loader.get_attack_document("phishing")
    assert doc is not None
    assert len(doc) > 100
    assert "Phishing" in doc


def test_nist_preparation_knowledge_loads():
    """Verify that NIST Preparation phase guidelines load successfully."""
    doc = knowledge_loader.get_nist_document("preparation")
    assert doc is not None
    assert len(doc) > 100
    assert "Preparation" in doc


def test_all_attack_and_nist_documents_load():
    """Verify all four core attack documents and four NIST phase documents load."""
    attack_docs = knowledge_loader.load_all_attack_docs()
    assert len(attack_docs) == 4
    for key in ["brute-force", "phishing", "powershell", "ddos"]:
        assert key in attack_docs
        assert len(attack_docs[key]) > 50

    nist_docs = knowledge_loader.load_all_nist_docs()
    assert len(nist_docs) == 4
    for key in ["preparation", "detection-analysis", "containment-eradication-recovery", "post-incident"]:
        assert key in nist_docs
        assert len(nist_docs[key]) > 50


def test_loader_does_not_modify_files():
    """Verify that reading knowledge documents never mutates files or changes mtime."""
    bf_path = knowledge_loader.base_dir / "attacks" / "brute-force.md"
    assert bf_path.is_file()

    mtime_before = os.path.getmtime(bf_path)
    content_before = bf_path.read_text(encoding="utf-8")

    # Call loader multiple times
    _ = knowledge_loader.get_attack_document("brute-force")
    _ = knowledge_loader.load_all_attack_docs()
    _ = knowledge_loader.get_context_for_incident("Brute Force", "Detection & Analysis")

    mtime_after = os.path.getmtime(bf_path)
    content_after = bf_path.read_text(encoding="utf-8")

    assert mtime_before == mtime_after
    assert content_before == content_after


def test_missing_files_handled_safely():
    """Verify that requesting non-existent knowledge files returns None without crashing."""
    assert knowledge_loader.get_attack_document("non-existent-attack-vector") is None
    assert knowledge_loader.get_nist_document("non-existent-nist-phase") is None
