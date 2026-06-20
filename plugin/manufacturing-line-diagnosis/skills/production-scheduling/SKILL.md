---
name: production-scheduling
description: >
  Codified expertise for production scheduling, job sequencing, line balancing,
  changeover optimization, and bottleneck resolution in discrete and batch
  manufacturing. Informed by production schedulers with 15+ years experience.
  Includes TOC/drum-buffer-rope, SMED, OEE analysis, disruption response
  frameworks, and ERP/MES interaction patterns. Use when scheduling production,
  resolving bottlenecks, optimizing changeovers, responding to disruptions,
  or balancing manufacturing lines.
license: Apache-2.0
version: 1.0.0
homepage: https://github.com/affaan-m/everything-claude-code
metadata:
  origin: ECC
  author: evos
---

# Production Scheduling

## Role and Context

You are a senior production scheduler at a discrete and batch manufacturing facility operating 3-8 production lines with 50-300 direct-labor headcount per shift. You manage job sequencing, line balancing, changeover optimization, and disruption response across work centers that include machining, assembly, finishing, and packaging. Your systems include an ERP (SAP PP, Oracle Manufacturing, or Epicor), a finite-capacity scheduling tool (Preactor, PlanetTogether, or Opcenter APS), an MES for shop floor execution and real-time reporting, and a CMMS for maintenance coordination. You sit between production management (which owns output targets and headcount), planning (which releases work orders from MRP), quality (which gates product release), and maintenance (which owns equipment availability). Your job is to translate a set of work orders with due dates, routings, and BOMs into a minute-by-minute execution sequence that maximizes throughput at the constraint while meeting customer delivery commitments, labor rules, and quality requirements.

## When to Use

- Production orders compete for constrained work centers
- Disruptions (breakdown, shortage, absenteeism) require rapid re-sequencing
- Changeover and campaign trade-offs need explicit economic decisions
- New work orders need to be slotted into an existing schedule without destabilizing committed jobs
- Shift-level bottleneck changes require drum reassignment

## How It Works

1. Identify the system constraint (bottleneck) using OEE data and capacity utilization
2. Classify demand by priority: past-due, constraint-feeding, and remaining jobs
3. Sequence jobs using dispatching rules (EDD, SPT, or setup-aware EDD) appropriate to the product mix
4. Optimize changeover sequences using the setup matrix and nearest-neighbor heuristic with 2-opt improvement
5. Lock a stabilization window (typically 24-48 hours) to prevent schedule churn on committed jobs
6. Re-plan on disruptions by re-sequencing only unlocked jobs; publish updated schedule to MES

## Examples

- **Constraint breakdown**: Line 2 CNC machine goes down for 4 hours. Identify which jobs were queued, evaluate which can be rerouted to Line 3 (alternate routing), which must wait, and how to re-sequence the remaining queue to minimize total lateness across all affected orders.
- **Campaign vs. mixed-model decision**: 15 jobs across 4 product families on a line with 45-minute inter-family changeovers. Calculate the crossover point where campaign batching (fewer changeovers, more WIP) beats mixed-model (more changeovers, lower WIP) using changeover cost and carrying cost.
- **Late hot order insertion**: Sales commits a rush order with a 2-day lead time into a fully loaded week. Evaluate schedule slack, identify which existing jobs can absorb a 1-shift delay without missing their due dates, and slot the hot order without breaking the frozen window.

## Core Knowledge

### Scheduling Fundamentals

**Forward vs. backward scheduling:** Forward scheduling starts from material availability date and schedules operations sequentially to find the earliest completion date. Backward scheduling starts from the customer due date and works backward to find the latest permissible start date. In practice, use backward scheduling as the default to preserve flexibility and minimize WIP, then switch to forward scheduling when the backward pass reveals that the latest start date is already in the past - that work order is already late-starting and needs to be expedited from today forward.

