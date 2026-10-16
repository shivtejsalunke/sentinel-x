# ADR 0001: Local-first modular architecture

- **Status:** Accepted for the initial implementation
- **Decision date:** 2026-10-17

## Context

The first demonstrator must be runnable on a standard development workstation, function without continuous internet access, and be straightforward to test. A distributed microservice system would introduce avoidable deployment and integration overhead.

## Decision

Use a Python assessment service with clearly separated modules and SQLite persistence. Keep scenario definitions in versioned JSON. Treat the Unity client as a separate consumer of the session/event contract. Use deterministic software for scoring and simple rules for adaptation before introducing learned models.

## Consequences

- Local setup and test execution are straightforward.
- Fixed fixtures can be assessed reproducibly.
- SQLite limits concurrent multi-user scale; a later deployment may require PostgreSQL and explicit identity management.
- A completed Unity scene and deployment package are separate deliverables and are not implied by the service implementation.
- No cloud API or AI provider is required for the baseline workflow.
