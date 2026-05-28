"""End-to-end workflow tests for the completed Gradio research lab."""

from __future__ import annotations

import inspect
import os
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from app import main as app_main
from app.main import (
    AI_REJECTED,
    AI_VALIDATED,
    build_app,
    build_finite_report,
    configured_provider_names,
    finite_candidate_prompt,
    generate_ai_candidate_with_provider,
    generate_report_callback,
    no_key_action_result,
    no_key_provider_markdown,
    package_a_baseline_compact_rows,
    overview_markdown,
    package_a_baseline_results,
    package_a_visualize_source,
    provider_connection_test,
    provider_comparison_run,
    provider_statuses,
    settings_markdown,
    source_theorem_map_markdown,
    validate_all_exact_baselines_callback,
    validate_ai_candidate_payload,
    validate_explorer_text,
)
from counterexample_commons.claims import INITIAL_CLAIMS
from counterexample_commons.config import AppMode
from counterexample_commons.env_loader import EnvironmentStatus, load_local_env
from counterexample_commons.providers import (
    GenerationRequest,
    GenerationResponse,
    ProviderRegistry,
)


ROOT = Path(__file__).resolve().parents[1]


class FakeProvider:
    """Tiny fake provider for deterministic no-network tests."""

    def __init__(self, raw_text: str, name: str = "fake") -> None:
        self._raw_text = raw_text
        self._name = name
        self.calls = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_env_var(self) -> str:
        return "FAKE_PROVIDER_KEY"

    def is_available(self) -> bool:
        return True

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        self.calls += 1
        if "PROVIDER_LIVE_TEST_OK" in request.prompt:
            raw = "PROVIDER_LIVE_TEST_OK"
        else:
            raw = self._raw_text
        return GenerationResponse(
            provider_name=self.name,
            model=request.model,
            raw_text=raw,
        )


def fake_registry(raw_text: str) -> tuple[ProviderRegistry, FakeProvider]:
    provider = FakeProvider(raw_text)
    registry = ProviderRegistry()
    registry.register(provider)
    return registry, provider


def valid_candidate_json(claimed: int = 2) -> str:
    return (
        '{"candidate_name": "finite rational triangle", '
        '"points": [["0", "0"], ["3/5", "4/5"], ["1", "0"]], '
        f'"claimed_unit_distance_edges": {claimed}, '
        '"scope": "finite candidate hypothesis only"}'
    )


def no_key_status() -> EnvironmentStatus:
    return EnvironmentStatus(
        repo_root=ROOT,
        local_env_file="NOT_FOUND",
        providers={
            "openai": "NOT_CONFIGURED",
            "anthropic": "NOT_CONFIGURED",
            "openrouter": "NOT_CONFIGURED",
            "google_gemini": "NOT_CONFIGURED",
            "mistral": "NOT_CONFIGURED",
            "ollama_cloud": "NOT_CONFIGURED",
        },
    )


def sawin_claim_state():
    claim = next(
        c for c in INITIAL_CLAIMS
        if c.claim_id == "UD-SAWIN-2026-001"
    )
    return claim.status, claim.locally_validated


def test_explorer_presets_validate_and_visualize():
    for text in [
        "0, 0\n1, 0\n1, 1\n0, 1",
        "0, 0\n3/5, 4/5\n1, 0",
        "0, 0\n1/2, 0\n1, 0\n0, 1/2",
    ]:
        summary, edges, data, state = validate_explorer_text(text)
        assert state is not None
        assert "Exactly validated unit-distance edges" in summary
        assert isinstance(edges, list)
        assert all(len(row) == 3 for row in edges)
        assert all(str(row[1]).startswith("(") for row in edges)
        fig, plot_summary, plot_data = package_a_visualize_source(
            "Latest Explorer Result",
            5,
            3,
            10,
            True,
            True,
            True,
            state,
            None,
        )
        assert fig is not None
        assert plot_data["source_kind"] == "explorer"
        assert "Explorer" in plot_summary
        plt.close(fig)
        assert data["source_kind"] == "explorer"


