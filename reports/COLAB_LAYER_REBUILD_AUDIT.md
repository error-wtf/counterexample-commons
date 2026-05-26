# Colab Layer Rebuild Audit

```
PREVIOUS_COLAB_PASS_CLAIM: REJECTED
LOCAL_NBCONVERT_WAS_NOT_COLAB_EVIDENCE: CONFIRMED
INITIAL_PUBLIC_COLAB_LAYER_STATUS: FAIL
REBUILD_REQUIRED: YES
```

## Per-Notebook Audit

| Notebook | Zweck | Importiert Projektcode? | Echter Colab-Bootstrap vorhanden? | Klont Repo? | Installiert Repo? | Führt echte Funktion aus? | Mock/Anleitung/Live? | Release-Status |
|----------|-------|------------------------|-----------------------------------|-------------|-------------------|--------------------------|---------------------|----------------|
| `00_START_HERE_Colab` | Einführung, Navigation | Ja | Ja (Testbranch) | Ja | Ja | Import + Version-Check | Live (safe) | PUBLIC TEST CANDIDATE |
| `00A_Launch_Gradio_UI_in_Colab` | Gradio Full UI starten | Ja | Ja (Testbranch) | Ja | Ja | Gradio launch (colab-public-demo) | Live (conditional) | CONDITIONAL PUBLIC TEST CANDIDATE |
| `00B_Launch_Public_Baseline_Demo_Only` | Sichere öffentliche Demo | Ja | Ja (Testbranch) | Ja | Ja | Gradio launch (colab-public-demo) | Live (safe) | PUBLIC TEST CANDIDATE |
| `01_Problem_and_Primary_Sources` | Inhalt / Quellen | Nein (reines Markdown+Print) | N/A | Nein | Nein | print() | Anleitung | PUBLIC TEST CANDIDATE |
| `02_Exact_Baseline_Reproduction` | Exakte Baselines berechnen | Ja | Ja (Testbranch) | Ja | Ja | validate_line/grid_configuration | Live (exact finite) | PUBLIC TEST CANDIDATE |
| `03_Interactive_Unit_Distance_Explorer` | Eigene Koordinaten validieren | Ja | Ja (Testbranch) | Ja | Ja | validate_custom_configuration | Live (exact finite) | PUBLIC TEST CANDIDATE |
| `04_Controlled_AI_Construction_Experiment` | KI-Experiment-Pipeline | Ja | Ja (Testbranch) | Ja | Ja | PreRegistration only; Generation deaktiviert | Private/Manual | PRIVATE OPTIONAL |
| `04A_Compare_Multiple_Providers` | Provider-Vergleich | Ja | Ja (Testbranch) | Ja | Ja | build_default_registry (no live calls) | Mock/Manual | PRIVATE OPTIONAL |
| `04B_Ollama_Local_Execution_Guide` | Ollama lokal einrichten | Ja | Ja (Testbranch) | Ja | Ja | Ollama-Verfügbarkeitscheck | Anleitung | LOCAL GUIDE ONLY |
| `05_Export_Validated_Report` | Validierten Bericht exportieren | Ja | Ja (Testbranch) | Ja | Ja | validate_grid + sanitize_for_export | Live (exact finite) | PUBLIC TEST CANDIDATE |

## Klassifikation

### A. Public Runtime Test Candidates
- `00_START_HERE_Colab`
- `00B_Launch_Public_Baseline_Demo_Only`
- `01_Problem_and_Primary_Sources`
- `02_Exact_Baseline_Reproduction`
- `03_Interactive_Unit_Distance_Explorer`
- `05_Export_Validated_Report`

### B. Conditional Public Test Candidate
- `00A_Launch_Gradio_UI_in_Colab` — Default colab-public-demo, keine Keys, read-only Claims.
  Link wird nach erfolgreichem Fresh-Runtime-Test hinzugefügt.

### C. Private / Optional / Not Release-Ready
- `04_Controlled_AI_Construction_Experiment` — PRIVATE_OPTIONAL_WORKFLOW, live API off
- `04A_Compare_Multiple_Providers` — MOCK_OR_PRIVATE_MANUAL_ONLY
- `04B_Ollama_Local_Execution_Guide` — LOCAL_OLLAMA_GUIDE_ONLY, nicht Colab-verifiziert

## Bekannte Vorschäden (präzise Dokumentation)

1. **Lokale nbconvert-Ausführung** wurde als Colab-Erfolg verbucht — **FALSCH**.
   nbconvert läuft im lokalen venv, nicht in einer frischen Colab-Runtime.

2. **Windows-Pfade in Outputs** (`E:\clone\counterexample-commons\.venv\...`) wurden
   committed — **BEREINIGT** in diesem Rebuild.

3. **`sys.path.insert(0, "..")`-Hacks** in mehreren Notebooks — **ENTFERNT**.
   Alle Notebooks verwenden jetzt den kanonischen Bootstrap.

4. **Falscher Branch** — vorherige Bootstraps klonten von `main` statt vom Testbranch.
   **KORRIGIERT**: Alle Bootstraps klonen jetzt `test/colab-runtime-validation`.

5. **`IN_COLAB` Detection** — `"google.colab" in sys.modules` war beim ersten Zellen-Run
   manchmal `False`. **KORRIGIERT**: 3-Wege-Check inkl. `COLAB_RELEASE_TAG`.

6. **App-Build ≠ App-Start** — `build_app()` ohne `launch()` wurde als Colab-Erfolg
   interpretiert. **KORRIGIERT**: `launch(share=True)` nur wenn `IN_COLAB`.