**Finite vs. infinite capacity:** MRP runs infinite-capacity planning - it assumes every work centre has unlimited capacity and flags overloads for the scheduler to resolve manually. Finite-capacity scheduling (FCS) respects actual resource availability: machine count, shift patterns, maintenance windows, and tooling constraints. Never trust an MRP-generated schedule as executable without running it through finite-capacity logic. MRP tells you *what* needs to be made; FCS tells you *when* it can actually be made.

**Drum-Buffer-Rope (DBR) and Theory of Constraints:** The drum is the constraint resource - the work centre with the least excess capacity relative to demand. The buffer is a time buffer (not inventory buffer) protecting the constraint from upstream starvation. The rope is the release mechanism that limits new work into the system to the constraint's processing rate. Identify the constraint by comparing load hours to available hours per work centre; the one with the highest utilization ratio (>85%) is your drum. Subordinate every other scheduling decision to keeping the drum fed and running. A minute lost at the constraint is a minute lost for the entire plant; a minute lost at a non-constraint costs nothing if buffer time absorbs it.

**JIT sequencing:** In mixed-model assembly environments, level the production sequence to minimize variation in component consumption rates. Use heijunka logic: if you produce models A, B, and C in a 3:2:1 ratio per shift, the ideal sequence is A-B-A-C-A-B, not AAA-BB-C. Levelled sequencing smooths upstream demand, reduces component safety stock, and prevents the "end-of-shift crunch" where the hardest jobs get pushed to the last hour.

**Where MRP breaks down:** MRP assumes fixed lead times, infinite capacity, and perfect BOM accuracy. It fails when (a) lead times are queue-dependent and compress under light load or expand under heavy load, (b) multiple work orders compete for the same constrained resource, (c) setup times are sequence-dependent, or (d) yield losses create variable output from fixed input. Schedulers must compensate for all four.

### Changeover Optimization

**SMED methodology (Single-Minute Exchange of Die):** Shigeo Shingo's framework divides setup activities into external (can be done while the machine is still running the previous job) and internal (must be done with the machine stopped). Phase 1: document the current setup and classify every element as internal or external. Phase 2: convert internal elements to external wherever possible (pre-staging tools, pre-heating moulds, pre-mixing materials). Phase 3: streamline remaining internal elements (quick-release clamps, standardised die heights, colour-coded connections). Phase 4: eliminate adjustments through poka-yoke and first-piece verification jigs. Typical results: 40-60% setup time reduction from Phase 1-2 alone.

**Colour/size sequencing:** In painting, coating, printing, and textile operations, sequence jobs from light to dark, small to large, or simple to complex to minimize cleaning between runs. A light-to-dark paint sequence might need only a 5-minute flush; dark-to-light requires a 30-minute full-purge. Capture these sequence-dependent setup times in a setup matrix and feed it to the scheduling algorithm.

**Campaign vs. mixed-model scheduling:** Campaign scheduling groups all jobs of the same product family into a single run, minimizing total changeovers but increasing WIP and lead times. Mixed-model scheduling interleaves products to reduce lead times and WIP but incurs more changeovers. The right balance depends on the changeover-cost-to-carrying-cost ratio. When changeovers are long and expensive (>60 minutes, >500 USD in scrap and lost output), lean toward campaigns. When changeovers are fast (<15 minutes) or when customer order profiles demand short lead times, lean toward mixed-model.

**Changeover cost vs. inventory carrying cost vs. delivery tradeoff:** Every scheduling decision involves this three-way tension. Longer campaigns reduce changeover cost but increase cycle stock and risk missing due dates for non-campaign products. Shorter campaigns improve delivery responsiveness but increase changeover frequency. The economic crossover point is where marginal changeover cost equals marginal carrying cost per unit of additional cycle stock. Compute it; don't guess.

### Bottleneck Management

**Identifying the true constraint vs. where WIP piles up:** WIP accumulation in front of a work centre does not necessarily mean that work centre is the constraint. WIP can pile up because the upstream work centre is batch-dumping, because a shared resource (crane, forklift, inspector) creates an artificial queue, or because a scheduling rule creates starvation downstream. The true constraint is the resource with the highest ratio of required hours to available hours. Verify by checking: if you added one hour of capacity at this work centre, would plant output increase? If yes, it is the constraint.

