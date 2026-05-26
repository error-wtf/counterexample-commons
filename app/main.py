"""Main Gradio application builder."""

from __future__ import annotations

import gradio as gr

from counterexample_commons.config import (
    AppMode,
    CAPABILITY_MATRIX,
)
from counterexample_commons.validators import (
    validate_line_configuration,
    validate_grid_configuration,
    validate_custom_configuration,
)
from counterexample_commons.claims import INITIAL_CLAIMS
from counterexample_commons.providers import build_default_registry
from counterexample_commons.experiments import (
    extract_candidate_coordinates,
    validate_candidate,
    sanitize_for_export,
)
from counterexample_commons.env_loader import load_local_env
from counterexample_commons import visualization

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


def _overview_tab():
    gr.Markdown("""
# Counterexample Commons
## An Anti-Capitalist AI-Assisted Mathematics Research Lab

**First case study:** The 2026 AI-generated counterexample to
ErdÅ‘s' planar unit-distance conjecture.

### The Problem

Let u(n) be the largest number of unordered pairs at Euclidean
distance exactly 1 among n planar points.

- **Line:** n collinear unit-spaced points â†’ nâˆ’1 edges
- **Grid:** kÃ—k square grid â†’ 2k(kâˆ’1) edges
- **Historical:** constructions achieving n^{1+C/log log n}

### What Changed in 2026

- OpenAI announced an AI-generated construction achieving
  n^{1+Î´} for fixed Î´>0
- Companion paper by Alon, Bloom, Gowers, Litt, Sawin et al.
  provides human-verified analysis
- Sawin gives explicit exponent: n^{1.014}
  (SOURCE_DOCUMENTED; not yet locally reproduced here)
- Upper bound O(n^{4/3}) remains far above â€” exact u(n) still open

### Scientific Integrity

""" + SCIENTIFIC_BOUNDARY)


def _baselines_tab():
    gr.Markdown("## Exact Finite Baselines\n\n**Boundary:** Finite exact validation only. NOT Sawin's n^1.014 construction.")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Line Configuration")
            n_line = gr.Slider(
                2, 100, value=16, step=1, label="n (points)"
            )
            btn_line = gr.Button("Validate Line")
            out_line = gr.JSON(label="Result")
            btn_line.click(
                fn=lambda n: validate_line_configuration(int(n)),
                inputs=n_line,
                outputs=out_line,
                api_name="validate_line_configuration",
            )

        with gr.Column():
            gr.Markdown("### Square Grid Configuration")
            k_grid = gr.Slider(
                2, 20, value=4, step=1, label="k (grid side)"
            )
            btn_grid = gr.Button("Validate Grid")
            out_grid = gr.JSON(label="Result")
            btn_grid.click(
                fn=lambda k: validate_grid_configuration(int(k)),
                inputs=k_grid,
                outputs=out_grid,
                api_name="validate_grid_configuration",
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


def _visualisierung_tab():
    from counterexample_commons import visualization
    gr.Markdown("""
## Visualisierung exakt validierter Punktkonfigurationen

Only edges confirmed by exact rational validation are drawn.
""")
    
    source = gr.Dropdown(choices=[\ Line Configuration\,\Square Grid Configuration\,\Rational 3/5-4/5 Example\,\Finite Rational Mesh Baseline\],value=\Square Grid Configuration\,label=\Configuration Source\)


def _settings_tab(mode: AppMode, caps):
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


def _reports_export_tab(enabled: bool, caps):
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
    env_loaded = load_local_env()
    caps = CAPABILITY_MATRIX[mode]

    with gr.Blocks(
        title="Counterexample Commons",
    ) as demo:
        gr.Markdown(
            "# Counterexample Commons\n"
            "*Exact Validation and Anti-Capitalist "
            "AI-Assisted Mathematics Research*"
        )

        with gr.Tabs():
            with gr.Tab("Overview"):
                _overview_tab()

            with gr.Tab("Exact Baselines"):
                _baselines_tab()

            with gr.Tab("Configuration Explorer"):
                _explorer_tab()

            with gr.Tab("Visualisierung"):
                _visualisierung_tab()

            # AI tab always visible, shows config status inside
            if caps.ai_candidate_lab or True:
                with gr.Tab("AI Candidate Lab"):
                    _ai_candidate_lab_tab(caps.ai_candidate_lab)

            # Provider tab always visible
            if caps.provider_comparison or True:
                with gr.Tab("Provider Comparison"):
                    _provider_comparison_tab(caps.provider_comparison)

            with gr.Tab("Claim Registry"):
                _claims_tab(caps.claim_registry_editable)

            with gr.Tab("Reports & Export"):
                _reports_export_tab(caps.export_full, caps)

            with gr.Tab("Settings"):
                _settings_tab(mode, caps)

    return demo
