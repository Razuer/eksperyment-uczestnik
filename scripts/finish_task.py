#!/usr/bin/env python3
"""Record the end of a participant task and optionally run public tests."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_CHOICES = ("implementation", "debugging")
MODE_CHOICES = ("no_ai", "cursor_ai")
TASK_TEST_FILES = {
    "implementation": "task_implementation/tests_public.py",
    "debugging": "task_debugging/tests_public.py",
}


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


def extract_pytest_counts(output: str) -> dict[str, int | None]:
    counts: dict[str, int | None] = {"passed": None, "failed": None, "errors": None, "skipped": None}
    category_patterns = {
        "passed": r"(\d+)\s+passed\b",
        "failed": r"(\d+)\s+failed\b",
        "errors": r"(\d+)\s+errors?\b",
        "skipped": r"(\d+)\s+skipped\b",
    }
    category_words = (" passed", " failed", " error", " errors", " skipped")
    summary_lines = [line for line in output.splitlines() if any(word in line for word in category_words)]
    search_area = "\n".join(summary_lines[-5:]) if summary_lines else output
    found_any_category = False
    for key, pattern in category_patterns.items():
        matches = re.findall(pattern, search_area)
        if matches:
            found_any_category = True
            counts[key] = int(matches[-1])

    if found_any_category:
        for key, value in counts.items():
            if value is None:
                counts[key] = 0

    non_empty_counts = [value for value in counts.values() if value is not None]
    counts["total"] = sum(non_empty_counts) if non_empty_counts else None
    return counts


def run_public_tests(task_id: str) -> dict[str, Any]:
    repo_dir = participant_repo_dir()
    test_file = TASK_TEST_FILES[task_id]
    command = [sys.executable, "-m", "pytest", test_file]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_dir,
            text=True,
            capture_output=True,
            check=False,
        )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        counts = extract_pytest_counts(combined_output)
        return {
            "not_run": False,
            "command": command,
            "cwd": str(repo_dir),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "errors": counts["errors"],
            "skipped": counts["skipped"],
            "total": counts["total"],
        }
    except OSError as exc:
        return {
            "not_run": False,
            "command": command,
            "cwd": str(repo_dir),
            "returncode": None,
            "stdout": "",
            "stderr": f"Nie udało się uruchomić testów: {exc}",
            "passed": None,
            "failed": None,
            "errors": None,
            "skipped": None,
            "total": None,
        }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zapisuje zakończenie zadania i wynik publicznych testów do lokalnych plików JSON."
    )
    parser.add_argument("--participant-id", required=True, help="Identyfikator uczestnika badania.")
    parser.add_argument("--task-id", required=True, choices=TASK_CHOICES, help="Identyfikator zadania.")
    parser.add_argument("--mode", required=True, choices=MODE_CHOICES, help="Tryb pracy uczestnika.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir(),
        help="Katalog wynikowy na metadane (domyślnie: participant_repo/results_local).",
    )
    parser.add_argument("--skip-tests", action="store_true", help="Nie uruchamiaj publicznych testów pytest.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    output_dir = args.output_dir.expanduser().resolve()
    timestamp = iso_timestamp()

    if args.skip_tests:
        test_result: dict[str, Any] = {
            "not_run": True,
            "command": None,
            "cwd": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "passed": None,
            "failed": None,
            "errors": None,
            "skipped": None,
            "total": None,
        }
    else:
        test_result = run_public_tests(args.task_id)

    event = {
        "event_type": "finish_task",
        "timestamp": timestamp,
        "participant_id": args.participant_id,
        "task_id": args.task_id,
        "mode": args.mode,
        "tests": test_result,
    }
    summary = {
        "participant_id": args.participant_id,
        "task_id": args.task_id,
        "mode": args.mode,
        "finished_at": timestamp,
        "tests": test_result,
    }
    summary_path = output_dir / f"summary_{args.participant_id}_{args.task_id}_{args.mode}.json"

    try:
        append_jsonl(output_dir / "events.jsonl", event)
        write_json(summary_path, summary)
    except OSError as exc:
        print(f"Błąd: nie udało się zapisać wyniku zakończenia zadania: {exc}", file=sys.stderr)
        return 1

    if test_result["not_run"]:
        print("Zapisano zakończenie zadania. Testy publiczne pominięto.")
    else:
        passed = test_result.get("passed")
        total = test_result.get("total")
        if passed is not None and total:
            print(
                f"Zapisano zakończenie zadania. Testy publiczne: {passed}/{total} zaliczonych "
                "(to tylko testy publiczne, nie ocena Twojej pracy)."
            )
        else:
            print("Zapisano zakończenie zadania. Wynik testów publicznych został zapisany.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
