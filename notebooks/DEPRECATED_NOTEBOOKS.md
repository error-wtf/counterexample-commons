# Deprecated Prototype Notebooks

These notebooks were the original multi-notebook Colab layer. They have been
**deprecated as public validated workflows** and superseded by the single
complete research lab notebook:

```text
notebooks/Counterexample_Commons_Complete_Lab_Colab.ipynb
```

They remain in the repository for historical reference and internal use only.
They are not advertised as public Colab releases.

## Status

```
PREVIOUS_MULTI_NOTEBOOK_LAYER_STATUS: DEPRECATED / PRO-FORMA ONLY
```

## Per-Notebook Record

| Notebook | Original purpose | Why deprecated | Integrated into complete lab? |
|----------|-----------------|----------------|-------------------------------|
| `00_START_HERE_Colab` | Navigation/intro | Incomplete workflow; local nbconvert incorrectly treated as Colab evidence | Yes — Section 0/1 |
| `00A_Launch_Gradio_UI_in_Colab` | Full Gradio UI launcher | Launch without full context; no explorer or baselines | Yes — Section 7 |
| `00B_Launch_Public_Baseline_Demo_Only` | Minimal public launcher | Launcher only; no educational content | Yes — Section 7 |
| `01_Problem_and_Primary_Sources` | Problem description | Static markdown; no computation | Yes — Section 0 |
| `02_Exact_Baseline_Reproduction` | Baseline calculations | Useful but isolated; no visualisation or export | Yes — Sections 3/4/8 |
| `03_Interactive_Unit_Distance_Explorer` | Custom configuration validator | Explorer without baselines context | Yes — Section 5 |
| `04_Controlled_AI_Construction_Experiment` | AI experiment pipeline | Private workflow; not a public Colab demo | Yes — Section 9 (disabled by default) |
| `04A_Compare_Multiple_Providers` | Multi-provider comparison | Mock data only; misleading as demo | Yes — Section 9 (disabled by default) |
| `04B_Ollama_Local_Execution_Guide` | Ollama local setup guide | Ollama not available in Colab | No — local guide only |
| `05_Export_Validated_Report` | Export validated result | No prior context; export without baselines | Yes — Section 8 |
