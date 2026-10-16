# Unity simulation client

This directory reserves the Unity client workstream for the interactive 3D environment described in the product architecture. The assessment service and scenario/event contracts are implemented independently so they can be tested before a complete 3D client is available.

## Current status

The repository contains source scaffolding, but not a complete Unity project: there is no `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, finished scene, or tested renderer. The existence of a directory is not evidence of a working 3D simulation.

## Integration contract

1. Read public scenario metadata from `/api/v1/scenarios`.
2. Create a session with a scenario ID and seed.
3. Present only observations intended for the trainee; do not embed answer keys in the client build.
4. Submit validated trainee events in order.
5. Finalize the session and retrieve assessment/AAR results.
6. Identify outputs as synthetic and training-only.

Do not connect the client to live aircraft or operational counter-drone equipment. Any future controller mapping must remain simulator-only until separately authorized and reviewed.

## First scene

Build one neutral training environment with selectable synthetic observations, scenario-state display, event logging, and a completion screen. Prioritize event correctness and repeatability over photorealism. Add Unity Test Framework Edit Mode and Play Mode tests once a Unity project has been created.