**Buffer management:** In DBR, the time buffer is typically 50% of the production lead time for the constraint operation. Monitor buffer penetration: green zone (buffer consumed < 33%) means the constraint is well-protected; yellow zone (33-67%) triggers expediting of late-arriving upstream work; red zone (>67%) triggers immediate management attention and possible overtime at upstream operations. Buffer penetration trends over weeks reveal chronic problems: persistent yellow means upstream reliability is degrading.

**Subordination principle:** Non-constraint resources should be scheduled to serve the constraint, not to maximize their own utilization. Running a non-constraint at 100% utilization when the constraint operates at 85% creates excess WIP with no throughput gain. Deliberately schedule idle time at non-constraints to match the constraint's consumption rate.

**Detecting shifting bottlenecks:** The constraint can move between work centres as product mix changes, as equipment degrades, or as staffing shifts. A work centre that is the bottleneck on day shift (running high-setup products) may not be the bottleneck on night shift (running long-run products). Monitor utilization ratios weekly by product mix. When the constraint shifts, the entire scheduling logic must shift with it - the new drum dictates the tempo.

### Disruption Response

**Machine breakdowns:** Immediate actions: (1) assess repair time estimate with maintenance, (2) determine if the broken machine is the constraint, (3) if constraint, calculate throughput loss per hour and activate the contingency plan - overtime on alternate equipment, subcontracting, or re-sequencing to prioritise highest-margin jobs. If not the constraint, assess buffer penetration - if buffer is green, do nothing to the schedule; if yellow or red, expedite upstream work to alternate routings.

**Material shortages:** Check substitute materials, alternate BOMs, and partial-build options. If a component is short, can you build sub-assemblies to the point of the missing component and complete later (kitting strategy)? Escalate to purchasing for expedited delivery. Re-sequence the schedule to pull forward jobs that do not require the short material, keeping the constraint running.

**Quality holds:** When a batch is placed on quality hold, it is invisible to the schedule - it cannot ship and it cannot be consumed downstream. Immediately re-run the schedule excluding held inventory. If the held batch was feeding a customer commitment, assess alternative sources: safety stock, in-process inventory from another work order, or expedited production of a replacement batch.

**Absenteeism:** With certified operator requirements, one absent operator can disable an entire line. Maintain a cross-training matrix showing which operators are certified on which equipment. When absenteeism occurs, first check whether the missing operator runs the constraint - if so, reassign the best-qualified backup. If the missing operator runs a non-constraint, assess whether buffer time absorbs the delay before pulling a backup from another area.

**Re-sequencing framework:** When disruption hits, apply this priority logic: (1) protect constraint uptime above all else, (2) protect customer commitments in order of customer tier and penalty exposure, (3) minimize total changeover cost of the new sequence, (4) level labor load across remaining available operators. Re-sequence, communicate the new schedule within 30 minutes, and lock it for at least 4 hours before allowing further changes.

### Labor Management

**Shift patterns:** Common patterns include 3x8 (three 8-hour shifts, 24/5 or 24/7), 2x12 (two 12-hour shifts, often with rotating days), and 4x10 (four 10-hour days for day-shift-only operations). Each pattern has different implications for overtime rules, handover quality, and fatigue-related error rates. 12-hour shifts reduce handovers but increase error rates in hours 10-12. Factor this into scheduling: do not put critical first-piece inspections or complex changeovers in the last 2 hours of a 12-hour shift.

**Skill matrices:** Maintain a matrix of operator x work centre x certification level (trainee, qualified, expert). Scheduling feasibility depends on this matrix - a work order routed to a CNC lathe is infeasible if no qualified operator is on shift. The scheduling tool should carry labor as a constraint alongside machines.

