from enrichment_engine import codelists


def test_decodes_known_code():
    assert codelists.decode(codelists.WALL_MATERIAL, "1") == "Mursten (tegl, kalksandsten, cementsten)"


def test_unknown_code_gets_visible_fallback_not_silently_dropped():
    assert codelists.decode(codelists.WALL_MATERIAL, "999") == "Ukendt (kode 999)"


def test_none_code_stays_none():
    assert codelists.decode(codelists.WALL_MATERIAL, None) is None


def test_summerhouse_use_code_decodes():
    # Added after a real address (a summer house) hit this as an unmapped
    # code - regression guard against it silently reverting to "Ukendt".
    assert codelists.decode(codelists.USE_CODE, "510") == "Sommerhus"
