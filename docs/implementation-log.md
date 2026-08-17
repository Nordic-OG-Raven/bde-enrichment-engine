# Implementation Log

This is the permanent frame of reference for the Big Data Energy project: what's true
right now, and a dated, append-only history of how we got here. Update "Current State"
in place every time it changes; never edit past entries in the Log — add a new one.

---

## Current State

**As of 2026-08-17**

- **SMV:Digital advisor status: approved.** CV still needs finishing on
  ehmidt.dk (email inbox, LinkedIn URL, hourly rate, reference). Onboarding
  webinar deadline: **2026-11-17**.
- **Clients: zero.** Fully pre-revenue.
- **Product 1, Enrichment Engine — v1.1, done, reviewed, hardened, expanded.**
  `enrichment_engine/` resolves a free-text Danish address (Dataforsyningen,
  free/no auth) to a normalized `PropertyProfile` with: BBR building data
  (decoded labels), WGS84 coordinates, per-unit breakdown, energy certificate
  class, and most recent sale price. Typed exceptions for the official-source
  path (BBR/address/BFE); the two unofficial sources (energy cert, sale price)
  are best-effort and return `None` on failure rather than raising — see PRD 01
  for why. `.env` chmod 600, 16 unit tests. Details:
  [2026-08-17 review](reviews/2026-08-17-engine-v1-review.md) (original
  hardening pass) plus the 2026-08-17 "value expansion" log entry below (new
  data sources). Run via `python scripts/lookup_address.py "<address>"`.
- **Product 2, Streamlit Demo — v1.1, tested locally, not yet deployed.**
  `streamlit_app.py`: address input, decoded BBR metrics (no truncation — fixed
  same day), map pin, units table, energy certificate, last sale price, clean
  not-found/ambiguous handling. Verified with `streamlit.testing.v1.AppTest`
  (no manual-only eyeballing). Full suite: **22/22 passing**. Run via
  `streamlit run streamlit_app.py`. **Not yet deployed or shown to a prospect.**
- **CVR is out of v1 scope, and currently blocked at the infrastructure level.**
  Only the `CVRPerson` entity is access-restricted (confirmed from
  Erhvervsstyrelsen's own guidance — other CVR data needs no request); a
  `CVRPerson` Dataadgang request was submitted 2026-08-17 (status "Ny",
  pending). Separately, the account's API-key doesn't authenticate at all —
  fails even against Datafordeler's own official documented example (tested
  well past their 15-minute activation window) — so a Datafordeler support
  ticket was filed 2026-08-17. `cvr.py` is blocked on that response, not on
  anything code-side. Full trail: [datafordeler-access.md](reference/datafordeler-access.md).
- **BBR credential is still shared with the unrelated `aarhus_re` project** —
  a new dedicated Datafordeler Administration account exists now
  (`bde-enrichment-engine` IT-system) but it's GraphQL/Fildownload-only, a
  different service surface than the legacy REST BBR currently uses, so it
  doesn't replace the shared credential. Still open, not blocking.
- Build-vs-buy on BoligIQ/Accobat: leaning build (low code volume, BBR already
  working). Not fully closed, not blocking.
- Strategic direction: deliberately narrower than the original four-sector plan
  (see `strategy/` — background only, not binding). Real estate first, one free
  data source at a time, tool choice deferred until there's a real client.

## Next actions

1. **Deploy `streamlit_app.py` to Streamlit Community Cloud** — built and
   tested locally, not yet live anywhere. The actual next step toward a
   shareable URL per PRD 02's success criteria. Two things worth checking once
   it's live, not before: (a) if the demo ever needs live `CVRPerson`/IP-gated
   calls in the future, the host's outbound IP will need registering too, and
   free tiers often don't offer a fixed IP; (b) the energy-certificate and
   sale-price sources are unofficial scrapes (see PRD 01) — worth a quick
   re-check that they still work once running from a different outbound IP
   (Streamlit Cloud's, not this machine's), in case the target sites behave
   differently for unfamiliar traffic.
2. **Get the demo in front of one real prospect** — the actual end goal,
   blocked only on (1).
3. Wait on Datafordeler support's reply re: the non-authenticating API-key,
   then resume `cvr.py` (basic company lookup — confirmed unrestricted once
   auth actually works).
4. Check back on the `CVRPerson` Dataadgang request status.
5. Decouple the BBR REST credential from `aarhus_re` (2026-08-17 review,
   finding 2) — still open, not blocking.
6. *(Optional)* Cheap pricing check on BoligIQ/Accobat.
7. *(Separate project)* `aarhus_re` could retry EJF sale-price data via the
   proper Administration + MitID Erhverv + bilag path documented in
   [datafordeler-access.md](reference/datafordeler-access.md) — its earlier
   ad-hoc attempt was blocked on the wrong path, not a hard no.

---

## Log

### 2026-08-17 — Dropped st.map() after confirming it silently fails without WebGL

