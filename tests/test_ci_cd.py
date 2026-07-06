from pathlib import Path

import yaml


def test_github_actions_ci_workflow_exists_and_has_required_jobs():
    workflow_path = Path(".github/workflows/ci.yml")
    assert workflow_path.exists(), "GitHub Actions workflow is missing."

    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    jobs = workflow.get("jobs", {})

    assert "test" in jobs, "CI workflow must include a test job."
    assert "docker-build" in jobs, "CI workflow must include Docker build validation."

    test_steps = [step.get("name", "") for step in jobs["test"].get("steps", [])]

    assert "Run pytest" in test_steps
    assert "Validate Kubernetes manifests" in test_steps
    assert "Generate research artifacts" in test_steps


def test_local_ci_runner_exists():
    assert Path("scripts/local_ci.py").exists(), "Local CI runner script is missing."


def test_makefile_exists():
    makefile = Path("Makefile")
    assert makefile.exists(), "Makefile is missing."

    content = makefile.read_text(encoding="utf-8")
    assert "test:" in content
    assert "validate-k8s:" in content
    assert "docker-build:" in content
