# Architecture decision record

## Decision

Separate the customer-facing deployment logic from the voice-provider integration behind a narrow adapter contract.

## Why

An enterprise deployment should not hard-wire business policy, CRM behaviour, evaluation criteria, or observability to one model or telephony provider. The voice platform is important, but it is one component of a larger operating system.

```mermaid
sequenceDiagram
    autonumber
    participant C as Caller
    participant V as Voice provider
    participant O as Orchestrator
    participant P as Policy layer
    participant T as Tool gateway
    participant R as CRM / calendar
    participant H as Human queue
    participant M as Monitoring

    C->>V: Audio turn
    V->>O: Transcript + conversation state
    O->>P: Intent, consent, proposed action
    P-->>O: Allow, constrain, or escalate
    alt tool-confirmed action
        O->>T: Read slots / reserve appointment
        T->>R: Authenticated idempotent request
        R-->>T: Confirmed result
        T-->>O: Structured tool response
        O-->>V: Grounded response
        V-->>C: Streamed speech
    else uncertainty or policy trigger
        O->>H: Warm transfer with summary
        H-->>C: Human continues call
    end
    O->>M: Latency, quality, cost, outcome events
```

## Component responsibilities

| Component | Owns | Must not own |
|---|---|---|
| Voice provider | speech, turn-taking, streaming | customer master data |
| Orchestrator | state, tool selection, response plan | raw credentials |
| Policy layer | consent, prohibited actions, escalation | business-system writes |
| Tool gateway | schemas, authentication, retries, idempotency | open-ended model reasoning |
| CRM/calendar | source-of-truth records and slots | conversational policy |
| Monitoring | events, alerts, quality sampling | unrestricted transcript access |

## Reliability choices

- A booking is never stated as confirmed until the calendar write succeeds.
- Tool writes carry idempotency keys so retries cannot create duplicate appointments.
- External calls have timeouts and circuit breakers.
- Degraded mode captures a callback instead of inventing availability.
- Human transfer is treated as a core product path, not a failure.
- Release gates combine technical, safety, customer, and commercial metrics.

## Provider integration boundary

The public repository supplies a deterministic provider for repeatable demonstrations. A production adapter would translate provider webhooks into the same request model and map approved responses back to the provider API. Credentials stay server-side in a managed secret store.

