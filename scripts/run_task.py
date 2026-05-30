#!/usr/bin/env python3
"""Interaktywny skrypt do uruchomienia jednego zadania."""

from __future__ import annotations

import json
import os
import platform
import re
import signal
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote_plus

import collect_metadata
import finish_task
import package_submission
import start_task

REPO_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_DIR / "results_local"
CACHE_PATH = RESULTS_DIR / "participant_cache.json"
METADATA_PATH = RESULTS_DIR / "metadata.json"
SURVEY_LINKS_PATH = REPO_DIR / "survey_links.json"

GROUP_PLAN: dict[str, list[tuple[str, str]]] = {
    "A": [("implementation", "no_ai"), ("debugging", "cursor_ai")],
    "B": [("debugging", "cursor_ai"), ("implementation", "no_ai")],
    "C": [("implementation", "cursor_ai"), ("debugging", "no_ai")],
    "D": [("debugging", "no_ai"), ("implementation", "cursor_ai")],
}
GROUP_CHOICES = set(GROUP_PLAN)
ORDINAL_CHOICES = {"1", "2"}
TIME_LIMIT_SECONDS = 15 * 60
ONE_MINUTE_WARNING_AT = TIME_LIMIT_SECONDS - 60
PARTICIPANT_ID_RE = re.compile(r"^S\d{2,}$")
TASK_DIR_NAME = {
    "implementation": "task_implementation",
    "debugging": "task_debugging",
}
TASK_LABEL = {
    "implementation": "implementacja",
    "debugging": "debugging",
}
MODE_LABEL = {
    "no_ai": "bez AI",
    "cursor_ai": "Cursor AI",
}


_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_USE_SOUND = sys.stderr.isatty()
BOLD, CYAN, YELLOW, GREEN, RED = "1", "36", "33", "32", "31"


def _beep(times: int = 1) -> None:
    """Dzwonek terminala (BEL). Tylko w terminalu, żeby nie śmiecić w potoku."""
    if _USE_SOUND:
        sys.stderr.write("\a" * times)
        sys.stderr.flush()


def _style(text: str, *codes: str) -> str:
    if not _USE_COLOR or not codes:
        return text
    prefix = "".join(f"\033[{code}m" for code in codes)
    return f"{prefix}{text}\033[0m"


def _action(text: str) -> str:
    """Wyróżniona linia 'do zrobienia' (np. wypełnij ankietę)."""
    return _style(f">> {text}", BOLD, YELLOW)


def _banner(text: str) -> None:
    line = "=" * 60
    print(f"\n{_style(line, CYAN)}")
    print(f"  {_style(text, BOLD, CYAN)}")
    print(_style(line, CYAN))


def _prompt(
    label: str,
    *,
    choices: set[str] | None = None,
    validator=None,
    normalize=str.strip,
    default: str | None = None,
) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        raw = input(f"{label}{suffix}: ")
        value = default if default and not raw.strip() else normalize(raw)
        if not value:
            print("  (puste, spróbuj jeszcze raz)")
            continue
        if choices is not None and value.upper() not in choices:
            print(f"  (dozwolone: {', '.join(sorted(choices))})")
            continue
        if validator is not None and not validator(value):
            print("  (nieprawidłowy format)")
            continue
        return value


def _confirm(message: str) -> bool:
    answer = (
        input(f"{message} [Enter = kontynuuj, q + Enter = anuluj]: ").strip().lower()
    )
    return answer != "q"


