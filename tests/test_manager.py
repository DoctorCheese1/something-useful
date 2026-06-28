from dataclasses import dataclass

from obs_autoclip.config import ClipMode, ObsAutoClipConfig
from obs_autoclip.manager import ObsAutoClipManager
from obs_autoclip.obs_client import ObsActivityState


@dataclass
class FakeClient:
    state: ObsActivityState
    started: bool = False
    stopped: bool = False
    saved: bool = False

    def connect(self) -> None: pass
    def disconnect(self) -> None: pass
    def get_activity_state(self) -> ObsActivityState: return self.state
    def start_replay_buffer(self) -> None: self.started = True
    def stop_replay_buffer(self) -> None: self.stopped = True
    def save_replay_buffer(self) -> None: self.saved = True
    scene: str = "Scene"

    def get_current_scene_name(self) -> str: return self.scene


def test_sync_starts_replay_buffer_when_streaming() -> None:
    client = FakeClient(ObsActivityState(streaming=True, recording=False, replay_buffer_active=False))
    manager = ObsAutoClipManager(ObsAutoClipConfig(enabled_for=ClipMode.STREAMS), client)

    assert manager.sync_replay_buffer() is True
    assert client.started
    assert not client.stopped


def test_sync_stops_replay_buffer_when_idle() -> None:
    client = FakeClient(ObsActivityState(streaming=False, recording=False, replay_buffer_active=True))
    manager = ObsAutoClipManager(ObsAutoClipConfig(), client)

    assert manager.sync_replay_buffer() is False
    assert client.stopped


def test_tick_auto_clips_on_scene_change_after_initial_scene() -> None:
    client = FakeClient(ObsActivityState(streaming=True, recording=False, replay_buffer_active=True))
    manager = ObsAutoClipManager(
        ObsAutoClipConfig(auto_clip_on_scene_change=True, auto_clip_cooldown_seconds=0, rename_saved_clips=False),
        client,
    )

    assert manager.tick() is None
    client.scene = "Gameplay"
    assert manager.tick() is None
    assert client.saved


def test_tick_auto_clips_on_interval(monkeypatch) -> None:
    client = FakeClient(ObsActivityState(streaming=True, recording=False, replay_buffer_active=True))
    manager = ObsAutoClipManager(
        ObsAutoClipConfig(auto_clip_interval_seconds=30, auto_clip_cooldown_seconds=0, rename_saved_clips=False),
        client,
    )
    times = iter([100.0, 131.0, 131.0])
    monkeypatch.setattr("obs_autoclip.manager.time.time", lambda: next(times))

    assert manager.tick() is None
    assert manager.tick() is None
    assert client.saved
