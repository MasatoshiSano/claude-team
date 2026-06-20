---
name: cmms-data-analysis-strategy
description: Uses CMMS work order history to challenge and adjust maintenance plans and strategy. Use when the user asks for CMMS-driven strategy review, PM plan tuning from work orders, maintenance strategy feedback from CMMS data, or evidence-based PM/interval changes.
---

# CMMS Data Analysis – Strategy

## When To Use

Use this skill when your **maintenance plan and strategy no longer match what CMMS history is showing on site** — repeat failures despite PMs, calendar tasks with no failure linkage, rising corrective work on "maintained" assets, or intervals that look arbitrary against actual breakdown timing.

This is not a generic data-cleaning exercise. It closes the loop between **field history and maintenance decisions**: what to keep, cut, merge, add, or retime — with the work-order evidence behind each call.

Typical cases: annual PM plan review backed by CMMS, challenging a time-based overhaul after repeat breakdowns, or retuning strategy after a bad-actor shortlist.

**You bring:** CMMS export (work orders, PM history, failure codes, dates, costs, downtime) and the current PM plan / strategy view (even a rough list).  
**Claude brings:** data-quality sanity check, plan-vs-reality comparison, evidence-backed strategy adjustments, and clear hand-offs to PM optimization, P-F sizing, RCA, or bad-actor skills where needed.

## Field-Grade Approach

1. **Data quality gates the strategy call.** Before recommending changes, assess whether the CMMS export is complete enough to trust. A strategy change on 40%-coded failure data needs a caveat, not false confidence.
2. **Plan vs reality, not just KPIs.** Compare scheduled tasks, intervals, and assumed failure modes against what actually happened — repeat failures, PM compliance gaps, breakdown clusters, and rising corrective load.
3. **Separate work types.** PM, corrective, breakdown, and project work must be split before any MTBF, repeat-failure, or PM-effectiveness read.
4. **Every adjustment needs evidence.** Each keep / cut / merge / add / retime call cites the work-order pattern behind it — not generic RCM theory.
5. **Strategy before cleanup.** Prefer actionable maintenance changes the team can implement now; CMMS taxonomy fixes are secondary unless bad coding blocks the strategy read.
6. **Hand off cleanly.** Route deep RCA, Weibull/life-data, fake-PM kills, or P-F interval sizing to the relevant skill once the strategy gap is framed.

Reference: ISO 14224 (failure data and coding), RCM/PM review practice, standard CMMS WO structure.

## Workflow

### 1. Frame the question

Confirm:
- Asset scope (single asset, system, site area, fleet).
- Current PM plan / strategy in scope (tasks, intervals, tactics).
- CMMS window and export fields available.
- The decision to support (plan review, interval challenge, strategy reset, bad-actor follow-up).

### 2. Profile and sanity-check the CMMS data

| Dimension | Check |
|---|---|
| Completeness | % missing on equipment ID, WO type, failure code, dates |
| Consistency | duplicate/variant asset IDs and codes |
| Work-type split | PM vs corrective vs breakdown vs project |
| PM compliance | scheduled vs completed PMs where trackable |

Flag what can and cannot be concluded from the data.

### 3. Compare plan vs CMMS reality

For each asset or failure theme, look for:
- Repeat failures after PM or inspection.
- Calendar PMs with no linked failure reduction.
- Breakdowns clustering between PMs (interval too long? wrong task?).
- Rising corrective cost or frequency on nominally "maintained" assets.
- Missing tasks for dominant failure modes in the history.

### 4. Draft strategy adjustments

For each finding, propose a concrete call:

| Call | When to use |
|---|---|
| Keep | PM/task still matches history and risk |
| Cut | Low-value or non-linked calendar work |
| Merge | Overlapping tasks on the same failure mechanism |
| Add | Dominant failure mode with no covering task |
| Retime | Interval misaligned with breakdown/PM timing evidence |

State assumptions and what field validation is still required.

### 5. Output the review

- Executive read: is the current plan fit for purpose?
- Evidence table: finding → WO pattern → recommended change.
- Priority shortlist: what to change first.
- Hand-offs: RCA, Weibull, PM optimization, P-F sizing, bad actor.

## Output Format

```markdown
# CMMS Data Analysis – Strategy — [Site / Scope], [window]

## Executive Read
[Is the current plan/strategy fit for purpose? Headline gaps and top 3 changes]

## Data Confidence
| Field / issue | Impact on conclusions |
|---|---|
[+ completeness, coding, PM compliance caveats]

## Plan vs Reality
| Asset / theme | Current plan | What CMMS shows | Gap |
|---|---|---|---|

## Strategy Adjustments
| Call (keep/cut/merge/add/retime) | Task / tactic | Evidence from CMMS | Priority |
|---|---|---|---|

## Intervals & Tactics To Revisit
- [Tasks needing retime, tactic change, or deeper analysis]

## Hand-offs
- [RCA, Weibull, PM optimization, P-F sizing, bad actor — as needed]

## Assumptions & Limits
- [What the data could not prove; what needs field validation]
```

## Quality Bar

- Data-confidence caveats precede any strategy recommendation.
- Work types are separated before repeat-failure or PM-effectiveness reads.
- Every adjustment cites CMMS evidence, not generic best practice alone.
- Outputs are decision-ready: keep / cut / merge / add / retime with priority.
- CMMS cleanup is secondary unless coding blocks the strategy read.
- No fabricated metrics or invented work-order patterns.

## Example Invocation

```text
Use the cmms-data-analysis-strategy skill on this 3-year CMMS export plus our current PM plan for the cooling-water pump fleet.
The plan says quarterly vibration routes and annual seal replacement, but we keep getting seal failures.
Tell me what the history supports, what to cut or retime, and what needs RCA or Weibull follow-up.
```
