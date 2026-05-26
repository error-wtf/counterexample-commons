# Colab Test Branch Candidate Validation

```
COLAB_TEST_BRANCH_CANDIDATE_STATUS

INITIAL_PUBLIC_COLAB_LAYER_STATUS: FAIL
REBUILD_APPROACH: MINIMAL_REAL_RUNTIME_CANDIDATES
LOCAL_PRECHECK: PASS
FRESH_COLAB_RUNTIME_EXECUTION: NOT_YET_VERIFIED
LIVE_API_EXECUTION: NOT_EXECUTED
LIVE_OLLAMA_EXECUTION: NOT_EXECUTED
NOTEBOOK_OUTPUTS_COMMITTED: CLEARED
WINDOWS_PATHS_IN_COMMITTED_NOTEBOOKS: NO
SECRETS_IN_COMMITTED_NOTEBOOKS: NO
SAWIN_STATUS_UNCHANGED: PASS
PYTEST: PASS (232/232)
FLAKE8: PASS
```

## Branch

```
test/colab-runtime-validation
```

## Bootstrap Pattern

All notebooks that import project code use the canonical bootstrap:

- Detects Colab via 3-way check:
  `"google.colab" in sys.modules`
  OR `COLAB_RELEASE_TAG` env var
  OR `COLAB_BACKEND_VERSION` env var
- In Colab: clones `test/colab-runtime-validation` branch, installs with `pip install -e`
- Local: traverses parents for repo root containing `counterexample_commons/` + `pyproject.toml`
- No `sys.path.insert(0, "..")` hacks

## Notebooks Rebuilt

| Notebook | Class | Local Precheck |
|----------|-------|---------------|
| `00_START_HERE_Colab` | PUBLIC_TEST_CANDIDATE | PASS |
| `00A_Launch_Gradio_UI_in_Colab` | CONDITIONAL_PUBLIC_TEST_CANDIDATE | SKIPPED (launch guard) |
| `00B_Launch_Public_Baseline_Demo_Only` | PUBLIC_TEST_CANDIDATE | SKIPPED (launch guard) |
| `01_Problem_and_Primary_Sources` | PUBLIC_TEST_CANDIDATE | PASS |
| `02_Exact_Baseline_Reproduction` | PUBLIC_TEST_CANDIDATE | PASS |
| `03_Interactive_Unit_Distance_Explorer` | PUBLIC_TEST_CANDIDATE | PASS |
| `04_Controlled_AI_Construction_Experiment` | PRIVATE_OPTIONAL | STATIC_ONLY |
| `04A_Compare_Multiple_Providers` | PRIVATE_OPTIONAL | STATIC_ONLY |
| `04B_Ollama_Local_Execution_Guide` | LOCAL_GUIDE_ONLY | STATIC_ONLY |
| `05_Export_Validated_Report` | PUBLIC_TEST_CANDIDATE | PASS |

## Invariants Preserved

- `UD-SAWIN-2026-001`: `SOURCE_DOCUMENTED`, `locally_validated=False` — UNCHANGED
- Rational Mesh: separate finite exact baseline, not Sawin — UNCHANGED
- Security: `local-private` / `colab-private` share block — UNCHANGED (test confirmed)
- Claim Registry: read-only — UNCHANGED
- CI: pytest 232/232 PASS, flake8 PASS — UNCHANGED
- License / Mission: Anti-Capitalist Software License — UNCHANGED

## Next Steps

1. Open `00_START_HERE_Colab` from testbranch link in a fresh Google Colab runtime.
2. Execute all cells — expect: clone, install, import, version output, no errors.
3. Open `00B_Launch_Public_Baseline_Demo_Only` — expect: Gradio demo URL in output.
4. Open `02_Exact_Baseline_Reproduction` — expect: line/grid results, Sawin note.
5. Open `03_Interactive_Unit_Distance_Explorer` — expect: coordinate validation output.
6. Open `05_Export_Validated_Report` — expect: sanitized JSON export, no secrets.
7. After all 5 pass: document results here and open PR to merge to main.
