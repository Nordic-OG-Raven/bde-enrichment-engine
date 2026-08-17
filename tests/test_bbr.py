from enrichment_engine.bbr import _pick_current


def test_prefers_status_6_over_more_complete_historical_record():
    demolished = {
        "status": "9",
        "byg026Opførelsesår": 1900,
        "byg038SamletBygningsareal": 500,
        "registreringFra": "2024-01-01T00:00:00+01:00",
    }
    current = {
        "status": "6",
        "byg026Opførelsesår": None,
        "byg038SamletBygningsareal": None,
        "registreringFra": "2020-01-01T00:00:00+01:00",
    }
    assert _pick_current([demolished, current]) is current


def test_falls_back_to_most_complete_recent_record_when_no_status_6():
    older_incomplete = {
        "status": "3",
        "byg026Opførelsesår": None,
        "byg038SamletBygningsareal": None,
        "registreringFra": "2020-01-01T00:00:00+01:00",
    }
    newer_complete = {
        "status": "3",
        "byg026Opførelsesår": 1990,
        "byg038SamletBygningsareal": 300,
        "registreringFra": "2021-01-01T00:00:00+01:00",
    }
    assert _pick_current([older_incomplete, newer_complete]) is newer_complete


def test_handles_missing_or_malformed_timestamps():
    no_timestamp = {"status": "3", "byg026Opførelsesår": 1990, "byg038SamletBygningsareal": 300}
    assert _pick_current([no_timestamp]) is no_timestamp


def test_empty_input_returns_none():
    assert _pick_current([]) is None
