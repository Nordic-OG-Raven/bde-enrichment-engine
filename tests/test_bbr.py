from enrichment_engine.bbr import _pick_current, _pick_current_per_unit

YEAR_FIELD = "byg026Opførelsesår"
AREA_FIELD = "byg038SamletBygningsareal"


def test_prefers_status_6_over_more_complete_historical_record():
    demolished = {
        "status": "9",
        YEAR_FIELD: 1900,
        AREA_FIELD: 500,
        "registreringFra": "2024-01-01T00:00:00+01:00",
    }
    current = {
        "status": "6",
        YEAR_FIELD: None,
        AREA_FIELD: None,
        "registreringFra": "2020-01-01T00:00:00+01:00",
    }
    assert _pick_current([demolished, current], YEAR_FIELD, AREA_FIELD) is current


def test_falls_back_to_most_complete_recent_record_when_no_status_6():
    older_incomplete = {
        "status": "3",
        YEAR_FIELD: None,
        AREA_FIELD: None,
        "registreringFra": "2020-01-01T00:00:00+01:00",
    }
    newer_complete = {
        "status": "3",
        YEAR_FIELD: 1990,
        AREA_FIELD: 300,
        "registreringFra": "2021-01-01T00:00:00+01:00",
    }
    assert _pick_current([older_incomplete, newer_complete], YEAR_FIELD, AREA_FIELD) is newer_complete


def test_handles_missing_or_malformed_timestamps():
    no_timestamp = {"status": "3", YEAR_FIELD: 1990, AREA_FIELD: 300}
    assert _pick_current([no_timestamp], YEAR_FIELD, AREA_FIELD) is no_timestamp


def test_empty_input_returns_none():
    assert _pick_current([], YEAR_FIELD, AREA_FIELD) is None


def test_pick_current_per_unit_groups_by_unit_id_independently():
    unit_a_old = {"id_lokalId": "a", "status": "3", "registreringFra": "2020-01-01T00:00:00+01:00"}
    unit_a_new = {"id_lokalId": "a", "status": "6", "registreringFra": "2021-01-01T00:00:00+01:00"}
    unit_b_only = {"id_lokalId": "b", "status": "3", "registreringFra": "2019-01-01T00:00:00+01:00"}

    result = _pick_current_per_unit([unit_a_old, unit_a_new, unit_b_only])

    assert len(result) == 2
    assert unit_a_new in result
    assert unit_b_only in result
    assert unit_a_old not in result
