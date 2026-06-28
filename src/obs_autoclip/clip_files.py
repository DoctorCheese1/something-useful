from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".flv", ".ts", ".m4v"}


def sanitize_filename(value: str) -> str:
    sanitized = _SAFE.sub("-", value.strip()).strip(".-")
    return sanitized or "clip"


def render_clip_name(template: str, scene: str, when: datetime | None = None) -> str:
    now = when or datetime.now()
    rendered = template.format(
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H-%M-%S"),
        scene=sanitize_filename(scene),
        timestamp=now.strftime("%Y%m%d-%H%M%S"),
    )
    return sanitize_filename(rendered)


def unique_path(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        candidate = folder / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def newest_video_file(folder: Path, after: float) -> Path | None:
    videos = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS and path.stat().st_mtime >= after
    ]
    if not videos:
        return None
    return max(videos, key=lambda path: path.stat().st_mtime)
