---
layer: instance
type: structure-principle
id: s-name-the-system-not-the-ui
name: Name the system by what it is, not the UI it's viewed through
status: draft
applies-to: [identity, descriptions, naming, foundational-files, output-format]
created: 2026-05-29
created-by: claude (harness reframe)
source: observed (2026-05-29 vault→harness reframe)
---

# Structure Principle · Name the system, not the window

**Principle:** Name and describe the system by what it *is* (a persistent harness — engine + state + content), not by the interface it's most often viewed through (Obsidian). Obsidian is one **window**; so are the CLI, Discord, and Feishu. The harness is the operating frame in every session, whatever the window.

**Why it's taste:** calling the system "the vault" silently couples it to one UI and undersells what it became — and it leaks into *behavior*: "Obsidian-optimized markdown" as a global rule produced recurring Feishu/Discord formatting friction (rich-text, `<at>` elements, shell-escaping). Naming reality fixes both the framing and the window-blind output.

**Tells when honored:** descriptions say "harness" for the system, "window" for an interface; output format is window-aware; "vault" survives only for the Obsidian-technical layer (paths, `.obsidian/`, wikilinks, Dataview).
**Tells when violated:** "the vault" used as the system's identity; output assumes Obsidian everywhere; one UI's conventions hardcoded as global rules.

**Boundary (so this doesn't become a sweep):** keep "vault" where it's *precise* — the Obsidian-indexed folder, paths, wikilinks, Dataview. Rename only the system-identity usages. A mechanical `s/vault/harness/` is cosmetic churn with link/eval breakage risk ([[s-no-stale-snapshots]] sibling caution; `corrections.jsonl:6` token-cost-per-value).

**Operationalized by:** the window-aware Formatting rule in [[CLAUDE.md]] § Communication Protocols; the windows model in [[CLAUDE.md]] intro; `harness-profiles.json` (windows/modes). **Born-from:** 2026-05-29 reframe + the Feishu/Discord formatting incidents in [[MEMORY]].
