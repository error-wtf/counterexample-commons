"""Main Gradio application builder."""

from __future__ import annotations

import gradio as gr
from sympy import Rational

from counterexample_commons.config import (
    AppMode,
    CAPABILITY_MATRIX,
)
from counterexample_commons.validators import (
    validate_line_configuration,
    validate_grid_configuration,
    validate_custom_configuration,
    count_unit_edges_exact,
)
from counterexample_commons.claims import INITIAL_CLAIMS
from counterexample_commons.providers import build_default_registry
from counterexample_commons.validated_result import (
    ValidatedConfigurationResult,
)
from counterexample_commons.visualization import plot_from_result
from counterexample_commons.experiments import (
    extract_candidate_coordinates,
    validate_candidate,
    sanitize_for_export,
)
from case_studies.erdos_unit_distance_2026.rational_mesh_baseline import (
    rational_mesh_points,
)
SCIENTIFIC_BOUNDARY = (
    "This UI cannot promote hypotheses to proofs. "
    "Exact finite validation is not an asymptotic theorem. "
    "AI-generated candidates require independent validation."
)

SECURITY_WARNING = (
    "A Gradio share link is accessible to anyone who "
    "receives the link. Public demo mode disables "
    "external AI API calls and secret use."
)


RATIONAL_MESH_BOUNDARY = (
    "Finite rational mesh baseline — not Sawin's construction. "
    "Finite exact validation only; not evidence for exponent n^1.014."
)
FINITE_SCOPE = "Finite exact validation only."
RATIONAL_345_SCOPE = (
    "Exact rational non-axis unit-distance example. "
    "The displacement (3/5, 4/5) is validated exactly. "
    "Finite exact validation only."
)


def _points_to_strings(points):
    return [(str(x), str(y)) for x, y in points]


def _validated_result_from_points(
    name: str,
    points,
    scientific_scope: str,
    source_kind: str = "baseline",
) -> ValidatedConfigurationResult:
    edge_count, edges = count_unit_edges_exact(points)
    return ValidatedConfigurationResult(
        name=name,
        points=_points_to_strings(points),
        exact_edges=edges,
        edge_count=edge_count,
        validation_status="LOCALLY_REPRODUCED_EXACT",
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


def package_a_result_summary(result: ValidatedConfigurationResult) -> str:
    """Return a UI summary for a validated configuration."""
    return result.to_summary_markdown()


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


def _overview_tab():
    gr.Markdown("""
# Counterexample Commons
## An Anti-Capitalist AI-Assisted Mathematics Research Lab

**First case study:** The 2026 AI-generated counterexample to
Erdős' planar unit-distance conjecture.

### The Problem

Let u(n) be the largest number of unordered pairs at Euclidean
distance exactly 1 among n planar points.

- **Line:** n collinear unit-spaced points → n−1 edges
- **Grid:** k×k square grid → 2k(k−1) edges
- **Historical:** constructions achieving n^{1+C/log log n}

### What Changed in 2026

- OpenAI announced an AI-generated construction achieving
  n^{1+δ} for fixed δ>0
- Companion paper by Alon, Bloom, Gowers, Litt, Sawin et al.
  provides human-verified analysis
- Sawin gives explicit exponent: n^{1.014}
  (SOURCE_DOCUMENTED; not yet locally reproduced here)
- Upper bound O(n^{4/3}) remains far above — exact u(n) still open

### Scientific Integrity

""" + SCIENTIFIC_BOUNDARY)


def _baselines_tab():
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
            "Exact unit-distance edges",
            "Status",
            "Scientific scope",
        ],
        interactive=False,
        label="Exact finite baseline results",
    )
    summary = gr.Markdown()
    technical = gr.JSON(label="Validated baseline state")
    latest_state = gr.State(None)

    def _run(line_n, grid_k, mesh_m):
        results = package_a_baseline_results(
            int(line_n),
            int(grid_k),
            int(mesh_m),
        )
        latest = results[-1]
        state = {
            result.name: result.to_state_dict()
            for result in results
        }
        summary_text = "\n\n---\n\n".join(
            result.to_summary_markdown() for result in results
        )
        return (
            package_a_baseline_table_rows(results),
            summary_text,
            state,
            latest.to_state_dict(),
        )

    btn.click(
        fn=_run,
        inputs=[n_line, k_grid, m_mesh],
        outputs=[table, summary, technical, latest_state],
        api_name="validate_all_exact_baselines",
    )
    # Keep existing public API names available while the UI moves to the
    # consolidated four-baseline workflow.
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
    return latest_state


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
        labels = gr.Checkbox(value=True, label="Show point labels")
        edges = gr.Checkbox(
            value=True,
            label="Show validated unit-distance edges",
        )
        grid = gr.Checkbox(value=True, label="Show coordinate grid")
    btn = gr.Button("Validate and Visualize")
    plot = gr.Plot(label="Visualization")
    summary = gr.Markdown()
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


