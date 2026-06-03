# judgment-loop

> A bring-your-own-content engine for building, growing, and **applying** a personal judgment graph — the values, frameworks, and taste that should shape your work, captured as a typed graph and fed back into every open-ended output.

Most "second brain" setups store *facts*. This stores *judgment* — and closes the loop so the judgment actually shapes what you produce next, instead of sitting in a folder.

## The loop

```
        ┌──────────── capture ────────────┐
        │  corrections + corpus harvest    │   (scripted, ~0 model tokens)
        ▼                                  │
   distill brief  ──►  model writes        │
   (scripted)          proposals           │
                          │                │
                          ▼                │
                   human approves  ──►  encode to graph nodes
                                              │
                                              ▼
                                      apply (lens) ──► shapes the next output
                                              │
                                              └──── new corrections feed capture ──┘
```

Four moves, one cycle (full walkthrough in **[PROTOCOL.md](PROTOCOL.md)**):

1. **Capture** — corrections you make + judgment already expressed in your notes get mined into a candidate pool. Scripted; no model call.
2. **Distill** — a scripted pre-pass briefs a model on what's derivable + what the captured events touch; the model writes *proposals*.
3. **Encode** — nothing reaches the graph without your approval. Approved proposals become typed nodes (`value` / `framework`) with edges.
4. **Apply** — the graph feeds the **lens**: it matches an output against your values/frameworks and returns a grounded frame set that shapes generation. The full pipeline — priors + frames + grounding — *is* the quality bar: a human comparison scored it **7/10 against 3/10** for a stripped priors-only draft (see [evals/RESULTS.md](evals/RESULTS.md)). **best-of-N** (a few full-pipeline passes, keep/merge the best) sits *on top* as a reliability multiplier — it lifts the floor against run-to-run variance; it does **not** replace the frames. And the LLM can't pick the winner: in the same eval an LLM judge rated the 3/10 draft ≈ the 7/10 one. The terminal judge is you.

## Design principles

- **Scripted halves are free.** Harvest, distill-brief, lens, and registry are pure Python — ~0 model tokens, runnable on a clock or a hook. A model is invoked only for the irreducibly-judgment step (writing proposals).
- **Human-gated encode.** The graph is yours; the loop *proposes*, you *approve*. No node is written or edited by a script.
- **Revealed > stated.** The richest signal is judgment you already expressed in your work (a corrected draft), not values declared in the abstract.
- **Portable by construction.** Zero hardcoded paths, zero dependencies (stdlib only, Python 3.11+ for `tomllib`). One TOML config = one instance: point it at *your* graph and *your* corpus.

## Quickstart

A complete, runnable demo instance ships in `seed/` — drive it immediately:

```bash
python cli.py lens     --config seed/seed.toml --context "strategy build investment decision"
python cli.py harvest  --config seed/seed.toml
python cli.py distill  --config seed/seed.toml --brief
python cli.py registry --config seed/seed.toml
```

To point it at your own content: copy `configs/example.toml` (fully commented), set `paths.root`, and adjust the graph schema + harvest sources to match your notes. See `seed/schema.md` for the node format.

## Components

| Command | What it does | Tokens |
|---|---|---|
| `lens` | apply the graph to an output context → frame set + baseline floor | 0 |
| `harvest` | mine your corpus (pluggable markdown / jsonl source adapters) for candidates | 0 |
| `distill` | brief a model on what to propose for the graph (threshold-triggered) | 0 (brief) |
| `registry` | manifest of the graph: nodes, `embodies` edges, coverage, gaps | 0 |

## Status — v0.1

Extracted from a working in-vault engine (months of live use) into this configurable tool, and **validated against the source vault** as a reference instance:

- [x] **lens** — byte-identical frame selection vs the original
- [x] **harvest** — identity-identical candidate set (73 found / 40 returned) vs the original
- [x] **distill** — identical cluster set + event count vs the original
- [x] **registry** — graph manifest + gap finder (graph-focused; the original's rules-governance scan stays vault-side)
- [x] **seed** — a runnable starter instance (2 values, 2 frameworks, sample corpus) so a new graph isn't empty

## Layout

```
judgment-loop/
├── README.md   ·  PROTOCOL.md      what it is · how the loop runs
├── cli.py                          python cli.py <cmd> --config <toml> ...
├── jloop/                          the engine (stdlib-only package)
│   ├── config.py                   TOML loader — all instance-coupling lives here
│   ├── lens.py  ·  harvest.py  ·  distill.py  ·  registry.py
├── configs/
│   ├── example.toml                generic, fully-commented template
│   └── rg-vault.toml               reference instance (validates the ports)
└── seed/                           runnable demo: seed.toml + _judgment/ + cards/ + state/
```
