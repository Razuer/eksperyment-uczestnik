#!/usr/bin/env python3
"""Collect participant environment and experience metadata."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CURSOR_PLAN_CHOICES = ("free", "pro", "unknown")


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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def optional_experience_fields(args: argparse.Namespace) -> dict[str, str | None]:
    return {
        "python_experience": args.python_experience,
        "ai_experience": args.ai_experience,
        "cursor_experience": args.cursor_experience,
        "programming_experience": args.programming_experience,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zapisuje metadane uczestnika i środowiska do metadata.json oraz events.jsonl."
    )
    parser.add_argument("--participant-id", required=True, help="Identyfikator uczestnika badania.")
    parser.add_argument("--group", required=True, help="Grupa eksperymentalna uczestnika.")
    parser.add_argument("--cursor-version", help="Wersja edytora Cursor (zwykle zbierana w ankiecie wstępnej).")
    parser.add_argument("--selected-model", help="Wybrany model AI w Cursorze (zwykle zbierany w ankiecie wstępnej).")
    parser.add_argument("--cursor-plan", choices=CURSOR_PLAN_CHOICES, help="Plan Cursor uczestnika (zwykle zbierany w ankiecie wstępnej).")
    parser.add_argument("--operating-system", required=True, help="System operacyjny uczestnika.")
    parser.add_argument("--python-experience", help="Opis lub poziom doświadczenia z Pythonem.")
    parser.add_argument("--ai-experience", help="Opis lub poziom doświadczenia z narzędziami AI.")
    parser.add_argument("--cursor-experience", help="Opis lub poziom doświadczenia z Cursorem.")
    parser.add_argument("--programming-experience", help="Opis lub poziom doświadczenia programistycznego.")
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
    timestamp = iso_timestamp()

    metadata = {
        "collected_at": timestamp,
        "participant_id": args.participant_id,
        "group": args.group,
        "cursor_version": args.cursor_version,
        "selected_model": args.selected_model,
        "cursor_plan": args.cursor_plan,
        "operating_system": args.operating_system,
        **optional_experience_fields(args),
    }
    event = {
        "event_type": "metadata_collected",
        "timestamp": timestamp,
        "participant_id": args.participant_id,
        "group": args.group,
        "metadata": metadata,
    }

    try:
        write_json(output_dir / "metadata.json", metadata)
        append_jsonl(output_dir / "events.jsonl", event)
    except OSError as exc:
        print(f"Błąd: nie udało się zapisać metadanych: {exc}", file=sys.stderr)
        return 1

    print("Zapisano dane o środowisku.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
