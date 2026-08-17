# PRD 02 — Real Estate Prospecting Demo

| | |
|---|---|
| Status | v1.1 implemented (`streamlit_app.py`): BBR fields, map, per-unit table, energy certificate, last sale price. Tested locally via `streamlit.testing.v1.AppTest` (22/22 suite) — not yet deployed/shared with a prospect |
| Owner | Jonas Haahr |
| Created | 2026-08-17 |
| Last updated | 2026-08-17 |
| Depends on | [PRD 01 — External Data Enrichment Engine](01-external-data-enrichment-engine.md) |

## Problem

There are zero clients today. The fastest way to get the first one is a free, shareable,
concrete demonstration of value — not a pitch deck, not a dashboard mockup with fake
data. Something a prospect (or a cold outreach recipient) can watch solve, in seconds,
a problem they currently solve manually.

Real estate is the sharpest first story: BBR + CVR lookups are currently manual,
multi-portal, multi-minute tasks for property administrators/developers/investors in
Aarhus/Midtjylland. Collapsing that into one instant lookup is a legible "wow."

## Goals

- A live, free-to-run, shareable web app: enter a Danish address or CVR number, get back
  an enriched property profile in seconds.
- Usable two ways: sent cold as a URL, or screen-shared live in a sales conversation.
- Costs nothing to host or run.

## Non-goals

- Not a client deliverable — no client's internal data (Business Central, etc.) is
  involved. Purely public-data enrichment, so no NDA/data-access issues block building
  or sharing it.
- No auth, no user accounts, no persistence of queries.
- No support for sectors other than real estate at this stage.
- Not trying to replicate what BoligIQ/Accobat already sell — this only needs to be
  good enough to make the *conversation-starting* point, not compete as a product.

## Target user

Prospects: real estate developers, administrators, and investors in Aarhus/Central
Jutland — either found cold (CVR industry-code list) or in a live sales conversation.

## Functional requirements

1. Single input field: Danish address.
2. On submit, call the Enrichment Engine (PRD 01) and render:
   - BBR fields: floor area, construction year, heating type, wall/roof material, floors.
   - Map pin (from address coordinates).
   - Per-unit table when the building has separately registered units.
   - Most recent sale price + date, when available (best-effort — unofficial source).
   - Energy certificate class, when available (best-effort — unofficial source).
   (CVR/owning-entity lookup still deferred — see PRD 01's 2026-08-17 log entry. Not a
   v1 demo field; add if/when CVR access is approved.)
3. Plain, clean, legible read-only output — a table or simple card layout. No editing,
   no export, no saved history for v1. Text fields must not truncate (caught and fixed
   2026-08-17 — `st.metric` isn't suited to descriptive text).
4. Graceful handling of "not found" / API errors (still needs to look credible in a
   live demo — a stack trace on screen kills the pitch). The two best-effort fields
   (energy certificate, sale price) simply omit their section rather than error when
   unavailable, since their sources are unofficial and expected to occasionally miss.

## Architecture

- Streamlit (free, fastest path from Python function to shareable web app).
- Hosted on Streamlit Community Cloud (free tier) for the cold-outreach URL use case;
  local `streamlit run` is enough for screen-shared live demos.
- Imports the Enrichment Engine (PRD 01) directly as a library — no duplicated
  fetch/normalize logic in this app.

## Success criteria

- A URL exists that can be sent to a stranger with zero setup on their end, and it
  produces a correct, fast, credible-looking result for a real Aarhus-area address.
- Usable live in a sales call without visible errors on the happy path.
- At least one real conversation (cold outreach or warm) where this demo was the thing
  that got a prospect to engage further.

## Explicitly deferred to later (only if there's a client)

- Joining against any client's actual internal data (Business Central budgets, etc.) —
  that's bespoke delivery work for an actual paying engagement, not part of this demo.
- Additional BBR/CVR fields, Tinglysning/energy-certificate/zoning data — add only if a
  specific prospect conversation calls for it.
