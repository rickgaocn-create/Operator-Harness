# Node schema

A judgment graph is a directory of markdown files, one per node. Two node types.

## Frontmatter

```yaml
---
type: value          # "value" (a root belief) or "framework" (a repeatable method)
id: v-honesty        # stable, unique; how edges reference this node
name: Truth over comfort
status: draft        # draft | live | archived
applies-to: [analysis, decision, baseline]   # tags the lens matches an output context against
embodies: [v-honesty]   # frameworks only — the value-id(s) this framework serves
---
```

- **`applies-to`** is what makes a node *selectable* by the lens. When you ask the lens for a context like `"bd proposal channel"`, it scores each node by how many of its `applies-to` tags appear in that context. A node with no `applies-to` can never be picked.
- **`baseline`** in `applies-to` marks an always-on lens — the *floor* carried into every output, never diverged across (e.g. honesty, rigor).
- **`embodies`** (frameworks → values) is the graph's main edge. `registry` derives the reverse (value ← the frameworks that embody it) and flags values with no framework.

## Body

Lift-able fields the engine reads (bold label, exactly as written):

- **`Statement:`** (values) or **`Procedure:`** (frameworks) — the essence the lens turns into a generator prompt.
- **`Rules that serve it:`** / **`Operationalized by:`** — the concrete rules; shown by the lens and distill.
- An unfilled edge is marked with a phase token, e.g. `**Rules that serve it:** (J2 — ...)`. `distill` lists these as placeholders for the model to fill. (The token is configurable — `placeholder_marker`.)

Everything above (field names, the baseline tag, the placeholder token) is configurable per instance — see `configs/example.toml`. The defaults match this seed.
