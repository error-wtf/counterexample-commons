# Colab Complete Lab Local Precheck

```
COLAB_COMPLETE_LAB_LOCAL_PRECHECK

OLD_MULTI_NOTEBOOK_LAYER_PUBLICLY_WITHDRAWN: PASS
NEW_COMPLETE_LAB_NOTEBOOK_CREATED: PASS

NOTEBOOK_SECTIONS_PRESENT:
- Fresh runtime bootstrap:                PASS
- Scientific scope and source boundary:   PASS
- Exact validator self-test:              PASS
- Exact finite baseline table:            PASS
- Visualisations:                         PASS
- Interactive explorer:                   PASS
- Read-only claim registry:               PASS
- Safe public Gradio demo:                PASS (launch guard active; MANUAL_RUNTIME_REQUIRED in Colab)
- Finite result export:                   PASS
- Optional private AI lab disabled:       PASS
- Limitations/status section:             PASS

LOCAL_NBCONVERT_PRECHECK: PASS
FRESH_COLAB_RUNTIME_EXECUTION: NOT_YET_VERIFIED
PUBLIC_GRADIO_LAUNCH_IN_COLAB: NOT_YET_VERIFIED
PRIVATE_AI_LIVE_EXECUTION: NOT_EXECUTED
NOTEBOOK_OUTPUTS_CLEARED_BEFORE_COMMIT: PASS
WINDOWS_PATHS_IN_COMMITTED_NOTEBOOK: NO
SECRETS_IN_COMMITTED_NOTEBOOK: NO
SAWIN_STATUS_UNCHANGED: PASS
PYTEST: PASS (232/232)
FLAKE8: PASS
```

## Evidence

- `nbconvert --execute` completed without errors (ZMQ assertion noise on Windows is expected; exit 0 confirmed by write).
- Self-test output confirmed: `LAB_SELF_TEST: PASS`
- Baseline table printed with all expected rows.
- Visualisation cell executed and wrote `/tmp/lab_viz.png`.
- Claim registry printed with `REGISTRY_MODE: READ_ONLY`.
- Export cell wrote `/tmp/counterexample_commons_lab_export.json`, `Safe for export: True`.
- Private AI lab cell printed disabled message (no API calls).
- Gradio launch guard correctly printed `LOCAL PRECHECK: Gradio launch skipped`.
- Output scan found Windows paths in cell 12 output — cleared before commit.
- Final scan: no Windows paths, no secrets in committed notebook.
