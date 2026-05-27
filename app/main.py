"""Main Gradio application builder."""

from __future__ import annotations

import json

import gradio as gr

from counterexample_commons.claims import INITIAL_CLAIMS
from counterexample_commons.config import AppMode, CAPABILITY_MATRIX
from counterexample_commons.env_loader import EnvironmentStatus, load_local_env
from counterexample_commons.experiments import sanitize_for_export
from counterexample_commons.lab import (
    AI_REJECTED,
    baseline_records,
    explorer_preset,
    generate_and_validate,
    grid_record,
    line_record,
    rational_345_record,
    rational_mesh_record,
    record_summary,
    test_provider_connection,
    validate_ai_candidate_json,
    validate_explorer_text,
    write_report_files,
)
from counterexample_commons.providers import build_default_registry
from counterexample_commons.source_map import (
    PROOF_ARCHITECTURE_SUMMARY,
    REPRODUCTION_LEVELS,
    source_map_rows,
)
from counterexample_commons.visualization import plot_record


SCIENTIFIC_BOUNDARY = (
    "Sawin n^1.014: SOURCE_DOCUMENTED - not locally reproduced.\n\n"
    "Finite rational mesh baseline: LOCALLY_REPRODUCED_EXACT - not "
    "Sawin's construction.\n\n"
    "AI-generated candidates remain finite hypotheses until independently "
    "checked by the exact finite validator."
)

SAFE_NO_KEY_MESSAGE = (
    "SAFE NO-KEY SESSION\n\n"
    "No live provider is configured.\n"
    "Exact finite baselines, explorer, visualisation, read-only claims and "
    "finite exports are available.\n"
    "AI actions are visible but inactive until local provider credentials "
    "are configured.\n"
    "No live API request can be sent in the current state.\n\n"
    f"{SCIENTIFIC_BOUNDARY}"
)

LIVE_AI_MESSAGE = (
    "LIVE AI CONFIGURED\n\n"
    "Real provider requests are available in this running session.\n"
    "Requests may consume quota or incur cost.\n"
    "Credentials are never displayed or exported.\n"
    "AI-generated candidates remain hypotheses until independently checked "
    "by the exact finite validator.\n\n"
    f"{SCIENTIFIC_BOUNDARY}"
)

LIVE_SHARE_WARNING = (
    "A shared live-AI session may allow anyone with access to trigger "
    "provider requests and consume quota or incur cost. The key is not "
    "displayed or exported, but the configured provider account may be used "
    "through the running session."
)


def _provider_rows(env_status: EnvironmentStatus) -> list[list[str]]:
    """Return provider status rows without secret values."""
    return [
        [name, status]
        for name, status in sorted(env_status.providers.items())
    ]


def _records_to_table(records: list[dict]) -> list[list[str | int]]:
    """Format validation records as readable table rows."""
    return [
        [
            record["configuration"],
            len(record["points"]),
            record["exact_edges"],
            record["status"],
            record["scientific_scope"],
        ]
        for record in records
    ]


def _overview_tab(
    env_status: EnvironmentStatus,
    live_share_enabled: bool,
) -> None:
    message = (
        LIVE_AI_MESSAGE
        if env_status.any_provider_configured
        else SAFE_NO_KEY_MESSAGE
    )
    gr.Markdown(f"# Counterexample Commons\n\n```\n{message}\n```")
    gr.Markdown(
        "Inspired by OpenAI's 2026 unit-distance breakthrough, this app is "
        "a local exact finite validation laboratory. It does not locally "
        "reproduce the asymptotic OpenAI/Sawin construction."
    )
    gr.Markdown("### Sources & Theorem Map")
    gr.Dataframe(
        value=source_map_rows(),
        headers=[
            "Result",
            "Official source type",
            "Locally executable?",
            "Status",
            "Provenance note",
        ],
        interactive=False,
    )
    gr.Markdown(
        "### Proof Architecture Boundary\n\n"
        f"{PROOF_ARCHITECTURE_SUMMARY}\n\n"
        "The locally executable finite baselines in this repository do not "
        "reproduce the algebraic-number-theoretic asymptotic construction "
        "from the OpenAI proof or Sawin's announced refinement."
    )
    gr.Dataframe(
        value=[list(row) for row in REPRODUCTION_LEVELS],
        headers=["Level", "Scope", "Current status"],
        interactive=False,
        label="Reproduction Roadmap",
    )
    if live_share_enabled:
        gr.Markdown(f"### Live-AI Share Warning\n\n{LIVE_SHARE_WARNING}")


