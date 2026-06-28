from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import ClipMode, ObsAutoClipConfig
from .manager import ObsAutoClipManager
from .obs_client import ObsConnectionError, ObsDependencyError, ReplayBufferUnavailableError


def add_common_arguments(parser: argparse.ArgumentParser, *, suppress_defaults: bool = False) -> None:
    default = argparse.SUPPRESS if suppress_defaults else None
    parser.add_argument("--host", default=default or os.getenv("OBS_WEBSOCKET_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=default or int(os.getenv("OBS_WEBSOCKET_PORT", "4455")))
    parser.add_argument("--password", default=default or os.getenv("OBS_WEBSOCKET_PASSWORD"))
    parser.add_argument("--clip-length", type=int, choices=(15, 30, 60), default=default or 30)
    parser.add_argument("--output-folder", type=Path, default=default or Path("clips"))
    parser.add_argument("--name-format", default=default or "{date}-{time}-{scene}.mp4")
    parser.add_argument("--enabled-for", choices=[mode.value for mode in ClipMode], default=default or ClipMode.BOTH.value)
    parser.add_argument("--poll-interval", type=float, default=default or 2.0)
    parser.add_argument("--no-rename", action="store_true", default=default or False, help="leave OBS-generated replay filenames unchanged")
    parser.add_argument("--auto-clip-on-scene-change", action="store_true", default=default or False, help="save a replay whenever the active OBS scene changes")
    parser.add_argument("--auto-clip-interval", type=int, default=default, help="save replays automatically every N seconds while clipping is active")
    parser.add_argument("--auto-clip-cooldown", type=float, default=default or 10.0, help="minimum seconds between automatic clips")


def build_parser() -> argparse.ArgumentParser:
    root_common = argparse.ArgumentParser(add_help=False)
    add_common_arguments(root_common)
    subcommand_common = argparse.ArgumentParser(add_help=False)
    add_common_arguments(subcommand_common, suppress_defaults=True)
    parser = argparse.ArgumentParser(
        description="OBS Replay Buffer auto-clipping companion",
        parents=[root_common],
    )
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("watch", help="keep Replay Buffer synced with stream/recording state", parents=[subcommand_common])
    subcommands.add_parser("clip", help="save the current Replay Buffer immediately", parents=[subcommand_common])
    return parser


def config_from_args(args: argparse.Namespace) -> ObsAutoClipConfig:
    return ObsAutoClipConfig(
        host=args.host,
        port=args.port,
        password=args.password,
        clip_length_seconds=args.clip_length,
        output_folder=args.output_folder,
        clip_naming_format=args.name_format,
        enabled_for=ClipMode(args.enabled_for),
        poll_interval_seconds=args.poll_interval,
        rename_saved_clips=not args.no_rename,
        auto_clip_on_scene_change=args.auto_clip_on_scene_change,
        auto_clip_interval_seconds=args.auto_clip_interval,
        auto_clip_cooldown_seconds=args.auto_clip_cooldown,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "watch"
    manager = ObsAutoClipManager(config_from_args(args))

    try:
        if command == "clip":
            manager.connect()
            try:
                clip_path = manager.save_clip()
                print(f"Saved clip: {clip_path}" if clip_path else "Saved clip via OBS Replay Buffer")
            finally:
                manager.disconnect()
            return 0

        manager.run_forever()
        return 0
    except (ObsDependencyError, ObsConnectionError, ReplayBufferUnavailableError) as exc:
        parser.exit(1, f"obs-autoclip: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
