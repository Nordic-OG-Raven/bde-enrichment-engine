# Implementation Log

This is the permanent frame of reference for the Big Data Energy project: what's true
right now, and a dated, append-only history of how we got here. Update "Current State"
in place every time it changes; never edit past entries in the Log — add a new one.

---

## Current State

**As of 2026-08-17**

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

1. Confirm Datafordeler.dk auth/access requirements (open question in PRD 01).
2. Scaffold the `enrichment_engine` Python package per PRD 01.
3. Implement BBR + CVR fetch/normalize/join for a single address lookup.
4. Build the Streamlit demo (PRD 02) on top of it.
5. Get it in front of one real prospect.

---

## Log

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
