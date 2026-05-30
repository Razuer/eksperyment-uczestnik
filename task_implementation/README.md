# Zadanie 1: analiza logów

Zaimplementuj funkcję `analyze_logs` w pliku `solution.py`.

```python
def analyze_logs(logs: list[dict], timeout_ms: int) -> dict:
    ...
```

Funkcja otrzymuje listę wpisów logów aplikacji. Każdy wpis może zawierać między innymi pola:

- `level` - poziom logu, np. `"INFO"`, `"WARN"`, `"ERROR"`,
- `service` - nazwa usługi,
- `response_time_ms` - czas odpowiedzi w milisekundach.

Zwróć słownik z dokładnie następującymi kluczami:

```python
{
    "errors": ...,                    # liczba wpisów z level == "ERROR"
    "warnings": ...,                  # liczba wpisów z level == "WARN"
    "average_response_time_ms": ...,  # średni czas odpowiedzi
    "slow_services": ...,             # lista nazw wolnych usług
}
```

Wymagania szczegółowe:

- `errors` liczy wpisy, w których pole `level` ma wartość `"ERROR"`.
- `warnings` liczy wpisy, w których pole `level` ma wartość `"WARN"`.
- `average_response_time_ms` to średnia arytmetyczna z poprawnych wartości `response_time_ms`.
- Jeżeli lista logów jest pusta albo nie ma żadnych poprawnych czasów odpowiedzi, średnia powinna wynosić `0`.
- Średnia ma być zaokrąglona do najbliższej liczby całkowitej przy użyciu standardowego `round`.
- `slow_services` to lista unikalnych nazw usług, dla których `response_time_ms > timeout_ms`.
- Kolejność w `slow_services` ma odpowiadać pierwszemu wystąpieniu danej usługi w logach.
- Brakujące lub niepoprawne pola w pojedynczym wpisie logu nie powinny przerywać działania funkcji. Taki wpis pomiń w częściach obliczeń, które wymagają brakującego albo niepoprawnego pola.
- Elementy listy, które nie są słownikami, np. `None` albo tekst, traktuj jako niepoprawne wpisy i pomiń.
- Waliduj dane per pole: wpis bez `level` nie zwiększa `errors` ani `warnings`, ale jeśli ma poprawne `service` i `response_time_ms`, nadal może zostać uwzględniony w `average_response_time_ms` oraz `slow_services`.

Uruchomienie testów publicznych:

```bash
python -m pytest task_implementation/tests_public.py
```

Testy publiczne sprawdzają tylko część przypadków. Rozważ także przypadki brzegowe, np. pustą listę, brak pola `service`, brak pola `response_time_ms` oraz powtórzone usługi.
