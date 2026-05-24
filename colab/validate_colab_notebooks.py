"""Validate structural completeness of Colab notebooks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_NOTEBOOKS = [
    "00_START_HERE_Colab.ipynb",
    "00A_Launch_Gradio_UI_in_Colab.ipynb",
    "00B_Launch_Public_Baseline_Demo_Only.ipynb",
    "01_Problem_and_Primary_Sources.ipynb",
    "02_Exact_Baseline_Reproduction.ipynb",
    "03_Interactive_Unit_Distance_Explorer.ipynb",
    "04_Controlled_AI_Construction_Experiment.ipynb",
    "04A_Compare_Multiple_Providers.ipynb",
    "04B_Ollama_Local_Execution_Guide.ipynb",
    "05_Export_Validated_Report.ipynb",
]


def validate_notebook(path: Path) -> list[str]:
    """Validate a single notebook file."""
    errors: list[str] = []

    if not path.exists():
        errors.append(f"MISSING: {path.name}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"INVALID_JSON: {path.name}: {e}")
        return errors

    if "cells" not in data:
        errors.append(f"NO_CELLS: {path.name}")
        return errors

    if len(data["cells"]) == 0:
        errors.append(f"EMPTY: {path.name}")
        return errors

    # Check for install cell (first code cell should have pip install)
    code_cells = [
        c for c in data["cells"] if c.get("cell_type") == "code"
    ]
    if not code_cells:
        errors.append(f"NO_CODE_CELLS: {path.name}")

    return errors


def main() -> int:
    """Validate all required notebooks."""
    root = Path(__file__).resolve().parent.parent
    notebooks_dir = root / "notebooks"

    all_errors: list[str] = []

    for nb_name in REQUIRED_NOTEBOOKS:
        path = notebooks_dir / nb_name
        errs = validate_notebook(path)
        all_errors.extend(errs)

    if all_errors:
        print(f"FAIL: {len(all_errors)} notebook issues:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: All {len(REQUIRED_NOTEBOOKS)} notebooks valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
