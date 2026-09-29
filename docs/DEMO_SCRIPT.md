# Five-minute demo script

## 0:00 - Customer problem

An automotive retail group receives 12,000 monthly service calls. Availability lives in a calendar, customer context lives in the CRM, and failed transfers damage conversion. The goal is not to demonstrate a talking bot; it is to deploy a reliable booking workflow.

## 0:40 - Business case

Adjust volume, handle time, labour cost, expected containment, and voice-platform cost. The model shows its assumptions and refuses to recommend scale when economics or risks are unfavourable.

## 1:30 - Runtime

Run the successful call. Explain where consent, orchestration, CRM reads, calendar writes, speech generation, and telemetry occur. Highlight that the agent confirms only after the tool write succeeds.

## 2:20 - Failure handling

Make the CRM unavailable. The system times out, avoids inventing a slot, captures a callback, records degraded mode, and routes the issue to operations.

## 3:00 - Quality gates

Show that task success alone is insufficient. Safety, transfer success, latency, write integrity, and cohort-level quality all gate expansion.

## 3:40 - Rollout and operations

Walk from shadow mode to assisted use, limited production, controlled expansion, and scale. Point to the rollback owner, observability signals, and incident runbook.

## 4:30 - Delivery discipline

Show the tests and CI pipeline: lint, coverage threshold, policy cases, API contract, container build, smoke test, CodeQL, dependency updates, and GitHub Pages deployment.

## Closing

The demo is deliberately provider-neutral and uses transparent synthetic calls. A real ElevenLabs adapter would sit behind the narrow provider contract while the business workflow, controls, evaluations, and operating model remain stable.
