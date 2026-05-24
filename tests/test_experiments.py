"""Tests for AI experiment pipeline."""

import json

from counterexample_commons.experiments import (
    RunManager,
    ExperimentStatus,
    PreRegistration,
    extract_candidate_coordinates,
    validate_candidate,
    sanitize_for_export,
)
from counterexample_commons.experiments.sanitization import (
    contains_secret,
    is_safe_for_export,
)
from counterexample_commons.experiments.extraction import (
    _is_valid_candidate,
)
from counterexample_commons.experiments.report_builder import (
    build_run_report,
    build_comparison_report,
)
from counterexample_commons.experiments.comparison import (
    ComparisonEntry,
    build_comparison_table,
)
from counterexample_commons.experiments.prompt_templates import (
    format_generation_prompt,
)


class TestRunManager:
    def test_create_run(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test question")
        assert run.path.exists()
        assert (run.path / "metadata.json").exists()
        assert (run.path / "research_question.md").exists()

    def test_list_runs(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        mgr.create_run("openai", "gpt-4o", "Q1")
        mgr.create_run("anthropic", "claude", "Q2")
        runs = mgr.list_runs()
        assert len(runs) == 2

    def test_list_runs_empty(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        assert mgr.list_runs() == []


class TestRunDirectory:
    def test_save_preregistration(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test")
        run.save_preregistration("My claim", "My falsifier")
        assert (run.path / "preregistered_claim.md").exists()
        assert (run.path / "falsifier.md").exists()

    def test_save_raw_output(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test")
        run.save_raw_output("Raw model text here")
        content = (run.path / "raw_model_output.md").read_text(
            encoding="utf-8"
        )
        assert "Raw model text" in content

    def test_save_result(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test")
        run.save_result(
            ExperimentStatus.PASS_FINITE_CONFIGURATION_VALIDATED,
            {"actual_edges": 5, "n": 4},
        )
        result = json.loads(
            (run.path / "result.json").read_text(encoding="utf-8")
        )
        assert result["status"] == (
            "PASS_FINITE_CONFIGURATION_VALIDATED"
        )

    def test_failed_run_preserved(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test")
        run.save_raw_output("Garbled output")
        run.save_result(
            ExperimentStatus.FAIL_INVALID_COORDINATES,
            {"error": "bad parse"},
        )
        # The directory and all artifacts still exist
        assert run.path.exists()
        assert (run.path / "raw_model_output.md").exists()
        assert (run.path / "result.json").exists()


class TestExtraction:
    def test_extract_from_json_block(self):
        text = 'Here:\n```json\n[[0, 0], [1, 0]]\n```\n'
        result = extract_candidate_coordinates(text)
        assert result is not None
        assert len(result["points"]) == 2

    def test_extract_from_raw_array(self):
        text = "The answer is [[0, 0], [1, 0], [0, 1]]."
        result = extract_candidate_coordinates(text)
        assert result is not None
        assert len(result["points"]) == 3

    def test_extract_fails_on_garbage(self):
        text = "No coordinates here, just text."
        result = extract_candidate_coordinates(text)
        assert result is None

    def test_extract_handles_dict_with_points(self):
        text = '```json\n{"points": [[0,0],[1,0]]}\n```'
        result = extract_candidate_coordinates(text)
        assert result is not None
        assert len(result["points"]) == 2

    def test_invalid_candidate_empty(self):
        assert _is_valid_candidate([]) is False

    def test_invalid_candidate_wrong_shape(self):
        assert _is_valid_candidate([[1, 2, 3]]) is False


class TestExactValidation:
    def test_valid_square(self):
        candidate = {
            "points": [[0, 0], [1, 0], [1, 1], [0, 1]]
        }
        result = validate_candidate(candidate)
        assert result["status"] == (
            "PASS_FINITE_CONFIGURATION_VALIDATED"
        )
        assert result["actual_edges"] == 4

    def test_claimed_count_correct(self):
        candidate = {"points": [[0, 0], [1, 0]]}
        result = validate_candidate(candidate, claimed_edge_count=1)
        assert result["status"] == (
            "PASS_FINITE_CONFIGURATION_VALIDATED"
        )

    def test_claimed_count_wrong(self):
        candidate = {"points": [[0, 0], [1, 0]]}
        result = validate_candidate(candidate, claimed_edge_count=5)
        assert result["status"] == (
            "FAIL_CLAIMED_COUNT_INCORRECT"
        )

    def test_duplicate_rejected(self):
        candidate = {"points": [[0, 0], [1, 0], [0, 0]]}
        result = validate_candidate(candidate)
        assert result["status"] == "FAIL_INVALID_COORDINATES"

    def test_bad_coordinates_rejected(self):
        candidate = {"points": [["abc", 0]]}
        result = validate_candidate(candidate)
        assert result["status"] == "FAIL_INVALID_COORDINATES"


class TestSanitization:
    def test_detects_openai_key(self):
        prefix = "sk" + "-"
        text = f"key: {prefix}abcdefghijklmnopqrstuvwxyz1234"
        assert contains_secret(text) is True

    def test_clean_text_safe(self):
        text = "Just some math coordinates"
        assert contains_secret(text) is False

    def test_sanitize_redacts(self):
        prefix = "sk" + "-"
        text = f"Token: {prefix}abcdefghijklmnopqrstuvwxyz1234"
        result = sanitize_for_export(text)
        assert "[REDACTED]" in result
        assert prefix not in result

    def test_is_safe_for_export(self):
        safe, _ = is_safe_for_export("clean text")
        assert safe is True

    def test_is_not_safe_with_key(self):
        prefix = "sk" + "-"
        safe, reason = is_safe_for_export(
            f"{prefix}abcdefghijklmnopqrstuvwxyz1234"
        )
        assert safe is False


class TestPreRegistration:
    def test_to_markdown(self):
        reg = PreRegistration(
            research_question="Can GPT-4o find > 15 edges?",
            claim="GPT-4o will produce a valid config",
            falsifier="Exact validator returns FAIL",
            success_criterion="actual_edges > 15",
            provider="openai",
            model="gpt-4o",
        )
        md = reg.to_markdown()
        assert "# Pre-Registration" in md
        assert "GPT-4o" in md


class TestReportBuilder:
    def test_build_run_report(self, tmp_path):
        mgr = RunManager(tmp_path / "runs")
        run = mgr.create_run("openai", "gpt-4o", "Test Q")
        run.save_result(
            ExperimentStatus.PASS_FINITE_CONFIGURATION_VALIDATED,
            {"actual_edges": 4},
        )
        report = build_run_report(run.path)
        assert "Experiment Run Report" in report

    def test_build_comparison_report(self):
        entries = [
            ComparisonEntry("openai", "gpt-4o", 10, 15, "PASS", 500),
            ComparisonEntry("anthropic", "claude", 10, 12, "PASS", 800),
        ]
        table = build_comparison_table(entries)
        report = build_comparison_report(table)
        assert "openai" in report
        assert "anthropic" in report

    def test_empty_comparison(self):
        report = build_comparison_report([])
        assert "No comparison" in report


class TestPromptTemplates:
    def test_format_generation_prompt(self):
        prompt = format_generation_prompt(16)
        assert "n = 16" in prompt
        assert "rational" in prompt.lower()
