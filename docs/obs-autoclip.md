# OBS Auto-Clipping Design

The project integrates with OBS through OBS WebSocket v5 at `ws://localhost:4455` by default. OBS WebSocket authentication is optional; no-password setups work by leaving the CLI password option unset. This keeps clipping independent from platform-specific hotkey automation and avoids requiring a compiled OBS plugin.

## Connection lifecycle

`ObsAutoClipManager` validates configuration, ensures the output folder exists and is writable, connects to OBS, and polls stream/record/replay-buffer state. If streaming or recording matches the configured mode, it starts Replay Buffer. When neither activity is eligible, it stops Replay Buffer.

## Clip creation

Manual and automatic clips call `SaveReplayBuffer` through OBS WebSocket. OBS writes the replay using its configured Replay Buffer output settings. When renaming is enabled, the companion watches the configured output folder for the newly written video file and renames it with the configured template. Built-in automatic triggers include scene changes and fixed time intervals while streaming or recording is eligible.

## Trigger extension points

Trigger adapters should be thin wrappers that call `ObsAutoClipManager.save_clip()` after their own authorization or debounce logic. Suitable adapters include chat commands, keyboard shortcuts, audio spike detectors, and marker/event HTTP endpoints; scene-change and interval triggers are built into the manager.
