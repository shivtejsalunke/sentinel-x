# Unity simulation client

The Unity project under this directory contains a runtime-generated training UI and an HTTP client for the local SENTINEL-X assessment service. The first increment supports the synthetic OBS-001 scenario, ordered classification submissions, session completion, and display of the returned score.

## Open and run

1. Install Unity Hub and a compatible Unity 6 editor.
2. Open this `simulation/` directory as the Unity project.
3. Start the assessment API following `services/assessment/README.md`.
4. Enter `http://127.0.0.1:8000` in the client and select **Start Scenario**.
5. Submit one response for each prompt and complete the session.

The client uses loopback by default and is intended for local testing. A desktop client running on another machine cannot reach the API via its own loopback address; configure an appropriate trusted endpoint only after the service has been secured for that environment.

## Included

- Unity project metadata and UGUI package manifest.
- JSON API contracts and a UnityWebRequest client.
- Runtime-generated training form with scenario prompt, response selection, event submission, and assessment completion.
- Synthetic scenario only; no physical equipment or live aircraft control.

## Current limitations

- The client is a functional workflow prototype, not a finished 3D environment.
- Only OBS-001 is selected by the initial UI; scenario discovery and instructor configuration are not yet exposed in the client.
- The seed currently provides session reproducibility metadata; the current scenario data does not vary by seed.
- Authentication, instructor/trainee roles, multi-user deployment, and network transport security are not implemented.
- The Python CI workflow does not compile the Unity client. Open it in the supported editor and run a smoke test before treating the client as validated.
