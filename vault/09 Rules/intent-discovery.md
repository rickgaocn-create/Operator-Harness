---
layer: platform
type: rule
scope: intent-discovery
created: 2026-06-02
created-by: claude
companion-rules:
  - "[[09 Rules/operator-intents.md]]"
  - "[[09 Rules/discovery-pass.md]]"
  - "[[04 Notes/_system/(C) skill-lifecycle-intent-discovery-addendum-2026-06-02]]"
---

# Intent Discovery · diverge / converge

> **Why.** Users are often ambiguous not because they hid a preference but because **the intent isn't formed yet** — they discover what they want by seeing options (DiscoverLLM, arXiv 2602.03429). On an *unformed* ask, neither guess-and-execute nor a bare "what do you want?" is right: **diverge** (surface concrete options) until the intent concretizes, then **converge** (commit + execute). Reported effect: higher task success, ~40% shorter conversations — serves {{USER_NAME}}'s "max judgment over regular conversation" + low-overhead goals.

## Where this sits (ordering — don't double-prompt)

Runs **after** `[[09 Rules/operator-intents.md]]` / `/operate` route the ask to one of the 5 intent contracts. Those resolve *which kind of intent* (intent-ambiguity). This rule resolves a **different axis — is the OBJECT/scope formed enough to execute?** (object-formedness). One ambiguity check per axis; never fire both into a double question.

Pairs with `[[09 Rules/discovery-pass.md]]`: discovery-pass is the *within-task* coherence pass; this is the *at-the-ask* layer.

## Concretization signal (cheap heuristic)

- **UNFORMED** — open-ended framing (*what about / explore / look into / develop / improve / strengthen / consider / think about / what can we do*) **and** no concrete deliverable / target / action named.
- **FORMED** — a specific deliverable, target, file, or action is named (*build X / fix Y / send Z / spec the W*).
- Unsure → treat as unformed; a quick diverge is cheap, a wrong guess-execute is not.

## Diverge (UNFORMED)

Surface **2–4 concrete option-directions + a recommendation**, then let the operator react. Do **not** guess-execute; do **not** ask a bare "what do you want?". Use the numbered text-picker (canonical source: the **global** `~/.claude/CLAUDE.md` AskUserQuestion→text-mode rule; restated here so this rule is self-contained):

> ❓ **<one-line question>**
> 1. **<option>** — <one-line description> (rec, if recommending one — put it first)
> 2. **<option>** — <one-line description>
> *(Reply with the number, the label, or free text.)*

Options must be **concrete directions**, not generic questions. Lead with a recommendation when you have one.

## Converge (FORMED, or after the operator picks)

Once a deliverable/target is named or the operator picks/refines → **commit + execute** (run the discovery-pass during execution). **Don't keep diverging** — the goal is shorter conversations, not endless option menus. The discovered intent (what they chose/refined) is **gold** for the reflect-back.

## Hard rules

- **NEVER** guess-execute an UNFORMED, non-trivial / irreversible ask — diverge first.
- **NEVER** answer an unformed ask with a bare clarifier ("what do you want?") — diverge with **concrete options**.
- **Converge promptly** once formed; one good round of options beats three.
- This is a *posture*, not a new organ — `/operate` and the operator apply it; register no new state.
