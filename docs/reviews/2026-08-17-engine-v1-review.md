# Review — Engine v1 (BBR-only)

Self-review of the first working cut of `enrichment_engine/` (commit `8156af0`),
done deliberately adversarially before this touches a real demo or a prospect.
Findings below; each is marked with its resolution once fixed (see the matching
implementation-log.md entry for the commit that closed it).

## Security

**1. `.env` was created world-readable.** Holds a plaintext password; default file
permissions let any other local user read it.
**Status: Fixed** — `chmod 600 .env`.

**2. The BBR credential is shared, undocumented, load-bearing infrastructure for two
unrelated projects.** Reused from `aarhus_re` without that project knowing this one
exists. If either project's traffic gets the account rate-limited/flagged, both break.
The credential is also hardcoded as a source default in `aarhus_re/config/credentials.py`,
so it's only as safe as that project's git history.
**Status: Fixed 2026-08-19.** `bbr.py` migrated to Datafordeler's GraphQL API on a
dedicated `DATAFORDELER_API_KEY`, no longer touching the shared credential. See the
[2026-08-19 log entry](../implementation-log.md). **Partially open still**: `bfe.py`
(the BFE-number resolution hop for sale-price lookups) remains on the shared REST
credential — its GraphQL equivalent wasn't chased down, tracked in Next Actions.

**3. `config.py` raised a raw `KeyError` with no guidance if `.env` was missing.**
**Status: Fixed** — friendly `RuntimeError` pointing at `.env.example`.

## Reliability / correctness

**4. Zero error handling anywhere, despite PRD 02 requiring graceful failure.**
`address.py` and `bbr.py` let `requests` exceptions propagate raw; no retry/backoff
on `429` despite the precedent project documenting exactly that failure mode.
**Status: Fixed** — typed exceptions (`AddressLookupError`, `BBRLookupError`,
`AddressNotFoundError`), retry-with-backoff on 429 respecting `Retry-After`,
CLI catches and prints a clean message instead of a traceback.

**5. `_pick_current()` ignored the BBR `status` field entirely**, risking silently
surfacing a demolished/historical building record over the current one.
**Status: Fixed, with a caveat.** Confirmed via Datafordeler/BBR Instruks
documentation that `status == "6"` means "opført" (constructed/current) — now
preferred when present. Could not find a fully authoritative table of every status
code (1–9) despite real effort (BBR's own DAWA docs don't publish one); the fallback
heuristic (latest `registreringFra`, parsed as an actual datetime now, not a string)
still applies when no status-6 record exists. Meaningfully better, not provably
complete — worth a proper look if a client engagement ever depends on this being
exactly right rather than demo-good.

**6. `property_profile()` conflated "address not found" and "address found, no BBR
record" into the same `None`.**
**Status: Fixed** — `AddressNotFoundError` raised distinctly; `building=None` now
means specifically "address exists, no BBR building record."

**7. Comparing BBR `registreringFra` timestamps as raw strings isn't guaranteed
chronologically correct across differing UTC offsets (DST boundaries).**
**Status: Fixed** — parsed via `datetime.fromisoformat` and compared as real datetimes.

## Code quality

**8. `scripts/lookup_address.py`'s docstring told the reader to run it in a way that
actually raised `ModuleNotFoundError`** (missing `PYTHONPATH=.`).
**Status: Fixed** — script now bootstraps its own path; docstring corrected.

**9. Type hints were inaccurate** — `total_area_sqm`/`footprint_sqm` typed `float`
when BBR actually returns plain ints.
**Status: Fixed** — retyped `int | None`.

**10. No tests**, despite `_pick_current()` (finding 5) being exactly the kind of
fiddly pure logic worth covering.
**Status: Fixed** — `tests/` added covering `_pick_current` (status-6 preference,
fallback heuristic) and codelist decoding (known code, unknown code fallback).

**11. No logging** — a failed/empty lookup gave no signal about which layer failed.
**Status: Fixed** — `logging` calls added to `address.py` and `bbr.py`, matching the
`aarhus_re` precedent's style.

## Product / user-friendliness

**12. Output was raw BBR codes (`use_code='140'`, `wall_material='1'`), not labels** —
undermining the entire "instant, legible answer" pitch of PRD 02.
**Status: Fixed** — `codelists.py` decodes use/wall/roof/heating codes to Danish
labels (sourced from BBR Instruks, cited in-file), with an explicit
`"Ukendt (kode X)"` fallback for anything not in the mapping rather than silently
dropping data.

**13. No ambiguity signal on address resolution** — a near-miss query silently
resolved to *some* address rather than flagging uncertainty.
**Status: Fixed** — `ResolvedAddress.ambiguous` is set when the address API returns
candidates spanning more than one distinct building. First cut of this compared raw
result count, which false-positived on every normal multi-unit building (one row per
floor/door, same building) - caught immediately by live-testing against "Ryesgade 1"
and corrected to compare distinct `adgangsadresse` IDs instead. Not surfaced in the
CLI yet (v1 script just uses the top match) but available for the Streamlit demo to
warn on.
