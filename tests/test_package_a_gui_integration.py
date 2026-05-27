"""Package A GUI and exact-baseline integration tests."""

import inspect

import matplotlib.pyplot as plt

from app import main as app_main
from app.main import (
    build_app,
    package_a_baseline_results,
    package_a_baseline_table_rows,
    package_a_visualize_source,
)
from counterexample_commons.claims import ClaimStatus, INITIAL_CLAIMS
from counterexample_commons.config import AppMode


def _sawin_claim():
    return next(c for c in INITIAL_CLAIMS if c.claim_id == "UD-SAWIN-2026-001")


def test_app_text_exposes_package_a_labels():
    """App source includes all required Package A user-facing labels."""
    source = inspect.getsource(app_main)
    for label in [
        "Line Configuration",
        "Square Grid Configuration",
        "Rational 3/5–4/5 Example",
        "Finite Rational Mesh Baseline",
        "Visualisierung exakt validierter Punktkonfigurationen",
    ]:
        assert label in source
    assert "Package A: Baseline visualization coming" not in source
    assert "Test." not in source


def test_app_builds_with_visualisierung_tab():
    """The Gradio app builds and exposes the dedicated Visualisierung tab."""
    demo = build_app(mode=AppMode.LOCAL_PRIVATE)
    labels = [
        block.label for block in demo.blocks.values()
        if hasattr(block, "label") and block.label
    ]
    assert "Visualisierung" in labels
    assert "Visualization" in labels


def test_baseline_callback_produces_all_four_records():
    """The consolidated baseline path validates all four baselines."""
    results = package_a_baseline_results(5, 3, 10)
    assert [result.name for result in results] == [
        "Line Configuration",
        "Square Grid Configuration",
        "Rational 3/5–4/5 Example",
        "Finite Rational Mesh Baseline",
    ]
    rows = package_a_baseline_table_rows(results)
    assert rows[-1][1] == 121
    assert rows[-1][2] == 82
    assert "not Sawin's construction" in rows[-1][4]


def test_rational_345_contains_expected_exact_edge():
    """The non-axis rational example uses exact rational validation."""
    result = package_a_baseline_results(5, 3, 10)[2]
    assert result.edge_count == 2
    assert (0, 1) in result.exact_edges
    assert "3/5" in result.scientific_scope


def test_visualization_callback_returns_figures_for_all_baselines():
    """Visualisierung returns real Matplotlib figures for baseline sources."""
    for source in [
        "Line Configuration",
        "Square Grid Configuration",
        "Rational 3/5–4/5 Example",
        "Finite Rational Mesh Baseline",
    ]:
        fig, summary, data = package_a_visualize_source(
            source,
            5,
            3,
            10,
            True,
            True,
            True,
            None,
            None,
        )
        assert fig is not None
        assert data["edge_count"] >= 1
        assert "Exactly validated unit-distance edges" in summary
        plt.close(fig)


def test_visualization_missing_session_results_are_controlled():
    """Explorer/AI sources must not fabricate data in Package A."""
    _, explorer_summary, explorer_data = package_a_visualize_source(
        "Latest Explorer Result",
        5,
        3,
        10,
        True,
        True,
        True,
        None,
        None,
    )
    _, ai_summary, ai_data = package_a_visualize_source(
        "Latest AI Candidate Result",
        5,
        3,
        10,
        True,
        True,
        True,
        None,
        None,
    )
    assert explorer_summary == (
        "No validated Explorer result available in this session."
    )
    assert ai_summary == "No validated AI candidate available in this session."
    assert explorer_data == {}
    assert ai_data == {}


def test_rational_mesh_summary_has_required_boundary():
    """Rational mesh summary states the finite-only boundary."""
    _, summary, data = package_a_visualize_source(
        "Finite Rational Mesh Baseline",
        5,
        3,
        10,
        True,
        True,
        True,
        None,
        None,
    )
    assert data["name"] == "Finite Rational Mesh Baseline"
    assert "Number of points: 121" in summary
    assert "Exactly validated unit-distance edges: 82" in summary
    assert "Validation status: LOCALLY_REPRODUCED_EXACT" in summary
    assert "not Sawin's construction" in summary
    assert "not evidence for exponent n^1.014" in summary


def test_sawin_claim_status_not_mutated_by_package_a():
    """Package A must not upgrade or mutate Sawin claim status."""
    sawin = _sawin_claim()
    before = (sawin.status, sawin.locally_validated)
    package_a_baseline_results(5, 3, 10)
    package_a_visualize_source(
        "Finite Rational Mesh Baseline",
        5,
        3,
        10,
        True,
        True,
        True,
        None,
        None,
    )
    after = (sawin.status, sawin.locally_validated)
    assert before == (ClaimStatus.SOURCE_DOCUMENTED, False)
    assert after == before


def test_package_a_functions_do_not_use_providers_or_network():
    """Baseline/visualization functions must be no-key local operations."""
    source = inspect.getsource(app_main.package_a_baseline_results)
    source += inspect.getsource(app_main.package_a_visualize_source)
    forbidden = ["build_default_registry", "provider", "requests", "http"]
    for token in forbidden:
        assert token not in source
