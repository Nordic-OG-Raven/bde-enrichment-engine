# Implementation Log

This is the permanent frame of reference for the Big Data Energy project: what's true
right now, and a dated, append-only history of how we got here. Update "Current State"
in place every time it changes; never edit past entries in the Log — add a new one.

---

## Current State

**As of 2026-08-17 (updated)**

- **Engine v1 (BBR-only) is implemented and working.** `enrichment_engine/` resolves a
  free-text Danish address (via Dataforsyningen, free/no auth) and returns a normalized
  `PropertyProfile` with BBR building data (year built, area, floors, wall/roof
  material, heating type). Tested end-to-end against two real Aarhus addresses.
  Run via `PYTHONPATH=. python scripts/lookup_address.py "<address>"` (venv at
  `.venv/`, deps in `requirements.txt`, credentials in `.env` — gitignored).
- Open question 1 (Datafordeler.dk auth) resolved for BBR: a working tjenestebruger
  account already exists, reused from the `aarhus_re` project (at
  `/Users/jonas/aarhus_re`), live-tested — HTTP 200, confirmed working.
- **CVR is out of v1 scope.** It's not a matter of reusing the BBR credential — CVR
  access requires its own request/approval process (MitID Erhverv+OAuth, or legacy
  REST with mandatory IP whitelisting), with no free instant path. Decision: ship the
  BBR-only demo first; submit the free CVR access request in parallel since it has
  lead time regardless.
- Build-vs-buy on BoligIQ/Accobat: leaning build, given proven low code volume and
  now-working BBR access. Not fully closed — still worth a cheap pricing check on
  their side — but no longer blocking.
- Engine architecture: `requests` only, no `pandas` — precedent project needed pandas
  for bulk ML-training pulls; this engine's single-record lookups don't, and lighter
  dependencies are more portable into a future client's environment.
- Heads-up for later: Datafordeler REST (the API style used here) is being phased out
  Datafordeler-wide by end of 2026 in favor of GraphQL. Not a v1 concern (months of
  runway), but worth remembering before investing heavily in more REST-based fetches.

- SMV:Digital advisor status: **approved** (approval email received 2026-08-17).
  CV still needs finishing on ehmidt.dk — open items: which email inbox to list,
  full LinkedIn URL, hourly rate, named vs. anonymized SME reference. Onboarding
  webinar deadline: **2026-11-17** (3 months from approval).
- Clients: **zero**. Fully pre-revenue, fully flexible on sector/tooling.
- Products in scope right now: two.
  1. [External Data Enrichment Engine](prd/01-external-data-enrichment-engine.md) — not started.
  2. [Real Estate Prospecting Demo](prd/02-real-estate-prospecting-demo.md) — not started, depends on (1).
- No code written yet. No repo dependencies installed yet.
- Strategic direction: deliberately narrower than the original sector-broad plan
  (see `strategy/` for the superseded four-sector research — kept as background,
  not a binding roadmap). Current approach: build the cheapest possible free proof
  of value in one sector (real estate), let the first real client's actual tooling
  (Power BI or otherwise) dictate delivery mechanics, rather than pre-committing to
  a tool or building infrastructure across sectors before there's demand signal.

## Next actions

1. Build the Streamlit demo (PRD 02) on top of the working engine.
2. Submit the free CVR access request (MitID Erhverv + OAuth via Datafordeler
   Administration) in parallel — not blocking, but has lead time.
3. Get the demo in front of one real prospect.
4. (Optional, not blocking) Cheap pricing check on BoligIQ/Accobat, mostly to settle
   the build-vs-buy question fully rather than because it's needed.

---

## Log

### 2026-08-17 — Built and tested the v1 (BBR-only) engine; CVR moved out of scope

Scaffolded `enrichment_engine/` (Python 3.12, venv, `requests` + `python-dotenv` only):

- `address.py` — resolves a free-text address to an adgangsadresse ID via
  Dataforsyningen's free, unauthenticated `/adresser` API. Confirmed the returned
  `adgangsadresse.id` is the same UUID BBR calls `husnummer`.
- `bbr.py` — queries `BBR/BBRPublic/1/REST/Bygning` filtered by `husnummer` (confirmed
  this filter param works via a live test), then normalizes to a `BuildingProfile`.
  BBR returns full registration history per building, not just current state, so
  `_pick_current()` heuristically picks the record with populated year/area fields
  and the latest `registreringFra` — worth revisiting if a client engagement needs
  provably-current-only data rather than "good enough for a demo."
- `engine.py` — ties the two together into `property_profile(address) -> PropertyProfile`.
- Tested end-to-end against two real Aarhus addresses (Ryesgade 1, Park Allé 5) —
  both returned plausible BBR data (year built, area, floors, materials).

