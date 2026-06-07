---
type: method
id: m-bd-partnership-call
name: BD partnership call
task-kind: bd/partnership/go-no-go
status: draft
deliverable: a 05 Decisions/ record (go / no-go / hold / downgrade / terminate) with rationale, reversibility, and a review date
calls-skills: [meeting-note, distill, relation-map, localize-cn]
grounds-in: [v-resource-exchange, f-value-mechanism, f-strategic-systems]
precipitated-from: the BD-decision class in 05 Decisions/ (~11 records 2026-04..06; 2 stamped as instances so far — 雷电, 小鹏)
created: 2026-06-06
created-by: claude
---

# BD partnership call

## Method
Templates an **{{USER_NAME}}/org-owned partnership decision** — a platform/vendor/cross-industry deal that needs a go / no-go / hold / downgrade / terminate call. A run produces one immutable `05 Decisions/` record (per [[09 Rules/decisions.md]]) and wires it to the entities it concerns. Value-free: the steps *invoke* resource-exchange and value-mechanism judgment ([[v-resource-exchange]], [[f-value-mechanism]]); they do not encode it. The call itself is human-owned — this scaffolds the path to it, the operator makes it.

## Steps (DAG)

### frame_offer
**after:** —
**calls:** meeting-note, distill
**reads:** source note / meeting / conversation
**writes:** the situation + what each side is putting on the table
State the opportunity or the stuck arrangement, and concretely what we give and what we get. Strip nothing yet. (乐元素: bilateral intel; 雷电: PC→APK emulator pitch; 小鹏: 一年使用权.)

### model_exchange
**after:** frame_offer
**calls:** —
Decompose **supply vs demand** — what we offer vs what we want them to do — and ask whether it's a *recirculating loop* (both sides compound) or a *one-time spend*. This is [[v-resource-exchange]] / [[f-value-mechanism]] applied. Platform-level swaps need an equivalent commitment signal. (B站: 1000万 全量 ↔ 头部位 + 几百万创作者资源.)

### check_constraints
**after:** frame_offer
**calls:** —
Run the hard gates that *cap* the option space before you weigh anything: **legal/法务**, **budget/预算**, **🔴 lane-isolation** ({{PROJECT_A}} ↔ {{ORG_B}} / {{ORG_A}} / {{ORG_D}} never cross), **confidentiality/红线**. A veto here removes options; it does not get traded away. (小鹏: 法务 + 预算 double-veto.)

### enumerate_options
**after:** model_exchange, check_constraints
**calls:** —
List ≥2 real options — typically **aggressive (full)** vs **conservative (fallback floor / exit)**. Always carry a *minimum-viable-residual* fallback so a hard veto doesn't mean zero. (小鹏: 全方案 vs 单场试玩会兜底; 雷电: 推进 vs 终止.)

### classify_reversibility
**after:** enumerate_options
**calls:** —
Tag each option **one-way** vs **reversible**. One-way (irreversible spend,公司级预算占用) is decided slower and weighed heavier; reversible (MOU, no contract lock) can move fast and pause anytime. Sets the decision's `reversibility` field. (B站 1000万 = one-way; 乐元素 MOU = reversible.)

### make_call
**after:** enumerate_options, classify_reversibility
**calls:** —
Make the go / no-go / hold / downgrade / terminate call, stating the **trade-off knowingly accepted**. Default to early stop-loss over sunk-cost when the value-prop is structurally mismatched; default to preserving the minimum-viable residual when the full deal is vetoed. (雷电: 及早止损; 小鹏: 止损保残值.)

### record_and_wire
**after:** make_call
**calls:** relation-map, localize-cn
**writes:** 05 Decisions/YYYY-MM-DD-<slug>.md
Write the immutable record from `07 Templates/decision.md` (headings verbatim — `reflect.py` parses them), set `reversibility` + a `review_on` date (sooner for one-way), **stamp `method: m-bd-partnership-call`** (closes the review→Memory loop), link entities **outbound + lane-isolated** via relation-map, supersede any prior call both-ways. CN-audience business decisions get localize-cn.

## Memory
- 2026-06-05 — When a full deal hits a hard veto (法务/预算), don't push it; **downgrade to the minimum-viable residual + a resource-exchange fallback**. Preserves残值 instead of going to zero. [[05 Decisions/2026-05-29-小鹏合作降级为单场试玩会]]
- 2026-06-05 — **One-way calls demand a fallback floor and decide slower**; a公司级 irreversible spend is justified only by a platform-level resource swap with an equivalent commitment signal. [[05 Decisions/2026-05-19-B站全量投放1000万]]
- 2026-06-05 — **Value-prop / product-architecture mismatch → early stop-loss beats sunk-cost.** Terminate the specific vendor, not the underlying capability (re-evaluate the need later, a different way). [[05 Decisions/2026-05-14-雷电模拟器合作终止]]
- 2026-06-05 — **Non-direct-competitor intel exchange = low-risk / high-info-density**; keep it to high层, MOU not contract, pausable anytime — exposure stays controlled. [[05 Decisions/2026-04-27-乐元素常态化情报互通]]
