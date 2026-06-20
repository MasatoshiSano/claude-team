---
name: pm-optimization
description: Reviews preventive maintenance tasks and flags weak or calendar-driven PMs. Use when the user asks for PM optimization, PM review, fake PM, calendar task rationalization, or PM effectiveness challenge.
license: MIT
metadata:
  origin: Rob-Reliability/reliability-skills-for-claude
  author: Joss Bohler / Rob Reliability
---

# PM Optimization (Fake-PM Killer)

## When To Use

Use this skill to purge a maintenance plan of tasks that aren't tied to any real failure mode - the "fake PMs" that survive only because they've always been there. Cross-checking every PM line against a credible failure mode is mechanical, exhausting work that the AI does fast and consistently. Typical cases: a bloated PM program, a PM cost-reduction drive, or a plan inherited from an OEM template nobody validated.

**You bring:** the existing PM plan (CMMS export), and known failure modes (ideally from FMEA / history).
**Claude brings:** a task-by-task cross-check against failure modes, identification of fake/duplicate/intrusive PMs, and a justified keep / cut / change kill-list.

## Field-Grade Approach

1. **Every PM must target a failure mode.** A task that doesn't address a credible failure mode is a candidate for deletion - that's the core test.
2. **Calendar != justified.** A monthly/annual frequency inherited with no failure basis is a red flag, not evidence the task is needed.
3. **Beware intrusive maintenance.** PMs that open up healthy equipment can *induce* failures (infant mortality). Challenge "overhaul every X" tasks where the failure pattern is random (beta approx 1).
4. **Effectiveness, not just existence.** Even a task tied to a mode must be applicable and worth its cost - same applicable + effective test as RCM.
5. **Consolidate and re-route.** Merge duplicate/overlapping tasks; convert calendar tasks to on-condition where a P-F interval exists; route hidden-function checks to failure-finding.
6. **Don't cut blind on safety.** Any PM touching a safety/regulatory function is kept or escalated for review, not cut on economics alone.

Reference: RCM task logic (SAE JA1011/JA1012), P-F concept for calendar->on-condition conversion, failure-pattern reasoning (Nowlan & Heap).

## Workflow

### 1. Inventory the PM plan

- List every PM task: description, equipment, frequency, type (calendar/runtime/condition), duration/cost, intrusive or not.
- Note the stated reason/origin if available (OEM, regulatory, legacy, RCM-derived).

### 2. Map tasks to failure modes

For each task, ask:
- Which credible failure mode does this address?
- Is that mode real for this asset (history/FMEA), or assumed?
- Does the task actually detect/prevent that mode (applicable)?

Tag each task: `Mode-linked`, `Weak link`, `No link (fake PM)`, `Duplicate`, `Regulatory/safety`.

### 3. Classify and decide

| Tag | Default decision |
|---|---|
| Mode-linked + effective | Keep (optionally re-interval) |
| Calendar but P-F interval exists | Change -> on-condition |
| Intrusive on random-failure item | Cut or reduce (induces failures) |
| Duplicate / overlapping | Merge |
| No link (fake PM) | Cut - unless regulatory |
| Regulatory / safety | Keep / escalate, never economic-cut |

### 4. Build the kill-list with justification

- For every cut/change, give the reason and the residual risk (what mode, if any, is now uncovered).
- For keeps, confirm the failure mode and whether the interval should change.

### 5. Quantify the win and the risk

- Estimate labour-hours / cost freed (where data allows).
- List any new risk created by cuts and what would mitigate it (e.g. add an operator round, condition check).

## Output Format

```markdown
# PM Optimization Review - [Asset / System]

## Executive Read
[How many PMs reviewed, how many fake/duplicate/intrusive, estimated hours or cost freed, any safety items held]

## Review Scope
| Field | Value |
|---|---|
| PM tasks reviewed | |
| Failure-mode source | |
| Period / asset scope | |

## PM Review Table
| PM task | Freq | Type | Failure mode addressed | Link strength | Decision (keep/cut/change/merge) | Residual risk | Justification |
|---|---|---|---|---|---|---|---|

## Kill-List (cut / change)
| PM task | Action | Why | Risk introduced | Mitigation |
|---|---|---|---|---|

## Estimated Impact
- Hours/cost freed: ...
- New risks to accept/mitigate: ...

## Safety / Regulatory Hold
- [Tasks not cut on economics - flagged for separate review]

## Assumptions & Limits
- [Where failure-mode linkage was assumed; data to confirm before deletion]
```

## Quality Bar

- Every task is mapped (or explicitly not mapped) to a failure mode before any decision.
- Fake PMs are justified for deletion with their residual risk stated - not cut silently.
- Intrusive PMs on random-failure items are challenged for inducing failures.
- Calendar tasks with a P-F interval are converted to on-condition, not just kept.
- Safety/regulatory tasks are never economic-cut; they're held for review.
- Cost/hours savings are estimated only where data supports it, and labelled as estimates.

## Example Invocation

```text
Use the pm-optimization skill on this 40-line PM plan for a centrifugal pump (CSV attached).
Failure modes from our FMEA are in the second tab. Flag the fake PMs, the intrusive ones, and the duplicates,
and give me a kill-list with the risk of each cut.
```
