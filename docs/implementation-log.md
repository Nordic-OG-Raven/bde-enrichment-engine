# Implementation Log

This is the permanent frame of reference for the Big Data Energy project: what's true
right now, and a dated, append-only history of how we got here. Update "Current State"
in place every time it changes; never edit past entries in the Log — add a new one.

---

## Current State

**As of 2026-08-17 (updated again — post self-review)**

- **Engine v1 (BBR-only) is implemented, self-reviewed, and hardened.**
  `enrichment_engine/` resolves a free-text Danish address (via Dataforsyningen,
  free/no auth) and returns a normalized `PropertyProfile` with BBR building data
  (year built, area, floors, wall/roof material, heating type) — now decoded to
  human-readable Danish labels, not raw codes. Errors are typed and caught (no raw
  tracebacks), 429s retry with backoff, `.env` is permission-locked, and 7 tests
  cover the fiddly logic. Full findings + resolutions in
  [docs/reviews/2026-08-17-engine-v1-review.md](reviews/2026-08-17-engine-v1-review.md).
  Run via `python scripts/lookup_address.py "<address>"` (venv at `.venv/`, prod deps
  in `requirements.txt`, dev+test deps in `requirements-dev.txt`, credentials in
  `.env` — gitignored, chmod 600).
- **Dedicated BDE Datafordeler Administration account now exists** (owner: Jonas
  Haahr, org: Nordic Raven Solutions, CVR 46097750), with its own IT-system
  (`bde-enrichment-engine`) holding an API-key and an OAuth Shared Secret — see the
  dated log entry below for full metadata. This is groundwork for CVR, not yet a fix
  for the BBR finding: Datafordeler Administration's own copy describes API-keys/
  OAuth as granting access "via Fildownload (HTTPS) og GraphQL" — a different auth
  model from the legacy REST endpoints `bbr.py` currently calls. So the BBR credential
  is still shared with `aarhus_re` for now; this new account unblocks CVR specifically,
  not a drop-in BBR replacement. Needs confirming either way before assuming otherwise.
  **Update, same day, confirmed from Datafordeler's own access guidance**: only the
  `CVRPerson` entity is access-restricted. Every other CVR entity (basic company
  data) is unrestricted and already fetchable with the existing credentials — no
  Dataadgang request needed for that. Full guidance captured at
  [docs/reference/datafordeler-access.md](reference/datafordeler-access.md).
  **`CVRPerson` access request: submitted 2026-08-17, status "Ny" (pending), no
  attachment included** — the guidance never called for one and the form didn't
  mark it required, so none was sent. Small residual risk Erhvervsstyrelsen asks
  for more information before approving; low-effort to supply if/when they do,
  not worth pre-empting with a document to a spec we don't actually have. IP
  `83.94.224.228` (this machine's current network) registered as `/32` on the
  IT-system — required before Datafordeler would even accept a Dataadgang request,
  not documented anywhere until the portal's own error surfaced it.
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

1. Build a `cvr.py` module for basic (non-`CVRPerson`) company lookup — confirmed
   unrestricted, no approval wait needed. Worth doing before or alongside the
   Streamlit demo since it's now unblocked.
2. Build the Streamlit demo (PRD 02) on top of the working engine. **Before/when
   deploying it to a cloud host** (Streamlit Community Cloud per PRD 02): if the
   demo ever needs live calls to `CVRPerson` or any other OAuth/IP-whitelisted
   Datafordeler service, that host's outbound IP will need registering on the
   IT-system too — and free hosting tiers often don't give a fixed IP, which could
   be a real obstacle, not just paperwork. Not a problem yet (local dev only,
   and the v1 demo doesn't use CVR at all), but don't assume "it works locally"
   implies "it'll work once deployed" for anything IP-gated.
3. `CVRPerson` Dataadgang request: submitted 2026-08-17, status "Ny" — check back
   for approval; not blocking anything else in the meantime.
4. Confirm whether the Administration API-key/OAuth credentials authenticate
   against classic REST endpoints too, or are GraphQL/Fildownload-only as
   Administration's own copy suggests — decides whether `cvr.py` can reuse
   `bbr.py`'s REST pattern or needs a GraphQL client instead.
5. Get the demo in front of one real prospect.
6. Decouple the BBR REST credential from `aarhus_re` (2026-08-17 review, finding 2) —
   still open; the new Administration account's scope relative to BBR is unconfirmed
   per item 4 above.
7. (Optional, not blocking) Cheap pricing check on BoligIQ/Accobat, mostly to settle
   the build-vs-buy question fully rather than because it's needed.
8. (Separate project, noted for whenever it's relevant) `aarhus_re` could retry EJF
   sale-price data via the proper Administration + MitID Erhverv + bilag path
   documented in [docs/reference/datafordeler-access.md](reference/datafordeler-access.md)
   — its earlier ad-hoc REST attempt was blocked on IP whitelisting for the wrong
   reason (wrong path, not a hard no).

---

## Log

### 2026-08-17 — Confirmed CVR access tiers from Datafordeler's own guidance; applying for CVRPerson anyway

Pulled the full "Vejledning og bilag til ansøgning" content from inside Datafordeler
Administration (authenticated portal — captured in full at
[docs/reference/datafordeler-access.md](reference/datafordeler-access.md) since it
can't be re-fetched later without logging back in). This settles something the
earlier web-search-based research had only indirectly suggested: Erhvervsstyrelsen's
own text states plainly that **only `CVRPerson` needs an access request** — every
other CVR entity is unrestricted and already usable with the existing
`bde-enrichment-engine` credentials, no waiting required.

Decision: apply for `CVRPerson` access anyway, despite it not being needed for
anything currently in scope. Reasoning — unlike writing code ahead of need, an
access *request* has a real approval lead time and zero ongoing cost, so applying
now is free optionality, not scope creep. Ownership/participant tracing (who
actually controls a property-holding company) was in the original strategic
analysis's CVR value proposition and is a plausible real differentiator for the
real estate vertical later. No CVR-specific bilag document appears to be required
per the guidance (unlike EJF/SVR, which do); the on-screen form's own fields don't
mark the attachment as required either.

Side finding, not for this project: `aarhus_re`'s earlier blocked attempt at EJF
(Ejerfortegnelsen) sale-price data was blocked on IP whitelisting for a legacy
Zone-5 REST endpoint — this guidance shows the actual supported path (Administration
+ MitID Erhverv + a specific EJF bilag document) was never tried. Noted in next
actions in case that project revisits it.

### 2026-08-17 — Set up a dedicated Datafordeler Administration account for CVR

The old-style Webbruger/Tjenestebruger signup (same model as the shared BBR
credential) is explicitly being phased out end of 2026 — Datafordeler's own login
page now tells new signups to use **Administration** with API-key/OAuth instead.
Registered there (email login tied to Jonas Haahr / Nordic Raven Solutions, CVR
46097750, rights: Ejer/Owner) and created a new, purpose-specific IT-system:

- **IT-system**: `bde-enrichment-engine`
- **API-key** (for free/open data): named `local-dev`, active, expires 2028-08-17.
- **OAuth Shared Secret** (for protected/confidential data, if needed): named
  `local-dev-secret`, Client ID `2d4f59b7-1593-4f91-a29c-7170a3783134`, active,
  expires 2028-08-16.
- Both stored in `.env` only (chmod 600, gitignored) — raw values are **not** in
  this log, any other doc, or git history. Metadata only, by design: don't repeat
  the `aarhus_re` pattern of hardcoding a real secret as a source-code default.
- **OAuth Certifikat** and **IP-adresser**: both empty, untouched — no certificate
  or IP whitelisting set up yet. Only relevant if the CVR data actually needed
  turns out to require the protected/OAuth path (see next actions).
- **Dataadgang** (access requests for protected register data): empty. Having
  credentials doesn't grant data access by itself — a request still has to be
  submitted per-register/entity and approved before any CVR lookup will return data.

Net effect: CVR groundwork (account + credentials) is in place, but **no CVR data
is accessible yet** — the access request is the actual next blocking step, not
anything code-side. Also clarified this account's scope doesn't (yet, or maybe at
all) cover BBR: Administration's own description of API-key/OAuth access is "via
Fildownload (HTTPS) og GraphQL," which reads as a different service surface than
the classic REST endpoints `bbr.py` currently calls — needs confirming before
assuming this new account can ever replace the shared `aarhus_re` BBR credential.

### 2026-08-17 — Adversarial self-review of the v1 engine; 13 findings, 12 fixed

Reviewed the just-built engine deliberately critically (security, correctness,
code quality, product/UX) before it goes anywhere near a demo. Findings and
resolutions documented in full at
[docs/reviews/2026-08-17-engine-v1-review.md](reviews/2026-08-17-engine-v1-review.md).
Highlights:

- **`_pick_current()` could have silently surfaced a demolished building's data as
  current** (no `status` field check at all). Researched BBR's actual status
  codelist via Datafordeler/BBR Instruks docs — confirmed `status == 6` means
  "opført"/current — and now prefer that when present, falling back to the old
  heuristic (now datetime-aware, not string-comparison) otherwise. Full status
  codelist (1-9) wasn't fully confirmable from public docs despite real effort;
  documented as a known limitation rather than papered over.
- **Zero error handling previously existed**, despite PRD 02 explicitly requiring
  graceful failure. Added typed exceptions (`AddressLookupError`,
  `AddressNotFoundError`, `BBRLookupError`), 429 retry-with-backoff respecting
  `Retry-After`, and a CLI that prints a clean message instead of a traceback.
- **Raw BBR codes (`wall_material='1'`) were being shown undecoded**, undermining
  PRD 02's whole "instant, legible" pitch. Researched and added `codelists.py`
  (sourced from BBR Instruks, cited in-file) decoding use/wall/roof/heating codes
  to Danish labels, with a visible `"Ukendt (kode X)"` fallback for anything unmapped
  rather than silently dropping data.
- **Added an ambiguity flag** to `ResolvedAddress` for queries matching multiple
  distinct buildings. First implementation compared raw result count and immediately
  false-positived in testing on every normal multi-unit building (multiple
  floor-level address rows, same building) — caught live and fixed to compare
  distinct `adgangsadresse` IDs instead.
- Fixed `.env` permissions (was world-readable), `config.py`'s raw `KeyError` on
  missing env vars, inaccurate type hints, a stale docstring in
  `scripts/lookup_address.py` that told readers to run it in a way that actually
  raised `ModuleNotFoundError`, and added logging plus 7 tests
  (`tests/test_bbr.py`, `tests/test_codelists.py`) covering the fiddliest logic.
- **One finding left deliberately unresolved**: the shared-with-`aarhus_re`
  credential (finding 2) needs a new Datafordeler account, not a code change —
  documented and queued rather than false-claimed as fixed.
- Re-tested end-to-end against real Aarhus addresses post-fix; all 7 tests pass.

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
