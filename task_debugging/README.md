# Zadanie 2: debugowanie modułu rezerwacji

W pliku `booking.py` znajduje się celowo błędna implementacja prostego modułu rezerwacji. Twoim zadaniem jest poprawić kod tak, aby spełniał poniższą specyfikację i przechodził testy.

## Funkcje do poprawienia

```python
def has_conflict(existing_reservations: list[dict], new_reservation: dict) -> bool:
    ...

def calculate_price(days: int, price_per_day: float, discount: float = 0.0) -> float:
    ...

def summarize_reservations(reservations: list[dict]) -> dict:
    ...
```

## Specyfikacja

### `has_conflict`

Rezerwacje mają pola `start_date` i `end_date` w formacie `YYYY-MM-DD`.

`end_date` oznacza dzień wyjazdu, więc przedziały są półotwarte: `[start_date, end_date)`.

- Rezerwacja kończąca się dokładnie w dniu startu nowej rezerwacji **nie** jest konfliktem.
- Nowa rezerwacja zaczynająca się dokładnie w dniu końca starej rezerwacji **nie** jest konfliktem.
- Rzeczywiste nakładanie się przedziałów jest konfliktem.
- Jeżeli nowa rezerwacja ma nieprawidłowy zakres dat (`start_date >= end_date`), funkcja powinna zgłosić `ValueError`.

### `calculate_price`

Oblicz cenę według wzoru:

```python
days * price_per_day * (1 - discount)
```

Wymagania:

- `days > 0`,
- `price_per_day >= 0`,
- `discount` jest w przedziale `[0, 1]`,
- wynik jest zaokrąglony do 2 miejsc po przecinku,
- niepoprawne wartości powinny powodować `ValueError`.

### `summarize_reservations`

Dla listy rezerwacji zwróć słownik:

```python
{
    "count": liczba_rezerwacji,
    "total_days": łączna_liczba_dni,
    "services": unikalne_usługi_w_kolejności_pierwszego_wystąpienia,
}
```

Dla pustej listy zwróć:

```python
{"count": 0, "total_days": 0, "services": []}
```

Pole `services` w pojedynczej rezerwacji może zawierać listę usług, np. `["breakfast", "parking"]`.

## Wskazówki

Kod startowy zawiera kilka realnych błędów rozsianych po wszystkich trzech funkcjach. Znajdź je samodzielnie, porównując zachowanie kodu ze specyfikacją powyżej i z testami - błędy dotyczą m.in. obsługi dat granicznych, liczenia ceny oraz podsumowania.

Testy publiczne wykrywają tylko część problemów. Testy ukryte mogą sprawdzać dodatkowe przypadki brzegowe, więc warto zweryfikować rozwiązanie również względem specyfikacji.

Uruchomienie testów publicznych:

```bash
python -m pytest task_debugging/tests_public.py
```
