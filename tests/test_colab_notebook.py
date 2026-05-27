"""Safety checks for the complete Colab lab notebook."""

from __future__ import annotations

import json
from pathlib import Path


NOTEBOOK = (
    Path(__file__).resolve().parents[1]
    / "notebooks"
    / "Counterexample_Commons_Complete_Lab_Colab.ipynb"
)


def _load_notebook():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


def _all_source_text() -> str:
    nb = _load_notebook()
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in nb["cells"]
    )


def test_complete_colab_notebook_exists():
    assert NOTEBOOK.exists()


def test_complete_colab_targets_rescue_branch():
    text = _all_source_text()
    assert 'REPO_BRANCH = "main"' in text
    assert "rescue/integrated-complete-lab" not in text
    assert "rebuild/colab-complete-lab" not in text


def test_complete_colab_has_clean_outputs():
    nb = _load_notebook()
    for cell in nb["cells"]:
        assert cell.get("execution_count") is None
        assert cell.get("outputs", []) == []


def test_complete_colab_is_secret_safe_public_demo():
    text = _all_source_text()
    openai_key_prefix = "sk" + "-"
    github_pat_prefix = "ghp" + "_"
    github_oauth_prefix = "gho" + "_"
    forbidden_fragments = [
        "PRIMARY_PROOF_PENDING",
        "Sawin Lattice",
        openai_key_prefix,
        github_pat_prefix,
        github_oauth_prefix,
        "E:\\",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in text

    assert "Provider credential environment variables are present" in text
    assert "colab-public-demo" in text
    assert "share=True" in text


def test_complete_colab_scientific_boundaries():
    text = _all_source_text()
    assert "arXiv:2605.20579" in text
    assert "not locally reproduced" in text
    assert "not Sawin's construction" in text
    assert "not evidence for exponent n^1.014" in text
    assert "121 points" in text
    assert "82 exactly validated unit-distance edges" in text


def test_complete_colab_code_cells_compile():
    nb = _load_notebook()
    for index, cell in enumerate(nb["cells"], start=1):
        if cell["cell_type"] == "code":
            source = "".join(cell.get("source", []))
            compile(source, f"colab-cell-{index}", "exec")
