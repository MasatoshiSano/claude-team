---
name: bad-actor-analysis
description: Identifies chronic bad actors from maintenance data and builds a hypothesis register. Use when the user asks for bad actor analysis, chronic failures, top maintainable items, Pareto of breakdowns, or repeat offender review.
license: MIT
metadata:
  origin: Rob-Reliability/reliability-skills-for-claude
  author: Joss Bohler / Rob Reliability
---

# Bad Actor Analysis

## When To Use

Use this skill to find the handful of assets that consume a disproportionate share of your maintenance cost, downtime, and MTBF damage - then decide which deserve an RCA. A few percent of equipment usually drives most of the pain; finding them by hand in a raw CMMS export is half a day of Excel. The AI does the sort/aggregate/Pareto in minutes.

**You bring:** the CMMS export (work orders, costs, dates, downtime, failure codes).
**Claude brings:** cleaning and aggregation, a Pareto of losses, the ranked bad-actor list by cost and by frequency, and a prioritised RCA candidate list with the hypotheses to test.

## Field-Grade Approach

1. **Rank by impact, not noise.** A frequently-failing cheap item may matter less than a rare, catastrophic one. Produce both cost and frequency (and downtime) Paretos and reconcile them.
2. **Aggregate to the right asset level.** Roll work orders up to the equipment unit / maintainable item so the offender is the *asset*, not a single WO.
3. **Clean before you count.** Normalise inconsistent equipment IDs, dedupe, strip non-failure WOs (projects, mods, calibrations) before ranking - or the Pareto is garbage.
4. **Separate symptom from chronic.** Distinguish a one-off expensive event from a *chronic* repeat offender; chronic repeats are the prime RCA targets.
5. **Data quality is a finding.** If 30% of WOs have no failure code or cost, that limitation goes in the output - don't present a confident ranking on bad data.
6. **Hand off, don't solve.** Bad-actor analysis prioritises; the actual investigation goes to the RCA Copilot skill.

Reference: Pareto principle, ISO 14224 failure data structure, standard CMMS WO fields (cost, downtime, failure code).

## Workflow

### 1. Frame and clean

- Identify the columns available: asset ID, WO type, cost (labour + parts), start/finish, downtime, failure code.
- Define the analysis window (e.g. trailing 24 months) and the asset level to aggregate to.
- Exclude non-failure work (capital, mods, routine calibration) unless the user wants total cost of ownership.
- Normalise asset IDs and flag records with missing cost/downtime/code.

### 2. Aggregate per asset

Compute per equipment unit:
- Failure event count and frequency (events/year).
- Total and mean repair cost.
- Total downtime and mean time to repair (MTTR).
- MTBF (where run-time/events allow) - caveat if uptime isn't known.

### 3. Build the Paretos

- Cost Pareto (cumulative % of spend vs assets).
- Frequency Pareto (cumulative % of events vs assets).
- Downtime Pareto where data allows.
- Identify the vital few that cross the ~80% line on each.

### 4. Reconcile and shortlist

- Cross the lists: assets high on cost AND frequency are top bad actors.
- Separate chronic repeats from single large events.
- Produce a ranked bad-actor shortlist with the dominant failure pattern/code per asset.

### 5. Prioritise RCA candidates

- For each top bad actor, state the leading hypothesis from the data (dominant failure code, timing, recurrence) and what to verify.
- Recommend the order to investigate, weighing impact vs. likelihood of a fixable cause.

## Output Format

```markdown
# Bad Actor Analysis - [Site / System], [window]

## Executive Read
[The vital few, what they cost you, and the top 3 RCA candidates]

## Data Scope & Quality
| Field | Value |
|---|---|
| Records analysed | |
| Window | |
| Asset level | |
| Excluded WO types | |
| Missing cost / code / downtime | % flagged |

## Cost Pareto (top assets)
| Rank | Asset | Events | Total cost | % of spend | Cum % |
|---|---|---|---|---|---|

## Frequency Pareto (top assets)
| Rank | Asset | Events/yr | Downtime | MTTR | Dominant failure code |
|---|---|---|---|---|---|

## Bad Actor Shortlist (cost x frequency)
| Asset | Why it's a bad actor | Chronic or one-off | Leading hypothesis | RCA priority |
|---|---|---|---|---|

## RCA Candidates (recommended order)
1. [Asset] - [impact] - [what to verify first]

## Assumptions & Limits
- [Data-quality caveats; what the ranking can't yet tell you]
```

## Quality Bar

- Data is cleaned and non-failure work is excluded before ranking - or the limitation is stated.
- Both cost and frequency (and downtime where possible) views are produced and reconciled.
- Chronic repeat offenders are distinguished from single large events.
- MTBF/MTTR carry caveats when uptime or downtime data is incomplete.
- Data-quality gaps are reported as a finding, not hidden.
- The output prioritises RCA targets; it does not claim to have found root causes.

## Example Invocation

```text
Use the bad-actor-analysis skill on this 24-month work order export (CSV attached).
Columns: equipment, WO type, labour cost, parts cost, downtime hours, failure code, dates.
Give me the cost and frequency Paretos, the top bad actors, and which 3 to RCA first.
```
