from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ClipMode(StrEnum):
    """Activity modes that can keep OBS Replay Buffer running."""

    STREAMS = "streams"
    RECORDINGS = "recordings"
    BOTH = "both"


@dataclass(frozen=True)
class ObsAutoClipConfig:
    """Configuration for OBS Replay Buffer based auto-clipping."""

    host: str = "localhost"
    port: int = 4455
    password: str | None = None
    clip_length_seconds: int = 30
    output_folder: Path = Path("clips")
    clip_naming_format: str = "{date}-{time}-{scene}.mp4"
    enabled_for: ClipMode = ClipMode.BOTH
    poll_interval_seconds: float = 2.0
    rename_saved_clips: bool = True

    def validate(self) -> None:
        if not self.host:
            raise ValueError("OBS WebSocket host is required")
        if not 1 <= self.port <= 65535:
            raise ValueError("OBS WebSocket port must be between 1 and 65535")
        if self.clip_length_seconds not in {15, 30, 60}:
            raise ValueError("clip length must be one of 15, 30, or 60 seconds")
        if self.poll_interval_seconds <= 0:
            raise ValueError("poll interval must be greater than zero")
        if not self.clip_naming_format:
            raise ValueError("clip naming format is required")

    def ensure_output_folder(self) -> None:
        self.output_folder.mkdir(parents=True, exist_ok=True)
        probe = self.output_folder / ".obs-autoclip-write-test"
        try:
            probe.write_text("ok", encoding="utf-8")
        finally:
            probe.unlink(missing_ok=True)

    def activity_enabled(self, streaming: bool, recording: bool) -> bool:
        if self.enabled_for == ClipMode.STREAMS:
            return streaming
        if self.enabled_for == ClipMode.RECORDINGS:
            return recording
        return streaming or recording
