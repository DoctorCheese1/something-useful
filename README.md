# Something Useful

This repository contains an OBS auto-clipping companion that uses the OBS WebSocket API and Replay Buffer to save recent gameplay or video segments while streaming or recording.

## OBS auto-clipping

The `obs-autoclip` CLI connects to OBS WebSocket, watches stream and recording state, starts Replay Buffer when clipping should be active, stops it when OBS is idle, and can trigger a manual replay save.

### Required OBS settings

1. Install OBS 28 or newer, which includes OBS WebSocket v5.
2. In OBS, open **Tools → WebSocket Server Settings**.
3. Enable the WebSocket server and keep the default port `4455`. A password is optional; if you leave OBS WebSocket authentication disabled or blank, omit `--password` when running this tool.
4. Open **Settings → Output → Replay Buffer** and enable Replay Buffer.
5. Set the Replay Buffer maximum replay time to match the configured clip length, such as 15, 30, or 60 seconds.
6. Set the OBS recording/replay output folder to the same folder passed to `--output-folder` if you want `obs-autoclip` to rename clips.

### Configuration

Install the package, then run the watcher:

```bash
obs-autoclip watch \
  --host localhost \
  --port 4455 \
  --clip-length 30 \
  --output-folder ./clips \
  --name-format "{date}-{time}-{scene}.mp4" \
  --enabled-for both \
  --auto-clip-on-scene-change \
  --auto-clip-interval 300 \
  --auto-clip-cooldown 10
```

Supported `--enabled-for` values are:

- `streams` — run Replay Buffer only while streaming.
- `recordings` — run Replay Buffer only while recording.
- `both` — run Replay Buffer while either streaming or recording.

The naming template supports `{date}`, `{time}`, `{timestamp}`, and `{scene}`. Duplicate names automatically receive a numeric suffix. If OBS WebSocket has no password, do not pass `--password`; if you later enable one, pass `--password "your-password"` or set `OBS_WEBSOCKET_PASSWORD`.


### Windows `.bat` launcher

On Windows, double-click `start-obs-autoclip.bat` from the repository folder to start the watcher with the default no-password OBS WebSocket setup. Keep the Command Prompt window open while you stream or record; if it appears idle after the startup messages, that means the watcher is running and waiting for OBS activity. Edit the variables at the top of the batch file if you need a different port, clip folder, clip length, password, or auto-clip interval.

If dependency installation fails on Windows, install the OBS WebSocket dependency directly:

```bat
python -m pip install obsws-python
```

If you want to install this project as an editable package, change into the project folder first and install the current directory:

```bat
cd /d "D:\Downloads\something-useful-main (2)\something-useful-main"
python -m pip install -e .
```

### Triggering clips

Automatic clipping can be enabled with `--auto-clip-on-scene-change` or `--auto-clip-interval N`. The cooldown prevents duplicate clips when multiple automatic triggers fire close together.

Run this command from a hotkey tool, Stream Deck action, chat bot, marker API handler, or shell while the Replay Buffer is active:

```bash
obs-autoclip clip --output-folder ./clips --name-format "{date}-{time}-{scene}.mp4"
```

Future trigger adapters can call `ObsAutoClipManager.save_clip()` for audio spikes, `!clip` chat commands, keyboard shortcuts, or external marker/event APIs.

### Error handling

The companion validates the WebSocket host and port, clip length, output folder writability, and filename template before connecting. Runtime errors surface clear failures for OBS not running, WebSocket authentication issues, Replay Buffer being disabled in OBS, and replay save failures.