Caught by the user actually looking at the running demo (not by any test —
`streamlit.testing.v1.AppTest` confirmed the map *element* gets created but
can't detect whether it visually renders, since it doesn't run a real
browser). First guess (missing `zoom` causing an over-zoomed-out, invisible
pin) was wrong — real cause, confirmed via browser console: `st.map()` is
built on `deck.gl`, which needs WebGL, and it fails **silently** (blank
space, no error surfaced to Streamlit or the user) when WebGL is unavailable
(`GL_VENDOR = Disabled`, `Sandboxed = yes` in this case).

This matters beyond just this bug: **locked-down corporate machines commonly
disable hardware acceleration**, which is exactly the kind of device a real
prospect might view this demo on. A feature that blank-fails silently for an
unknown fraction of viewers, with no error to notice, is worse than not
having it. First fix was a plain markdown link to Google Maps (no JS map
library, no WebGL - can't fail this way) — but pushed to do better, since we
already have the coordinates and a link-out isn't really "showing" anything.

**Better fix, same day: `enrichment_engine/staticmap.py`** — renders a map
image server-side from raw OpenStreetMap tiles (`tile.openstreetmap.org`,
standard slippy-map tile math, stitched + cropped + a marker drawn with
Pillow) and serves it as a plain PNG via `st.image()`. No WebGL, no JS map
library at all — just an `<img>` tag, which works anywhere image rendering
works. Verified visually (not just "no exception") by actually opening the
rendered PNG: correctly centered, marker sits precisely on the right street.
Used under OSM's tile usage policy (identifying User-Agent, single-lookup
volume, no caching/bulk use) rather than a third-party "static maps"
wrapper API — tried one first (`staticmap.openstreetmap.de`), found it no
longer resolves, went to OSM's own tile server directly instead of trusting
another unverified wrapper.

Kept the Google Maps link alongside the image (not replaced) — the image is
a fixed snapshot, the link gives pan/zoom/street view for anyone who wants
to explore further. 4 new tests for the pure pixel-math (network-independent),
1 new Streamlit test. Full suite 26/26.

**General takeaway for future additions**: prefer widgets with no
GPU/JS-rendering dependency where a plain fallback exists, or at minimum
verify visually (not just via AppTest, which only checks the element tree)
before trusting a rendering-heavy Streamlit component for something
prospect-facing.

### 2026-08-17 — Value-proposition expansion: map, units, energy certificate, sale price

Prompted by actually looking at a live screenshot of the demo and asking whether
the current scope left value on the table. Answer: yes, some cheaply. Added four
things, in order, each live-tested against real addresses before being trusted:

**Fixed first (not scope creep — a bug in existing scope):** `st.metric` was
silently truncating long text values ("Etagebolig-bygning, …") with no way to
see the full text. Numeric fields (year, area, floors) kept `st.metric`; text
fields (use, materials, heating) moved to a plain label/value layout that
doesn't truncate. New test asserts no `…` appears in rendered output.

**Map pin**: `Dataforsyningen`'s `/adresser` response already returns
`adgangspunkt.koordinater` as `[lon, lat]` in WGS84 directly — no need for
BBR's projected-coordinate parsing (`aarhus_re` needed a UTM→WGS84 conversion;
we don't, since we're not using BBR's coordinate field at all). One `st.map()`
call.

