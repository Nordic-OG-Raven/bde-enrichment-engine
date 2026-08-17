from enrichment_engine.ois import _parse_price


def test_parses_danish_thousands_separators():
    assert _parse_price("28.500.000 DKK") == 28500000


def test_parses_small_amount():
    assert _parse_price("850.000 DKK") == 850000


def test_none_input_returns_none():
    assert _parse_price(None) is None


def test_empty_string_returns_none():
    assert _parse_price("") is None
