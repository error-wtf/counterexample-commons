"""Main Gradio application builder."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gradio as gr
from sympy import Rational

from counterexample_commons.claims import INITIAL_CLAIMS
from counterexample_commons.config import AppMode, CAPABILITY_MATRIX
from counterexample_commons.env_loader import EnvironmentStatus, load_local_env
from counterexample_commons.experiments import sanitize_for_export
from counterexample_commons.providers import (
    GenerationRequest,
    ProviderConnectionError,
    ProviderNotConfiguredError,
    ProviderResponseError,
    build_default_registry,
)
from counterexample_commons.providers.config import PROVIDER_DEFAULTS
from counterexample_commons.validated_result import (
    ValidatedConfigurationResult,
)
from counterexample_commons.validators import (
    count_unit_edges_exact,
    validate_custom_configuration,
    validate_grid_configuration,
    validate_line_configuration,
)
from counterexample_commons.visualization import plot_from_result
from case_studies.erdos_unit_distance_2026.rational_mesh_baseline import (
    rational_mesh_points,
)


SCIENTIFIC_BOUNDARY = (
    "This UI cannot promote hypotheses to proofs. "
    "Exact finite validation is not an asymptotic theorem. "
    "AI-generated candidates require independent validation."
)

SECURITY_WARNING = (
    "A Gradio share link is accessible to anyone who receives the link. "
    "Public demo mode disables external AI API calls and secret use."
)

LIVE_AI_SHARE_WARNING = (
    "WARNING - SHARED LIVE AI SESSION\n\n"
    "This running Gradio session may send real requests to configured AI "
    "providers. Anyone with access to the shared URL may be able to trigger "
    "API requests, consume quota or incur cost.\n\n"
    "Your provider key is not displayed or exported, but your configured "
    "account may be used through this session.\n\n"
    "Proceed only if you accept responsibility for who receives access and "
    "for resulting usage."
)

RATIONAL_MESH_BOUNDARY = (
    "Finite rational mesh baseline - not Sawin's construction. "
    "Finite exact validation only; not evidence for exponent n^1.014."
)
FINITE_SCOPE = "Finite exact validation only."
RATIONAL_345_SCOPE = (
    "Exact rational non-axis unit-distance example. "
    "The displacement (3/5, 4/5) is validated exactly. "
    "Finite exact validation only."
)
EXPLORER_SCOPE = (
    "Finite exact validation only. This explorer does not reproduce Sawin's "
    "asymptotic construction and does not generate formal proofs."
)
AI_SCOPE = (
    "Finite infrastructure test only; not Sawin's construction, "
    "not an asymptotic theorem, and not a new proof."
)
FINITE_EXPORT_BOUNDARY = (
    "Finite exact validation export only; not an asymptotic theorem, "
    "not a Sawin reproduction, and not a formal proof of a new bound."
)
AI_EXPORT_BOUNDARY = (
    "AI-generated candidate independently checked by the finite exact "
    "validator. Validation applies only to this finite point configuration."
)

AI_VALIDATED = "AI_GENERATED_HYPOTHESIS_VALIDATED_FINITE_ONLY"
AI_REJECTED = "AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR"
NOT_CONFIGURED_MESSAGE = (
    "RESULT: NOT_CONFIGURED\n"
    "No live provider request was executed.\n"
    "Configure a provider locally via `.env` and restart the app."
)


EXPLORER_PRESETS = {
    "Unit Square": "0, 0\n1, 0\n1, 1\n0, 1",
    "Rational 3/5–4/5 Example": "0, 0\n3/5, 4/5\n1, 0",
    "Small Rational Mesh": "0, 0\n1/2, 0\n1, 0\n0, 1/2\n1/2, 1/2\n1, 1/2",
}


SOURCE_THEOREM_ROWS = [
    [
        "OpenAI fixed delta > 0",
        "OpenAI announcement and proof PDF",
        "SOURCE_DOCUMENTED",
        "No",
        "Not locally reproduced.",
    ],
    [
        "Original OpenAI proof explicit delta = 0.014",
        "Original proof source boundary",
        "NOT_PROVIDED_BY_ORIGINAL_PROOF",
        "No",
        "The original proof establishes fixed delta > 0, not 0.014.",
    ],
    [
        "Sawin explicit n^1.014",
        "Will Sawin, arXiv:2605.20579",
        "SOURCE_DOCUMENTED",
        "No",
        "Primary-source documented; not locally reproduced.",
    ],
    [
        "Finite Rational Mesh Baseline",
        "Repository exact validator",
        "LOCALLY_REPRODUCED_EXACT",
        "Yes",
        "Finite exact baseline only; not Sawin's construction.",
    ],
]


APP_CSS = """
.gradio-container {
    max-width: 1280px !important;
}
.cc-wrap, .cc-wrap * {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
}
.cc-card {
    border: 1px solid var(--border-color-primary);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin: 0.6rem 0;
    background: var(--background-fill-secondary);
}
.cc-status {
    border-left: 4px solid #2f55ff;
    padding: 0.85rem 1rem;
    background: var(--background-fill-secondary);
}
"""


def _points_to_strings(points):
    return [(str(x), str(y)) for x, y in points]


def _validated_result_from_points(
    name: str,
    points,
    scientific_scope: str,
    source_kind: str = "baseline",
    validation_status: str = "LOCALLY_REPRODUCED_EXACT",
) -> ValidatedConfigurationResult:
    edge_count, edges = count_unit_edges_exact(points)
    return ValidatedConfigurationResult(
        name=name,
        points=_points_to_strings(points),
        exact_edges=edges,
        edge_count=edge_count,
        validation_status=validation_status,
        scientific_scope=scientific_scope,
        source_kind=source_kind,
    )


def line_baseline_result(n: int) -> ValidatedConfigurationResult:
    """Validate a finite line configuration through the exact path."""
    points = [(Rational(i), Rational(0)) for i in range(int(n))]
    return _validated_result_from_points(
        "Line Configuration",
        points,
        FINITE_SCOPE,
    )


def square_grid_baseline_result(k: int) -> ValidatedConfigurationResult:
    """Validate a finite square grid through the exact path."""
    points = [
        (Rational(i), Rational(j))
        for i in range(int(k))
        for j in range(int(k))
    ]
    return _validated_result_from_points(
        "Square Grid Configuration",
        points,
        FINITE_SCOPE,
    )


def rational_345_baseline_result() -> ValidatedConfigurationResult:
    """Validate the exact rational 3/5-4/5 example."""
    points = [
        (Rational(0), Rational(0)),
        (Rational(3, 5), Rational(4, 5)),
        (Rational(1), Rational(0)),
    ]
    return _validated_result_from_points(
        "Rational 3/5–4/5 Example",
        points,
        RATIONAL_345_SCOPE,
    )


def rational_mesh_baseline_result(m: int) -> ValidatedConfigurationResult:
    """Validate the finite rational mesh baseline through the exact path."""
    return _validated_result_from_points(
        "Finite Rational Mesh Baseline",
        rational_mesh_points(int(m)),
        RATIONAL_MESH_BOUNDARY,
    )


def package_a_baseline_results(
    line_n: int,
    grid_k: int,
    mesh_m: int,
) -> list[ValidatedConfigurationResult]:
    """Return all Package-A baseline results."""
    return [
        line_baseline_result(line_n),
        square_grid_baseline_result(grid_k),
        rational_345_baseline_result(),
        rational_mesh_baseline_result(mesh_m),
    ]


def package_a_baseline_table_rows(results) -> list[list[str | int]]:
    """Return readable rows for the Exact Baselines tab."""
    return [result.to_table_row() for result in results]


def package_a_baseline_compact_rows(results) -> list[list[str | int]]:
    """Return compact rows that keep long scope text out of table cells."""
    return [
        [
            result.name,
            result.point_count,
            result.edge_count,
            result.validation_status,
        ]
        for result in results
    ]


def package_a_result_summary(result: ValidatedConfigurationResult) -> str:
    """Return a UI summary for a validated configuration."""
    return result.to_summary_markdown()


def baseline_scope_cards_markdown(results) -> str:
    """Return readable scope summaries outside cramped table columns."""
    sections = [
        "### Scientific scope",
        "",
        "Each row above was checked through the exact rational validator.",
    ]
    for result in results:
        sections.extend([
            "",
            '<div class="cc-card">',
            f"<strong>{result.name}</strong><br>",
            f"Points: {result.point_count}<br>",
            f"Exactly validated unit-distance edges: {result.edge_count}<br>",
            f"Status: <code>{result.validation_status}</code><br>",
            f"Scientific scope: {result.scientific_scope}",
            "</div>",
        ])
    return "\n".join(sections)


def validate_all_exact_baselines_callback(
    line_n: int,
    grid_k: int,
    mesh_m: int,
) -> tuple[list[list[str | int]], str, dict, dict]:
    """Validate all exact baselines and update shared latest-baseline state."""
    results = package_a_baseline_results(
        int(line_n),
        int(grid_k),
        int(mesh_m),
    )
    latest = results[-1]
    technical = {
        "latest_result": latest.to_state_dict(),
        "all_results": {
            result.name: result.to_state_dict()
            for result in results
        },
    }
    return (
        package_a_baseline_compact_rows(results),
        baseline_scope_cards_markdown(results),
        technical,
        latest.to_state_dict(),
    )


def package_a_visualize_source(
    source_name: str,
    line_n: int,
    grid_k: int,
    mesh_m: int,
    show_labels: bool,
    show_edges: bool,
    show_grid: bool,
    latest_explorer,
    latest_ai,
):
    """Validate and visualize a Package-A source selection."""
    if source_name == "Line Configuration":
        result = line_baseline_result(line_n)
    elif source_name == "Square Grid Configuration":
        result = square_grid_baseline_result(grid_k)
    elif source_name == "Rational 3/5–4/5 Example":
        result = rational_345_baseline_result()
    elif source_name == "Finite Rational Mesh Baseline":
        result = rational_mesh_baseline_result(mesh_m)
    elif source_name == "Latest Explorer Result":
        if not latest_explorer:
            return (
                None,
                "No validated Explorer result available in this session.",
                {},
            )
        result = ValidatedConfigurationResult.from_state_dict(
            latest_explorer,
        )
    elif source_name == "Latest AI Candidate Result":
        if not latest_ai:
            return (
                None,
                "No validated AI candidate available in this session.",
                {},
            )
        result = ValidatedConfigurationResult.from_state_dict(latest_ai)
    else:
        raise ValueError(f"Unknown configuration source: {source_name}")

    fig = plot_from_result(
        result,
        show_labels=show_labels,
        show_edges=show_edges,
        show_grid=show_grid,
    )
    return fig, package_a_result_summary(result), result.to_state_dict()


def explorer_preset_text(name: str) -> str:
    """Return explorer preset text."""
    if name == "Small Rational Mesh":
        points = rational_mesh_points(2)
        return "\n".join(f"{x}, {y}" for x, y in points)
    return EXPLORER_PRESETS.get(name, "")


def parse_rational_points_text(text: str) -> list[tuple[Rational, Rational]]:
    """Parse one rational point per line from explorer text."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < 2:
        raise ValueError("Need at least two finite rational points.")

    points = []
    for index, line in enumerate(lines, start=1):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            raise ValueError(
                f"Line {index}: expected `x, y`, got {line!r}."
            )
        try:
            points.append((Rational(parts[0]), Rational(parts[1])))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Line {index}: invalid rational coordinate."
            ) from exc
    if len(set(points)) != len(points):
        raise ValueError("Duplicate points are not allowed.")
    return points


