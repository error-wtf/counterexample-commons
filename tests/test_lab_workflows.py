"""Tests for local finite lab workflows."""

import json

from counterexample_commons.lab import (
    AI_REJECTED,
    AI_VALIDATED,
    baseline_records,
    build_finite_report,
    generate_and_validate,
    grid_record,
    rational_345_record,
    rational_mesh_record,
    test_provider_connection as run_provider_connection_test,
    validate_ai_candidate_json,
    validate_explorer_text,
    write_report_files,
)
from counterexample_commons.providers import GenerationResponse
from counterexample_commons.visualization import plot_record


class FakeProvider:
    def __init__(self, raw_text, available=True):
        self.raw_text = raw_text
        self.available = available
        self.calls = 0

    def is_available(self):
        return self.available

    def generate(self, request):
        self.calls += 1
        expected = "Return exactly the string: PROVIDER_LIVE_TEST_OK"
        if request.prompt == expected:
            raw = "PROVIDER_LIVE_TEST_OK"
        else:
            raw = self.raw_text
        return GenerationResponse(
            provider_name="fake",
            model=request.model,
            raw_text=raw,
        )


def test_all_four_baselines_validate():
    records = baseline_records(4, 3, 2)
    assert [r["configuration"] for r in records] == [
        "Line Configuration",
        "Square Grid Configuration",
        "Rational 3/5-4/5 Example",
        "Finite Rational Mesh Baseline",
    ]
    assert all(r["exact_edges"] >= 1 for r in records)
    assert "not Sawin" in records[-1]["scientific_scope"]


def test_visualization_creates_real_plot():
    fig = plot_record(grid_record(3).to_dict())
    assert fig is not None
    assert len(fig.axes) == 1


def test_rational_345_has_non_axis_unit_edge():
    record = rational_345_record().to_dict()
    assert record["exact_edges"] == 2
    assert (0, 1) in [tuple(edge) for edge in record["edges"]]


def test_rational_mesh_boundary_visible():
    record = rational_mesh_record(3).to_dict()
    assert "not Sawin" in record["scientific_scope"]
    assert "not evidence" in record["scientific_scope"]


def test_explorer_result_is_validatable_and_visualizable():
    record, summary, details = validate_explorer_text("0, 0\n1, 0\n3/5, 4/5")
    assert record is not None
    assert details["exact_edges"] == 2
    assert "Finite exact validation only" in summary
    assert plot_record(record) is not None


def test_valid_ai_candidate_pipeline_succeeds():
    raw = json.dumps({
        "candidate_name": "finite rational candidate",
        "points": [["0", "0"], ["1", "0"], ["3/5", "4/5"]],
        "claimed_unit_distance_edges": 2,
        "scope": "finite candidate hypothesis only",
    })
    record, summary, details = validate_ai_candidate_json(raw)
    assert record is not None
    assert details["status"] == AI_VALIDATED
    assert "Finite AI candidate validation only" in summary


def test_rejected_ai_candidate_stays_rejected():
    raw = json.dumps({
        "candidate_name": "bad finite rational candidate",
        "points": [["0", "0"], ["1", "0"], ["3/5", "4/5"]],
        "claimed_unit_distance_edges": 5,
        "scope": "finite candidate hypothesis only",
    })
    record, summary, details = validate_ai_candidate_json(raw)
    assert record is not None
    assert details["status"] == AI_REJECTED
    assert "Candidate rejected" in summary


def test_ai_overclaim_is_rejected():
    raw = json.dumps({
        "candidate_name": "proof of Sawin",
        "points": [["0", "0"], ["1", "0"], ["3/5", "4/5"]],
        "claimed_unit_distance_edges": 2,
        "scope": "proves Sawin asymptotic theorem",
    })
    record, _, details = validate_ai_candidate_json(raw)
    assert record is None
    assert details["status"] == AI_REJECTED


def test_no_key_provider_actions_send_no_request():
    provider = FakeProvider("{}", available=False)
    status = run_provider_connection_test(provider)
    assert status["status"] == "NOT_CONFIGURED"
    record, _, details = generate_and_validate(provider)
    assert record is None
    assert details["status"] == "NOT_CONFIGURED"
    assert provider.calls == 0


def test_fake_provider_connection_and_generation_work():
    raw = json.dumps({
        "candidate_name": "fake provider finite candidate",
        "points": [["0", "0"], ["1", "0"], ["3/5", "4/5"]],
        "claimed_unit_distance_edges": 2,
        "scope": "finite candidate hypothesis only",
    })
    provider = FakeProvider(raw)
    assert run_provider_connection_test(provider)["status"] == "PASS"
    record, _, details = generate_and_validate(provider)
    assert record is not None
    assert details["status"] == AI_VALIDATED


def test_report_contains_provenance_and_no_secret():
    record = rational_mesh_record(2).to_dict()
    report, payload = build_finite_report(record)
    assert payload["available"] is True
    assert "SOURCE-DOCUMENTED RESULTS" in report
    assert "NON-IMPLICATION" in report
    assert "not locally reproduce" in report


def test_report_writes_markdown_and_json(tmp_path):
    record = rational_345_record().to_dict()
    md_path, json_path, report, payload = write_report_files(
        record,
        tmp_path,
    )
    assert payload["available"] is True
    assert md_path is not None
    assert json_path is not None
    assert "SOURCE-DOCUMENTED RESULTS" in report
    assert "finite_validation_report.md" in md_path
    assert "finite_validation_report.json" in json_path