def test_explorer_malformed_input_is_controlled():
    summary, edges, data, state = validate_explorer_text("0, 0\nbad")
    assert summary.startswith("ERROR:")
    assert edges == []
    assert "error" in data
    assert state is None


def test_explorer_edge_rows_show_exact_endpoint_coordinates():
    _summary, edges, _data, state = validate_explorer_text(
        "0, 0\n1, 0\n1, 1\n0, 1",
    )
    assert state is not None
    assert edges == [
        [1, "(0, 0)", "(1, 0)"],
        [2, "(0, 0)", "(0, 1)"],
        [3, "(1, 0)", "(1, 1)"],
        [4, "(1, 1)", "(0, 1)"],
    ]


def test_finite_reports_for_baseline_explorer_and_ai_are_real():
    baseline = package_a_baseline_results(5, 3, 10)[-1]
    baseline_md, baseline_json, details = build_finite_report(baseline)
    assert "Finite exact validation export only" in baseline_md
    assert "arXiv:2605.20579" in baseline_json
    assert details["secrets_displayed_or_exported"] == "NO"

    _, _, _, explorer_state = validate_explorer_text("0, 0\n1, 0\n0, 1")
    explorer = app_main.ValidatedConfigurationResult.from_state_dict(
        explorer_state,
    )
    explorer_md, _, _ = build_finite_report(explorer)
    assert "Explorer Configuration" in explorer_md

    _, _, ai_state = validate_ai_candidate_payload(valid_candidate_json())
    ai = app_main.ValidatedConfigurationResult.from_state_dict(ai_state)
    ai_md, _, _ = build_finite_report(ai)
    assert "AI-generated candidate independently checked" in ai_md


def test_shared_state_flows_from_baseline_and_explorer_to_export():
    table, summary, technical, baseline_state = (
        validate_all_exact_baselines_callback(5, 3, 10)
    )
    assert table[-1] == [
        "Finite Rational Mesh Baseline",
        121,
        82,
        "LOCALLY_REPRODUCED_EXACT",
    ]
    assert "Scientific scope" in summary
    assert "not Sawin's construction" in summary
    assert technical["latest_result"]["edge_count"] == 82

    preview, md_path, json_path, details = generate_report_callback(
        "Latest Baseline Result",
        baseline_state,
        None,
        None,
    )
    assert not preview.startswith("ERROR:")
    assert "Finite exact validation export only" in preview
    assert "<details>" in preview
    assert "Point Preview (16 of 121)" in preview
    assert "Exact Edge Preview (16 of 82)" in preview
    assert Path(md_path).exists()
    assert Path(json_path).exists()
    assert details["secrets_displayed_or_exported"] == "NO"

    _, _, _, explorer_state = validate_explorer_text(
        "0, 0\n1, 0\n1, 1\n0, 1",
    )
    fig, plot_summary, plot_data = package_a_visualize_source(
        "Latest Explorer Result",
        5,
        3,
        10,
        False,
        True,
        True,
        explorer_state,
        None,
    )
    assert fig is not None
    assert "Explorer Configuration" in plot_summary
    assert plot_data["source_kind"] == "explorer"
    plt.close(fig)
    preview, md_path, json_path, _ = generate_report_callback(
        "Latest Explorer Result",
        None,
        explorer_state,
        None,
    )
    assert not preview.startswith("ERROR:")
    assert Path(md_path).exists()
    assert Path(json_path).exists()


def test_shared_state_flows_from_fake_ai_to_visualisation_and_export():
    _, _, ai_state = validate_ai_candidate_payload(valid_candidate_json())
    fig, summary, data = package_a_visualize_source(
        "Latest AI Candidate Result",
        5,
        3,
        10,
        False,
        True,
        True,
        None,
        ai_state,
    )
    assert fig is not None
    assert data["source_kind"] == "ai_candidate"
    assert AI_VALIDATED in summary
    plt.close(fig)
    preview, md_path, json_path, _ = generate_report_callback(
        "Latest AI Candidate Result",
        None,
        None,
        ai_state,
    )
    assert not preview.startswith("ERROR:")
    assert "AI-generated candidate independently checked" in preview
    assert Path(md_path).exists()
    assert Path(json_path).exists()