def validate_explorer_text(
    text: str,
    name: str = "Explorer Configuration",
) -> tuple[str, list[list[str | int]], dict, dict | None]:
    """Validate explorer text and return UI-ready values."""
    try:
        points = parse_rational_points_text(text)
    except ValueError as exc:
        return f"ERROR: {exc}", [], {"error": str(exc)}, None

    # Preserve legacy validator behaviour as a secondary schema check.
    validate_custom_configuration(_points_to_strings(points))
    result = _validated_result_from_points(
        name,
        points,
        EXPLORER_SCOPE,
        source_kind="explorer",
    )
    edge_rows = [
        [
            index,
            f"({result.points[i][0]}, {result.points[i][1]})",
            f"({result.points[j][0]}, {result.points[j][1]})",
        ]
        for index, (i, j) in enumerate(result.exact_edges, start=1)
    ]
    return (
        result.to_summary_markdown(),
        edge_rows,
        result.to_state_dict(),
        result.to_state_dict(),
    )


def _result_from_state(data: dict | None) -> ValidatedConfigurationResult:
    if not data:
        raise ValueError("No validated result is available.")
    return ValidatedConfigurationResult.from_state_dict(data)


def result_options(
    baseline_state,
    explorer_state,
    ai_state,
) -> list[str]:
    """Return available finite result labels."""
    labels = []
    if baseline_state:
        labels.append("Latest Baseline Result")
    if explorer_state:
        labels.append("Latest Explorer Result")
    if ai_state:
        labels.append("Latest AI Candidate Result")
    return labels


