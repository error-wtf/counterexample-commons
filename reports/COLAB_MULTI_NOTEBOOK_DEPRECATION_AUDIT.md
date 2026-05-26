# Colab Multi-Notebook Deprecation Audit

```
PREVIOUS_MULTI_NOTEBOOK_LAYER_STATUS: DEPRECATED / PRO-FORMA ONLY

REASON:
- Incomplete workflows: each notebook contained only a partial slice of useful work
- Local nbconvert output incorrectly treated as Colab validation evidence
- Missing real fresh-runtime bootstrap in the originally published version
- App build confused with app launch: build_app() called without launch()
- AI/provider/Ollama notebooks were not genuine public workflows
- Windows-local paths committed in stored outputs
- sys.path.insert(0, "..") hacks used instead of proper bootstrap

NEW_DIRECTION:
- One complete end-to-end Colab Research Lab notebook
- notebooks/Counterexample_Commons_Complete_Lab_Colab.ipynb
```

## Per-Notebook Audit

| Old Notebook | Actual content | Why not a public product | Integrated into new lab? |
|---|---|---|---|
| `00_START_HERE_Colab` | Markdown intro + import check | Incomplete; nbconvert run locally was not Colab evidence | Yes — Sections 0, 1 |
| `00A_Launch_Gradio_UI_in_Colab` | Gradio launch cell only | Launch without scientific context | Yes — Section 7 |
| `00B_Launch_Public_Baseline_Demo_Only` | Minimal launcher | Launcher only; no content | Yes — Section 7 |
| `01_Problem_and_Primary_Sources` | Static markdown | No computation; read-only page | Yes — Section 0 |
| `02_Exact_Baseline_Reproduction` | Line/grid baselines | Useful but isolated; no visualisation | Yes — Sections 3, 4, 8 |
| `03_Interactive_Unit_Distance_Explorer` | Custom validator | Explorer without prior baseline context | Yes — Section 5 |
| `04_Controlled_AI_Construction_Experiment` | AI experiment pipeline | Private workflow; no public value as demo | Yes — Section 9 (disabled) |
| `04A_Compare_Multiple_Providers` | Provider comparison | Mock data only; misleading as research demo | Yes — Section 9 (disabled) |
| `04B_Ollama_Local_Execution_Guide` | Ollama local setup | Ollama unavailable in standard Colab | No — local guide only |
| `05_Export_Validated_Report` | Export cell | Export without prior computation context | Yes — Section 8 |

## Root Cause

The multi-notebook structure was never validated in a fresh Colab runtime.
Evidence collected was exclusively local `nbconvert --execute` runs inside an
existing `E:\clone\counterexample-commons` checkout. This is fundamentally
different from Colab execution, where:

1. No local packages exist.
2. No pre-cloned repository exists.
3. No `.venv` exists.
4. The bootstrap must work from scratch.

The notebooks were published to `main` with this incorrect evidence status.
This audit documents the correction.
