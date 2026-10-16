# Requirements and acceptance criteria

## Product objective

Provide a reproducible training workflow in which a trainee interacts with a controlled scenario, records decisions, receives a deterministic assessment, reviews the evidence, and is directed to suitable follow-up practice.

## Scope

### In scope for the software baseline

- Versioned JSON scenario definitions and structural validation.
- Synthetic observation and classification exercises.
- Session lifecycle and ordered event capture.
- Deterministic scoring, independent metric calculation, and explicit review flags.
- A rules-based recommendation engine whose rationale is persisted.
- Event-linked AAR output.
- SQLite persistence and documented local API.
- Automated tests, CI checks, threat-model documentation, and licensing records.
- Unity client scaffolding for the intended interactive 3D experience.

### Out of scope for the initial baseline

- Connection to live aircraft, operational counter-drone systems, or autonomous physical control.
- Claims that synthetic observations reproduce real sensor performance.
- A learned perception model or generative model in the assessment path.
- Formal institutional certification, accreditation, or approved operational doctrine.
- Multi-user synchronization, cloud account integration, or VR.
- Claims of training effectiveness before an appropriate evaluation.

## Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| REQ-001 | Load a versioned scenario and reject invalid definitions | Schema and service tests |
| REQ-002 | Create a session with a stable ID, seed, scenario version, and lifecycle state | API/integration tests |
| REQ-003 | Record events with strictly increasing sequence numbers | Duplicate and out-of-order requests are rejected |
| REQ-004 | Finalize a valid session once | Repeated completion is idempotent or rejected without duplicate scoring |
| REQ-005 | Calculate scores deterministically from event evidence and a rubric version | Same fixture yields identical assessment |
| REQ-006 | Calculate accuracy, false-positive/miss measures, response latency, and procedure completeness where supported by data | Edge-case tests, including zero denominators |
| REQ-007 | Generate an AAR from stored evidence | Each error/flag references a specific event or score component |
| REQ-008 | Recommend follow-up practice from competency gaps | A known weak competency selects a matching approved exercise with a rationale |
| REQ-009 | Persist sessions, events, assessments, recommendations, and version metadata | Data remains after service restart |
| REQ-010 | Keep ground truth away from the trainee-facing scenario listing | Public scenario API excludes scoring answer keys |
| REQ-011 | Provide a health endpoint and API schema | Health and OpenAPI endpoints respond locally |
| REQ-012 | Keep core functionality available offline once dependencies are installed | Offline integration test / deployment checklist |
| REQ-013 | Keep simulation separate from any live equipment | No physical equipment/control integration in this release |

## Quality requirements

- Input validation on every externally supplied object.
- Deterministic scoring for a fixed event log, scenario version, and rubric version.
- Stable identifiers and event ordering.
- Clear failure responses; never report persistence success if a write failed.
- Role and deployment security reviewed before exposing the service beyond loopback.
- Minimal personal data, synthetic test identifiers, and an explicit retention policy.
- Documented dependency and asset licensing.
- Tests for incomplete sessions, missing evidence, duplicate events, and database errors.

## User roles

- **Trainee:** completes assigned sessions and reviews permitted feedback.
- **Instructor:** selects/approves scenarios and reviews evidence and reports.
- **Administrator:** configures the local installation and manages access.

The current API is a development baseline and does not yet provide production-grade identity management. Do not infer that named roles are enforced simply because the product design defines them.

## Definition of done for the first end-to-end increment

A developer can install the assessment service, run the tests, start the local API, create a session from an approved scenario, submit a valid decision event, complete the session, retrieve the score and AAR, and request a follow-up recommendation. The Unity simulation experience remains a separate client integration deliverable until its project assets and scenes are completed and tested.