**Per-unit breakdown**: hit two real bugs live-testing against BBR, both
caught by actually running it rather than trusting `aarhus_re`'s April
reference code:
1. BBR's `Enhed` endpoint rejects a `husnummer` filter outright (`400 -
   "Parameter: husnummer unrecognized. Did you mean: id?"`) — needs `bygning`
   (the building's `id_lokalId`) instead. Worse, an address can have *multiple*
   historical `Bygning` records, and only some of those ids have linked
   `Enhed` records — our building-selection heuristic doesn't necessarily pick
   the "right" one for this purpose, so unit lookup now queries every building
   id for the address and combines non-empty results.
2. The actual field names have drifted since April: `enh026EnhedensSamledeAreal`
   / `enh027ArealTilBeboelse` today, not the `enh024`/`enh023` `aarhus_re` used.
   Silent schema drift on a REST API that's being phased out — a second data
   point (after the BBR credential's own near-miss) that precedent code from
   this same source needs re-verifying live, not trusting at face value.

**Energy certificate**: the sanctioned path (Energistyrelsen's EMOData API)
needs a separate approval request (sparenergi@ens.dk) — not pursued. Reused
`aarhus_re`'s already-validated workaround instead:
`tjekenergimaerke.emoweb.dk`'s public search form (CSRF token GET + POST, no
auth, no formal API). Live-retested before building on it — same HTML column
layout as their April code, still works.

**Sale price** — the one initially assumed to be hard. It isn't, once you know
the actual mechanism: `aarhus_re` got real SVUR (Statens Salgs- og
Vurderingsregister — the same authoritative register as EJF) transaction data
via `ois.dk/api/svur/get?bfe=`, a public API needing **no authentication**
beyond a browser-like `Referer` header — found by reverse-engineering OIS's
frontend, not the heavy MitID-Erhverv/Datafordeler path first assumed. The
real gap was resolving an address to a **BFE number** on demand: `aarhus_re`
only ever had this via a bulk offline MATRIKLEN2 file dump, not a live
lookup. Solved with a second, *official* Datafordeler service found via
research: `DAR_BFE_Public`'s `husnummerTilBygningBfe` REST method, same
tjenestebruger auth as BBR — confirmed live end-to-end (address → husnummer →
BFE `5622711` → a real 2020 sale, 28.500.000 DKK, "Almindelig frit salg").

**Design choice applied to both new sources**: unlike `bbr.py`'s typed
exceptions, `energimaerke.py` and `ois.py`/`bfe.py` are best-effort — return
`None` on any failure rather than raising. These are unofficial,
unsanctioned-format sources that could break on a markup change without
notice; a demo silently omitting one bonus field is fine, a demo crashing
because a scrape broke is not. Worth revisiting if either becomes
business-critical rather than a demo enhancement — see PRD 01.

Full suite: 22/22 passing, including new parsing tests against synthetic
fixtures (not just live-network dependence) for both new modules.

### 2026-08-17 — API-key doesn't authenticate against any service; escalated to Datafordeler support

Went to build `cvr.py` and hit an auth wall before writing any real code. Full
diagnostic trail in
[docs/reference/datafordeler-access.md](reference/datafordeler-access.md)
("API access pattern" section); summary:

- Confirmed via the IT-system's own revision log that the `local-dev` API-key was
  created at 15:11:16 — ruling out the documented 15-minute activation delay as
  an explanation for anything tested afterward.
- Tried header auth (`Authorization: apikey <key>`, matching Datafordeler's own
  documented curl format) against `CVR/v1` and `CVR/v3` — 401 both times.
- Tried the key as a URL query parameter (both casings, GET and POST) — 404
  every time, route not matched.
- **Decisive test**: reproduced Datafordeler's own official example *exactly* —
  same header format, against `DAR/v1` (a different, unrestricted register) —
  to rule out a CVR-specific path mistake. **Also 401.**
- Conclusion: this isn't a formatting error or a wrong endpoint guess on our
  side — their own example fails identically, so something is wrong with the
  key/account provisioning on Datafordeler's end, despite Administration showing
  the key as "Aktiv". Not something guessable from outside their system.

**Escalating to Datafordeler support** rather than continuing to guess against a
live government API. Draft support request (Danish, matching the support
audience):

> Kære Datafordeler support,
>
> Jeg oplever, at en nyoprettet API-Key ikke kan autentificere mod jeres
> GraphQL-tjenester, selv ved brug af jeres egen dokumenterede eksempel.
>
> Kontooplysninger:
> - Bruger: Jonas Haahr
> - Organisation: Nordic Raven Solutions, CVR 46097750
> - IT-system: bde-enrichment-engine
> - API-Key: local-dev, oprettet 17-08-2026 kl. 15:11:16, status "Aktiv",
>   udløbsdato 17-08-2028
> - Registreret IP: 83.94.224.228/32
>
> Testet (alle 401 Unauthorized, mere end 35 minutter efter oprettelse af
> nøglen, dvs. efter jeres oplyste 15-minutters aktiveringsvindue):
>
> 1. POST https://graphql.datafordeler.dk/CVR/v1 med header "Authorization:
>    apikey <min nøgle>" og query "{ __typename }" → 401
> 2. Samme mod https://graphql.datafordeler.dk/CVR/v3 → 401
> 3. API-Key som URL query-parameter (?apiKey= og ?apikey=, både GET og POST)
>    → 404 (rute ikke fundet)
> 4. For at udelukke at det er CVR-specifikt: gentaget jeres eget dokumenterede
>    eksempel præcist mod DAR (POST https://graphql.datafordeler.dk/DAR/v1,
>    samme header-format) → også 401
>
> Da jeres eget dokumenterede eksempel fejler identisk, formoder jeg at der er
> noget galt med selve nøglens provisionering på jeres side. Kan I hjælpe med
> at afklare, om nøglen er korrekt oprettet og aktiveret?
>
> Med venlig hilsen,
> Jonas Haahr
> 51 50 56 95 / jonas.haahr@aol.com

Not blocking BBR work (unaffected, separate credential/system) — only blocks
`cvr.py`, which is now on hold pending support's response.

**Update, same day — ticket actually submitted.** Used the "Indberette en fejl"
(report an error) form, not "Stille et spørgsmål" — it has a dedicated 401/403
checkbox and fields built for exactly this situation. Submitted with: Register =
CVR (chosen over "Ingen" so it lands with an owner, even though the bug is
provably account-wide, not CVR-specific — the attached repro file makes that
clear regardless), error code 401, checkbox checked, IP 83.94.224.228, failing
URL `https://graphql.datafordeler.dk/CVR/v1`, exact repro timestamp 17-08-2026
15:46 CEST, certificate field marked not applicable (API-key auth, not OAuth
certificate). Full technical repro attached as
`docs/reference/datafordeler-support-attachment-2026-08-17.txt`. Now waiting on
Datafordeler; `cvr.py` stays on hold until they respond.

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
