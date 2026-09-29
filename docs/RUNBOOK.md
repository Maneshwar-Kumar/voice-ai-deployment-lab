# Operations runbook

## Severity levels

| Severity | Example | Response |
|---|---|---|
| SEV-1 | unsafe instruction, PII leak, widespread incorrect booking | disable traffic immediately; notify security, product, operations |
| SEV-2 | transfer or CRM integration materially degraded | enter degraded mode; page service owners |
| SEV-3 | quality regression affecting a segment | freeze expansion; investigate within one business day |

## First 15 minutes

1. Confirm the alert and incident owner.
2. Stop or reduce automated traffic if customer harm is plausible.
3. Preserve request IDs, release version, provider status, and relevant redacted events.
4. Switch affected journeys to human handling or callback capture.
5. Notify the operating owner in plain business language.

## Diagnosis

- Is the issue tied to a new release, provider, language, intent, or integration?
- Did response latency increase before errors appeared?
- Are tool calls failing, timing out, or returning unexpected schemas?
- Did policy configuration or consent wording change?
- Can the issue be reproduced using a synthetic evaluation case?

## Recovery

- Roll back to the last approved version.
- Run the critical regression pack.
- Validate CRM writes and transfer routing.
- Restore traffic gradually while monitoring the affected cohort.
- Record the defect, customer impact, cause, and permanent corrective action.