def _baselines_tab():
    gr.Markdown(
        "## Exact Baselines\n\n"
        "Finite exact validation only. The rational mesh baseline is not "
        "Sawin's construction."
    )
    with gr.Row():
        line_n = gr.Slider(2, 100, value=16, step=1, label="Line n")
        grid_k = gr.Slider(2, 20, value=4, step=1, label="Grid k")
        mesh_m = gr.Slider(1, 12, value=4, step=1, label="Rational mesh m")
    btn = gr.Button("Validate Baselines")
    table = gr.Dataframe(
        headers=[
            "Configuration",
            "Points",
            "Exact unit-distance edges",
            "Status",
            "Scientific scope",
        ],
        datatype=["str", "number", "number", "str", "str"],
        interactive=False,
        label="Baseline Results",
    )
    summary = gr.Textbox(label="Boundary", lines=5)
    details = gr.JSON(label="Raw exact validation details")
    state = gr.State(None)

    def run(line_value, grid_value, mesh_value):
        records = baseline_records(
            int(line_value),
            int(grid_value),
            int(mesh_value),
        )
        latest = records[-1]
        text = record_summary(latest)
        return _records_to_table(records), text, records, latest

    btn.click(
        run,
        inputs=[line_n, grid_k, mesh_m],
        outputs=[table, summary, details, state],
        api_name="validate_all_baselines",
    )
    return state


def _explorer_tab():
    gr.Markdown(
        "## Configuration Explorer\n\n"
        "Finite exact validation only. This explorer does not reproduce "
        "Sawin's asymptotic construction and does not generate formal proofs."
    )
    preset = gr.Dropdown(
        choices=[
            "Unit Square",
            "Rational 3/5-4/5 Example",
            "Small Rational Mesh",
        ],
        value="Unit Square",
        label="Preset",
    )
    coords = gr.Textbox(
        value=explorer_preset("Unit Square"),
        label="Rational points, one 'x, y' pair per line",
        lines=10,
    )
    preset.change(explorer_preset, preset, coords)
    btn = gr.Button("Validate Explorer Configuration")
    summary = gr.Textbox(label="Validation Summary", lines=7)
    details = gr.JSON(label="Raw exact validation details")
    state = gr.State(None)
    btn.click(
        validate_explorer_text,
        inputs=coords,
        outputs=[state, summary, details],
        api_name="validate_explorer_configuration",
    )
    return state


def _visualisierung_tab(baseline_state, explorer_state, ai_state):
    gr.Markdown(
        "## Visualisierung\n\n"
        "Only exactly validated unit-distance edges are drawn."
    )
    source = gr.Dropdown(
        choices=[
            "Line Configuration",
            "Square Grid Configuration",
            "Rational 3/5-4/5 Example",
            "Finite Rational Mesh Baseline",
            "Latest Explorer Result",
            "Latest AI Candidate Result",
        ],
        value="Square Grid Configuration",
        label="Configuration Source",
    )
    with gr.Row():
        n_value = gr.Slider(2, 30, value=6, step=1, label="Line n / Grid k")
        mesh_m = gr.Slider(1, 10, value=4, step=1, label="Mesh m")
    with gr.Row():
        labels = gr.Checkbox(value=True, label="Show point labels")
        edges = gr.Checkbox(
            value=True,
            label="Show validated unit-distance edges",
        )
        grid = gr.Checkbox(value=True, label="Show coordinate grid")
    btn = gr.Button("Validate and Visualize")
    plot = gr.Plot(label="Validated geometry")
    summary = gr.Textbox(label="Scientific Summary", lines=8)
    details = gr.JSON(label="Raw exact validation details")

    def visualize(source_name, n_param, mesh_param, show_l, show_e,
                  show_g, latest_baseline, latest_explorer, latest_ai):
        if source_name == "Line Configuration":
            record = line_record(int(n_param)).to_dict()
        elif source_name == "Square Grid Configuration":
            record = grid_record(int(n_param)).to_dict()
        elif source_name == "Rational 3/5-4/5 Example":
            record = rational_345_record().to_dict()
        elif source_name == "Finite Rational Mesh Baseline":
            record = rational_mesh_record(int(mesh_param)).to_dict()
        elif source_name == "Latest Explorer Result":
            record = latest_explorer
            if not record:
                return None, "No validated Explorer result available.", {}
        elif source_name == "Latest AI Candidate Result":
            record = latest_ai
            if not record:
                return None, "No validated AI candidate available.", {}
        else:
            record = latest_baseline
        return (
            plot_record(record, show_l, show_e, show_g),
            record_summary(record),
            record,
        )

    btn.click(
        visualize,
        inputs=[
            source,
            n_value,
            mesh_m,
            labels,
            edges,
            grid,
            baseline_state,
            explorer_state,
            ai_state,
        ],
        outputs=[plot, summary, details],
        api_name="visualize_exact_configuration",
    )


