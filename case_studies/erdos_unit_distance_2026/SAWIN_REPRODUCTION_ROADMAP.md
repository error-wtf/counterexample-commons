# Asymptotic Reproduction Roadmap

**Current recovery scope:** L0, L1 and L2 only.

The repository does not locally reproduce the OpenAI proof, the companion
proof, or Sawin's announced `delta = 0.014` refinement.

## Source-Distinct Claims

| Result | Current repository status |
|--------|---------------------------|
| OpenAI proof: exists fixed `delta > 0` | `SOURCE_DOCUMENTED`, not locally reproduced |
| Original proof explicit `delta = 0.014` | `NOT_PROVIDED_BY_ORIGINAL_PROOF` |
| Companion tiny exponent around `1 + 6.24e-38` | `SOURCE_DOCUMENTED`, not locally reproduced |
| Sawin `delta = 0.014` | OpenAI announcement of forthcoming refinement; primary proof pending |
| Finite rational mesh | locally exact finite baseline; not Sawin |

## Real Proof Architecture

The source-documented asymptotic proof is not a finite rational mesh. At a
high level it uses:

1. totally real number fields `L`;
2. CM fields `K = L(i)`;
3. unramified tower / Golod-Shafarevich machinery;
4. rational primes splitting completely;
5. many norm-one elements under complex embeddings;
6. high-dimensional Minkowski lattices;
7. product-of-discs window selection;
8. projection to one complex coordinate.

## Reproduction Levels

| Level | Description | Current status |
|-------|-------------|----------------|
| L0 | finite exact line/grid/rational/mesh baselines | implemented |
| L1 | finite AI-generated rational candidates, exactly validated | implemented |
| L2 | official source and theorem provenance map | implemented |
| L3 | algebraic toy models: Gaussian integers, norm-one examples, small embeddings | not implemented |
| L4 | CM-field, splitting-prime and Minkowski-embedding prototypes | not implemented |
| L5 | lemma-by-lemma reconstruction of source proof machinery | not implemented |
| L6 | independently verified asymptotic result reproduction | not implemented |

## Upgrade Rule

Do not upgrade any asymptotic claim based on:

- square grids;
- finite rational mesh plots;
- AI-produced small rational point sets;
- visual density;
- finite exact validation alone.

Only a complete independently verified L6 programme may support a local
asymptotic reproduction claim.
