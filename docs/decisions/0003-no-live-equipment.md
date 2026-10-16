# ADR 0003: No direct live-equipment integration in the initial release

- **Status:** Accepted for the initial implementation
- **Decision date:** 2026-10-17

## Context

The initial goal is a software training and assessment demonstrator. Live hardware adds safety, authorization, operational security, regulatory, and deployment concerns that are not necessary to test the core learning workflow.

## Decision

The initial repository contains no live aircraft control or operational counter-drone equipment interface. Future controller familiarization must remain simulator-only unless a separate, explicitly authorized and safety-reviewed integration plan is approved.

## Consequences

- The MVP can be built and tested without physical equipment.
- No operational capability or certification is implied.
- A future hardware adapter requires its own threat model, interface constraints, tests, authorization, and release gate.
