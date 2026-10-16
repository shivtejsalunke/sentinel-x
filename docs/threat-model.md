# Threat model

## Scope and assumptions

This model covers the local assessment API, scenario files, event records, generated reports, and developer workstation. The first deployment is intended for loopback/local use. It is not a certification assessment and does not claim to cover the security needs of a connected institutional installation.

## Assets

- Integrity and reproducibility of assessments.
- Scenario ground truth and rubric definitions.
- Session event history and trainee progress records.
- Local database and exported reports.
- Source code, release artefacts, dependency metadata, and configuration.
- Separation between simulated actions and real equipment.

## Trust boundaries

1. User/client inputs crossing the HTTP API.
2. Scenario packages read from the filesystem.
3. Runtime service and the local SQLite database.
4. Exported JSON/CSV/PDF reports copied outside the installation.
5. Future simulator/hardware adapters, which are not part of the current physical control path.

## Threats and controls

| Threat | Potential impact | Current/required control | Residual concern |
|---|---|---|---|
| Malformed scenario JSON | Crash or invalid assessment conditions | Schema validation and allowlisted values | Resource limits and fuzzing need ongoing work |
| Forged or reordered events | Incorrect scoring or audit sequence | Session ownership checks where available, typed event schema, unique sequence constraints | Production authentication is not complete |
| Duplicate completion requests | Duplicate score/event aggregation | Idempotent completion logic and persisted result lookup | Verify with concurrency tests for the target database/runtime |
| Scenario answer-key exposure | Trainee can memorize/cheat on exercise | Public API strips private evaluation metadata | Filesystem/API deployment permissions must be reviewed |
| Database theft or workstation compromise | Disclosure or alteration of training history | OS permissions, disk protection, minimal data, backup access controls | Local admin compromise remains possible |
| Unauthorized record access | Privacy and assessment integrity breach | Add server-side identity and authorization before multi-user/network deployment | Not suitable as-is for a shared network service |
| Unsupported AAR claims | Misleading trainee feedback | Generate from metrics and event references; no unconstrained model in scoring path | Text templates still require tests/review |
| Dependency/supply-chain issue | Compromise or unexpected behavior | Pinned dependency ranges, CI checks, dependency inventory and update review | Vulnerability scanning/release signing are future gates |
| Secrets committed to Git | Account compromise | `.gitignore`, local environment configuration | Automated secret scanning should be enabled where available |
| Accidental live equipment path | Unsafe real-world action | Current code has no live control integration | Any future adapter requires isolation, explicit approval, and safety review |
| Misinterpreted synthetic outcomes | Invalid operational conclusions | Label synthetic fixtures, document limits, separate validation evidence | Domain experts must review training assumptions |

## Minimum release controls

- Bind the development service to `127.0.0.1` unless a reviewed deployment configuration is used.
- Never store credentials or access tokens in source control.
- Use synthetic IDs and synthetic events during development.
- Keep session records out of the public repository.
- Review dependencies and licences before building redistributable packages.
- Validate input at the service boundary, not only in the UI.
- Treat imported scenario packages as untrusted until validated and approved.
- Define retention, backup, restore, and report-export procedures before institutional use.
- Test for broken access control before allowing more than one user to share a service.
- Maintain a clear separation between simulated decisions and real equipment.

## Residual risks and review ownership

This is a working threat model. It must be revisited whenever network exposure, user identities, sensitive data, third-party AI, multiplayer synchronization, or physical training hardware is introduced. An authorized security review is required before institutional deployment. Offline operation reduces external attack surface but does not eliminate local compromise, malicious removable media, or supply-chain risk.