Then investigated CVR access (the other open question) via web search, since the BBR
credential turned out not to transfer:

- Official Datafordeler CVR REST requires emailing cvrselvbetjening@erst.dk, mandatory
  IPv4 whitelisting, and a separate web+service user — and REST itself is being phased
  out Datafordeler-wide by end of 2026.
- The modern replacement (CVRPerson entity) needs MitID Erhverv + OAuth via the
  Datafordeler Administration portal.
- cvr.dev (third-party wrapper) is free for 30 days only, then paid.
- No free, fast path exists. **Decision: drop CVR from v1**, ship the BBR-only demo
  (still a real "wow" vs. manual portal lookups on its own), and submit the free
  MitID Erhverv/OAuth request in parallel since it costs nothing but time-to-approve.
  PRD 01 and PRD 02 updated accordingly.

### 2026-08-17 — Resolved BBR auth; revised engine dependencies

Went over PRD 01's two open questions in detail:

1. **Datafordeler.dk auth**: found an existing, already-working tjenestebruger account
   in the unrelated `aarhus_re` project (`/Users/jonas/aarhus_re/config/credentials.py`),
   originally set up there to pull BBR data for an ML training set (213k buildings,
   254k units, Aarhus kommune). That project's notes flagged a phaseout of the
   webbruger/tjenestebruger auth system dated 30 June 2026, in favor of MitID Erhverv +
   OAuth — a real risk since today is well past that date. Live-tested with a single
   GET to `BBR/BBRPublic/1/REST/Bygning`: **HTTP 200, valid data**. The old auth still
   works, at least for this endpoint (the phaseout note may have applied only to a
   different, already-blocked Zone-5 endpoint). CVR auth remains unconfirmed — the
   precedent project never queried CVR, only BBR and cadastral (Matrikel) data.
   Reassuring fallback if CVR does need the new OAuth flow: it explicitly requires a
   CVR number to enroll, and Nordic Raven Solutions (CVR 46097750) qualifies.
2. **Build vs. buy (BoligIQ/Accobat)**: leaning build. The precedent BBR collector is
   156 lines for a full bulk pull; a single-address lookup (what the engine actually
   needs) is simpler still. Estimated full engine (BBR + CVR + join) at 150–250 lines —
   low enough that buying access is hard to justify unless CVR auth turns out to be a
   real blocker. Not fully closed (still worth a cheap look at their pricing), but no
   longer gating anything.

Also revised PRD 01's architecture: dropped `pandas` as a dependency for v1. The
precedent project needed it for bulk ML-training pulls; this engine's single-record
lookups don't, and a lighter (`requests`-only) dependency footprint is more portable
if this code ever needs to run inside a future client's environment.

### 2026-08-17 — Re-scoped from four-sector plan to two products

Original planning docs (`strategy/big-data-energy-strategic-analysis.md` and
`strategy/big-data-energy-implementation-plan.md`, both dated 2026-07-04/05) proposed
a broad four-sector rollout (real estate, agrifood, retail, maritime) with Power BI as
the fixed delivery vehicle from day one, and a Phase 1 that included building a general
"connector library" across sources before any client existed.

Revisited from scratch given: (a) it's been over a month since the SMV:Digital
application was drafted, (b) there are still zero clients, and (c) budget is
effectively zero until a client is signed. Conclusion: the old plan front-loaded
infrastructure and tool commitment before there was any market signal to justify it.

Decisions made:
- **Tool-agnostic core, opportunistic presentation layer.** Don't commit to Power BI
  as the build tool before a client's actual stack is known. Power BI Desktop is free
  to author in (only Pro, needed for sharing, typically ends up being the client's
  existing spend) — so the earlier "no budget for Power BI" constraint was partly a
  misconception, but the tool-agnostic core decision stands independent of that, since
  the real risk was locking business logic into Power Query M before knowing who the
  client even is.
- **Two products only, not a sector-wide build-out.** External Data Enrichment Engine
  (durable, sector-agnostic Python core) + Real Estate Prospecting Demo (Streamlit,
  first-sector proof of value, sales tool not revenue product). Agrifood/retail/
  maritime get their own PRD only when a real prospect in that sector justifies it.
- **Real estate stays the first sector** — sharpest "wow" story (multi-portal manual
  lookup collapsed into one instant query), cheapest to demo (pure public data, no
  client data / NDA involved), single clean free API (Datafordeler.dk BBR+CVR).
- Wrote PRD 01 and PRD 02 (this session) to formalize scope before writing any code.

Old strategy docs moved to `docs/strategy/` — kept as background/inspiration per
their own conclusions on sector selection and Danish SME digitalization context, but
explicitly not binding on tooling or phasing anymore.
