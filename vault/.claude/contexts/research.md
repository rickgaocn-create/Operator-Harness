# Mode: Research — vault-first grounding lens

> Soft session lens. Subordinate to `09 Rules/**` / `CLAUDE.md` / judgment graph (see `_README.md`). Biases tools + posture only; never overrides a rule or the graph.

## Posture
- **Grounding order (`f-corpus-grounding`):** vault grep → public web → ask the user → assume. In that order, every time. Don't guess what the vault can tell you.
- **Breadth, then synthesis.** Gather wide, then compress to the conclusion — don't narrate the search.
- **待核实 anything unconfirmed.** Never fabricate precision (dates/numbers/quotes). Cite sources for public claims.
- **Token discipline (`f-value-mechanism`):** push heavy reading to subagents; keep the main thread for the judgment, not the file dumps.

## Tools to favor
- **Read / Grep / Glob** (vault) · **vault-researcher** (semantic + entity sweep)
- **Explore / general-purpose** subagents — fan-out reading, return conclusions only
- **context7** — library / API / SDK docs (prefer over guessing from memory)
- **WebSearch / WebFetch / firecrawl / exa** — web intel when the vault is silent

## Defer to (mode yields)
`f-corpus-grounding` + `f-rigor-verification` (the grounding/rigor frameworks own the hard discipline) · `attribution-discipline` for anything that will be forwarded.
