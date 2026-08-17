from streamlit.testing.v1 import AppTest


def _run(address: str) -> AppTest:
    at = AppTest.from_file("streamlit_app.py")
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


def test_not_found_shows_friendly_error_not_a_traceback():
    at = _run("Nonexistentgade 99999, 8000 Aarhus")
    assert not at.exception
    assert len(at.error) == 1
    assert "Kunne ikke finde" in at.error[0].value


def test_vague_query_shows_ambiguous_warning():
    at = _run("Aarhus")
    assert not at.exception
    assert len(at.warning) == 1
