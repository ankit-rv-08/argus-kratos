import pandas as pd

from tools import (
    _billions,
    _headline,
    _percent_delta,
    _risk_vectors,
    _safe_calculate,
    _statement_value,
)


def _sample_statement():
    return pd.DataFrame(
        {"2025": [500.0, 300.0], "2024": [450.0, 280.0]},
        index=["Total Assets", "Total Liabilities"],
    )


def test_statement_value_reads_first_column_by_default():
    assert _statement_value(_sample_statement(), ("Total Assets",)) == 500.0


def test_statement_value_reads_prior_column():
    assert _statement_value(_sample_statement(), ("Total Assets",), column=1) == 450.0


def test_statement_value_tries_fallback_labels():
    assert _statement_value(
        _sample_statement(),
        ("Total Liabilities Net Minority Interest", "Total Liabilities"),
    ) == 300.0


def test_statement_value_missing_label_returns_zero():
    assert _statement_value(_sample_statement(), ("Nonexistent Field",)) == 0.0


def test_statement_value_none_statement_returns_zero():
    assert _statement_value(None, ("Total Assets",)) == 0.0


def test_statement_value_empty_statement_returns_zero():
    assert _statement_value(pd.DataFrame(), ("Total Assets",)) == 0.0


def test_billions_converts():
    assert _billions(5_000_000_000) == 5.0


def test_billions_zero_stays_zero():
    assert _billions(0) == 0.0


def test_percent_delta_normal():
    assert _percent_delta(110, 100) == "+10.0%"


def test_percent_delta_no_prior_is_na():
    assert _percent_delta(110, 0) == "N/A"


def test_headline_direct_title():
    assert _headline({"title": "Apple hits new high"}) == "Apple hits new high"


def test_headline_nested_content_title():
    assert _headline({"content": {"title": "Nested title"}}) == "Nested title"


def test_headline_fallback():
    assert _headline({}) == "Market update"


def test_safe_calculate_normal():
    assert _safe_calculate("a / b", {"a": 10, "b": 4}) == 2.5


def test_safe_calculate_missing_variable_returns_zero_not_crash():
    assert _safe_calculate("a + b", {"a": 1}) == 0.0


def test_safe_calculate_division_by_zero_returns_zero_not_crash():
    assert _safe_calculate("a / b", {"a": 5, "b": 0}) == 0.0


class FakeStock:
    def __init__(self, news):
        self.news = news


def test_risk_vectors_uses_injected_model_not_real_one():
    result = _risk_vectors(
        FakeStock([{"title": "Company beats earnings"}]),
        analyze_fn=lambda title: {"sentiment": "Bullish"},
    )
    assert result[0]["severity"] == "LOW"
    assert "Bullish" in result[0]["text"]


def test_risk_vectors_bearish_marks_watch():
    result = _risk_vectors(
        FakeStock([{"title": "Company misses earnings"}]),
        analyze_fn=lambda title: {"sentiment": "Bearish"},
    )
    assert result[0]["severity"] == "WATCH"


def test_risk_vectors_no_news_returns_default():
    result = _risk_vectors(
        FakeStock([]),
        analyze_fn=lambda title: {"sentiment": "Neutral"},
    )
    assert result[0]["title"] == "News telemetry unavailable"
