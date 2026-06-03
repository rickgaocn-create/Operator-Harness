# The loop

judgment-loop is four moves around one cycle. Three are scripted (~0 model tokens); one
needs a model; one needs *you*. Nothing reaches the graph without your approval.

```
   capture ──► harvest ──► distill ──► [model proposes] ──► YOU approve ──► encode ──► apply
      ▲                                                                                  │
      └──────────────────────── corrections from real work ◄────────────────────────────┘
```

## 1. Capture  (you, in the moment — ~0 tokens)

When you correct a draft, make a call, or notice a belief firing, append one line to your
corrections log (`state/corrections.jsonl`):

```json
{"ts":"...","artifact":"what you were doing","ai_output":"what was wrong/flat",
 "correction":"what you changed it to","why":"the reason","candidate_rule":"the rule in one line",
 "touches":{"values":["v-..."],"frameworks":["f-..."]},"polarity":"positive","status":"new"}
```

The richest signal is *revealed* judgment (a correction you actually made), not values you
declare in the abstract.

## 2. Harvest  (scripted)

`harvest` mines your existing corpus — notes, cards, work logs, the corrections log — for
passages that already express judgment, scores them, and returns a capped candidate set.
This is how a starved graph catches up on months of expressed-but-uncaptured judgment.

```bash
python cli.py harvest --config <cfg> --json     # feed the candidates to the model step
```

## 3. Distill  (scripted brief → model proposes)

`distill` lays out, per node: the unfilled placeholder edges, the mechanically-derivable
edges (a value ← the frameworks whose `embodies` lists it), and the captured events that
touch it. A model reads this small brief and writes concrete **proposals** — edge fills,
rule promotions, new nodes — to `state/distill-proposals.jsonl` as `status: pending-review`.

```bash
python cli.py distill --config <cfg> --status   # is a distill "due"? (event count vs threshold)
python cli.py distill --config <cfg> --brief     # the brief the model turns into proposals
```

Threshold-triggered: run it when enough new events have accrued, not on a clock.

## 4. Encode  (you — the human gate)

Read the proposals. Approve the ones that are真. Approved proposals become / update node
files in your graph dir; the source events flip `new → distilled`. **No script writes a
node** — encoding is a decision, and the graph is yours.

## Apply  (closes the loop)

The **lens** is the apply step. It matches an output against the graph and returns the frame
set — lead + supports + one wild — each carrying a generator vantage **plus a grounding rider**
(name a party / number / date / first action; no category, standard, or whitepaper as an end).
At synthesis the critic **enforces that gate**: any angle that doesn't reduce to a concrete
move is cut. This is the corpus-grounding/rigor floor made to bite, not just be "carried."

The full pipeline — priors + frames + grounding — *is* the quality bar: a human comparison
scored it **7/10 against 3/10** for a stripped priors-only draft (see `evals/RESULTS.md`). Pick
the lead frame **deliberately** — frame *selection* is the real skill, and a mis-fit frame can
drift a draft into abstraction.

```bash
python cli.py lens --config <cfg> --context "bd proposal partnership channel"
```

Ambient by default (cheap, inline). For a major or make-or-break artifact, run **best-of-N on
top**: a few independent full-pipeline passes (each its own isolated generator run), then a
critic dud-filters and surfaces each one's distinct moves — and **you** keep/merge the winner.
best-of-N is a reliability multiplier against run-to-run variance, not a replacement for the
frames; and the selection is yours, because in the same eval an LLM judge rated the 3/10 draft
≈ the 7/10 one. New corrections from the drafting feed straight back into capture.

## registry  (the manifest)

`registry` is the "what's in my graph" view — nodes, the `embodies` edges, `applies-to`
coverage, and the gaps worth filling (values no framework embodies, dangling edges, nodes
the lens can never pick). Run it whenever you want to see the shape of what you've built.
