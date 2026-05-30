#!/usr/bin/env python3
"""Record the start of a participant task."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_CHOICES = ("implementation", "debugging")
MODE_CHOICES = ("no_ai", "cursor_ai")


def participant_repo_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_output_dir() -> Path:
    return participant_repo_dir() / "results_local"


def iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        json.dump(event, handle, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zapisuje rozpoczęcie zadania uczestnika do lokalnego pliku events.jsonl."
    )
    parser.add_argument("--participant-id", required=True, help="Identyfikator uczestnika badania.")
    parser.add_argument("--group", required=True, help="Grupa eksperymentalna uczestnika.")
    parser.add_argument("--task-id", required=True, choices=TASK_CHOICES, help="Identyfikator zadania.")
    parser.add_argument("--mode", required=True, choices=MODE_CHOICES, help="Tryb pracy uczestnika.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Katalog wynikowy na metadane (domyślnie: participant_repo/results_local).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    output_dir = args.output_dir.expanduser().resolve()

    event = {
        "event_type": "start_task",
        "timestamp": iso_timestamp(),
        "participant_id": args.participant_id,
        "group": args.group,
        "task_id": args.task_id,
        "mode": args.mode,
    }

    try:
        append_jsonl(output_dir / "events.jsonl", event)
    except OSError as exc:
        print(f"Błąd: nie udało się zapisać zdarzenia start_task: {exc}", file=sys.stderr)
        return 1

    print(f"Zapisano rozpoczęcie zadania ({args.task_id}, {args.mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
