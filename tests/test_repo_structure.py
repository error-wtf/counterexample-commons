"""Tests that validate repository structure and metadata integrity."""

import json
from pathlib import Path

import yaml
import pytest


ROOT = Path(__file__).resolve().parent.parent


class TestRequiredFilesExist:
    REQUIRED = [
        "LICENSE",
        "LICENSE_POLICY.md",
        "NOTICE.md",
        "README.md",
        "CHANGELOG.md",
        "CITATION.cff",
        ".zenodo.json",
        ".gitignore",
        "pyproject.toml",
        "requirements.txt",
        "THIRD_PARTY_SOURCES_AND_LICENSES.md",
        "references/references.bib",
        "references/PRIMARY_SOURCES.md",
        "references/CLAIM_TO_SOURCE_MATRIX.md",
        ".github/REPOSITORY_TOPICS.md",
        "branding/README.md",
        "branding/SOCIAL_PREVIEW_BRIEF.md",
        "docs/CITATION_AND_ARCHIVAL_POLICY.md",
        "docs/UI_SCIENTIFIC_INTEGRITY_POLICY.md",
        "docs/PUBLIC_DEMO_SECURITY_POLICY.md",
        "case_studies/erdos_unit_distance_2026/README.md",
        "reports/IDENTITY_LICENSE_METADATA_VALIDATION.md",
        "counterexample_commons/__init__.py",
        "counterexample_commons/config.py",
        "counterexample_commons/claims.py",
        "counterexample_commons/validators/__init__.py",
        "counterexample_commons/validators/unit_distance.py",
        "app/__init__.py",
        "app/main.py",
        "scripts/run_gradio_local.py",
    ]

    @pytest.mark.parametrize("path", REQUIRED)
    def test_file_exists(self, path):
        full = ROOT / path
        assert full.exists(), f"Missing required file: {path}"

    @pytest.mark.parametrize("path", REQUIRED)
    def test_file_not_empty(self, path):
        full = ROOT / path
        if full.exists():
            assert full.stat().st_size > 0, (
                f"Required file is empty: {path}"
            )


class TestLicense:
    def test_contains_acsl_v14(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        assert "ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)" in text

    def test_contains_copyright_holder(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        assert "Lino Casu" in text

    def test_contains_year_2026(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        assert "2026" in text

    def test_not_called_open_source(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        lower = text.lower()
        assert "osi-defined open-source" not in lower or (
            "not osi-defined" in lower
            or "not OSI-defined" in text
        )


class TestCitationCff:
    def test_valid_yaml(self):
        data = yaml.safe_load(
            (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        )
        assert data is not None

    def test_has_required_fields(self):
        data = yaml.safe_load(
            (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        )
        for key in ["title", "authors", "version", "type"]:
            assert key in data, f"CITATION.cff missing field: {key}"

    def test_author_is_casu(self):
        data = yaml.safe_load(
            (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        )
        names = [
            a.get("family-names", "")
            for a in data["authors"]
        ]
        assert "Casu" in names


class TestZenodoJson:
    def test_valid_json(self):
        data = json.loads(
            (ROOT / ".zenodo.json").read_text(encoding="utf-8")
        )
        assert data is not None

    def test_has_title(self):
        data = json.loads(
            (ROOT / ".zenodo.json").read_text(encoding="utf-8")
        )
        assert "title" in data
        assert "Counterexample Commons" in data["title"]

    def test_has_creators(self):
        data = json.loads(
            (ROOT / ".zenodo.json").read_text(encoding="utf-8")
        )
        names = [c["name"] for c in data["creators"]]
        assert "Casu, Lino" in names


class TestGitignore:
    def test_env_ignored(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".env" in text

    def test_pycache_ignored(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "__pycache__" in text


class TestRepositoryTopics:
    def test_no_open_source_topic(self):
        text = (ROOT / ".github" / "REPOSITORY_TOPICS.md").read_text(
            encoding="utf-8"
        )
        lines = [
            ln.strip() for ln in text.split("\n")
            if ln.strip() and not ln.startswith("#")
            and not ln.startswith("*") and not ln.startswith("```")
        ]
        assert "open-source" not in lines


class TestNoSecrets:
    def test_no_api_keys_in_source(self):
        prefix = "sk" + "-"
        patterns = [prefix, f"OPENAI_API_KEY={prefix}"]
        for py_file in ROOT.rglob("*.py"):
            if py_file.name == "test_repo_structure.py":
                continue
            content = py_file.read_text(encoding="utf-8")
            for pat in patterns:
                assert pat not in content, (
                    f"Possible API key in {py_file}: {pat}"
                )
