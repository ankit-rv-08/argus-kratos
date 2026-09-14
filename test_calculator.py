import pytest

from calculator import calculate


def test_basic_arithmetic():
    assert calculate("a + b", {"a": 2, "b": 3}) == 5.0
    assert calculate("a - b", {"a": 5, "b": 3}) == 2.0
    assert calculate("a * b", {"a": 4, "b": 2}) == 8.0
    assert calculate("a / b", {"a": 10, "b": 4}) == 2.5


def test_nested_expression():
    assert calculate("(a - b) / c", {"a": 10, "b": 4, "c": 3}) == 2.0


def test_missing_variable_raises_keyerror():
    with pytest.raises(KeyError):
        calculate("a + b", {"a": 1})


def test_disallowed_function_call_raises_valueerror():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('echo pwned')", {})


def test_disallowed_string_constant_raises_valueerror():
    with pytest.raises(ValueError):
        calculate("'not a number'", {})


def test_division_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        calculate("a / b", {"a": 5, "b": 0})