def _ai_candidate_lab_tab(env_status: EnvironmentStatus, state):
    gr.Markdown("## AI Candidate Lab")
    gr.Markdown(
        "Current AI Lab scope: `FINITE_CANDIDATE_MODE` only.\n\n"
        "`ASYMPTOTIC_PROOF_REPRODUCTION_MODE`: NOT_IMPLEMENTED / "
        "SOURCE_ONLY.\n\n"
        "This tool does not attempt the algebraic-number-theoretic "
        "construction used in the OpenAI proof, does not reproduce Sawin's "
        "announced delta = 0.014 refinement, and does not establish "
        "asymptotic bounds."
    )
    gr.Dataframe(
        value=_provider_rows(env_status),
        headers=["Provider", "Status"],
        interactive=False,
        label="Provider Configuration",
    )
    if not env_status.any_provider_configured:
        gr.Markdown(
            "NOT_CONFIGURED\n\n"
            "Copy `.env.example` to `.env` and configure a provider key. "
            "No live API request can be sent in the current state."
        )
    raw = gr.Textbox(
        label="Strict AI candidate JSON or provider output",
        lines=12,
        placeholder=json.dumps(
            {
                "candidate_name": "rational triangle candidate",
                "points": [["0", "0"], ["3/5", "4/5"], ["1", "0"]],
                "claimed_unit_distance_edges": 2,
                "scope": "finite candidate hypothesis only",
            },
            indent=2,
        ),
    )
    btn_parse = gr.Button("Validate Pasted Candidate Exactly")
    provider = gr.Dropdown(
        choices=sorted(env_status.providers.keys()),
        value="openai",
        label="Provider",
    )
    btn_test = gr.Button("Test Provider Connection")
    btn_generate = gr.Button("Generate Finite Candidate and Validate Exactly")
    summary = gr.Textbox(label="AI Candidate Summary", lines=8)
    details = gr.JSON(label="Raw finite validation details")

    def parse(raw_text):
        return validate_ai_candidate_json(raw_text)

    def provider_obj(name):
        return build_default_registry().get(name)

    def test_connection(name):
        if env_status.providers.get(name) != "CONFIGURED":
            return {"status": "NOT_CONFIGURED", "message": "No request sent."}
        return test_provider_connection(provider_obj(name))

    def generate(name):
        if env_status.providers.get(name) != "CONFIGURED":
            error = {"status": "NOT_CONFIGURED", "message": "No request sent."}
            return None, "NOT_CONFIGURED: no request sent.", error
        return generate_and_validate(provider_obj(name))

    btn_parse.click(
        parse,
        inputs=raw,
        outputs=[state, summary, details],
        api_name="validate_pasted_ai_candidate",
    )
    btn_test.click(
        test_connection,
        inputs=provider,
        outputs=details,
        api_name="test_provider_connection",
    )
    btn_generate.click(
        generate,
        inputs=provider,
        outputs=[state, summary, details],
        api_name="generate_and_validate_ai_candidate",
    )
    return state


def _provider_comparison_tab(env_status: EnvironmentStatus):
    gr.Markdown(
        "## Provider Comparison\n\n"
        "Provider comparison sends at most one small explicit request per "
        "selected provider. Requests may consume quota or incur cost."
    )
    gr.Dataframe(
        value=_provider_rows(env_status),
        headers=["Provider", "Status"],
        interactive=False,
        label="Provider Configuration",
    )
    providers = gr.CheckboxGroup(
        choices=sorted(env_status.providers.keys()),
        label="Providers to compare",
    )
    btn = gr.Button("Run One Finite Candidate Request Per Provider")
    table = gr.Dataframe(
        headers=[
            "Provider",
            "Connection",
            "Candidate status",
            "Exact edges",
            "Claim match",
            "Scope",
        ],
        interactive=False,
    )

    def compare(selected):
        rows = []
        for name in selected or []:
            if env_status.providers.get(name) != "CONFIGURED":
                rows.append([name, "NOT_CONFIGURED", "", "", "", ""])
                continue
            record, _, details = generate_and_validate(
                build_default_registry().get(name)
            )
            if not record:
                rows.append([name, "ERROR", details.get("status"), "", "", ""])
                continue
            rows.append([
                name,
                "REQUEST_SENT",
                record["status"],
                record["exact_edges"],
                "YES" if record["status"] != AI_REJECTED else "NO",
                record["scientific_scope"],
            ])
        return rows

    btn.click(compare, providers, table, api_name="compare_providers")