def _explorer_tab():
    gr.Markdown("""
## Configuration Explorer

Enter rational coordinates (integers or fractions like `3/5`).
One point per line: `x, y`
""")
    coords_input = gr.Textbox(
        label="Points (x, y per line)",
        placeholder="0, 0\n1, 0\n0, 1\n1, 1",
        lines=10,
    )
    btn_validate = gr.Button("Validate Candidate Exactly")
    out_result = gr.JSON(label="Validation Result")

    def _parse_and_validate(text: str):
        lines = [
            ln.strip() for ln in text.strip().split("\n")
            if ln.strip()
        ]
        coords = []
        for ln in lines:
            parts = ln.split(",")
            if len(parts) != 2:
                return {"error": f"Bad line: {ln}"}
            coords.append((parts[0].strip(), parts[1].strip()))
        try:
            return validate_custom_configuration(coords)
        except ValueError as e:
            return {"error": str(e)}

    btn_validate.click(
        fn=_parse_and_validate,
        inputs=coords_input,
        outputs=out_result,
        api_name="validate_custom_configuration",
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


def _settings_tab(mode: AppMode):
    caps = CAPABILITY_MATRIX[mode]
    yn = {True: "Yes", False: "No"}
    en = {True: "Enabled", False: "Disabled"}
    gr.Markdown(
        f"## Settings & Security\n\n"
        f"- **Runtime mode:** `{mode.value}`\n"
        f"- **AI Candidate Lab:** {en[caps.ai_candidate_lab]}\n"
        f"- **Provider Comparison:** {en[caps.provider_comparison]}\n"
        f"- **Ollama Local:** {en[caps.ollama_local]}\n"
        f"- **Secrets loaded:** {yn[caps.secrets_loaded]}\n"
        f"- **Share link:** {en[caps.share_link]}\n"
        f"- **Google Drive:** {en[caps.google_drive]}\n"
        f"- **Filesystem write:** {en[caps.filesystem_write]}\n\n"
        f"### Scientific Integrity Boundary\n\n"
        f"{SCIENTIFIC_BOUNDARY}"
    )
    if not caps.secrets_loaded:
        gr.Markdown(f"### Security\n\n{SECURITY_WARNING}")


def _ai_candidate_lab_tab(enabled: bool):
    if not enabled:
        gr.Markdown(
            "## AI Candidate Lab\n\n"
            "**Disabled in this mode.**\n\n"
            "External AI API calls are not available in public "
            "demo mode to prevent uncontrolled provider spending."
        )
        return

    gr.Markdown(
        "## AI Candidate Lab\n\n"
        "Paste raw AI model output below. The system will "
        "extract coordinates and validate them exactly.\n\n"
        "*To generate output from a provider, use the Python "
        "API or a Colab notebook with colab-private mode.*"
    )
    raw_input = gr.Textbox(
        label="Raw Model Output",
        placeholder='Paste model output containing [[x,y],...] here',
        lines=12,
    )
    claimed_edges = gr.Number(
        label="Claimed edge count (optional, 0 = skip)",
        value=0,
        precision=0,
    )
    btn_extract = gr.Button("Extract & Validate")
    out_result = gr.JSON(label="Validation Result")

    def _extract_and_validate(raw_text, claimed):
        candidate = extract_candidate_coordinates(raw_text)
        if candidate is None:
            return {
                "status": "INCONCLUSIVE_EXTRACTION_FAILED",
                "error": "Could not extract coordinates from text",
            }
        claimed_int = int(claimed) if claimed else None
        if claimed_int == 0:
            claimed_int = None
        return validate_candidate(candidate, claimed_int)

    btn_extract.click(
        fn=_extract_and_validate,
        inputs=[raw_input, claimed_edges],
        outputs=out_result,
        api_name="extract_and_validate",
    )


def _provider_comparison_tab(enabled: bool):
    if not enabled:
        gr.Markdown(
            "## Provider Comparison\n\n"
            "**Disabled in this mode.**\n\n"
            "Available in private research modes only."
        )
        return

    registry = build_default_registry()
    provider_names = registry.list_names()
    available = registry.list_available()

    status_lines = []
    for name in provider_names:
        p = registry.get(name)
        avail = "Available" if name in available else "Not configured"
        key_info = (
            f"({p.api_key_env_var})" if p.requires_api_key
            else "(no key needed)"
        )
        status_lines.append(f"- **{name}**: {avail} {key_info}")

    gr.Markdown(
        "## Provider Comparison\n\n"
        "### Registered Providers\n\n"
        + "\n".join(status_lines)
        + "\n\n### How to Compare\n\n"
        "1. Configure API keys in environment variables\n"
        "2. Use `04A_Compare_Multiple_Providers.ipynb` or the "
        "Python API to run the same prompt across providers\n"
        "3. Results are tabulated with exact validation"
    )


def _reports_export_tab(enabled: bool):
    gr.Markdown("## Reports & Export")

    if not enabled:
        gr.Markdown(
            "**Export is limited in this mode.**\n\n"
            "Run in `local-private` or `colab-private` mode "
            "for full export capabilities."
        )

    gr.Markdown(
        "### Sanitize Text for Export\n\n"
        "Paste text below to check for and redact potential "
        "secrets before sharing."
    )
    text_input = gr.Textbox(
        label="Text to sanitize",
        lines=8,
    )
    btn_sanitize = gr.Button("Sanitize & Check")
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


def build_app(mode: AppMode = AppMode.LOCAL_PRIVATE) -> gr.Blocks:
    """Build the Gradio application for the given mode."""
    caps = CAPABILITY_MATRIX[mode]

    with gr.Blocks(
        title="Counterexample Commons",
    ) as demo:
        gr.Markdown(
            "# Counterexample Commons\n"
            "*Exact Validation and Anti-Capitalist "
            "AI-Assisted Mathematics Research*"
        )
        explorer_state = gr.State(None)
        ai_state = gr.State(None)

        with gr.Tabs():
            with gr.Tab("Overview"):
                _overview_tab()

            with gr.Tab("Exact Baselines"):
                _baselines_tab()

            with gr.Tab("Configuration Explorer"):
                _explorer_tab()

            with gr.Tab("Visualisierung"):
                _visualisierung_tab(explorer_state, ai_state)

            with gr.Tab("AI Candidate Lab"):
                _ai_candidate_lab_tab(caps.ai_candidate_lab)

            with gr.Tab("Provider Comparison"):
                _provider_comparison_tab(
                    caps.provider_comparison
                )

            with gr.Tab("Claim Registry"):
                _claims_tab(
                    editable=caps.claim_registry_editable,
                )

            with gr.Tab("Reports & Export"):
                _reports_export_tab(caps.export_full)

            with gr.Tab("Settings"):
                _settings_tab(mode)

    return demo