def select_result(
    source_name: str,
    baseline_state,
    explorer_state,
    ai_state,
) -> ValidatedConfigurationResult:
    """Select a result from Gradio state."""
    if source_name == "Latest Baseline Result":
        return _result_from_state(baseline_state)
    if source_name == "Latest Explorer Result":
        return _result_from_state(explorer_state)
    if source_name == "Latest AI Candidate Result":
        return _result_from_state(ai_state)
    raise ValueError(f"Unknown report source: {source_name}")


def provenance_markdown() -> str:
    """Return source/theorem provenance markdown."""
    return "\n".join([
        "## Provenance",
        "",
        "SOURCE-DOCUMENTED RESULTS:",
        "- OpenAI proof: existence of fixed delta > 0, not locally "
        "reproduced.",
        "- Original OpenAI proof: explicit delta = 0.014 is not provided "
        "by the original proof.",
        "- Sawin n^1.014: primary-source documented through "
        "arXiv:2605.20579, not locally reproduced.",
        "",
        "LOCALLY EXECUTED RESULTS:",
        "- Specific finite baseline, explorer, or AI candidate checked in "
        "this runtime.",
        "",
        "NON-IMPLICATION:",
        "- A finite validated configuration does not locally reproduce the "
        "asymptotic OpenAI theorem or Sawin's explicit result.",
    ])


def _compact_sequence_markdown(
    title: str,
    items,
    total: int,
    limit: int = 16,
) -> str:
    """Return compact preview text for report markdown."""
    preview = list(items)[:limit]
    body = "\n".join([
        f"## {title}",
        "",
        "```json",
        json.dumps(preview, indent=2),
        "```",
    ])
    if total > limit:
        body += (
            f"\n\nShowing {len(preview)} of {total}. "
            "The complete data is included in the JSON download."
        )
        return "\n".join([
            "<details>",
            f"<summary>{title} ({len(preview)} of {total})</summary>",
            "",
            body,
            "",
            "</details>",
        ])
    return body


