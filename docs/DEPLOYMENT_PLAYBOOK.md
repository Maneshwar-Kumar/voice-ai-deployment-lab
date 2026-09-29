# Deployment playbook

## 1. Discovery

Start from a measurable customer workflow, not from a model demo.

- Observe current calls and failure modes.
- Baseline volume, handle time, transfer rate, conversion, cost, and quality.
- Identify the system of record and its owner.
- Map callers, agents, supervisors, compliance, IT, and executive sponsors.
- Agree which decisions the AI may make and which require a person.
- Define a narrow first use case with a safe fallback.

**Exit criterion:** named process owner, baseline data, integration feasibility, approved success metrics, and an accountable executive sponsor.

## 2. Solution and integration design

Document every external contract:

- Telephony and voice-provider events
- CRM reads and writes
- Calendar availability and reservation semantics
- Consent and disclosure wording
- Identity and authorization
- Handoff queue and context package
- Outcome events and analytics destinations

For each dependency, specify authentication, data fields, timeout, retry policy, idempotency, owner, and degraded behaviour.

## 3. Evaluation before launch

Build an evaluation set from synthetic and appropriately governed examples. Include:

- routine successful journeys
- ambiguous intents
- interruptions and corrections
- multilingual and accented speech
- unavailable systems
- prompt-injection attempts
- policy-prohibited requests
- explicit requests for a human
- adversarial and emotionally charged callers

Score task success, policy compliance, tool accuracy, transfer quality, latency, and customer effort. Averages do not replace inspection of critical failures.

## 4. Phased rollout

| Stage | Customer exposure | Purpose | Promotion gate |
|---|---:|---|---|
| Shadow | 0% | Compare proposed actions with human outcomes | evaluation thresholds met |
| Assisted | internal users | Let advisers inspect and approve suggestions | adoption and correction rates acceptable |
| Limited production | 5-10% | Validate real integrations and behaviour | no critical safety event; KPIs stable |
| Controlled expansion | 25-50% | Test operating capacity and segment variance | sustained quality across cohorts |
| Scale | policy-defined | Optimise unit economics and extend use cases | governance board approval |

Every stage has a rollback owner and a one-action traffic-disable mechanism.

## 5. Live operations

Monitor four layers:

- **Experience:** completion, transfer, repeat-call rate, customer effort
- **Quality and safety:** grounded responses, policy flags, evaluation regressions
- **Systems:** latency, errors, tool timeouts, queue health
- **Economics:** cost per completed task, conversion, avoided handle time

Sample calls for human review using a risk-weighted policy. Feed confirmed defects into the regression evaluation set before the next release.

## 6. Change management

- Train advisers on what context arrives during a handoff.
- Give supervisors an escalation and override path.
- Publish what the system can and cannot do.
- Review early calls daily with operations and engineering.
- Tie expansion to demonstrated workload reduction and customer outcomes.
- Share field insights with product and research teams as structured evidence, not anecdotes.

