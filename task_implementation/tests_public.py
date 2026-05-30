from .solution import analyze_logs


def test_analyze_logs_basic_counts_and_average():
    logs = [
        {"level": "INFO", "service": "api", "response_time_ms": 100},
        {"level": "ERROR", "service": "payments", "response_time_ms": 500},
        {"level": "WARN", "service": "api", "response_time_ms": 250},
    ]

    assert analyze_logs(logs, timeout_ms=300) == {
        "errors": 1,
        "warnings": 1,
        "average_response_time_ms": 283,
        "slow_services": ["payments"],
    }


def test_analyze_logs_empty_input():
    assert analyze_logs([], timeout_ms=100) == {
        "errors": 0,
        "warnings": 0,
        "average_response_time_ms": 0,
        "slow_services": [],
    }


def test_analyze_logs_ignores_incomplete_entries_for_relevant_parts():
    logs = [
        {"level": "ERROR"},
        {"service": "api", "response_time_ms": 150},
        {"level": "WARN", "service": "search", "response_time_ms": "slow"},
        {"level": "INFO", "service": "api", "response_time_ms": 200},
    ]

    result = analyze_logs(logs, timeout_ms=100)

    assert result["errors"] == 1
    assert result["warnings"] == 1
    assert result["average_response_time_ms"] == 175
    assert result["slow_services"] == ["api"]


def test_analyze_logs_keeps_first_occurrence_order_for_slow_services():
    logs = [
        {"level": "INFO", "service": "search", "response_time_ms": 450},
        {"level": "INFO", "service": "api", "response_time_ms": 300},
        {"level": "INFO", "service": "search", "response_time_ms": 700},
        {"level": "INFO", "service": "billing", "response_time_ms": 301},
    ]

    assert analyze_logs(logs, timeout_ms=300)["slow_services"] == ["search", "billing"]