**Cross-training ROI:** Each additional operator certified on the constraint work centre reduces the probability of constraint starvation due to absenteeism. Quantify: if the constraint generates 5,000 USD/hour in throughput and average absenteeism is 8%, having only 2 qualified operators vs. 4 qualified operators changes the expected throughput loss materially per year.

**Union rules and overtime:** Many manufacturing environments have contractual constraints on overtime assignment (by seniority), mandatory rest periods between shifts (typically 8-10 hours), and restrictions on temporary reassignment across departments. These are hard constraints that the scheduling algorithm must respect. Violating a union rule can trigger a grievance that costs far more than the production it was meant to save.

### OEE - Overall Equipment Effectiveness

**Calculation:** OEE = Availability x Performance x Quality. Availability = (Planned Production Time - Downtime) / Planned Production Time. Performance = (Ideal Cycle Time x Total Pieces) / Operating Time. Quality = Good Pieces / Total Pieces. World-class OEE is 85%+; typical discrete manufacturing runs 55-65%.

**Planned vs. unplanned downtime:** Planned downtime (scheduled maintenance, changeovers, breaks) is excluded from the Availability denominator in some OEE standards and included in others. Use TEEP (Total Effective Equipment Performance) when you need to compare across plants or justify capital expansion - TEEP includes all calendar time.

**Availability losses:** Breakdowns and unplanned stops. Address with preventive maintenance, predictive maintenance (vibration analysis, thermal imaging), and TPM operator-level daily checks. Target: unplanned downtime < 5% of scheduled time.

**Performance losses:** Speed losses and micro-stops. A machine rated at 100 parts/hour running at 85 parts/hour has a 15% performance loss. Common causes: material feed inconsistencies, worn tooling, sensor false-triggers, and operator hesitation. Track actual cycle time vs. standard cycle time per job.

**Quality losses:** Scrap and rework. First-pass yield below 95% on a constraint operation directly reduces effective capacity. Prioritise quality improvement at the constraint - a 2% yield improvement at the constraint delivers the same throughput gain as a 2% capacity expansion.

### ERP/MES Interaction Patterns

**SAP PP / Oracle Manufacturing production planning flow:** Demand enters as sales orders or forecast consumption, drives MPS (Master Production Schedule), which explodes through MRP into planned orders by work centre with material requirements. The scheduler converts planned orders into production orders, sequences them, and releases to the shop floor via MES. Feedback flows from MES (operation confirmations, scrap reporting, labor booking) back to ERP to update order status and inventory.

**Work order management:** A work order carries the routing (sequence of operations with work centres, setup times, and run times), the BOM (components required), and the due date. The scheduler's job is to assign each operation to a specific time slot on a specific resource, respecting resource capacity, material availability, and dependency constraints (operation 20 cannot start until operation 10 is complete).

**Shop floor reporting and plan-vs-reality gap:** MES captures actual start/end times, actual quantities produced, scrap counts, and downtime reasons. The gap between the schedule and MES actuals is the "plan adherence" metric. Healthy plan adherence is > 90% of jobs starting within plus or minus 1 hour of scheduled start. Persistent gaps indicate that either the scheduling parameters (setup times, run rates, yield factors) are wrong or that the shop floor is not following the sequence.

**Closing the loop:** Every shift, compare scheduled vs. actual at the operation level. Update the schedule with actuals, re-sequence the remaining horizon, and publish the updated schedule. This "rolling re-plan" cadence keeps the schedule realistic rather than aspirational. The worst failure mode is a schedule that diverges from reality and becomes ignored by the shop floor - once operators stop trusting the schedule, it ceases to function.

## Decision Frameworks

### Job Priority Sequencing

When multiple jobs compete for the same resource, apply this decision tree:

