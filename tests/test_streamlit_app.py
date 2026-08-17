from streamlit.testing.v1 import AppTest


TIMEOUT = 20  # real network calls (address + building + per-building unit lookups)


def _run(address: str) -> AppTest:
    at = AppTest.from_file("streamlit_app.py", default_timeout=TIMEOUT)
    at.run()
    at.text_input[0].input(address).run()
    at.button[0].click().run()
    return at


def test_happy_path_shows_building_metrics_and_untruncated_details():
    at = _run("Ryesgade 1, 8000 Aarhus")
    assert not at.exception
    assert not at.error
    metric_labels = [m.label for m in at.metric]
    assert "Opførelsesår" in metric_labels

    markdown_text = " ".join(m.value for m in at.markdown)
    write_text = " ".join(str(w.value) for w in at.get("write"))
    assert "Anvendelse" in markdown_text
    # The full label text should be present, not cut off with an ellipsis -
    # this is the truncation bug the st.metric layout had.
    assert "…" not in write_text


def test_multi_unit_building_shows_map_and_units_table():
    at = _run("Guldsmedgade 21, 8000 Aarhus")
    assert not at.exception
    assert not at.error
    assert len(at.get("deck_gl_json_chart") + at.get("map")) >= 1  # st.map renders as one of these
    # Plain link fallback - can't fail the way a tile-loading JS map can, so
    # this should always be present whenever coordinates are available,
    # independent of whether st.map's own rendering works in a given browser.
    markdown_text = " ".join(m.value for m in at.markdown)
    assert "Google Maps" in markdown_text
    subheader_text = " ".join(s.value for s in at.subheader)
    assert "Enheder" in subheader_text
    assert len(at.dataframe) == 1


def test_shows_energy_label_when_available():
    at = _run("Guldsmedgade 21, 8000 Aarhus")
    assert not at.exception
    metric_labels = {m.label: m.value for m in at.metric}
    assert "Energimærke" in metric_labels
    assert metric_labels["Energimærke"] in {"A", "B", "C", "D", "E", "F", "G"}


def test_shows_last_sale_price_when_available():
    at = _run("Guldsmedgade 21, 8000 Aarhus")
    assert not at.exception
    metric_labels = {m.label: m.value for m in at.metric}
    assert "Seneste salg" in metric_labels
    assert "kr." in metric_labels["Seneste salg"]


def test_not_found_shows_friendly_error_not_a_traceback():
    at = _run("Nonexistentgade 99999, 8000 Aarhus")
    assert not at.exception
    assert len(at.error) == 1
    assert "Kunne ikke finde" in at.error[0].value


def test_vague_query_shows_ambiguous_warning():
    at = _run("Aarhus")
    assert not at.exception
    assert len(at.warning) == 1
