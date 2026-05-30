#!/usr/bin/env python3
"""Tworzy paczkę ZIP z plikami potrzebnymi po eksperymencie."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_DIR / "results_local"
CACHE_PATH = RESULTS_DIR / "participant_cache.json"
DEFAULT_OUTPUT_DIR = REPO_DIR / "submissions_local"

FILES_TO_INCLUDE = [
    REPO_DIR / "task_implementation" / "solution.py",
    REPO_DIR / "task_debugging" / "booking.py",
    RESULTS_DIR / "events.jsonl",
    RESULTS_DIR / "metadata.json",
    CACHE_PATH,
]


def _safe_part(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value.strip())
    return cleaned or "unknown"


def _read_json(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def infer_participant_data() -> tuple[str, str]:
    cache = _read_json(CACHE_PATH)
    metadata = _read_json(RESULTS_DIR / "metadata.json")
    participant_id = str(cache.get("participant_id") or metadata.get("participant_id") or "unknown")
    group = str(cache.get("group") or metadata.get("group") or "unknown")
    return participant_id, group


def _iter_existing_files() -> list[Path]:
    files = [path for path in FILES_TO_INCLUDE if path.exists() and path.is_file()]
    files.extend(sorted(RESULTS_DIR.glob("summary_*.json")))
    return files


def create_package(participant_id: str | None = None, group: str | None = None, output_dir: Path | None = None) -> Path:
    inferred_id, inferred_group = infer_participant_data()
    participant_id = participant_id or inferred_id
    group = group or inferred_group
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"submission_{_safe_part(participant_id)}_{_safe_part(group)}_{timestamp}.zip"
    archive_path = output_dir / archive_name

    files = _iter_existing_files()
    if not files:
        raise FileNotFoundError("Nie znaleziono plików do spakowania.")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(REPO_DIR))

    return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tworzy ZIP z rozwiązaniami i lokalnymi wynikami eksperymentu.")
    parser.add_argument("--participant-id", default=None, help="ID uczestnika, np. S01")
    parser.add_argument("--group", default=None, help="Grupa, np. A")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Katalog na gotową paczkę ZIP")
    args = parser.parse_args(argv)

    try:
        archive_path = create_package(args.participant_id, args.group, args.output_dir)
    except OSError as exc:
        print(f"Nie udało się przygotować paczki: {exc}", file=sys.stderr)
        return 1

    print("Gotowa paczka do wysłania:")
    print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