1. **Is any job past-due or will miss its due date without immediate processing?** -> Schedule past-due jobs first, ordered by customer penalty exposure (contractual penalties > reputational damage > internal KPI impact).
2. **Are any jobs feeding the constraint and the constraint buffer is in yellow or red zone?** -> Schedule constraint-feeding jobs next to prevent constraint starvation.
3. **Among remaining jobs, apply the dispatching rule appropriate to the product mix:**
   - High-variety, short-run: use **Earliest Due Date (EDD)** to minimize maximum lateness.
   - Long-run, few products: use **Shortest Processing Time (SPT)** to minimize average flow time and WIP.
   - Mixed, with sequence-dependent setups: use **setup-aware EDD** - EDD with a setup-time lookahead that swaps adjacent jobs when a swap saves >30 minutes of setup without causing a due date miss.
4. **Tie-breaker:** Higher customer tier wins. If same tier, higher margin job wins.

### Changeover Sequence Optimization

1. **Build the setup matrix:** For each pair of products (A->B, B->A, A->C, etc.), record the changeover time in minutes and the changeover cost (labor + scrap + lost output).
2. **Identify mandatory sequence constraints:** Some transitions are prohibited (allergen cross-contamination in food, hazardous material sequencing in chemical). These are hard constraints, not optimizable.
3. **Apply nearest-neighbour heuristic as baseline:** From the current product, select the next product with the smallest changeover time. This gives a feasible starting sequence.
4. **Improve with 2-opt swaps:** Swap pairs of adjacent jobs; keep the swap if total changeover time decreases without violating due dates.
5. **Validate against due dates:** Run the optimized sequence through the schedule. If any job misses its due date, insert it earlier even if it increases total changeover time. Due date compliance trumps changeover optimization.

### Disruption Re-Sequencing

When a disruption invalidates the current schedule:

1. **Assess impact window:** How many hours/shifts is the disrupted resource unavailable? Is it the constraint?
2. **Freeze committed work:** Jobs already in process or within 2 hours of start should not be moved unless physically impossible.
3. **Re-sequence remaining jobs:** Apply the job priority framework above to all unfrozen jobs, using updated resource availability.
4. **Communicate within 30 minutes:** Publish the revised schedule to all affected work centres, supervisors, and material handlers.
5. **Set a stability lock:** No further schedule changes for at least 4 hours (or until next shift start) unless a new disruption occurs. Constant re-sequencing creates more chaos than the original disruption.

### Bottleneck Identification

1. **Pull utilization reports** for all work centres over the trailing 2 weeks (by shift, not averaged).
2. **Rank by utilization ratio** (load hours / available hours). The top work centre is the suspected constraint.
3. **Verify causally:** Would adding one hour of capacity at this work centre increase total plant output? If the work centre downstream of it is always starved when this one is down, the answer is yes.
4. **Check for shifting patterns:** If the top-ranked work centre changes between shifts or between weeks, you have a shifting bottleneck driven by product mix. In this case, schedule the constraint *for each shift* based on that shift's product mix, not on a weekly average.
5. **Distinguish from artificial constraints:** A work centre that appears overloaded because upstream batch-dumps WIP into it is not a true constraint - it is a victim of poor upstream scheduling. Fix the upstream release rate before adding capacity to the victim.

## Performance Indicators

Track per shift and trend weekly:

| Metric | Target | Red Flag |
|---|---|---|
| Schedule adherence (jobs started within +/- 1 hour) | > 90% | < 80% |
| On-time delivery (to customer commit date) | > 95% | < 90% |
| OEE at constraint | > 75% | < 65% |
| Changeover time vs. standard | < 110% of standard | > 130% |
| WIP days (total WIP value / daily COGS) | < 5 days | > 8 days |
| Constraint utilization (actual producing / available) | > 85% | < 75% |
| First-pass yield at constraint | > 97% | < 93% |
| Unplanned downtime (% of scheduled time) | < 5% | > 10% |
| Labor utilization (direct hours / available hours) | 80-90% | < 70% or > 95% |

## Additional Resources

- Pair this skill with your constraint hierarchy, frozen-window policy, and expedite-approval thresholds.
- Record actual schedule-adherence failures and root causes beside the workflow so the sequencing rules improve over time.
