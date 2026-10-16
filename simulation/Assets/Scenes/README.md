# Runtime scene

The client currently creates its training UI at runtime using `TrainingClientBootstrap`, so a blank scene can be used for initial smoke testing. The bootstrap creates its own persistent root after scene load. A dedicated authored 3D scene, lighting, terrain, and visual observation assets are separate work and must not be represented as completed by the UI client alone.
