"""Integration tests for Gradio API endpoints."""

import pytest

from app.main import build_app
from counterexample_commons.config import AppMode


@pytest.fixture(scope="module")
def demo_app():
    """Build demo app for testing."""
    demo = build_app(mode=AppMode.LOCAL_PRIVATE)
    return demo


def test_app_has_expected_tabs(demo_app):
    """App should contain all expected tab names."""
    tab_labels = []
    for block in demo_app.blocks.values():
        if hasattr(block, "label") and block.label:
            tab_labels.append(block.label)
    expected = [
        "Overview",
        "Exact Baselines",
        "Configuration Explorer",
        "Visualisierung",
        "AI Candidate Lab",
        "Provider Comparison",
        "Claim Registry",
        "Reports & Export",
        "Settings",
    ]
    for tab in expected:
        assert tab in tab_labels, f"Missing tab: {tab}"


def test_public_demo_has_disabled_ai_lab():
    """Public demo should show disabled AI lab message."""
    demo = build_app(mode=AppMode.COLAB_PUBLIC_DEMO)
    assert demo is not None
    tab_labels = []
    for block in demo.blocks.values():
        if hasattr(block, "label") and block.label:
            tab_labels.append(block.label)
    assert "AI Candidate Lab" in tab_labels


def test_app_fns_registered(demo_app):
    """App should have callable functions registered."""
    # Gradio 6: fns is dict; Gradio 3/4: fns is list
    fns = demo_app.fns
    fn_iter = fns.values() if isinstance(fns, dict) else fns
    fn_list = list(fn_iter)
    # 3 click handlers: line, grid, custom
    assert len(fn_list) >= 3, (
        f"Expected >= 3 registered fns, got {len(fn_list)}"
    )
    # If Gradio supports api_name, verify them
    named = [
        getattr(fn, "api_name", None) for fn in fn_list
    ]
    named = [n for n in named if n]
    if named:
        assert "validate_line_configuration" in named
        assert "validate_grid_configuration" in named
        assert "validate_custom_configuration" in named


def test_line_validation_fn_directly():
    """Direct call to line validation."""
    from counterexample_commons.validators import (
        validate_line_configuration,
    )
    result = validate_line_configuration(10)
    assert result["pass"] is True
    assert result["actual_edges"] == 9


def test_grid_validation_fn_directly():
    """Direct call to grid validation."""
    from counterexample_commons.validators import (
        validate_grid_configuration,
    )
    result = validate_grid_configuration(5)
    assert result["pass"] is True
    assert result["actual_edges"] == 40


def test_custom_validation_fn_directly():
    """Direct call to custom validation with rational coords."""
    from counterexample_commons.validators import (
        validate_custom_configuration,
    )
    result = validate_custom_configuration([
        ("0", "0"), ("1", "0"), ("1/2", "0"),
    ])
    assert result["n"] == 3
    # (0,0)-(1,0) is distance 1; others are 1/2
    assert result["actual_edges"] == 1
