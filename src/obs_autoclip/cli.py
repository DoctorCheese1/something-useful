from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import ClipMode, ObsAutoClipConfig
from .manager import ObsAutoClipManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OBS Replay Buffer auto-clipping companion")
    parser.add_argument("--host", default=os.getenv("OBS_WEBSOCKET_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("OBS_WEBSOCKET_PORT", "4455")))
    parser.add_argument("--password", default=os.getenv("OBS_WEBSOCKET_PASSWORD"))
    parser.add_argument("--clip-length", type=int, choices=(15, 30, 60), default=30)
    parser.add_argument("--output-folder", type=Path, default=Path("clips"))
    parser.add_argument("--name-format", default="{date}-{time}-{scene}.mp4")
    parser.add_argument("--enabled-for", choices=[mode.value for mode in ClipMode], default=ClipMode.BOTH.value)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--no-rename", action="store_true", help="leave OBS-generated replay filenames unchanged")
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("watch", help="keep Replay Buffer synced with stream/recording state")
    subcommands.add_parser("clip", help="save the current Replay Buffer immediately")
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
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "watch"
    manager = ObsAutoClipManager(config_from_args(args))

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


if __name__ == "__main__":
    raise SystemExit(main())
