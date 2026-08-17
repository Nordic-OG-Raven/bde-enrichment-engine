from enrichment_engine.energimaerke import _parse_results

# Structure mirrors the real singleDataTable markup (verified live 2026-08-17):
# 11+ <td> cells per row, class index 5, historic rows flagged via a CSS class.
ROW_TEMPLATE = (
    "<tr class='{cls}'>" + "".join(f"<td>{i}</td>" for i in range(5)) +
    "<td>{energy_class}</td><td>{nr}</td><td>{fra}</td><td>{til}</td><td>x</td><td>x</td></tr>"
)


def _table(rows_html: str) -> str:
    return f"<table id='singleDataTable'><tbody>{rows_html}</tbody></table>"


def test_parses_a_current_certificate():
    html = _table(ROW_TEMPLATE.format(cls="", energy_class="C", nr="123", fra="01/01/2020", til="01/01/2030"))
    results = _parse_results(html)
    assert len(results) == 1
    assert results[0]["energy_class"] == "C"
    assert results[0]["is_historic"] is False


def test_flags_historic_rows():
    html = _table(ROW_TEMPLATE.format(cls="historic-entry", energy_class="D", nr="1", fra="x", til="x"))
    results = _parse_results(html)
    assert results[0]["is_historic"] is True


def test_missing_table_returns_empty_list_not_an_error():
    assert _parse_results("<html><body>no table here</body></html>") == []


def test_row_with_too_few_cells_is_skipped():
    html = _table("<tr><td>only</td><td>a</td><td>few</td></tr>")
    assert _parse_results(html) == []
