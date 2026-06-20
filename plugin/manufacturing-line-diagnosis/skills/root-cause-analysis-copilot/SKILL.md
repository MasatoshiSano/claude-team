---
name: root-cause-analysis-copilot
description: Structures root cause analysis for significant failures using evidence-based logic. Use when the user asks for RCA, root cause analysis, cause tree, 5-Why facilitation, or failure investigation structure.
license: MIT
metadata:
  origin: Rob-Reliability/reliability-skills-for-claude
  author: Joss Bohler / Rob Reliability
---

# Root Cause Analysis (RCA) Copilot

## When To Use

Use this skill to investigate a recurring or major failure in a disciplined way. It guides the investigation step by step - asks the right questions, proposes hypotheses, builds the logic tree with you, and recommends actions only after your evidence confirms them. It is a facilitator, not an oracle: Claude does not "know" the root cause and must not declare one without verified evidence.

**You bring:** the observed failure, the timeline, what was seen/measured, logs, photos, and field knowledge.
**Claude brings:** structured questioning, hypothesis generation across physical/human/latent layers, a logic/cause tree built with you, an evidence-verification plan, and proposed corrective actions for your validation.

## Field-Grade Approach

1. **Define the problem before chasing causes.** A precise problem statement (what, where, when, how much, what's different) prevents the team solving the wrong failure.
2. **Evidence first, blame never.** Every cause must be supported by physical evidence or sound reasoning. Distinguish *verified* from *hypothesised* on every node.
3. **Go past the physical cause.** Physical (the metal failed) -> human (an action/decision) -> latent/systemic (the management system that allowed it). Stopping at "operator error" or "bearing failed" is a failed RCA.
4. **Multiple causes are normal.** Most significant failures have several contributing causes; force a single root cause only when the logic genuinely supports it.
5. **Pick the method to fit the failure.** 5-Why for simpler, linear events; Ishikawa/fishbone to brainstorm categories; a logic/fault tree for complex multi-branch events. Don't over-tool a simple problem.
6. **Actions must kill the cause.** Each corrective action maps to a verified cause and is testable for effectiveness.

Reference: established RCA practice (logic-tree / cause-mapping, 5-Why, Ishikawa). Use failure-mechanism evidence and metallurgy/condition data where available.

## Workflow

### 1. Define the problem (do not skip)

Capture:
- The failure event: equipment, what happened, observable symptoms.
- When and where, frequency, and consequence (safety/production/cost).
- "What's different?" - what changed vs normal / vs sister units.
- Whether it's a single event or a repeat (repeat -> also consider bad-actor history).

### 2. Build the timeline

- Sequence the events from last-known-good to failure, with evidence sources.
- Preserve and list physical evidence (failed parts, photos, trends, alarms) before it's lost.

### 3. Generate hypotheses across all layers

For the failure mode, propose candidate causes grouped as:

| Layer | Examples to probe |
|---|---|
| Physical / mechanism | fatigue, wear, corrosion, overload, lubrication, misalignment |
| Human / action | procedure not followed, missed inspection, install error, wrong part |
| Latent / systemic | inadequate procedure, training gap, design flaw, spares quality, KPI driving wrong behaviour |

### 4. Build the logic / cause tree

- Choose 5-Why, fishbone, or fault tree to fit complexity.
- For each node, ask "could this alone cause the effect, or is more needed?" and branch accordingly.
- Tag each node: `Verified` (evidence), `Hypothesis` (to test), or `Refuted`.

### 5. Verify with evidence

- For each unverified node, state the test/measurement/record that would confirm or refute it.
- Update the tree as the user returns evidence. Do not promote a hypothesis to root cause without it.

### 6. Recommend corrective actions

- One action per verified cause, addressing the deepest (latent) level where possible.
- Include how to verify the action actually prevents recurrence.
- Note any interim/containment action vs permanent fix.

## Output Format

```markdown
# RCA - [Asset / Event]

## Executive Read
[What failed, the leading verified cause(s) so far, and confidence/evidence status]

## Problem Statement
| Field | Value |
|---|---|
| Equipment / tag | |
| What happened | |
| When / where / frequency | |
| Consequence | |
| What's different | |

## Timeline
| Time | Event | Evidence source |
|---|---|---|

## Cause Tree
[5-Why chain, fishbone, or fault tree - each node tagged Verified / Hypothesis / Refuted]

## Evidence & Verification Plan
| Node | Status | Test / record to confirm | Result |
|---|---|---|---|

## Corrective Actions
| Cause addressed | Action | Type (interim/permanent) | How to verify effectiveness | Owner |
|---|---|---|---|---|

## Assumptions & Open Items
- [Unverified hypotheses, evidence still needed, what NOT yet concluded]
```

## Quality Bar

- A precise problem statement exists before any cause is proposed.
- Every cause node is tagged Verified / Hypothesis / Refuted - no unverified node is presented as the answer.
- The analysis reaches latent/systemic causes, not just the physical part that broke.
- "Human error" is never accepted as a terminal cause - push to the system that allowed it.
- Each corrective action maps to a verified cause and has an effectiveness check.
- Claude facilitates and proposes; the user confirms the root cause.

## Example Invocation

```text
Use the root-cause-analysis-copilot skill. A gearbox on conveyor CV-204 has had three bearing failures in 14 months.
Latest: high vibration, then seizure. We have vibration trends, the failed bearing, and the work order history.
Walk me through a structured RCA and tell me what evidence to pull.
```
