from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ObsConnectionError(RuntimeError):
    """Raised when OBS WebSocket cannot be reached or authenticated."""


class ObsDependencyError(RuntimeError):
    """Raised when the OBS WebSocket Python dependency is not installed."""


class ReplayBufferUnavailableError(RuntimeError):
    """Raised when OBS Replay Buffer is disabled or cannot be controlled."""


@dataclass(frozen=True)
class ObsActivityState:
    streaming: bool
    recording: bool
    replay_buffer_active: bool


class ObsClientProtocol(Protocol):
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def get_activity_state(self) -> ObsActivityState: ...
    def start_replay_buffer(self) -> None: ...
    def stop_replay_buffer(self) -> None: ...
    def save_replay_buffer(self) -> None: ...
    def get_current_scene_name(self) -> str: ...


class ObsWebSocketClient:
    """Small adapter around obsws-python's ReqClient for OBS WebSocket v5."""

    def __init__(self, host: str, port: int, password: str | None) -> None:
        self.host = host
        self.port = port
        self.password = password
        self._client: Any | None = None

    def connect(self) -> None:
        try:
            from obsws_python import ReqClient
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on environment
            raise ObsDependencyError(
                "Missing dependency: obsws-python. Run `python -m pip install -e .` "
                "from the project folder, or use start-obs-autoclip.bat to install it automatically."
            ) from exc

        try:
            self._client = ReqClient(host=self.host, port=self.port, password=self.password or "")
        except Exception as exc:  # pragma: no cover - depends on local OBS
            raise ObsConnectionError(
                f"Unable to connect to OBS WebSocket at ws://{self.host}:{self.port}"
            ) from exc

    def disconnect(self) -> None:
        if self._client and hasattr(self._client, "disconnect"):
            self._client.disconnect()
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            raise ObsConnectionError("OBS WebSocket client is not connected")
        return self._client

    def get_activity_state(self) -> ObsActivityState:
        stream = self.client.get_stream_status()
        record = self.client.get_record_status()
        replay = self.client.get_replay_buffer_status()
        return ObsActivityState(
            streaming=bool(getattr(stream, "output_active", False)),
            recording=bool(getattr(record, "output_active", False)),
            replay_buffer_active=bool(getattr(replay, "output_active", False)),
        )

    def start_replay_buffer(self) -> None:
        try:
            self.client.start_replay_buffer()
        except Exception as exc:  # pragma: no cover - depends on OBS settings
            raise ReplayBufferUnavailableError(
                "OBS Replay Buffer could not be started. Enable it in OBS Output settings."
            ) from exc

    def stop_replay_buffer(self) -> None:
        try:
            self.client.stop_replay_buffer()
        except Exception as exc:  # pragma: no cover - depends on OBS state
            raise ReplayBufferUnavailableError("OBS Replay Buffer could not be stopped") from exc

    def save_replay_buffer(self) -> None:
        try:
            self.client.save_replay_buffer()
        except Exception as exc:  # pragma: no cover - depends on OBS settings
            raise ReplayBufferUnavailableError(
                "OBS Replay Buffer could not be saved. Ensure the buffer is active."
            ) from exc

    def get_current_scene_name(self) -> str:
        scene = self.client.get_current_program_scene()
        return str(getattr(scene, "current_program_scene_name", "unknown-scene"))
