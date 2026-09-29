# Security policy

## Reporting

Please report security issues privately through GitHub's security-advisory feature. Do not include credentials, personal data, or customer transcripts in a public issue.

## Demo data

The repository contains synthetic data only. The reference service does not persist call content.

## Credential handling

- Keep provider keys server-side in a managed secret store.
- Prefer workload identity or short-lived credentials for deployments.
- Never put keys in the static web application, source control, container image, or CI logs.
- Rotate a credential immediately if it is exposed.

## Production controls not included in this public lab

A real deployment must add authenticated endpoints, tenant isolation, durable encrypted storage, provider-specific webhook verification, data-retention enforcement, rate limits, and an approved privacy impact assessment.

