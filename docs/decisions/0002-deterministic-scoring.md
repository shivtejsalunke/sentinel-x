# ADR 0002: Deterministic assessment and separately versioned adaptation

- **Status:** Accepted for the initial implementation
- **Decision date:** 2026-10-17

## Context

Training outcomes need to be repeatable, explainable, and linked to recorded evidence. A generative or opaque model is not an appropriate authority for official grades or critical-error flags.

## Decision

Calculate assessment dimensions with deterministic code against a named rubric version. Keep adaptation as a separate rules-based recommendation function that consumes completed assessment results. Preserve the rationale for each recommendation. Any future machine-learning component must have a specifically defined task, documented data provenance, evaluation baseline, validation results, and human oversight.

## Consequences

- Tests can assert exact score values for fixtures.
- The adaptation behavior is explainable and predictable.
- Initial adaptation is not represented as a trained AI model.
- The prototype's rubric weights are illustrative until approved by a training authority.
