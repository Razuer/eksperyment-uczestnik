import pytest

from .booking import calculate_price, has_conflict, summarize_reservations


def test_has_conflict_detects_real_overlap():
    existing = [
        {"start_date": "2026-06-10", "end_date": "2026-06-15"},
    ]
    new = {"start_date": "2026-06-14", "end_date": "2026-06-18"}

    assert has_conflict(existing, new) is True


def test_has_conflict_allows_touching_checkout_and_checkin_dates():
    existing = [
        {"start_date": "2026-06-10", "end_date": "2026-06-15"},
    ]

    assert has_conflict(existing, {"start_date": "2026-06-15", "end_date": "2026-06-18"}) is False
    assert has_conflict(existing, {"start_date": "2026-06-01", "end_date": "2026-06-10"}) is False


def test_has_conflict_rejects_invalid_new_range():
    existing = [
        {"start_date": "2026-06-10", "end_date": "2026-06-15"},
    ]

    with pytest.raises(ValueError):
        has_conflict(existing, {"start_date": "2026-06-20", "end_date": "2026-06-20"})


def test_calculate_price_applies_fractional_discount_and_rounds():
    assert calculate_price(days=3, price_per_day=99.999, discount=0.10) == 270.0


def test_calculate_price_rejects_invalid_values():
    with pytest.raises(ValueError):
        calculate_price(days=0, price_per_day=100.0)

    with pytest.raises(ValueError):
        calculate_price(days=2, price_per_day=-1.0)

    with pytest.raises(ValueError):
        calculate_price(days=2, price_per_day=100.0, discount=1.5)


def test_summarize_reservations_empty_list():
    assert summarize_reservations([]) == {"count": 0, "total_days": 0, "services": []}


def test_summarize_reservations_counts_days_and_unique_services_in_order():
    reservations = [
        {
            "start_date": "2026-07-01",
            "end_date": "2026-07-04",
            "services": ["breakfast", "parking"],
        },
        {
            "start_date": "2026-07-10",
            "end_date": "2026-07-12",
            "services": ["parking", "spa"],
        },
    ]

    assert summarize_reservations(reservations) == {
        "count": 2,
        "total_days": 5,
        "services": ["breakfast", "parking", "spa"],
    }