def test_baseline_compact_rows_keep_scope_out_of_cramped_table():
    results = package_a_baseline_results(5, 3, 10)
    rows = package_a_baseline_compact_rows(results)
    assert len(rows[-1]) == 4
    assert "not Sawin" not in " ".join(str(cell) for cell in rows[-1])


def test_reports_sanitize_fake_secret():
    prefix = "s" + "k" + "-"
    result = package_a_baseline_results(5, 3, 10)[0]
    secret_result = app_main.ValidatedConfigurationResult(
        name="Secret Test",
        points=result.points,
        exact_edges=result.exact_edges,
        edge_count=result.edge_count,
        validation_status=result.validation_status,
        scientific_scope=prefix + "abcdefghijklmnopqrstuvwxyz1234",
        source_kind="baseline",
    )
    md, json_text, details = build_finite_report(secret_result)
    assert prefix not in md
    assert prefix not in json_text
    assert details["sanitization_status"] == "REDACTED"


def test_env_loader_root_local_override_false(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "outer-value")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n")
    (repo / ".env").write_text("OPENAI_API_KEY=inner-value\n")
    status = load_local_env(repo)
    assert status.local_env_file == "FOUND"
    assert os.environ["OPENAI_API_KEY"] == "outer-value"
    assert status.providers["openai"] == "CONFIGURED"


def test_env_example_uses_supported_provider_variables_only():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    supported = {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
        "MISTRAL_API_KEY",
        "OLLAMA_API_KEY",
    }
    for line in text.splitlines():
        if line.endswith("_API_KEY="):
            assert line.split("=")[0] in supported


def test_dot_env_is_gitignored():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text


def test_no_key_overview_settings_and_actions_are_safe(monkeypatch):
    class UnavailableRegistry:
        def list_names(self):
            return ["ollama_local", "openai"]

        def get(self, name):
            class Provider:
                api_key_env_var = "OPENAI_API_KEY" if name == "openai" else ""

                def is_available(self):
                    return False

            return Provider()

    monkeypatch.setattr(
        app_main,
        "build_default_registry",
        UnavailableRegistry,
    )
    for key in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
        "MISTRAL_API_KEY",
        "OLLAMA_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
    env = no_key_status()
    overview = overview_markdown(env)
    settings = settings_markdown(AppMode.LOCAL_PRIVATE, env)
    assert "SAFE NO-KEY SESSION" in overview
    assert "No live API request can be sent" in overview
    assert "```text" not in overview
    assert "Exact finite baselines, explorer, visualisation" in overview
    assert "LOCAL_ENV_FILE: NOT_FOUND" in settings
    assert "NOT_CONFIGURED" in no_key_provider_markdown(env)
    assert "RESULT: NOT_CONFIGURED" in no_key_action_result()
    assert provider_statuses(env)["openai"] == "NOT_CONFIGURED"
    assert build_app(AppMode.COLAB_PUBLIC_DEMO) is not None


def test_local_ollama_status_enables_full_local_ai_ui(monkeypatch):
    class FakeOllama:
        api_key_env_var = ""

        def is_available(self):
            return True

    class FakeRegistry:
        def list_names(self):
            return ["ollama_local"]

        def get(self, name):
            return FakeOllama()

    monkeypatch.setattr(app_main, "build_default_registry", FakeRegistry)
    env = no_key_status()
    statuses = provider_statuses(env)
    assert statuses["ollama_local"] == "CONFIGURED"
    assert app_main.any_live_provider_configured(env) is True
    assert configured_provider_names(env) == ["ollama_local"]
    assert "LIVE AI CONFIGURED" in overview_markdown(env)


