# Big Data Energy

A tool that enriches any Danish address with property data pulled live from five
government and public sources — building records (BBR), energy certificates, historical
sale prices, and per-unit breakdowns — including two sources with no official API,
reverse-engineered from scratch.

**Live demo:** [bde-ejendomsopslag.streamlit.app](https://bde-ejendomsopslag.streamlit.app)

Built solo as the technical foundation of a freelance BI/data consultancy (Nordic Raven
Solutions) aimed at helping Danish SMEs enrich internal data (Business Central,
e-conomic, etc.) with free external registries.

## Quickstart

```bash
git clone https://github.com/Nordic-OG-Raven/bde-enrichment-engine.git
cd bde-enrichment-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # fill in a free Datafordeler.dk API key

pytest                                    # 27 tests
python scripts/lookup_address.py "Ryesgade 1, 8000 Aarhus"
streamlit run streamlit_app.py            # full web demo
```

## Highlights

- **Reverse-engineered two undocumented data sources** (an energy-certificate lookup and
  a historical sale-price API) directly from browser network traffic — no official API
  exists for either.
- **Worked out Datafordeler's GraphQL API with introspection disabled** — no schema to
  query, so field names, filter shapes, and a required bitemporal query argument were
  all derived from trial queries and error messages. Findings written up in
  [datafordeler-access.md](docs/reference/datafordeler-access.md).
- **Diagnosed and got a live production bug fixed by the data provider's own support
  team** — an API key that showed "Active" in their admin panel but silently rejected
  every request. Full incident, including the wrong turns, in the
  [implementation log](docs/implementation-log.md).
- **Adversarial self-review before shipping**: a deliberate 13-finding security/
  reliability/code-quality pass against the first working version, each finding tracked
  to resolution — see [the review](docs/reviews/2026-08-17-engine-v1-review.md).
- Typed exceptions, retry-with-backoff, structured logging, and a documented
  best-effort/official-source distinction for the two unofficial data sources.

## Start here

- **[docs/implementation-log.md](docs/implementation-log.md)** — the living reference:
  current state, next actions, and a dated history of decisions.
- **[docs/prd/](docs/prd/)** — one PRD per product currently in scope:
  1. [External Data Enrichment Engine](docs/prd/01-external-data-enrichment-engine.md)
  2. [Real Estate Prospecting Demo](docs/prd/02-real-estate-prospecting-demo.md)
- **[docs/strategy/](docs/strategy/)** — earlier (2026-07) sector research and a
  four-sector rollout plan. Background/inspiration only — superseded as a binding
  roadmap; see the 2026-08-17 log entry for why.

## Current focus

One sector (real estate), one free data source (Datafordeler.dk BBR+CVR), one goal:
a live demo good enough to win the first client. See the implementation log for
next actions.
