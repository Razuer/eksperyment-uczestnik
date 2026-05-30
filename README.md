# Repozytorium uczestnika badania

To repozytorium zawiera materiały do pilotażowego eksperymentu porównującego pracę bez AI i pracę z Cursor AI. W obu zadaniach Cursor jest używany jako edytor. Różnica między trybami dotyczy wyłącznie możliwości korzystania z funkcji AI.

## Kolejność - przeczytaj w tej kolejności

1. **Ten plik (`README.md`)** - przygotowanie środowiska (sekcja niżej). Zacznij tutaj.
2. **`participant_instructions.md`** - zasady eksperymentu, tryby pracy i jak uruchomić zadanie.

Katalogów `task_implementation/` i `task_debugging/` **nie otwieraj** przed startem timera - czytanie treści zadania wlicza się do limitu 15 minut.

## Przygotowanie środowiska

1. Otwórz to repozytorium w Cursorze.
2. Zainstaluj rozszerzenie **Python** (zakładka Extensions / Rozszerzenia → wyszukaj „Python" → Install). Daje kolorowanie składni, uruchamianie i podpowiedzi oparte na analizie kodu (to nie jest AI - wolno z niego korzystać także w trybie bez AI).
3. Upewnij się, że masz Pythona 3.10 lub nowszego.
4. Utwórz i aktywuj środowisko wirtualne:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Na Windows aktywuj środowisko poleceniem `.venv\Scripts\activate` (w PowerShell: `.venv\Scripts\Activate.ps1`).

5. Zainstaluj zależności:

   ```bash
   pip install -r requirements.txt
   ```

6. Sprawdź, czy `pytest` działa:

   ```bash
   pytest
   ```

   Na początku część testów nie przejdzie. To normalne, bo zadania nie są jeszcze rozwiązane. Ważne, żeby `pytest` w ogóle się uruchomił.

## Uruchomienie zadania

Dla każdego z dwóch zadań:

```bash
python scripts/run_task.py
```

Skrypt zapyta o identyfikator, grupę i numer zadania, wykryje system, a przy pierwszym zadaniu pokaże link do ankiety wstępnej - dopiero potem wystartuje timer. Reszta jest opisana w `participant_instructions.md`.

Po drugim zadaniu skrypt sam przygotuje paczkę ZIP w katalogu `submissions_local/`. Ten plik przekaż prowadzącemu (sposób przekazania poda prowadzący).

## Jak czytać wynik testów

Po zadaniu (oraz gdy uruchomisz testy samodzielnie) zobaczysz podsumowanie `pytest`:

- kropka `.` lub `PASSED` - test przeszedł,
- `F` lub `FAILED` - test nie przeszedł; w sekcji `FAILURES` znajdziesz nazwę testu, wartość oczekiwaną i to, co zwrócił Twój kod,
- ostatnia linia to podsumowanie, np. `3 passed, 1 failed`.

To testy **publiczne** - sprawdzają tylko część przypadków i **nie są oceną Ciebie**. Oddajesz aktualny stan kodu, nawet jeśli nie wszystkie przechodzą.
