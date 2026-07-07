from __future__ import annotations

from pathlib import Path

from scripts.validate_release_package import validate_release_package


def test_release_package_validator_passes():
    result = validate_release_package()

    assert result["passed"] is True
    assert result["errors"] == []
    assert result["milestone"] == "M17_FINAL_PORTFOLIO_RELEASE_PACKAGE"


def test_recruiter_docs_exist_and_contain_honest_scope():
    recruiter_summary = Path("docs/recruiter_project_summary.md")
    architecture = Path("docs/architecture.md")
    skills_matrix = Path("docs/skills_matrix.md")

    assert recruiter_summary.exists()
    assert architecture.exists()
    assert skills_matrix.exists()

    recruiter_text = recruiter_summary.read_text(encoding="utf-8")
    architecture_text = architecture.read_text(encoding="utf-8")
    skills_text = skills_matrix.read_text(encoding="utf-8")

    assert "Best Resume Bullet" in recruiter_text
    assert "Honest Scope" in recruiter_text
    assert "High-Level Architecture" in architecture_text
    assert "Honest Limitation" in architecture_text
    assert "Avoid overclaiming" in skills_text


def test_interview_and_release_docs_are_recruiter_ready():
    talking_points = Path("docs/interview_talking_points.md")
    repository_map = Path("docs/repository_map.md")
    release_checklist = Path("release/release_checklist.md")

    assert talking_points.exists()
    assert repository_map.exists()
    assert release_checklist.exists()

    talking_text = talking_points.read_text(encoding="utf-8")
    map_text = repository_map.read_text(encoding="utf-8")
    checklist_text = release_checklist.read_text(encoding="utf-8")

    assert "30-Second Pitch" in talking_text
    assert "If Asked: Is This Production-Deployed?" in talking_text
    assert "Best Files for Recruiters to Read First" in map_text
    assert "Honest Claims Allowed" in checklist_text
    assert "Do not say unless separately executed" in checklist_text
