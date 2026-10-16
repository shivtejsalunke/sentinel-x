# Unity simulation client

This directory reserves the Unity client workstream for the interactive 3D environment described in the product architecture. The assessment service and scenario/event contracts are implemented independently so they can be tested before a complete 3D client is available.

## Current status

The repository contains the planned folder structure, but not a complete Unity project: there is no `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, finished scene, or tested renderer. The existence of a directory is not evidence of a working 3D simulation.

## Integration contract

The client should:

1. Read approved public scenario metadata from `/api/v1/scenarios`.
2. Create a session with a scenario ID and seed.
3. Present only observations intended for the trainee; do not embed server-side answer keys in the client build.
4. Submit validated trainee events in order.
5. Finalize the session and retrieve assessment/AAR results.
6. Display that outputs are synthetic and training-only.

Do not connect the client to live aircraft or operational counter-drone equipment. Controller mapping, if later approved, should remain a simulation input adapter until a separate safety and authorization review is completed.

## Suggested first scene

Build one neutral training environment with selectable synthetic observations, a scenario state indicator, event logging, and a completion screen. Prioritize end-to-end event correctness and repeatability over photorealism. Use Unity Test Framework Edit Mode and Play Mode tests once the Unity project has been created.
