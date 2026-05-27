# Counterexample Commons

**An Anti-Capitalist AI-Assisted Mathematics Research Lab**
Exact finite validation for planar unit-distance configurations.

Counterexample Commons is inspired by OpenAI's 2026 unit-distance
breakthrough, but it does not locally reproduce the OpenAI/Sawin asymptotic
construction. The current product is a local Gradio laboratory for:

- exact finite baselines;
- rational point-set exploration;
- visualization of exactly validated unit-distance edges;
- finite AI-generated candidate hypotheses;
- read-only theorem provenance;
- finite validation reports.

This project is source-available under the Anti-Capitalist Software License
v1.4. It is not OSI-defined open source.

## Scientific Boundary

Let `u(n)` be the maximum number of unit-distance pairs determined by `n`
points in the plane.

The repository keeps these categories separate:

| Result | Source | Local status |
|--------|--------|--------------|
| OpenAI fixed-delta disproof: exists `delta > 0` | official proof PDF | `SOURCE_DOCUMENTED`, not locally reproduced |
| Original OpenAI proof explicit delta | official announcement/proof | `NOT_PROVIDED_BY_ORIGINAL_PROOF` |
| Companion human-digested proof | official companion remarks PDF | `SOURCE_DOCUMENTED`, not locally reproduced |
| Companion tiny exponent around `1 + 6.24e-38` | official companion remarks PDF | `SOURCE_DOCUMENTED`, not Sawin `1.014` |
| Sawin `delta = 0.014`, exponent `1.014` | OpenAI announcement of forthcoming refinement | `SOURCE_DOCUMENTED / PRIMARY_PROOF_PENDING` |
| Finite rational mesh baseline | local exact checker | `LOCALLY_REPRODUCED_EXACT`, finite-only |

The finite rational mesh baseline is useful local mathematics. It is not
Sawin's construction, not evidence for exponent `1.014`, and not a local
reproduction of the OpenAI asymptotic theorem.

## Official Sources

- [OpenAI announcement, 2026-05-20](https://openai.com/index/model-disproves-discrete-geometry-conjecture/)
- [Planar Point Sets with Many Unit Distances](https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-proof.pdf)
- [Remarks on the Disproof of the Unit Distance Conjecture](https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-remarks.pdf)

The OpenAI proof mechanism is not an ordinary two-dimensional rational mesh.
At a high level it uses totally real number fields `L`, associated CM fields
`K = L(i)`, unramified tower/Golod-Shafarevich machinery, rational primes
splitting completely, norm-one elements, high-dimensional Minkowski lattices,
product-of-discs window selection, and projection to one complex coordinate.

## Reproduction Levels

| Level | Scope | Current status |
|-------|-------|----------------|
| L0 | finite exact baselines | implemented |
| L1 | finite AI candidates | implemented |
| L2 | official source / theorem map | implemented |
| L3 | algebraic toy models | not implemented |
| L4 | number-field construction prototypes | not implemented |
| L5 | lemma-by-lemma reconstruction | not implemented |
| L6 | asymptotic result reproduction | not implemented |

No L3-L6 result may be claimed from grid, mesh, plot, or finite AI-candidate
success.

## Local No-Key App

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe scripts\run_gradio_local.py --mode local-private --no-browser --port 7861
```

Without `.env`, the app remains useful:

- Overview and Sources & Theorem Map;
- Exact Baselines;
- Configuration Explorer;
- Visualisierung;
- read-only Claim Registry;
- Reports & Export;
- AI/provider tabs visible as `NOT_CONFIGURED`.

No live provider request can be sent in a no-key state.

## Private Local AI Testing

```powershell
Copy-Item .env.example .env
notepad .env
```

Only `.env.example` is tracked. `.env` is ignored. The app reports provider
status only as `CONFIGURED` or `NOT_CONFIGURED`; it must never display keys,
fragments, token lengths, authorization headers, or `.env` contents.

Some provider adapters may still report `LIVE_ADAPTER_NOT_IMPLEMENTED`. That
is intentional honesty, not mock evidence.

## AI Candidate Lab Scope

Current mode:

```text
FINITE_CANDIDATE_MODE
```

The AI Lab can parse/generate small finite rational point candidates and check
them with the exact validator. It does not attempt the algebraic-number-
theoretic construction used in the OpenAI proof, does not reproduce Sawin's
announced `delta = 0.014` refinement, and does not establish asymptotic bounds.

Future proof-oriented AI experiments must be separate from finite candidate
validation.

## Reports

Reports distinguish:

- source-documented results;
- locally executed finite checks;
- non-implications.

A finite validated configuration does not locally reproduce the asymptotic
OpenAI theorem or Sawin's announced refinement.

## Colab Status

The existing Complete-Lab Colab notebook is intentionally unchanged during this
local app recovery. It hardcodes `REPO_BRANCH = "rebuild/colab-complete-lab"`
and cannot test this recovery branch directly. Colab deployment is deferred
until after local no-key and private `.env` testing.
