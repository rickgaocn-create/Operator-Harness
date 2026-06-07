---
type: method
id: m-deal-debrief
name: Deal / roadshow debrief
task-kind: debrief/deal/roadshow
status: draft
deliverable: an internal deal/roadshow debrief that preserves insider judgment verbatim (numbers, model abbreviations, ratings, competitor framing, org-relations) with NO sentiment classification
calls-skills: [meeting-note, preserve, to-internal-briefing]
grounds-in: [f-rigor-verification, f-value-mechanism]
precipitated-from: pp-20260529-003 (Deal-debrief mode promotion) + 09 Rules/auto-chain-style.md § Deal-debrief
created: 2026-06-06
created-by: claude
---

# Deal / roadshow debrief

## Method
Templates an **internal deal or roadshow debrief**. The trap (the forbidden behavior this method exists to prevent): routing it through generic `/pragmatic` compression, which strips insider judgment, fragments number+term clusters into <30-char sentences, and forces deal items into positive/less-positive sentiment buckets. Value-free: invokes verification + value-mechanism judgment ([[f-rigor-verification]], [[f-value-mechanism]]); the read of the deal is the operator's. Deliverable is an internal briefing, not a forwardable polish (contrast [[09 Rules/_methods/m-forwardable-competitive-intel-report]]).

## Steps (DAG)

### capture_verbatim
**after:** —
**calls:** meeting-note, preserve
**reads:** the deal/roadshow source
Capture the content in **preserve mode** — raw, full fidelity. Do not compress yet.

### keep_number_term_clusters
**after:** capture_verbatim
Preserve number+term clusters **intact** — do NOT fragment them into <30-char sentences. The valuation/terms/ratios are the signal; fragmenting destroys it.

### keep_competitor_framing
**after:** capture_verbatim
Preserve competitor framing and org-relations **verbatim** — who's positioned against whom, the relationship map. Do not paraphrase into blandness.

### retain_ratings_abbrevs
**after:** capture_verbatim
Keep model abbreviations and ratings as-is — they're insider shorthand carrying dense judgment; expanding or normalizing them loses it.

### assemble_debrief
**after:** keep_number_term_clusters, keep_competitor_framing, retain_ratings_abbrevs
**calls:** to-internal-briefing
**writes:** the debrief
Assemble as an internal briefing. **No sentiment classification** — do not bucket deal items into positive/less-positive. Structure by deal/term/counterparty, preserving the verbatim clusters above.

## Memory
- 2026-05-29 — **A deal/roadshow debrief is NOT generic /pragmatic compression.** Generic compression strips insider judgment, fragments number+term clusters, and forces sentiment buckets — the exact forbidden behavior. Enable Deal-debrief mode instead. (pp-20260529-003, verdict: passed)
- 2026-05-29 — **Preserve verbatim:** numbers, model abbreviations, ratings, competitor framing, org-relations. These carry the dense judgment; normalizing them loses the point.
- 2026-05-29 — **No sentiment classification** on deal items — that's a report-mode move, wrong for a debrief.
