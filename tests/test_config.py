from pathlib import Path

import pytest

from obs_autoclip.config import ClipMode, ObsAutoClipConfig


def test_activity_enabled_for_both_modes() -> None:
    config = ObsAutoClipConfig(enabled_for=ClipMode.BOTH)

    assert config.activity_enabled(streaming=True, recording=False)
    assert config.activity_enabled(streaming=False, recording=True)
    assert not config.activity_enabled(streaming=False, recording=False)


def test_invalid_clip_length_rejected() -> None:
    config = ObsAutoClipConfig(clip_length_seconds=10)

    with pytest.raises(ValueError, match="15, 30, or 60"):
        config.validate()


def test_output_folder_created(tmp_path: Path) -> None:
    folder = tmp_path / "clips"
    config = ObsAutoClipConfig(output_folder=folder)

    config.ensure_output_folder()

    assert folder.is_dir()


def test_invalid_auto_clip_interval_rejected() -> None:
    config = ObsAutoClipConfig(auto_clip_interval_seconds=0)

    with pytest.raises(ValueError, match="auto clip interval"):
        config.validate()
