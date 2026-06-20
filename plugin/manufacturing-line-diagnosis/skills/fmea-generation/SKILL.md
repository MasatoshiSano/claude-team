---
name: fmea-generation
description: Drafts workshop-ready FMEA/FMECA tables from asset context, component breakdown, and failure history. Use when the user asks for FMEA, FMECA, failure mode analysis, criticality ranking, RPN scoring, or pre-workshop failure mode drafting per IEC 60812 / SAE J1739 style methods.
license: MIT
metadata:
  origin: Rob-Reliability/reliability-skills-for-claude
  author: Joss Bohler / Rob Reliability
---

# FMEA Generation

## When To Use

Use this skill when the user needs a structured FMEA or FMECA draft before a reliability workshop. Typical cases include new asset families, RCM/FMECA campaigns, criticality refresh, and accelerating weeks of manual spreadsheet work into a review-ready starting point.

**You bring:** asset hierarchy, functions, operating context, failure history, OEM data, and scoring judgment.
**Claude brings:** MECE structure, draft failure modes, effects chains, proposed S/O/D with rationale, and ranked output for workshop validation.

## Field-Grade Approach

Build the analysis bottom-up from functions, not from generic templates.

1. **Function first** - every failure mode must tie to a defined function or functional failure.
2. **Component-level MECE** - failure modes at the maintainable item / component level, not vague system labels.
3. **Evidence hierarchy** - site history > OEM / industry data > engineering judgment > AI suggestion. Label each row's evidence source.
4. **Workshop-ready, not workshop-final** - draft for challenge, not for sign-off. Flag low-confidence rows explicitly.
5. **No false precision** - S/O/D scales are ordinal. Do not present RPN as physics.

Reference standards when relevant: IEC 60812, SAE J1739, ISO 14224 (failure taxonomy).

## Workflow

### 1. Frame the analysis

Confirm:

- Asset tag, name, and boundary (what is in / out of scope)
- Analysis type: Design FMEA, Process FMEA, or Equipment FMECA
- Scoring scale (typically 1-10 for S, O, D unless user specifies otherwise)
- Available inputs: BOM, P&ID, SOP, failure history, OEM manual, prior FMEA

If functions are missing, stop and ask for them or offer to run function-definition first at component level.

### 2. Structure the worksheet

Build rows at **component x function x failure mode** granularity.

Required columns (minimum):

| Column | Content |
|---|---|
| Item / Component | Maintainable item from hierarchy |
| Function | What the component must do |
| Failure mode | How the function is lost (use observable, specific language) |
| Failure effect (local) | Effect at component level |
| Failure effect (system) | Effect at asset/system level |
| Cause / mechanism | Initiating cause or failure mechanism |
| S | Severity |
| O | Occurrence |
| D | Detection |
| RPN | S x O x D |
| Current controls | Existing detection/prevention |
| Recommended action | Proposed mitigation |
| Evidence | Site / OEM / judgment / AI-draft |
| Confidence | High / Medium / Low |

### 3. Draft failure modes

For each component:

1. List credible failure modes tied to each function (not generic "fails to operate").
2. Use ISO 14224-style language where helpful (leak, vibration, overheat, seize, etc.).
3. Cross-check against failure history - prioritize modes with site evidence.
4. Add OEM / industry modes the site may not have seen yet, flagged as **Low confidence**.
5. Challenge duplicates and vague modes ("malfunction", "failure") - rewrite or merge.

### 4. Build effects and causes

For each failure mode:

- Trace **local effect -> next-level effect -> end effect** (production, safety, environment).
- Separate **failure mechanism** from **root cause** where the worksheet format allows.
- If safety or environmental consequence is possible, state it explicitly in the system effect column.

### 5. Propose S / O / D

For each row:

- **Severity (S):** worst credible consequence at the defined system boundary. Reference user's scale definitions.
- **Occurrence (O):** rate/likelihood given operating context and history. If no data, state assumption and use conservative O with Low confidence.
- **Detection (D):** how likely current controls catch the failure before consequence. PM, PdM, operator rounds, alarms, trips.

Show brief rationale per score - one line, not an essay.

### 6. Rank and recommend

1. Calculate RPN.
2. Sort by RPN and by Severity (S >= threshold if user defines one).
3. Produce top-N action list (default top 20 or user-specified).
4. Group recommended actions: inspection, PM/PdM, redesign, procedural, spare strategy.
5. List rows that **must not** go to workshop without SME review (Low confidence + high S).

## Output Format

```markdown
# FMEA / FMECA Draft - [Asset Tag / Name]

## Executive Read
[2-3 sentences: scope, row count, top risk themes, workshop readiness]

## Analysis Context
| Field | Value |
|---|---|
| Asset | |
| Boundary | |
| Analysis type | |
| Scoring scale | |
| Data sources used | |
| Rows drafted | |
| High-confidence rows | |
| Low-confidence rows (need SME) | |

## FMEA Table
| Item | Function | Failure mode | Local effect | System effect | Cause | S | O | D | RPN | Current controls | Recommended action | Evidence | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Top Critical Items
| Rank | Failure mode | RPN | Why it matters | Recommended action | Owner suggestion |
|---|---|---|---|---|---|

## Workshop Challenge List
Questions the team must answer before approving scores:
1. [Question]
2. [Question]

## Data Gaps
| Gap | Impact on analysis | How to close |
|---|---|---|

## Assumptions & Limits
- [What Claude assumed]
- [What requires human sign-off]
```

Export as markdown table by default. Offer CSV or Excel-friendly tab-separated format if the user asks.

## Quality Bar

- Do not invent failure history - if data is missing, label rows as AI-draft / Low confidence.
- Do not assign high Severity without understanding safety and production consequence at the defined boundary.
- Do not produce a single generic template reused across unrelated asset classes.
- Every failure mode must map to a function.
- Separate facts (history, OEM) from proposals (scores, new modes).
- End with a workshop challenge list - the output is a draft for human validation.
- Never present the FMEA as approved or audit-ready without explicit user confirmation.

## Example Invocation

```text
Use the fmea-generation skill for tag F-22, an industrial centrifugal fan.
Functions: deliver design airflow, maintain vibration within trip limits, run continuously in dusty environment.
I have 3 years of CMMS history and OEM manual excerpts. Use 1-10 S/O/D scale.
```
