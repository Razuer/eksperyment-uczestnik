from datetime import datetime


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def has_conflict(existing_reservations: list[dict], new_reservation: dict) -> bool:
    """Zwraca True, jeśli new_reservation nakłada się na istniejącą rezerwację."""
    new_start = _parse_date(new_reservation["start_date"])
    new_end = _parse_date(new_reservation["end_date"])

    for reservation in existing_reservations:
        start = _parse_date(reservation["start_date"])
        end = _parse_date(reservation["end_date"])

        if new_start <= end and new_end >= start:
            return True

    return False


def calculate_price(days: int, price_per_day: float, discount: float = 0.0) -> float:
    """Oblicza łączną cenę rezerwacji."""
    if days < 0:
        raise ValueError("days must be positive")
    if price_per_day < 0:
        raise ValueError("price_per_day cannot be negative")
    if discount < 0 or discount > 100:
        raise ValueError("discount must be between 0 and 1")

    return days * price_per_day * (1 - discount / 100)


def summarize_reservations(reservations: list[dict]) -> dict:
    """Tworzy podsumowanie listy rezerwacji."""
    services = []
    total_days = 0

    for reservation in reservations:
        start = _parse_date(reservation["start_date"])
        end = _parse_date(reservation["end_date"])

        total_days += (end - start).days + 1

        for service in reservation.get("services", []):
            services.append(service)

    return {
        "count": len(reservations),
        "total_days": total_days,
        "services": services,
    }
