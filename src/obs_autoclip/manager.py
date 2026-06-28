from __future__ import annotations

import time
from pathlib import Path

from .clip_files import newest_video_file, render_clip_name, unique_path
from .config import ObsAutoClipConfig
from .obs_client import ObsClientProtocol, ObsWebSocketClient


class ObsAutoClipManager:
    """Coordinates OBS connection state and Replay Buffer clipping."""

    def __init__(self, config: ObsAutoClipConfig, client: ObsClientProtocol | None = None) -> None:
        self.config = config
        self.client = client or ObsWebSocketClient(config.host, config.port, config.password)
        self._last_scene_name: str | None = None
        self._last_clip_time = 0.0

    def connect(self) -> None:
        self.config.validate()
        self.config.ensure_output_folder()
        self.client.connect()

    def disconnect(self) -> None:
        self.client.disconnect()

    def sync_replay_buffer(self) -> bool:
        state = self.client.get_activity_state()
        should_run = self.config.activity_enabled(state.streaming, state.recording)
        if should_run and not state.replay_buffer_active:
            self.client.start_replay_buffer()
        elif not should_run and state.replay_buffer_active:
            self.client.stop_replay_buffer()
        return should_run

    def save_clip(self) -> Path | None:
        self._last_clip_time = time.time()
        before = self._last_clip_time
        scene = self.client.get_current_scene_name()
        self.client.save_replay_buffer()
        if not self.config.rename_saved_clips:
            return None

        # OBS writes asynchronously; wait briefly for the saved replay to appear.
        saved = None
        for _ in range(20):
            saved = newest_video_file(self.config.output_folder, before)
            if saved is not None:
                break
            time.sleep(0.25)
        if saved is None:
            return None

        target = unique_path(
            self.config.output_folder,
            render_clip_name(self.config.clip_naming_format, scene),
        )
        saved.rename(target)
        return target

    def maybe_auto_clip(self, replay_should_run: bool) -> Path | None:
        if not replay_should_run:
            return None

        now = time.time()
        if now - self._last_clip_time < self.config.auto_clip_cooldown_seconds:
            return None

        if self.config.auto_clip_interval_seconds is not None:
            if self._last_clip_time == 0.0:
                self._last_clip_time = now
            elif now - self._last_clip_time >= self.config.auto_clip_interval_seconds:
                return self.save_clip()

        if self.config.auto_clip_on_scene_change:
            scene = self.client.get_current_scene_name()
            if self._last_scene_name is None:
                self._last_scene_name = scene
            elif scene != self._last_scene_name:
                self._last_scene_name = scene
                return self.save_clip()

        return None

    def tick(self) -> Path | None:
        replay_should_run = self.sync_replay_buffer()
        return self.maybe_auto_clip(replay_should_run)

    def run_forever(self) -> None:
        self.connect()
        try:
            while True:
                self.tick()
                time.sleep(self.config.poll_interval_seconds)
        finally:
            self.disconnect()
