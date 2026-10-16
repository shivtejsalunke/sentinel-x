# Compliance and governance register

This is an applicability register, not a legal opinion, certification, or declaration of compliance. The responsible institution or organization must determine which laws, standards, policies, and approvals apply to the actual deployment.

| Area | Initial control/evidence | Status | Next action before institutional use |
|---|---|---|---|
| Personal data protection | Synthetic development identities; data-minimization design | Partial | Identify roles and purposes, applicable obligations/effective dates, lawful basis, retention and request procedures |
| Cybersecurity incident handling | Threat model and local-first deployment | Partial | Assess applicable CERT-In and institutional requirements, logs, time synchronization, retention, and incident response |
| Secure software development | CI checks, input validation, tests, dependency declarations | Partial | Add systematic dependency/secret scanning, review gates, release integrity, and vulnerability response |
| Authentication and access control | Roles documented; production identity not complete | Not ready for shared network deployment | Implement and test server-side authentication/authorization and least privilege |
| Drone/aviation rules | Initial release is software-only; no live aircraft path | Applicability review required | Obtain qualified review before any physical aircraft or controlled training operation |
| Defence/institutional approval | No approval is implied | Not assessed | Confirm permission for curriculum, data, location, branding, hardware, and any restricted material |
| AI governance | Deterministic scoring; transparent rules-based adaptation | Partial | Version policies, record recommendation evidence, and review instructor approval/override requirements |
| Model and dataset provenance | Synthetic fixtures with manifests | Partial | Record source, licence, renderer/version, labels, split methodology, and evaluation evidence for any added data/model |
| Software and asset licensing | `LICENSES.md`, MIT project licence, no bundled third-party art | Partial | Audit each added dependency and asset before redistribution |
| Accessibility and usability | Not formally assessed | Open | Conduct usability/accessibility review with target users |
| Backup and recovery | Persistence tests planned | Partial | Demonstrate restore from backup on a clean installation |
| Formal certification/accreditation | No certification claimed | Not applicable to current prototype | Do not claim certification unless independent formal assessment is completed |

## Reference points for applicability review

- India's Digital Personal Data Protection Act, 2023 and the Digital Personal Data Protection Rules, 2025; verify current provisions and implementation timelines using official MeitY publications.
- CERT-In Directions of 28 April 2022; assess whether and how these apply to the actual operating entity/deployment.
- NIST Secure Software Development Framework (SSDF) as a development-process reference.
- OWASP Application Security Verification Standard (ASVS) as a review checklist for web/API security where applicable.
- Indian Drone Rules, 2021 and other relevant rules, institutional restrictions, and written authorizations when physical aircraft or hardware is involved.

None of these references automatically certifies this project. Applicability must be reviewed for the real deployment by suitably qualified personnel.
