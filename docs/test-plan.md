# Test plan

## Objectives

Validate the scenario contract, event lifecycle, scoring calculations, adaptation behavior, AAR traceability, data persistence, API error handling, and repeatable deployment. Functional tests do not prove training efficacy or physical sensor fidelity.

## Test levels

1. **Unit:** schema validation, metrics, rubric weights, state transitions, recommendation selection, AAR evidence links.
2. **Integration:** API → scenario loader → event log → assessment → SQLite → AAR.
3. **Regression:** run a fixed fixture and compare exact score components and flags.
4. **End-to-end:** start scenario session, record events, complete, restart service, retrieve persisted results, and get a recommendation.
5. **Offline/deployment:** install dependencies, run tests, and execute the core service without external network access.
6. **Training validation:** separate approved study with equivalent baseline/post-test conditions, retention evaluation, participant reporting, and domain review.

## Mandatory cases

| ID | Setup | Expected result |
|---|---|---|
| TEST-001 | Valid scenario definition | Loads and exposes public task information |
| TEST-002 | Missing scenario field | Rejected with validation error |
| TEST-003 | Unknown scenario ID | Not found; no session created |
| TEST-004 | Duplicate event sequence number | Rejected without event mutation |
| TEST-005 | Event timestamp before prior event | Rejected or explicitly handled by documented contract |
| TEST-006 | Same fixture assessed twice | Identical result without double counting |
| TEST-007 | No evaluated observations | Metric unavailable rather than zero-divide or perfect score |
| TEST-008 | Incomplete session completion | Cannot be treated as a valid completed assessment |
| TEST-009 | Weak, evidenced competency | Recommendation targets a matching approved scenario |
| TEST-010 | Insufficient competency evidence | Conservative fallback with rationale |
| TEST-011 | AAR error flag | Links to a stored event and named scoring component |
| TEST-012 | Service restart | Session and assessment remain retrievable |
| TEST-013 | Missing database write | API reports failure and does not claim persistence success |
| TEST-014 | Invalid or oversized payload | Rejected safely |
| TEST-015 | Public scenario list request | Evaluation-only ground truth is not returned |
| TEST-016 | Network disabled | Core local workflow remains functional after installation |
| TEST-017 | Different permitted seed | Variation remains within schema constraints |
| TEST-018 | Same seed and version | Scenario parameter variation remains reproducible |

## Engineering checks

```bash
ruff check services/assessment
ruff format --check services/assessment
mypy services/assessment/app
pytest
```

CI runs these checks for changes to the assessment service. A Unity build/test job must be added after Unity project metadata and a supported build runner are committed.

## Test evidence and release gate

Store the test command, commit, environment, pass/fail count, and unresolved defects with release evidence. Do not commit personal or operational session data. A release candidate should have no unresolved critical/high severity defects in the agreed scope, repeatable scoring for fixed fixtures, tested database recovery, and a documented limitations section.

## Training study design

Do not conflate software QA with validation of learning. A credible study should define the participant cohort, consent/approval process, baseline task, targeted practice, equivalent post-test, optional retention test, missing-data treatment, analysis method, and limitations in advance. Report measured results only after tests have actually been performed.
