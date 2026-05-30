# Instrukcja dla uczestnika

Bierzesz udział w pilotażowym eksperymencie, w którym porównujemy pracę bez AI i pracę z Cursor AI. Badanie nie jest egzaminem. Nie oceniamy uczestnika, tylko sposób pracy i samo narzędzie.

## Co przeczytać i w jakiej kolejności

1. Jeśli jeszcze nie przygotowałeś/aś środowiska, zrób to najpierw wg `README.md` (Python, środowisko wirtualne, zależności). Ten plik zawiera zasady eksperymentu i sposób uruchomienia zadania.
2. Gdy prowadzący poda Ci ID (`S01`), grupę (`A`/`B`/`C`/`D`) i numer zadania (`1` albo `2`), uruchom skrypt opisany niżej.
3. Katalog zadania (`task_implementation/` albo `task_debugging/`) otwórz dopiero po starcie timera. Czytanie treści zadania wlicza się do limitu 15 minut.
4. Po obu zadaniach wypełnisz ankietę końcową.

## Zasady eksperymentu

- Pracujesz w Cursorze w obu trybach. Różni się tylko to, czy możesz używać funkcji AI.
- Każde zadanie trwa maksymalnie 15 minut. Możesz zakończyć wcześniej, jeśli uznasz rozwiązanie za gotowe.
- Po zadaniu skrypt sam uruchomi testy publiczne. Oddajesz aktualny stan kodu, nawet jeśli nie jest kompletny.
- Nie korzystaj z pomocy innych osób.
- Wyniki są anonimizowane (identyfikator typu `S01`).

## Tryb bez AI (`no_ai`)

W tym trybie używasz Cursora tylko jako edytora.

Nie używaj Cursor Chat, Cursor Agent, Cursor Tab / AI autocomplete, inline AI edit, ChatGPT, Copilota, Claude, Gemini ani innych asystentów AI. Nie korzystaj też z ogólnych wyszukiwarek (m.in. ze względu na odpowiedzi generowane przez AI, np. Google AI Overviews), Stack Overflow ani forów.

Zanim wystartujesz, **wyłącz Cursor Tab**: kliknij „Cursor Tab" na dolnym pasku Cursora i włącz **Snooze na minimum 15 minut**. Dzięki temu podpowiedzi AI nie pojawią się przypadkiem podczas pracy bez AI.

Możesz używać edytora, terminala, treści zadania, testów publicznych, **oficjalnej dokumentacji Pythona i bibliotek** oraz własnej wiedzy.

## Tryb z Cursor AI (`cursor_ai`)

Możesz korzystać z funkcji Cursora z AI: chatu, agenta, podpowiedzi Tab, inline edit, generowania kodu i analizy błędów z testów.

AI ma być **wsparciem, nie wyręczeniem**: używaj go do fragmentów kodu, poprawek, wyjaśnień i analizy błędów, ale prowadź rozwiązanie samodzielnie - czytaj, decyduj, integruj zmiany i uruchamiaj testy. **Nie wklejaj całej treści zadania do Cursor Agent po gotowe rozwiązanie** i nie oddawaj go bez weryfikacji. To Ty decydujesz, które zmiany zaakceptować i kiedy oddać rozwiązanie.

Nie zapisuj promptów w trakcie zadania - po zakończeniu w ankiecie pojawi się krótkie pytanie o użycie AI (1-3 najważniejsze polecenia albo krótki opis).

## Jak uruchomić zadanie

Dla każdego z dwóch zadań uruchamiasz jedno polecenie:

```bash
python scripts/run_task.py
```

Skrypt poprowadzi Cię tak:

1. Zapyta o identyfikator (`S01`), grupę (`A`/`B`/`C`/`D`) i numer zadania (`1` albo `2`). Te dane dostaniesz od prowadzącego. Po pierwszym uruchomieniu ID i grupa będą już podpowiadane. Skrypt sam ustali, czy robisz implementację czy debugging oraz czy pracujesz z AI czy bez AI.
2. Jeżeli metadane nie były jeszcze zapisane, skrypt zapyta o wersję Cursora, model, plan/licencję, system operacyjny i krótkie samooceny doświadczenia. Ten krok odbywa się przed startem timera.
3. Pokaże typ zadania, tryb pracy, katalog i limit czasu. Na tym etapie timer jeszcze nie działa.
4. Zapyta, czy jesteś gotowy/gotowa. Gdy klikniesz Enter startuje pomiar czasu.
5. W terminalu będzie widać czas `[mm:ss / 15:00]`. Około minutę przed końcem pojawi się ostrzeżenie. Po przekroczeniu limitu zobaczysz komunikat, że trzeba oddać aktualny stan.
6. W tym czasie otwórz katalog zadania, przeczytaj jego `README.md` i pracuj. Terminal z timerem niech zostanie w tle, nie wyłączaj go.
7. Gdy skończysz albo gdy minie czas, wróć do terminala i naciśnij Enter. Skrypt uruchomi testy publiczne i zapisze koniec zadania.

Skrypt obsługuje wybór zadania, trybu pracy, pomiar czasu i uruchomienie testów publicznych. Nie modyfikuj plików w `scripts/` ani `results_local/`.

## Po obu zadaniach

- Skrypt po każdym zadaniu wyświetli link do ankiety (a na początku link do ankiety wstępnej i na końcu do ankiety końcowej). Wypełnij je zgodnie z poleceniem prowadzącego.
- Po zadaniu wykonanym z Cursor AI w ankiecie pojawi się krótkie pytanie o użycie AI. Wystarczy krótki opis albo 1-3 najważniejsze polecenia użyte wobec Cursor AI.

## Co wysłać prowadzącemu

Po drugim zadaniu skrypt sam przygotuje plik ZIP w katalogu `submissions_local/`. Nazwa będzie wyglądać mniej więcej tak:

```text
submission_S01_A_20260601_183000.zip
```

Przekaż prowadzącemu ten plik ZIP. W środku znajdują się rozwiązania obu zadań i lokalne pliki z pomiarem czasu. Jeśli paczka nie utworzy się automatycznie, uruchom:

```bash
python scripts/package_submission.py
```

Dziękujemy za udział w badaniu.