def _read_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_json_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_cache(participant_id: str, group: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {"participant_id": participant_id, "group": group},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _metadata_matches(participant_id: str, group: str) -> bool:
    metadata = _read_json_file(METADATA_PATH)
    return (
        metadata.get("participant_id") == participant_id
        and metadata.get("group") == group
    )


def _ensure_metadata(participant_id: str, group: str) -> bool:
    """Zapisz automatycznie wykryty system. Resztę metadanych zbiera ankieta wstępna."""
    if _metadata_matches(participant_id, group):
        return True
    return (
        collect_metadata.main(
            [
                "--participant-id",
                participant_id,
                "--group",
                group,
                "--operating-system",
                platform.platform(),
            ]
        )
        == 0
    )


def _is_unset(value: str | None) -> bool:
    text = value.strip() if value else ""
    return not text or text.startswith("<")


def _apply_prefill(template: str, tokens: dict[str, str]) -> str:
    url = template.strip()
    for name, value in tokens.items():
        url = url.replace("{" + name + "}", quote_plus(str(value)))
    return url


def _resolve_survey_url(
    links: dict[str, str], key: str, tokens: dict[str, str]
) -> str | None:
    """Zwróć link z pre-fillem, jeśli prowadzący go ustawił; inaczej zwykły link."""
    prefill = links.get(f"{key}_prefill")
    if not _is_unset(prefill):
        return _apply_prefill(prefill, tokens)
    return links.get(key)


def _task_tokens(
    participant_id: str, ordinal: int, task_id: str, mode: str
) -> dict[str, str]:
    return {
        "participant_id": participant_id,
        "task_number": str(ordinal),
        "task_type": TASK_LABEL[task_id],
        "mode": MODE_LABEL[mode],
    }


def _survey_link_line(label: str, url: str | None) -> str:
    target = url.strip() if url else ""
    if not target or target.startswith("<"):
        target = "(link poda prowadzący)"
    return f"  {_style(label + ':', BOLD, YELLOW)}\n    {_style(target, CYAN)}"


def _format_mmss(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 60:02d}:{total % 60:02d}"


def _wait_for_enter_with_timer(limit_seconds: int) -> float:
    stop_event = threading.Event()
    start = time.monotonic()

    def loop() -> None:
        warned_one_minute = False
        warned_overrun = False
        while not stop_event.is_set():
            elapsed = time.monotonic() - start
            remaining = limit_seconds - elapsed
            label = f"[{_format_mmss(elapsed)} / {_format_mmss(limit_seconds)}]"
            if remaining < 0:
                label += _style("  PRZEKROCZONO LIMIT", BOLD, RED)
                if not warned_overrun:
                    sys.stderr.write(
                        _style(
                            "\n  !! Przekroczono limit 15 minut. Oddaj rozwiązanie.\n",
                            BOLD,
                            RED,
                        )
                    )
                    sys.stderr.flush()
                    _beep(3)
                    warned_overrun = True
            elif elapsed >= ONE_MINUTE_WARNING_AT and not warned_one_minute:
                sys.stderr.write(_style("\n  !! Pozostała ~1 minuta.\n", BOLD, YELLOW))
                sys.stderr.flush()
                _beep()
                warned_one_minute = True
            sys.stderr.write(f"\r  {label}  (Enter = koniec)   ")
            sys.stderr.flush()
            stop_event.wait(1.0)
        sys.stderr.write("\r" + " " * 70 + "\r")
        sys.stderr.flush()

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

    # Ignoruj Ctrl+C (SIGINT) podczas pomiaru, żeby przypadkowe kopiowanie
    # w terminalu nie zakończyło zadania. Zadanie kończy się Enterem.
    try:
        previous_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
    except (ValueError, OSError):
        previous_sigint = None

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        stop_event.set()
        thread.join(timeout=2)
        if previous_sigint is not None:
            try:
                signal.signal(signal.SIGINT, previous_sigint)
            except (ValueError, OSError):
                pass

    return time.monotonic() - start


def _collect_inputs() -> tuple[str, str, int, str, str]:
    cache = _read_cache()
    cached_participant_id = cache.get("participant_id")
    cached_group = cache.get("group")
    participant_id = _prompt(
        "Identyfikator uczestnika (np. S01)",
        validator=lambda v: bool(PARTICIPANT_ID_RE.match(v.upper())),
        default=cached_participant_id if cached_participant_id else None,
    ).upper()
    group = _prompt(
        "Grupa (A/B/C/D)",
        choices=GROUP_CHOICES,
        default=cached_group if cached_group in GROUP_CHOICES else None,
    ).upper()
    ordinal = int(_prompt("Numer zadania w sesji (1 albo 2)", choices=ORDINAL_CHOICES))
    task_id, mode = GROUP_PLAN[group][ordinal - 1]
    _write_cache(participant_id, group)
    return participant_id, group, ordinal, task_id, mode


def _print_summary(
    participant_id: str, group: str, ordinal: int, task_id: str, mode: str
) -> None:
    _banner("Twoje zadanie")
    print(f"  Uczestnik:    {participant_id}")
    print(f"  Grupa:        {group}")
    print(f"  Numer:        {ordinal} z 2")
    print(f"  Typ zadania:  {TASK_LABEL[task_id]}")
    print(f"  Tryb pracy:   {MODE_LABEL[mode]}")
    print(f"  Katalog:      {TASK_DIR_NAME[task_id]}/")
    print(f"  Limit czasu:  {TIME_LIMIT_SECONDS // 60} minut")
    print()
    if mode == "no_ai":
        print(
            "  -> Tryb bez AI: nie używaj Cursor Chat, Cursor Agent, Cursor Tab ani innych narzędzi AI."
        )
        print(
            "     Dozwolona jest tylko oficjalna dokumentacja (bez wyszukiwarek, Stack Overflow i forów)."
        )
        print(
            "     Zanim wystartujesz, wyłącz Cursor Tab: kliknij 'Cursor Tab' na dolnym pasku Cursora"
        )
        print("     i włącz Snooze na minimum 15 minut.")
    else:
        print(
            "  -> Tryb z Cursor AI: korzystaj z AI jako wsparcia, ale prowadź rozwiązanie samodzielnie."
        )
        print(
            "     Nie wklejaj całej treści zadania do Agenta po gotowca - czytaj, decyduj i weryfikuj."
        )
    print()
    print("  Po naciśnięciu Enter wystartuje timer. Wtedy:")
    print(f"    1. Otwórz katalog '{TASK_DIR_NAME[task_id]}/' w Cursorze.")
    print("    2. Przeczytaj README.md zadania. To też wlicza się do limitu 15 minut.")
    print("    3. Pracuj nad rozwiązaniem.")
    print("    4. Gdy skończysz, wróć tu i naciśnij Enter.")
    print()


def main() -> int:
    _banner("Eksperyment programistyczny: uruchamianie zadania")
    print(
        "Ten skrypt prowadzi Cię przez jedno zadanie: zbiera podstawowe dane, mierzy czas i na końcu uruchamia testy publiczne."
    )
    print(
        "Najpierw podaj trzy informacje od prowadzącego. Potem zobaczysz podsumowanie i zdecydujesz, kiedy wystartować.\n"
    )

    try:
        participant_id, group, ordinal, task_id, mode = _collect_inputs()
    except (EOFError, KeyboardInterrupt):
        print("\nPrzerwano.")
        return 1

    survey_links = _read_json_file(SURVEY_LINKS_PATH)
    if ordinal == 1:
        _banner("Najpierw ankieta wstępna (zgoda + kilka pytań)")
        print(
            _action(
                "Zanim wystartujesz, wypełnij ankietę wstępną (zgoda + pytania o doświadczenie i środowisko):"
            )
        )
        print()
        pre_url = _resolve_survey_url(
            survey_links, "pre_survey", {"participant_id": participant_id}
        )
        print(_survey_link_line("Ankieta wstępna", pre_url))
        print()
        try:
            input(
                _style(
                    "Gdy wypełnisz ankietę wstępną, naciśnij Enter, aby kontynuować... ",
                    BOLD,
                )
            )
        except (EOFError, KeyboardInterrupt):
            print("\nPrzerwano.")
            return 1

    if not _ensure_metadata(participant_id, group):
        print("\nNie udało się zapisać danych technicznych.")
        return 1

    _print_summary(participant_id, group, ordinal, task_id, mode)

    if not _confirm("Gotów/gotowa do startu?"):
        print("Anulowano przed startem.")
        return 1

    _banner("START: pomiar czasu wystartował")
    start_rc = start_task.main(
        [
            "--participant-id",
            participant_id,
            "--group",
            group,
            "--task-id",
            task_id,
            "--mode",
            mode,
        ]
    )
    if start_rc != 0:
        print("\nNie udało się zapisać startu zadania.")
        return start_rc

    print()
    print(
        _action(
            f"Otwórz '{TASK_DIR_NAME[task_id]}/README.md', przeczytaj treść i pracuj nad rozwiązaniem."
        )
    )
    print()
    print(
        "Aby w trakcie sprawdzić testy publiczne tego zadania, otwórz osobny terminal i uruchom:"
    )
    print(
        _style(
            f"    python -m pytest {TASK_DIR_NAME[task_id]}/tests_public.py", BOLD, CYAN
        )
    )
    print("    (kopiowanie: zaznacz tekst i kliknij prawym przyciskiem myszy → Kopiuj)")
    print()
    print(_action("Gdy skończysz albo upłynie czas - wróć tutaj i naciśnij Enter."))
    print()
    elapsed = _wait_for_enter_with_timer(TIME_LIMIT_SECONDS)
    print(f"\nZmierzony czas pracy: {_format_mmss(elapsed)} (mm:ss).")

    _banner("KONIEC: zapisuję wynik i uruchamiam testy publiczne")
    finish_rc = finish_task.main(
        [
            "--participant-id",
            participant_id,
            "--task-id",
            task_id,
            "--mode",
            mode,
        ]
    )
    if finish_rc != 0:
        print("\nNie udało się zapisać końca zadania.")
        return finish_rc

    _banner("Zadanie zakończone")
    task_tokens = _task_tokens(participant_id, ordinal, task_id, mode)
    post_task_url = _resolve_survey_url(survey_links, "post_task", task_tokens)
    if ordinal == 1:
        print("To było zadanie 1 z 2.")
        print()
        print(_action("1) Wypełnij teraz ankietę po zadaniu 1:"))
        print(_survey_link_line("Ankieta po zadaniu", post_task_url))
        print()
        print(_action("2) Potem uruchom drugie zadanie:"))
        print(_style("    python scripts/run_task.py", BOLD, CYAN))
        print("    (ID i grupa będą już podpowiedziane - wpisz tylko numer zadania: 2)")
    else:
        print("To było drugie i ostatnie zadanie.")
        print("Przygotowuję paczkę ZIP do wysłania...")
        try:
            archive_path = package_submission.create_package(participant_id, group)
        except OSError as exc:
            print(f"Nie udało się przygotować paczki automatycznie: {exc}")
            print("Możesz spróbować ręcznie: python scripts/package_submission.py")
        else:
            print()
            print(_action("Wyślij prowadzącemu ten plik:"))
            print(f"  {_style(str(archive_path), BOLD, GREEN)}")
        print()
        print(_action("Na koniec wypełnij dwie ankiety:"))
        final_url = _resolve_survey_url(
            survey_links, "final_survey", {"participant_id": participant_id}
        )
        print(_survey_link_line("Ankieta po zadaniu 2", post_task_url))
        print(_survey_link_line("Ankieta końcowa", final_url))
        print()
        print("Dziękujemy za udział!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