def build_finite_report(
    result: ValidatedConfigurationResult,
) -> tuple[str, str, dict]:
    """Build sanitized Markdown and JSON finite validation reports."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "configuration_name": result.name,
        "source_type": result.source_kind,
        "point_count": result.point_count,
        "exact_unit_distance_edge_count": result.edge_count,
        "validation_status": result.validation_status,
        "scientific_scope": result.scientific_scope,
        "points": list(result.points),
        "exact_edges": list(result.exact_edges),
        "boundary": FINITE_EXPORT_BOUNDARY,
        "provenance": {
            "openai_fixed_delta": "SOURCE_DOCUMENTED; not locally "
            "reproduced",
            "openai_original_explicit_delta_0014": (
                "NOT_PROVIDED_BY_ORIGINAL_PROOF"
            ),
            "sawin_explicit_n_1_014": (
                "SOURCE_DOCUMENTED; primary source arXiv:2605.20579; "
                "not locally reproduced"
            ),
            "non_implication": (
                "Finite validation does not reproduce the asymptotic "
                "OpenAI theorem or Sawin result."
            ),
        },
    }
    if result.source_kind == "ai_candidate":
        payload["ai_boundary"] = AI_EXPORT_BOUNDARY

    markdown = "\n".join([
        f"# Finite Validation Report - {result.name}",
        "",
        f"- Configuration name: {result.name}",
        f"- Source type: {result.source_kind}",
        f"- Number of points: {result.point_count}",
        "- Exactly validated unit-distance edges: "
        f"{result.edge_count}",
        f"- Validation status: {result.validation_status}",
        f"- Scientific scope: {result.scientific_scope}",
        "",
        "## Boundary",
        FINITE_EXPORT_BOUNDARY,
        "",
        AI_EXPORT_BOUNDARY if result.source_kind == "ai_candidate" else "",
        provenance_markdown(),
        "",
        _compact_sequence_markdown(
            "Point Preview",
            result.points,
            result.point_count,
        ),
        "",
        _compact_sequence_markdown(
            "Exact Edge Preview",
            result.exact_edges,
            result.edge_count,
        ),
    ])
    json_text = json.dumps(payload, indent=2)
    sanitized_md = sanitize_for_export(markdown)
    sanitized_json = sanitize_for_export(json_text)
    details = {
        "sanitization_status": (
            "UNCHANGED" if sanitized_md == markdown
            and sanitized_json == json_text
            else "REDACTED"
        ),
        "secrets_displayed_or_exported": "NO",
    }
    return sanitized_md, sanitized_json, details


def write_report_files(
    result: ValidatedConfigurationResult,
) -> tuple[str, str, str, dict]:
    """Create temp Markdown/JSON report files for Gradio download."""
    markdown, json_text, details = build_finite_report(result)
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", result.name).strip("_")
    out_dir = Path(tempfile.mkdtemp(prefix="counterexample_commons_report_"))
    md_path = out_dir / f"{safe_name}.md"
    json_path = out_dir / f"{safe_name}.json"
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json_text, encoding="utf-8")
    return markdown, str(md_path), str(json_path), details


def generate_report_callback(
    source_name: str,
    baseline_state,
    explorer_state,
    ai_state,
):
    """Generate report preview and download files."""
    try:
        result = select_result(
            source_name,
            baseline_state,
            explorer_state,
            ai_state,
        )
    except ValueError as exc:
        return f"ERROR: {exc}", None, None, {"error": str(exc)}
    return write_report_files(result)


def _empty_env_status() -> EnvironmentStatus:
    providers = {
        name: "NOT_CONFIGURED"
        for name in PROVIDER_DEFAULTS
        if name != "ollama_local"
    }
    return EnvironmentStatus(
        repo_root=Path.cwd(),
        local_env_file="NOT_FOUND",
        providers=providers,
    )


def environment_for_mode(mode: AppMode) -> EnvironmentStatus:
    """Load env only in private modes; public modes stay no-key."""
    if mode in {AppMode.LOCAL_PRIVATE, AppMode.COLAB_PRIVATE}:
        return load_local_env()
    return _empty_env_status()


def provider_statuses(
    env_status: EnvironmentStatus,
    registry=None,
) -> dict[str, str]:
    """Return provider CONFIGURED / NOT_CONFIGURED statuses."""
    registry = registry or build_default_registry()
    statuses = {}
    for name in registry.list_names():
        provider = registry.get(name)
        if name == "ollama_local":
            statuses[name] = (
                "CONFIGURED"
                if provider and provider.is_available()
                else "NOT_CONFIGURED"
            )
        elif provider and provider.api_key_env_var:
            configured = env_status.providers.get(name) == "CONFIGURED"
            statuses[name] = "CONFIGURED" if configured else "NOT_CONFIGURED"
        else:
            statuses[name] = "NOT_CONFIGURED"
    return statuses


def any_live_provider_configured(env_status: EnvironmentStatus) -> bool:
    """Return whether any live provider key is configured."""
    return (
        env_status.any_provider_configured
        or provider_statuses(env_status).get("ollama_local") == "CONFIGURED"
    )


def configured_provider_names(
    env_status: EnvironmentStatus,
    registry=None,
) -> list[str]:
    """Return provider names that can be explicitly selected now."""
    registry = registry or build_default_registry()
    statuses = provider_statuses(env_status, registry)
    return [
        name for name in registry.list_names()
        if statuses.get(name) == "CONFIGURED"
    ]


def overview_markdown(
    env_status: EnvironmentStatus,
    live_ai_share: bool = False,
) -> str:
    """Build the Overview text for current env status."""
    if any_live_provider_configured(env_status):
        session_lines = [
            "**LIVE AI CONFIGURED**",
            "",
            "- Real provider requests are available in this running session.",
            "- Requests may consume quota or incur cost.",
            "- Credentials are never displayed or exported.",
            "- AI-generated candidates remain hypotheses until independently "
            "checked by the exact finite validator.",
        ]
    else:
        session_lines = [
            "**SAFE NO-KEY SESSION**",
            "",
            "- No live provider is configured.",
            "- Exact finite baselines, explorer, visualisation, read-only "
            "claims and finite exports are available.",
            "- AI actions are visible but inactive until local provider "
            "credentials are configured.",
            "- No live API request can be sent in the current state.",
        ]
    warning = (
        "\n\n## Live Share Warning\n\n" + LIVE_AI_SHARE_WARNING
        if live_ai_share else ""
    )
    return "\n".join([
        "# Counterexample Commons",
        "## An Anti-Capitalist AI-Assisted Mathematics Research Lab",
        "",
        "First case study: exact finite validation around the 2026 "
        "unit-distance breakthrough.",
        "",
        '<div class="cc-status">',
        *session_lines,
        "</div>",
        "",
        "Sawin n^1.014: SOURCE_DOCUMENTED - primary source "
        "arXiv:2605.20579; not locally reproduced.",
        "",
        "Finite rational mesh baseline: LOCALLY_REPRODUCED_EXACT - "
        "not Sawin's construction.",
        "",
        SCIENTIFIC_BOUNDARY,
        warning,
    ])


def settings_markdown(
    mode: AppMode,
    env_status: EnvironmentStatus,
    live_ai_share: bool = False,
) -> str:
    """Build secret-free Settings text."""
    caps = CAPABILITY_MATRIX[mode]
    statuses = provider_statuses(env_status)
    provider_lines = [
        f"- **{name}:** {status}"
        for name, status in sorted(statuses.items())
    ]
    return "\n".join([
        "## Settings & Configuration",
        "",
        f"- **Runtime mode:** `{mode.value}`",
        f"- LOCAL_ENV_FILE: {env_status.local_env_file}",
        f"- **AI Candidate Lab capability:** {caps.ai_candidate_lab}",
        f"- **Provider Comparison capability:** "
        f"{caps.provider_comparison}",
        f"- **Claim Registry editable:** {caps.claim_registry_editable}",
        f"- **Live AI sharing confirmed:** {live_ai_share}",
        "",
        "### Provider Status",
        "",
        *provider_lines,
        "",
        "Secret values, fragments, token lengths and headers are never "
        "displayed.",
    ])


def no_key_ai_markdown() -> str:
    """Return visible no-key AI state."""
    return "\n".join([
        "## AI Candidate Lab",
        "",
        "NO LIVE PROVIDER CONFIGURED",
        "",
        "No API key has been configured for this session.",
        "",
        "To run real AI candidate tests locally:",
        "1. Copy `.env.example` to `.env`.",
        "2. Enter your own supported provider key in `.env`.",
        "3. Restart the Gradio app in local-private mode.",
        "",
        "No live request has been sent.",
        "Exact finite baseline, explorer, visualisation and export "
        "functions remain available without AI access.",
    ])


def no_key_provider_markdown(env_status: EnvironmentStatus) -> str:
    """Return visible no-key provider comparison state."""
    statuses = provider_statuses(env_status)
    lines = [
        f"- {name}: {status}"
        for name, status in sorted(statuses.items())
    ]
    return "\n".join([
        "## Provider Comparison",
        "",
        "No providers configured for live comparison.",
        "Configure one or more supported providers locally via `.env` and "
        "restart the app.",
        "No mock results are shown as live provider results.",
        "",
        *lines,
    ])


def no_key_action_result() -> str:
    """Return the server-side no-key action result."""
    return NOT_CONFIGURED_MESSAGE


def _json_from_text(raw_text: str) -> dict[str, Any] | None:
    candidates = re.findall(
        r"```(?:json)?\s*(.*?)```",
        raw_text,
        re.DOTALL,
    )
    candidates.append(raw_text)
    for text in candidates:
        try:
            parsed = json.loads(text.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _forbidden_overclaim_text(candidate: dict[str, Any]) -> str | None:
    searchable = " ".join(
        str(candidate.get(key, ""))
        for key in [
            "candidate_name",
            "name",
            "scope",
            "claim",
            "notes",
            "description",
        ]
    ).lower()
    forbidden = [
        "reproduces sawin",
        "sawin construction",
        "sawin's construction",
        "asymptotic",
        "theorem",
        "formal proof",
        "new proof",
        "n^1.014",
        "delta = 0.014",
        "δ = 0.014",
    ]
    for phrase in forbidden:
        if phrase in searchable:
            return phrase
    return None


def validate_ai_candidate_payload(
    raw_text: str,
) -> tuple[str, dict, dict | None]:
    """Parse and exactly validate strict finite AI candidate JSON."""
    candidate = _json_from_text(raw_text)
    if candidate is None:
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            "Could not parse strict JSON object.",
            {"status": AI_REJECTED, "error": "PARSE_FAILED"},
            None,
        )
    overclaim = _forbidden_overclaim_text(candidate)
    if overclaim:
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            f"Forbidden overclaim detected: {overclaim}",
            {"status": AI_REJECTED, "error": "FORBIDDEN_OVERCLAIM"},
            None,
        )

    points_raw = candidate.get("points")
    claimed = candidate.get(
        "claimed_unit_distance_edges",
        candidate.get("claimed_edges"),
    )
    name = str(
        candidate.get("candidate_name")
        or candidate.get("name")
        or "AI Finite Candidate"
    )
    if not isinstance(points_raw, list) or not isinstance(claimed, int):
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            "Schema requires `points` and integer "
            "`claimed_unit_distance_edges`.",
            {"status": AI_REJECTED, "error": "SCHEMA_FAILED"},
            None,
        )
    if len(points_raw) < 3 or len(points_raw) > 8:
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            "Candidate must contain 3-8 distinct rational points.",
            {"status": AI_REJECTED, "error": "POINT_COUNT_OUT_OF_RANGE"},
            None,
        )

    try:
        points = [
            (Rational(str(point[0])), Rational(str(point[1])))
            for point in points_raw
        ]
    except (TypeError, ValueError, IndexError) as exc:
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            "Invalid rational coordinate.",
            {"status": AI_REJECTED, "error": str(exc)},
            None,
        )
    if len(set(points)) != len(points):
        return (
            "RESULT: AI_GENERATED_HYPOTHESIS_REJECTED_BY_EXACT_VALIDATOR\n"
            "Duplicate point rejected.",
            {"status": AI_REJECTED, "error": "DUPLICATE_POINT"},
            None,
        )

    exact_count, edges = count_unit_edges_exact(points)
    status = AI_VALIDATED if exact_count == claimed else AI_REJECTED
    result = ValidatedConfigurationResult(
        name=name,
        points=_points_to_strings(points),
        exact_edges=edges,
        edge_count=exact_count,
        validation_status=status,
        scientific_scope=AI_SCOPE,
        source_kind="ai_candidate",
    )
    details = {
        **result.to_state_dict(),
        "claimed_unit_distance_edges": claimed,
        "claim_match": exact_count == claimed,
    }
    summary = "\n".join([
        f"RESULT: {status}",
        f"Candidate: {name}",
        f"AI claimed: {claimed}",
        f"Exact validator found: {exact_count}",
        f"Claim match: {exact_count == claimed}",
        AI_SCOPE,
    ])
    return summary, details, result.to_state_dict()


def finite_candidate_prompt() -> str:
    """Return strict JSON prompt for finite candidate generation."""
    return "\n".join([
        "Return strict JSON only.",
        "Generate a finite planar unit-distance candidate.",
        "Schema:",
        "{",
        '  "candidate_name": "short descriptive name",',
        '  "points": [["0", "0"], ["3/5", "4/5"], ["1", "0"]],',
        '  "claimed_unit_distance_edges": 2,',
        '  "scope": "finite candidate hypothesis only"',
        "}",
        "Requirements:",
        "- 3-8 distinct rational planar points.",
        "- Coordinates must be strings containing integers or fractions.",
        "- No proof, theorem, Sawin, asymptotic, exponent or bound claims.",
    ])


def provider_model(name: str) -> str:
    """Return configured default provider model."""
    model_env_vars = {
        "openai": "OPENAI_MODEL",
        "anthropic": "ANTHROPIC_MODEL",
        "openrouter": "OPENROUTER_MODEL",
        "google_gemini": "GEMINI_MODEL",
        "mistral": "MISTRAL_MODEL",
        "ollama_cloud": "OLLAMA_MODEL",
        "ollama_local": "OLLAMA_MODEL",
    }
    env_var = model_env_vars.get(name)
    if env_var and os.environ.get(env_var):
        return str(os.environ[env_var])
    return str(
        PROVIDER_DEFAULTS.get(name, {}).get("default_model", "default")
    )


def _registry_or_default(registry=None):
    return registry or build_default_registry()


def provider_connection_test(
    provider_name: str,
    registry=None,
) -> tuple[str, dict]:
    """Run one explicit provider connectivity check."""
    registry = _registry_or_default(registry)
    provider = registry.get(provider_name)
    if provider is None:
        return (
            f"PROVIDER: {provider_name}\nRESULT: FAIL_MODEL_UNAVAILABLE",
            {"provider": provider_name, "result": "FAIL_MODEL_UNAVAILABLE"},
        )
    if not provider.is_available():
        return (
            f"PROVIDER: {provider_name}\nCONFIGURATION: NOT_CONFIGURED\n"
            "RESULT: NOT_CONFIGURED\nSECRETS_DISPLAYED: NO",
            {"provider": provider_name, "result": "NOT_CONFIGURED"},
        )
    request = GenerationRequest(
        prompt="Return exactly the string: PROVIDER_LIVE_TEST_OK",
        model=provider_model(provider_name),
        temperature=0.0,
        max_tokens=32,
    )
    try:
        response = provider.generate(request)
    except ProviderNotConfiguredError:
        result = "NOT_CONFIGURED"
    except ProviderConnectionError as exc:
        result = _classify_connection_error(str(exc))
    except ProviderResponseError:
        result = "FAIL_MODEL_UNAVAILABLE"
    except NotImplementedError:
        result = "FAIL_MODEL_UNAVAILABLE"
    except Exception:
        result = "FAIL_NETWORK"
    else:
        result = (
            "PASS"
            if response.raw_text.strip() == "PROVIDER_LIVE_TEST_OK"
            else "FAIL_MODEL_UNAVAILABLE"
        )
    data = {
        "provider": provider_name,
        "configuration": "CONFIGURED",
        "request_scope": "MINIMAL_CONNECTIVITY_CHECK",
        "result": result,
        "secrets_displayed": "NO",
        "scientific_claim_generated": "NO",
    }
    return (
        "\n".join([
            "LIVE_PROVIDER_CONNECTION_TEST",
            f"PROVIDER: {provider_name}",
            "CONFIGURATION: CONFIGURED",
            "REQUEST_SCOPE: MINIMAL_CONNECTIVITY_CHECK",
            f"RESULT: {result}",
            "SECRETS_DISPLAYED: NO",
            "SCIENTIFIC_CLAIM_GENERATED: NO",
        ]),
        data,
    )


def _classify_connection_error(text: str) -> str:
    if "401" in text or "403" in text:
        return "FAIL_AUTH"
    if "429" in text:
        return "FAIL_RATE_LIMIT"
    if "402" in text or "quota" in text.lower():
        return "FAIL_BILLING_OR_QUOTA"
    return "FAIL_NETWORK"


def generate_ai_candidate_with_provider(
    provider_name: str,
    registry=None,
) -> tuple[str, dict, dict | None]:
    """Ask one configured provider for a finite candidate and validate it."""
    registry = _registry_or_default(registry)
    provider = registry.get(provider_name)
    if provider is None or not provider.is_available():
        return NOT_CONFIGURED_MESSAGE, {
            "provider": provider_name,
            "status": "NOT_CONFIGURED",
        }, None
    request = GenerationRequest(
        prompt=finite_candidate_prompt(),
        model=provider_model(provider_name),
        temperature=0.0,
        max_tokens=1200,
    )
    try:
        response = provider.generate(request)
    except ProviderNotConfiguredError:
        return NOT_CONFIGURED_MESSAGE, {
            "provider": provider_name,
            "status": "NOT_CONFIGURED",
        }, None
    except Exception:
        return (
            "RESULT: INCONCLUSIVE_PROVIDER_ERROR\n"
            "Provider request failed without exposing raw exception text.",
            {"provider": provider_name, "status": "PROVIDER_ERROR"},
            None,
        )
    summary, data, state = validate_ai_candidate_payload(response.raw_text)
    data["provider"] = provider_name
    return summary, data, state


def provider_comparison_run(
    provider_names: list[str],
    registry=None,
) -> tuple[list[list[Any]], str]:
    """Run one finite-candidate request per selected configured provider."""
    registry = _registry_or_default(registry)
    if not provider_names:
        return [], "No providers selected."
    rows = []
    for name in provider_names:
        provider = registry.get(name)
        if provider is None or not provider.is_available():
            rows.append([
                name,
                "NOT_CONFIGURED",
                "NOT_RUN",
                "",
                "",
                "Finite candidate comparison only.",
            ])
            continue
        summary, data, _state = generate_ai_candidate_with_provider(
            name,
            registry=registry,
        )
        rows.append([
            name,
            data.get("status", data.get("validation_status", "REQUESTED")),
            "PASS" if "edge_count" in data else "FAIL",
            data.get("edge_count", ""),
            data.get("claim_match", ""),
            AI_SCOPE,
        ])
        if "INCONCLUSIVE_PROVIDER_ERROR" in summary:
            rows[-1][1] = "PROVIDER_ERROR"
    return rows, (
        "Provider comparison complete. Each configured provider received at "
        "most one finite-candidate request."
    )


def source_theorem_map_markdown() -> str:
    """Return user-facing source map text."""
    return "\n".join([
        "## Sources & Theorem Map",
        "",
        '<div class="cc-card">',
        "<strong>OpenAI fixed delta > 0</strong><br>",
        "Status: <code>SOURCE_DOCUMENTED</code><br>",
        "Source: OpenAI announcement and proof PDF<br>",
        "Locally executable: No<br>",
        "Boundary: not locally reproduced.",
        "</div>",
        "",
        '<div class="cc-card">',
        "<strong>Original OpenAI proof explicit delta = 0.014</strong><br>",
        "Status: <code>NOT_PROVIDED_BY_ORIGINAL_PROOF</code><br>",
        "Source: original proof source boundary<br>",
        "Locally executable: No<br>",
        "Boundary: the original proof establishes fixed delta > 0, "
        "not 0.014.",
        "</div>",
        "",
        '<div class="cc-card">',
        "<strong>Sawin explicit n^1.014</strong><br>",
        "Status: <code>SOURCE_DOCUMENTED</code><br>",
        "Primary source: Will Sawin, arXiv:2605.20579<br>",
        "Locally executable: No<br>",
        "Boundary: primary-source documented; not locally reproduced.",
        "</div>",
        "",
        '<div class="cc-card">',
        "<strong>Finite Rational Mesh Baseline</strong><br>",
        "Status: <code>LOCALLY_REPRODUCED_EXACT</code><br>",
        "Source: repository exact validator<br>",
        "Locally executable: Yes<br>",
        "Boundary: not Sawin's construction. Finite exact validation only.",
        "</div>",
        "",
        "The locally executable finite baselines in this repository do not "
        "reproduce the algebraic-number-theoretic asymptotic construction "
        "from the OpenAI proof or Sawin's explicit result.",
    ])


def _overview_tab(
    env_status: EnvironmentStatus,
    live_ai_share: bool,
):
    gr.Markdown(
        overview_markdown(env_status, live_ai_share),
        elem_classes=["cc-wrap"],
    )


def _baselines_tab(baseline_state):
    gr.Markdown(
        "## Exact Baselines\n\n"
        "All rows are produced by the existing exact rational validator."
    )

    with gr.Row():
        n_line = gr.Slider(
            2, 100, value=16, step=1, label="Line Configuration n"
        )
        k_grid = gr.Slider(
            2, 20, value=4, step=1, label="Square Grid k"
        )
        m_mesh = gr.Slider(
            1, 12, value=10, step=1, label="Rational Mesh m"
        )
    btn = gr.Button("Validate All Exact Baselines")
    table = gr.Dataframe(
        headers=[
            "Configuration",
            "Points",
            "Exact edges",
            "Status",
        ],
        interactive=False,
        label="Exact finite baseline results",
        wrap=True,
    )
    summary = gr.Markdown(elem_classes=["cc-wrap"])
    with gr.Accordion("Technical JSON details (optional)", open=False):
        technical = gr.JSON(label="Validated baseline state")

    btn.click(
        fn=validate_all_exact_baselines_callback,
        inputs=[n_line, k_grid, m_mesh],
        outputs=[table, summary, technical, baseline_state],
        api_name="validate_all_exact_baselines",
    )
    legacy_line = gr.Button(visible=False)
    legacy_grid = gr.Button(visible=False)
    legacy_line_out = gr.JSON(visible=False)
    legacy_grid_out = gr.JSON(visible=False)
    legacy_line.click(
        fn=lambda n: validate_line_configuration(int(n)),
        inputs=n_line,
        outputs=legacy_line_out,
        api_name="validate_line_configuration",
    )
    legacy_grid.click(
        fn=lambda k: validate_grid_configuration(int(k)),
        inputs=k_grid,
        outputs=legacy_grid_out,
        api_name="validate_grid_configuration",
    )


def _explorer_tab(explorer_state):
    gr.Markdown(
        "## Configuration Explorer\n\n"
        + EXPLORER_SCOPE
        + "\n\nEnter one rational point per line: `x, y`."
    )
    preset = gr.Dropdown(
        choices=list(EXPLORER_PRESETS.keys()),
        value="Unit Square",
        label="Preset",
    )
    coords_input = gr.Textbox(
        label="Points",
        value=explorer_preset_text("Unit Square"),
        lines=10,
    )
    btn_validate = gr.Button("Validate Explorer Configuration")
    summary = gr.Markdown(elem_classes=["cc-wrap"])
    edges = gr.Dataframe(
        headers=["Edge", "Point A", "Point B"],
        interactive=False,
        label="Exactly validated unit-distance edges",
        wrap=True,
    )
    with gr.Accordion("Technical JSON details (optional)", open=False):
        details = gr.JSON(label="Validated Explorer result")

    preset.change(
        fn=explorer_preset_text,
        inputs=preset,
        outputs=coords_input,
    )
    btn_validate.click(
        fn=validate_explorer_text,
        inputs=coords_input,
        outputs=[summary, edges, details, explorer_state],
        api_name="validate_custom_configuration",
    )


def _visualisierung_tab(explorer_state, ai_state):
    gr.Markdown(
        "## Visualisierung exakt validierter Punktkonfigurationen\n\n"
        "Only edges confirmed by exact rational validation are drawn."
    )
    source = gr.Dropdown(
        choices=[
            "Line Configuration",
            "Square Grid Configuration",
            "Rational 3/5–4/5 Example",
            "Finite Rational Mesh Baseline",
            "Latest Explorer Result",
            "Latest AI Candidate Result",
        ],
        value="Finite Rational Mesh Baseline",
        label="Configuration Source",
    )
    with gr.Row():
        line_n = gr.Slider(
            2, 50, value=16, step=1, label="Line Configuration n"
        )
        grid_k = gr.Slider(
            2, 12, value=4, step=1, label="Square Grid k"
        )
        mesh_m = gr.Slider(
            1, 12, value=10, step=1, label="Rational Mesh m"
        )
    with gr.Row():
        labels = gr.Checkbox(value=False, label="Show point labels")
        edges = gr.Checkbox(
            value=True,
            label="Show validated unit-distance edges",
        )
        grid = gr.Checkbox(value=True, label="Show coordinate grid")
    btn = gr.Button("Validate and Visualize")
    plot = gr.Plot(label="Visualization")
    summary = gr.Markdown(elem_classes=["cc-wrap"])
    with gr.Accordion("Technical JSON details (optional)", open=False):
        technical = gr.JSON(label="Validated visualization data")

    btn.click(
        fn=package_a_visualize_source,
        inputs=[
            source,
            line_n,
            grid_k,
            mesh_m,
            labels,
            edges,
            grid,
            explorer_state,
            ai_state,
        ],
        outputs=[plot, summary, technical],
        api_name="visualize_exact_baseline",
    )


def _claims_tab(editable: bool):
    gr.Markdown("## Claim Registry")
    rows = []
    for c in INITIAL_CLAIMS:
        rows.append([
            c.claim_id,
            c.statement,
            c.status.value,
            c.primary_source,
            "Yes" if c.locally_validated else "No",
            c.limitations,
            c.last_reviewed,
        ])
    gr.Dataframe(
        value=rows,
        headers=[
            "ID", "Statement", "Status", "Source",
            "Validated", "Limitations", "Reviewed",
        ],
        interactive=editable,
    )
    gr.Markdown(
        source_theorem_map_markdown(),
        elem_classes=["cc-wrap"],
    )


def _settings_tab(
    mode: AppMode,
    env_status: EnvironmentStatus,
    live_ai_share: bool,
):
    gr.Markdown(settings_markdown(mode, env_status, live_ai_share))
    if mode not in {AppMode.LOCAL_PRIVATE, AppMode.COLAB_PRIVATE}:
        gr.Markdown(f"### Security\n\n{SECURITY_WARNING}")


def _ai_candidate_lab_tab(
    env_status: EnvironmentStatus,
    ai_state,
):
    configured = any_live_provider_configured(env_status)
    registry = build_default_registry()
    provider_names = registry.list_names()
    configured_names = configured_provider_names(env_status, registry)
    if not configured:
        gr.Markdown(no_key_ai_markdown())
        btn_test = gr.Button("Test Provider Connection")
        btn_generate = gr.Button("Generate Finite Candidate and Validate")
        out = gr.Markdown()
        btn_test.click(fn=no_key_action_result, outputs=out)
        btn_generate.click(fn=no_key_action_result, outputs=out)
        return

    gr.Markdown(
        "## AI Candidate Lab\n\n"
        "Current AI Lab scope: finite candidate generation only.\n\n"
        "This tool does not attempt the algebraic-number-theoretic "
        "construction used in the OpenAI proof, does not reproduce "
        "Sawin's n^1.014 result, and does not establish asymptotic bounds."
    )
    provider = gr.Dropdown(
        choices=provider_names,
        value=configured_names[0] if configured_names else None,
        label="Provider",
    )
    btn_test = gr.Button("Test Provider Connection")
    test_out = gr.Markdown()
    test_data = gr.JSON(label="Connection test details")
    btn_generate = gr.Button(
        "Generate Finite Candidate and Validate Exactly"
    )
    candidate_summary = gr.Markdown()
    with gr.Accordion("Technical JSON details (optional)", open=False):
        candidate_data = gr.JSON(label="AI candidate validation details")

    btn_test.click(
        fn=provider_connection_test,
        inputs=provider,
        outputs=[test_out, test_data],
        api_name="test_provider_connection",
    )
    btn_generate.click(
        fn=generate_ai_candidate_with_provider,
        inputs=provider,
        outputs=[candidate_summary, candidate_data, ai_state],
        api_name="generate_ai_candidate",
    )


def _provider_comparison_tab(env_status: EnvironmentStatus):
    configured = any_live_provider_configured(env_status)
    registry = build_default_registry()
    provider_names = configured_provider_names(env_status, registry)
    if not configured:
        gr.Markdown(no_key_provider_markdown(env_status))
        return
    gr.Markdown(
        "## Provider Comparison\n\n"
        "Select configured providers only. Each click sends at most one "
        "small finite-candidate request per selected provider and may "
        "consume quota or incur cost."
    )
    selected = gr.CheckboxGroup(
        choices=provider_names,
        label="Providers to compare",
    )
    btn = gr.Button("Compare Selected Providers")
    table = gr.Dataframe(
        headers=[
            "provider",
            "connection/result status",
            "parse/schema result",
            "exact edge count",
            "claim match",
            "finite-only scope",
        ],
        interactive=False,
    )
    summary = gr.Markdown()
    btn.click(
        fn=provider_comparison_run,
        inputs=selected,
        outputs=[table, summary],
        api_name="compare_providers",
    )


def _reports_export_tab(
    baseline_state,
    explorer_state,
    ai_state,
):
    gr.Markdown(
        "## Reports & Export\n\n"
        "Generate finite validation reports from results produced in this "
        "runtime. Sanitization is applied before download files are emitted."
    )
    source = gr.Dropdown(
        choices=[
            "Latest Baseline Result",
            "Latest Explorer Result",
            "Latest AI Candidate Result",
        ],
        value="Latest Baseline Result",
        label="Report Source",
    )
    btn = gr.Button("Generate Finite Validation Report")
    preview = gr.Markdown()
    markdown_file = gr.File(label="Markdown report")
    json_file = gr.File(label="JSON report")
    with gr.Accordion("Technical JSON details (optional)", open=False):
        details = gr.JSON(label="Sanitization details")
    btn.click(
        fn=generate_report_callback,
        inputs=[source, baseline_state, explorer_state, ai_state],
        outputs=[preview, markdown_file, json_file, details],
        api_name="generate_finite_report",
    )

    gr.Markdown("### Additional Sanitizer")
    text_input = gr.Textbox(
        label="Text to sanitize",
        lines=6,
    )
    btn_sanitize = gr.Button("Sanitize & Check")
    with gr.Accordion("Technical JSON details (optional)", open=False):
        out_sanitized = gr.JSON(label="Sanitization Result")

    def _sanitize(text):
        sanitized = sanitize_for_export(text)
        changed = sanitized != text
        return {
            "sanitized_text": sanitized,
            "secrets_found": changed,
            "safe_for_export": not changed,
        }

    btn_sanitize.click(
        fn=_sanitize,
        inputs=text_input,
        outputs=out_sanitized,
        api_name="sanitize_for_export",
    )


def build_app(
    mode: AppMode = AppMode.LOCAL_PRIVATE,
    live_ai_share: bool = False,
) -> gr.Blocks:
    """Build the Gradio application for the given mode."""
    caps = CAPABILITY_MATRIX[mode]
    env_status = environment_for_mode(mode)

    with gr.Blocks(title="Counterexample Commons") as demo:
        gr.HTML(f"<style>{APP_CSS}</style>")
        if live_ai_share:
            gr.Markdown("## WARNING\n\n" + LIVE_AI_SHARE_WARNING)
        gr.Markdown(
            "# Counterexample Commons\n"
            "*Exact Validation and Anti-Capitalist "
            "AI-Assisted Mathematics Research*"
        )
        baseline_state = gr.JSON(value=None, visible=False)
        explorer_state = gr.JSON(value=None, visible=False)
        ai_state = gr.JSON(value=None, visible=False)

        with gr.Tabs():
            with gr.Tab("Overview"):
                _overview_tab(env_status, live_ai_share)

            with gr.Tab("Exact Baselines"):
                _baselines_tab(baseline_state)

            with gr.Tab("Configuration Explorer"):
                _explorer_tab(explorer_state)

            with gr.Tab("Visualisierung"):
                _visualisierung_tab(explorer_state, ai_state)

            with gr.Tab("AI Candidate Lab"):
                if caps.ai_candidate_lab:
                    _ai_candidate_lab_tab(env_status, ai_state)
                else:
                    gr.Markdown(no_key_ai_markdown())

            with gr.Tab("Provider Comparison"):
                if caps.provider_comparison:
                    _provider_comparison_tab(env_status)
                else:
                    gr.Markdown(no_key_provider_markdown(env_status))

            with gr.Tab("Claim Registry"):
                _claims_tab(editable=caps.claim_registry_editable)

            with gr.Tab("Reports & Export"):
                _reports_export_tab(
                    baseline_state,
                    explorer_state,
                    ai_state,
                )

            with gr.Tab("Settings"):
                _settings_tab(mode, env_status, live_ai_share)

    return demo
