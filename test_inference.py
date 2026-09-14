from inference import _parse_model_output


def test_parses_clean_json():
    result = _parse_model_output('{"sentiment": "Bullish", "risk_factor": "strong demand"}')
    assert result["sentiment"] == "Bullish"


def test_parses_json_with_surrounding_text():
    result = _parse_model_output(
        'Sure, here you go: {"sentiment": "Bearish", "risk_factor": "export curbs"}'
    )
    assert result["sentiment"] == "Bearish"


def test_marks_unparseable_instead_of_faking_neutral():
    result = _parse_model_output("Sentiment: Bullish")
    assert result["sentiment"] == "Unparseable"
    assert result["parse_error"] is True
