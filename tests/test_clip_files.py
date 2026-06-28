from datetime import datetime
from pathlib import Path

from obs_autoclip.clip_files import render_clip_name, unique_path


def test_render_clip_name_sanitizes_scene() -> None:
    name = render_clip_name(
        "{date}-{time}-{scene}.mp4",
        "Gameplay / Boss Fight!",
        datetime(2026, 6, 28, 13, 14, 15),
    )

    assert name == "2026-06-28-13-14-15-Gameplay-Boss-Fight.mp4"


def test_unique_path_adds_suffix_for_duplicates(tmp_path: Path) -> None:
    existing = tmp_path / "clip.mp4"
    existing.write_text("x", encoding="utf-8")

    assert unique_path(tmp_path, "clip.mp4") == tmp_path / "clip-2.mp4"
