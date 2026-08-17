# PRD 01 — External Data Enrichment Engine

| | |
|---|---|
| Status | v1.1 implemented: BBR + coordinates + units + energy certificate + last sale price — see [2026-08-17 review](../reviews/2026-08-17-engine-v1-review.md) and implementation log |
| Owner | Jonas Haahr |
| Created | 2026-08-17 |
| Last updated | 2026-08-17 |

## Problem

Danish SME data (real estate, agrifood, retail, etc.) lives disconnected from the free,
authoritative public registries that would make it more valuable (BBR, CVR, DMI weather,
GHG emission factors). Today that enrichment happens manually: someone opens a portal,
looks up one record, copies it into Excel. That's the gap this project sells into.

To sell into that gap repeatedly — not as a one-off scripting favor per client — there
needs to be a single, reusable core that knows how to fetch, clean, and join external
registry data to a standard key. Everything client-facing (demos, dashboards, delivery
into a client's Power BI/Business Central) should sit on top of this, not duplicate it.

## Goals

- One Python core that, given a lookup key (address, CVR number, postcode+date), returns
  clean, joined external data — usable from a script, a notebook, a Streamlit app, or
  handed off as a file/table a client's own BI tool can read.
- Zero cost to run. No hosting, no paid API tiers, no client data ever required or stored.
- Sector-agnostic *shape* (a registry client + a normalizer + a join layer), even though
  v1 only implements one sector's registries.

## Non-goals (v1)

- Not a hosted API. No server, no auth, no multi-tenant concerns. Runs locally / from
  whatever demo or notebook imports it.
- Not agrifood, retail, or maritime data sources yet — no client or prospect signal to
  justify that scope. Added only when a specific engagement needs it.
- Not touching any client's internal data (Business Central, e-conomic, CRM). This engine
  only ever handles public, external data — the internal join happens later, per client,
  outside this engine's scope, which is also what keeps this GDPR/DPA-light.
- No caching/rate-limit infrastructure beyond simple politeness delays — current expected
  call volume (manual demos, low-volume client lookups) doesn't justify it yet.

## Scope — v1.1 data sources (Real Estate)

| Source | Registry | What it returns | Official? |
|---|---|---|---|
| Dataforsyningen (free, no auth) | Adresser | address resolution + adgangsadresse ID, kommunekode, WGS84 lon/lat | Yes |
| Datafordeler.dk | BBR (Bygnings- og Boligregistret) | building fields (area, year, materials, heating) + per-unit breakdown | Yes, documented REST |
| Datafordeler.dk | DAR_BFE_Public | husnummer → BFE number (join key for OIS) | Yes, documented REST |
| tjekenergimaerke.emoweb.dk | Energimærke | current/historic energy certificate class | **No** — unofficial public search form, no auth. See `energimaerke.py` docstring. |
| ois.dk | SVUR (via OIS) | most recent sale price + date | **No** — unofficial API, reverse-engineered (by `aarhus_re`, reused here). See `ois.py` docstring. |

**CVR moved out of v1** (2026-08-17) — see the Open Questions log below. Deferred to
when needed: Tinglysning (deeds/mortgages/easements — paid/restricted access, needs its
own access-cost evaluation), PlanSystemDK zoning.

**On the two unofficial sources**: energy certificate and sale-price data don't have a
practical official/documented path (the real ones — EMOData, EJF via Datafordeler —
need separate approval processes; see implementation log). Both are wired as
best-effort (return `None` on failure rather than raising) specifically because
they're not sanctioned APIs and could break on a markup/behavior change without
notice — a demo showing "no data available" for one field is fine; a demo crashing
because an unofficial scrape broke is not. Worth revisiting if either becomes
business-critical rather than a demo enhancement.

## Functional requirements

1. **Fetch**: given an address or CVR number, call Datafordeler.dk's BBR/CVR endpoints
   and return raw JSON.
2. **Normalize**: map raw registry fields to a stable, documented internal schema
   (so a future second source for the same concept — e.g. a paid aggregator instead of
   raw Datafordeler — can be swapped in without changing anything downstream).
3. **Join**: given multiple lookups sharing a key (CVR number, BFE/ejendomsnummer,
   postcode), return one combined record — e.g. "property profile" = BBR + owning CVR
   entity in a single object.
4. **Output**: return a plain Python object (dict/dataclass) or a pandas DataFrame.
   No opinion on presentation — that's the demo/delivery layer's job.

## Architecture

- Language: Python 3.11+, matching existing tooling conventions.
- HTTP: `requests` — matches proven precedent (`aarhus_re`'s BBR collector) and keeps
  dependencies minimal.
- Data shaping: plain dataclasses, not `pandas`. The precedent project needed pandas
  because it bulk-fetched 200k+ rows for ML training; this engine does single-record
  lookups, where pandas is unnecessary weight. Keeping dependencies to just `requests`
  matters beyond v1: if this code ever runs inside a client's environment (an Azure
  Function, a Power Automate step), fewer/heavier dependencies is friction worth
  avoiding in someone else's tenant.
- No database required for v1 — outputs are computed on demand. Add SQLite/DuckDB only
  if repeated demo queries make on-demand fetching too slow or Datafordeler rate limits
  become a problem.
- Packaged as an importable module (`enrichment_engine/`), not a script — so the
  Streamlit demo (Product 2) and any future client delivery code import it the same way.

## Success criteria (v1 done when)

- Given a Danish address, the engine returns a normalized property profile (BBR fields +
  owning CVR entity) in under a few seconds, with zero cost incurred.
- The BBR/CVR clients and the normalization layer are separated cleanly enough that
  adding a second sector's source later doesn't require touching existing code.
- Product 2 (the Streamlit demo) can import and call this engine directly with no
  duplicated fetch/normalize logic of its own.

## Open questions

- ~~Datafordeler.dk requires a (free) registered account/token — confirm exact auth flow
  and rate limits before committing to it as the sole v1 source.~~ **Resolved for BBR,
  2026-08-17**: a working tjenestebruger account already exists (from the `aarhus_re`
  project) — username/password as query params, live-tested against
  `BBR/BBRPublic/1/REST/Bygning` today, returns HTTP 200. Rate limit observed
  previously: 429 with `Retry-After`, 2s between paged requests was sufficient.
  **Resolved for CVR, 2026-08-17**: the BBR tjenestebruger does *not* carry over.
  CVR access is a separate, heavier process either way: the modern path needs MitID
  Erhverv + OAuth requested via the Datafordeler Administration portal; the legacy
  REST path (itself being phased out by end of 2026, Datafordeler-wide) needs an
  email request to cvrselvbetjening@erst.dk, mandatory IPv4 whitelisting, and a
  separate web+service user. No free, fast path exists today. Third-party wrappers
  (cvr.dev) are free for 30 days only, then paid. **Decision: CVR is out of v1
  scope.** Submit the free MitID Erhverv/OAuth access request now (no reason not
  to, given the lead time), but don't block the engine or demo on it — a BBR-only
  property profile is still a legitimate "wow" versus manual portal lookups, and
  CVR/ownership data becomes a v1.1 addition once access is approved or a specific
  client engagement justifies the extra build. See PRD 02 for the resulting scope
  change.
- Real-vs-build call: BoligIQ / Accobat's Datadrevet Ejendom already sell pre-joined
  registry aggregations — worth a cheap check on their pricing/access before investing
  further engine time in raw BBR+CVR joining, in case reselling is cheaper than building.
  Leaning build: existing precedent code (`aarhus_re/src/data/collectors/bbr.py`) shows
  BBR fetch+normalize is ~150 lines for a bulk pull, likely 50–80 for a single-address
  lookup; CVR lookup-by-number is typically a single GET call. Full engine (BBR + CVR +
  join) estimated at 150–250 lines total — low enough effort that buying access looks
  hard to justify unless CVR auth turns out to be a real blocker.
