from pathlib import Path

from obs_autoclip.cli import build_parser, config_from_args
from obs_autoclip.config import ClipMode


def test_watch_accepts_options_after_subcommand() -> None:
    parser = build_parser()

    args = parser.parse_args([
        "watch",
        "--host",
        "localhost",
        "--port",
        "4455",
        "--clip-length",
        "30",
        "--output-folder",
        "clips",
        "--name-format",
        "{date}-{time}-{scene}.mp4",
        "--enabled-for",
        "both",
        "--auto-clip-on-scene-change",
        "--auto-clip-interval",
        "300",
        "--auto-clip-cooldown",
        "10",
    ])
    config = config_from_args(args)

    assert args.command == "watch"
    assert config.host == "localhost"
    assert config.port == 4455
    assert config.clip_length_seconds == 30
    assert config.output_folder == Path("clips")
    assert config.enabled_for == ClipMode.BOTH
    assert config.auto_clip_on_scene_change
    assert config.auto_clip_interval_seconds == 300
    assert config.auto_clip_cooldown_seconds == 10


def test_watch_accepts_options_before_subcommand() -> None:
    parser = build_parser()

    args = parser.parse_args(["--host", "127.0.0.1", "--port", "4455", "watch"])
    config = config_from_args(args)

    assert args.command == "watch"
    assert config.host == "127.0.0.1"
    assert config.port == 4455