def _claims_tab(editable: bool):
    gr.Markdown("## Claim Registry\n\nRead-only scientific claim status.")
    rows = [
        [
            c.claim_id,
            c.statement,
            c.status.value,
            c.primary_source,
            "Yes" if c.locally_validated else "No",
            c.limitations,
            c.provenance,
            c.last_reviewed,
        ]
        for c in INITIAL_CLAIMS
    ]
    gr.Dataframe(
        value=rows,
        headers=[
            "ID",
            "Statement",
            "Status",
            "Source",
            "Validated",
            "Limitations",
            "Provenance",
            "Reviewed",
        ],
        interactive=editable,
    )
    gr.Markdown("### Sources & Theorem Map")
    gr.Dataframe(
        value=source_map_rows(),
        headers=[
            "Result",
            "Official source type",
            "Locally executable?",
            "Status",
            "Provenance note",
        ],
        interactive=False,
    )


def _reports_export_tab(baseline_state, explorer_state, ai_state):
    gr.Markdown(
        "## Reports & Export\n\n"
        "Finite exact validation export only; not an asymptotic theorem, "
        "not a Sawin reproduction, and not a formal proof of a new bound."
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
    btn = gr.Button("Build Finite Validation Report")
    preview = gr.Textbox(label="Report Preview", lines=14)
    payload = gr.JSON(label="Report JSON")
    markdown_file = gr.File(label="Markdown report download")
    json_file = gr.File(label="JSON report download")
    text_input = gr.Textbox(
        label="Additional text to sanitize",
        lines=5,
    )
    btn_sanitize = gr.Button("Sanitize Text")
    sanitized = gr.JSON(label="Sanitization Result")

    def report(source_name, baseline, explorer, ai):
        record = baseline
        if source_name == "Latest Explorer Result":
            record = explorer
        elif source_name == "Latest AI Candidate Result":
            record = ai
        md_path, json_path, text, data = write_report_files(record)
        return text, data, md_path, json_path

    def sanitize(text):
        clean = sanitize_for_export(text or "")
        return {
            "sanitized_text": clean,
            "secrets_found": clean != (text or ""),
            "safe_for_export": clean == (text or ""),
        }

    btn.click(
        report,
        inputs=[source, baseline_state, explorer_state, ai_state],
        outputs=[preview, payload, markdown_file, json_file],
        api_name="build_finite_report",
    )
    btn_sanitize.click(
        sanitize,
        inputs=text_input,
        outputs=sanitized,
        api_name="sanitize_for_export",
    )


def _settings_tab(
    mode: AppMode,
    env_status: EnvironmentStatus,
    live_share_enabled: bool,
):
    caps = CAPABILITY_MATRIX[mode]
    gr.Markdown(
        "## Settings / Configuration\n\n"
        f"- Runtime mode: `{mode.value}`\n"
        f"- LOCAL_ENV_FILE: {env_status.local_env_file}\n"
        f"- Live-AI sharing confirmed: {live_share_enabled}\n"
        f"- Claim registry editable: {caps.claim_registry_editable}\n"
        f"- Filesystem write: {caps.filesystem_write}\n"
    )
    gr.Dataframe(
        value=_provider_rows(env_status),
        headers=["Provider", "Status"],
        interactive=False,
        label="Provider Configuration",
    )
    if live_share_enabled:
        gr.Markdown(f"### Live-AI Share Warning\n\n{LIVE_SHARE_WARNING}")


def build_app(
    mode: AppMode = AppMode.LOCAL_PRIVATE,
    live_ai_share_enabled: bool = False,
) -> gr.Blocks:
    """Build the Gradio application for the given mode."""
    caps = CAPABILITY_MATRIX[mode]
    env_status = load_local_env()

    with gr.Blocks(title="Counterexample Commons") as demo:
        gr.Markdown(
            "# Counterexample Commons\n"
            "*Exact finite validation and AI-assisted hypothesis testing*"
        )
        if live_ai_share_enabled:
            gr.Markdown(f"**Live-AI Share Warning:** {LIVE_SHARE_WARNING}")

        ai_state = gr.State(None)

        with gr.Tabs():
            with gr.Tab("Overview"):
                _overview_tab(env_status, live_ai_share_enabled)

            with gr.Tab("Exact Baselines"):
                baseline_state = _baselines_tab()

            with gr.Tab("Configuration Explorer"):
                explorer_state = _explorer_tab()

            with gr.Tab("Visualisierung"):
                _visualisierung_tab(
                    baseline_state,
                    explorer_state,
                    ai_state,
                )

            with gr.Tab("AI Candidate Lab"):
                _ai_candidate_lab_tab(env_status, ai_state)

            with gr.Tab("Provider Comparison"):
                _provider_comparison_tab(env_status)

            with gr.Tab("Claim Registry"):
                _claims_tab(caps.claim_registry_editable)

            with gr.Tab("Reports & Export"):
                _reports_export_tab(
                    baseline_state,
                    explorer_state,
                    ai_state,
                )

            with gr.Tab("Settings / Configuration"):
                _settings_tab(mode, env_status, live_ai_share_enabled)

    return demo