def test_ai_candidate_validation_success_rejection_and_overclaims():
    summary, data, state = validate_ai_candidate_payload(
        valid_candidate_json(),
    )
    assert AI_VALIDATED in summary
    assert data["claim_match"] is True
    assert state is not None

    summary, data, state = validate_ai_candidate_payload(
        valid_candidate_json(claimed=5),
    )
    assert AI_REJECTED in summary
    assert data["claim_match"] is False
    assert state is not None

    duplicate = (
        '{"candidate_name": "dup", '
        '"points": [["0", "0"], ["0", "0"], ["1", "0"]], '
        '"claimed_unit_distance_edges": 1, '
        '"scope": "finite candidate hypothesis only"}'
    )
    summary, data, state = validate_ai_candidate_payload(duplicate)
    assert AI_REJECTED in summary
    assert data["error"] == "DUPLICATE_POINT"
    assert state is None

    overclaim = valid_candidate_json().replace(
        "finite candidate hypothesis only",
        "this is an asymptotic theorem",
    )
    summary, data, state = validate_ai_candidate_payload(overclaim)
    assert AI_REJECTED in summary
    assert data["error"] == "FORBIDDEN_OVERCLAIM"
    assert state is None


def test_fake_provider_connection_generation_and_comparison():
    registry, provider = fake_registry(valid_candidate_json())
    summary, data = provider_connection_test("fake", registry=registry)
    assert "RESULT: PASS" in summary
    assert data["secrets_displayed"] == "NO"

    summary, data, state = generate_ai_candidate_with_provider(
        "fake",
        registry=registry,
    )
    assert AI_VALIDATED in summary
    assert state is not None
    assert provider.calls == 2

    rows, comparison_summary = provider_comparison_run(
        ["fake", "missing"],
        registry=registry,
    )
    assert len(rows) == 2
    assert rows[0][3] == 2
    assert rows[1][1] == "NOT_CONFIGURED"
    assert "at most one" in comparison_summary


def test_ai_candidate_result_is_visualizable_and_claims_unchanged():
    before = sawin_claim_state()
    _, _, state = validate_ai_candidate_payload(valid_candidate_json())
    fig, summary, data = package_a_visualize_source(
        "Latest AI Candidate Result",
        5,
        3,
        10,
        True,
        True,
        True,
        None,
        state,
    )
    assert fig is not None
    assert data["validation_status"] == AI_VALIDATED
    assert "not Sawin's construction" in summary
    plt.close(fig)
    assert sawin_claim_state() == before


def test_source_map_provenance_is_correct():
    text = source_theorem_map_markdown()
    assert "OpenAI fixed delta > 0" in text
    assert "NOT_PROVIDED_BY_ORIGINAL_PROOF" in text
    assert "arXiv:2605.20579" in text
    assert "LOCALLY_REPRODUCED_EXACT" in text
    assert "Not Sawin" in text or "not Sawin" in text
    assert "| Result | Source |" not in text
    assert "PRIMARY_PROOF_PENDING" not in text


def test_finite_candidate_prompt_does_not_invite_overclaims():
    prompt = finite_candidate_prompt()
    assert "strict JSON" in prompt
    assert "No proof" in prompt
    assert "Sawin" in prompt


def test_default_private_launch_refuses_public_share_and_live_flag_exists():
    source = (
        ROOT / "scripts" / "run_gradio_local.py"
    ).read_text(encoding="utf-8")
    assert "--confirm-live-ai-share" in source
    assert "WARNING - SHARED LIVE AI SESSION" in source

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_gradio_local.py",
            "--mode",
            "local-private",
            "--confirm-public-share",
            "--no-browser",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert result.returncode != 0
    assert "Refusing public share" in result.stderr or result.stdout


def test_no_duplicate_edge_counter_in_app_workflows():
    source = inspect.getsource(app_main.validate_explorer_text)
    source += inspect.getsource(app_main.validate_ai_candidate_payload)
    assert "count_unit_edges_exact" in source
    assert "squared_distance" not in source
