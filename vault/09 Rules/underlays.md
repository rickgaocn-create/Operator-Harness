---
layer: platform
type: rule
scope: generated-underlays
created: 2026-05-27
created-by: codex
generator: ".claude/routines/build_underlays.py"
state:
  - ".claude/_state/underlays/source-graph.json"
  - ".claude/_state/underlays/taste-engine.json"
  - ".claude/_state/underlays/underlay-report.md"
---

# Underlays

This contract defines the generated machine underlays beneath `/operate` and future model flows. The underlays help agents ground claims and apply {{USER_NAME}}'s judgment patterns without turning authored Markdown into generated inventory.

## Components

| Underlay | Job | Primary reader |
|---|---|---|
| **Source Graph** | Machine-readable index of entities, claims, workstreams, decisions, open questions, tasks, and source anchors. | `/operate` "Make this forwardable", vault-researcher, future grounding tools |
| **Taste Engine v1** | Narrow judgment index from `_judgment/*` nodes and `corrections.jsonl` only. | `/operate` "Think with me", strategist, future judgment retrieval |
| **Underlay Report** | Human-readable generation summary, counts, skipped records, and fixture checks. | {{USER_NAME}}, `/operate` "Check the machine" |

## Hard Boundary

Generated underlays are read-only derived state.

- No generated Cards.
- No generated Actions.
- No generated Wiki replacements.
- No generated Tasks.
- No mass migration.
- No direct edits from the underlay builder outside `.claude/_state/underlays/`.
- Cards may be referenced as Source Graph context, but Cards are not promoted into Taste Engine v1.
- Generated Cards/Wiki/Actions are abandoned by default, not a roadmap item.

## Confidence Labels

| Label | Meaning |
|---|---|
| `source-anchored` | Tied to an explicit source anchor, quote boundary, or source note. |
| `file-derived` | Extracted from a typed vault file such as an Action, task line, project doc, Card, or judgment node. |
| `inferred` | Light deterministic inference from structure, such as linking a task to an Action by matching `chain-anchor`. |
| `needs-review` | Parsed but incomplete, ambiguous, malformed, or likely requiring human confirmation. |

## Source Graph Scope

Source Graph may index:

- Entities from frontmatter, wikilinks, counterparties, project artifacts, source notes, Cards, Actions, and task lines.
- Claims from `source_anchors`, source notes, Action decisions, meeting summaries, Cards, and project docs.
- Workstreams from Action files: `project`, `chain-anchor`, `status`, `counterparty`, `next-action`.
- Task bindings from Operon task lines: `operonId`, `status`, `chain-anchor`, source file.
- Decisions and open questions from Action files and meeting/project artifacts.

Source Graph does not certify truth. It records where a claim came from and how strongly the claim is anchored. Forwardable output must still pass attribution, confidentiality, audience, and language gates.

## Taste Engine v1 Scope

Taste Engine v1 includes only:

- `09 Rules/_judgment/v-*.md` value nodes.
- `09 Rules/_judgment/f-*.md` framework nodes.
- `.claude/_state/corrections.jsonl` entries with reusable `correction`, `candidate_rule`, `touches`, or promotion fields.

Taste Engine v1 explicitly excludes:

- Cards-as-principles.
- Inferred taste from the general Card corpus.
- Generated judgment from Action prose.
- Any model-classified principle without {{USER_NAME}} validation.

## `/operate` Usage

| Intent | Underlay use | Fallback |
|---|---|---|
| Make this forwardable | Check Source Graph for entity/claim grounding before running the existing best-of-N, biz, attribution, language, and style gates. | If missing or stale, read the live vault sources and say the underlay was unavailable. |
| Think with me | Pull Taste Engine v1 for values, frameworks, and correction patterns before generating options or a pre-mortem. | If missing or stale, read `_judgment/*` and `corrections.jsonl` directly and say the underlay was unavailable. |
| Check the machine | Report underlay freshness, counts, fixture checks, and skipped correction lines from `underlay-report.md`. | If missing, say underlays have not been generated and offer to run the builder. |

An underlay is stale when it is missing, older than the newest scoped source file, or older than 24 hours for active harness work.

## Builder Contract

`.claude/routines/build_underlays.py` must be deterministic, cross-platform Python. It may write only:

- `.claude/_state/underlays/source-graph.json`
- `.claude/_state/underlays/taste-engine.json`
- `.claude/_state/underlays/underlay-report.md`

The builder must tolerate malformed `corrections.jsonl` lines, report skipped records, and never edit Cards, Actions, Wiki, Tasks, project files, or rule files.

## Test Fixtures

- `10 Action/12 Active/T260526-channel-resource-push.md` must surface B站, TapTap, 好游快爆, 4399, `渠道争取`, decisions, open questions, and task bindings when present.
- The `5:5 -> 7:3` / `7:3` target in that workstream must not be treated as a counterparty agreement.
- Taste Engine v1 must include `v-truth-over-comfort`, `f-rigor-verification`, `v-resource-exchange`, and correction-derived rules with source paths.
