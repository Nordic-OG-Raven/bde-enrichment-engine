# Big Data Energy — Implementation Plan

Companion document to `big-data-energy-strategic-analysis.md`. This translates the strategic recommendations into a phased, actionable rollout plan.

## 0. Guiding Principles

- **Sequence by urgency, not by size of opportunity.** Regulatory deadlines (CSRD/VSME) and construction-cycle timing (real estate) create natural "why now" pressure that shortens sales cycles — start there.
- **Build once, resell many times.** Every sector engagement should produce a reusable Power BI template + API connector, not a bespoke one-off.
- **Free data first.** Datafordeler.dk and DMI Frie Data are zero marginal cost — margin comes from integration/modeling labor, not data licensing.
- **Grants fund the pilot, references fund the pipeline.** Use SMV:Digital to land first clients cheaply, then convert them into case studies.

## Phase 1 — Foundation (Weeks 1–6)

**Legal & administrative**
- [ ] Register CVR entity (ApS or enkeltmandsvirksomhed depending on liability/tax preference)
- [ ] Apply for SMV:Digital advisor/consultant registration so clients can use grant funding to pay for engagements
- [ ] Set up basic invoicing/bookkeeping (e-conomic or similar — dogfood the target ERP stack)

**Technical foundation**
- [ ] Register for Datafordeler.dk API access; obtain credentials for BBR, CVR, DAR, Matrikel endpoints
- [ ] Register for DMI Frie Data API access (free tier)
- [ ] Build a reusable Power BI / Power Query (M) connector library:
  - BBR lookup-by-address and lookup-by-BFE-number
  - CVR company lookup and ownership graph
  - DMI historical + forecast weather by municipality/postcode
- [ ] Stand up a lightweight Azure-based ingestion layer (Azure Functions or Logic Apps) if any API needs scheduled polling/caching rather than direct Power BI refresh
- [ ] Define standard "internal-to-external join key" conventions (CVR number, BFE/ejendomsnummer, postcode+date) to reuse across client engagements

**Positioning & collateral**
- [ ] One-page value proposition per target sector (real estate, agrifood, retail, maritime)
- [ ] A short demo dashboard per sector built on public data only (no client data needed) to use in sales conversations

## Phase 2 — Beachhead: Real Estate & PropTech (Weeks 4–14, overlapping Phase 1)

Rationale: lowest integration saturation + free, robust GraphQL data on Datafordeler.dk + high-value decisions (millions of DKK per transaction) = fastest path to a paid pilot.

- [ ] Identify 15–20 target SMEs: property developers, administrators, and investors in Aarhus/Central Jutland (use CVR industry codes to build the list)
- [ ] Build the flagship template: "Portfolio Screening Dashboard" — merges internal budget/expenditure (Business Central) with live BBR, energy certificates, zoning, and easement data
- [ ] Run 2–3 pilot engagements co-funded via SMV:Digital grants
- [ ] Convert pilots into reference case studies (with client permission) before moving to Phase 3

## Phase 3 — Regulatory Wedge: Agrifood & Food Processing (Months 3–6)

Rationale: CSRD/VSME compliance creates a mandatory, deadline-driven need — this is the most "unavoidable" sale in the portfolio.

- [ ] Identify SMEs in the Agro Food Park periphery and broader Food Valley cluster not already served by enterprise-grade sustainability platforms
- [ ] Build the flagship template: "Scope 1-2-3 Emissions Dashboard" — maps e-conomic/Business Central procurement line items to GHG Protocol emission factor databases
- [ ] Partner or cross-refer with an accountant/auditor network for CSRD assurance sign-off (the consultancy generates the data; the client still needs an auditor's stamp)
- [ ] Package as a recurring engagement (annual reporting cycle), not a one-off project — this is the first candidate for a subscription/retainer model

## Phase 4 — Expansion: Retail/E-commerce and Maritime/Logistics (Months 6–12)

- **Retail**: build the "Weather & Seasonality Impact Dashboard" (DMI + POS/Shopify/Business Central), target the Herning–Aarhus textile/fashion e-commerce corridor
- **Maritime**: build the "Voyage & Bunker Optimization Dashboard" (AIS + bunker price feeds + VMS), target SME ship operators/freight forwarders around Aarhus Havn — treat as higher-complexity/higher-effort due to AIS data volume; only pursue once Phases 2–3 are cash-flow positive

## Phase 5 — Productization & Scale (Months 9–18)

- [ ] Convert bespoke pilot templates into a licensable "connector pack" product (fixed price + lighter-touch implementation) to reduce delivery hours per client
- [ ] Evaluate hiring a second data engineer/consultant once pipeline exceeds ~3 concurrent engagements
- [ ] Reassess sector exclusions (manufacturing/robotics, energy trading) only if a client explicitly requests external-data work tied to compliance or supply chain — do not proactively target them

## Team & Capability Build

- Core skill needed from day one: Power BI (Power Query/M, DAX) + REST/GraphQL API integration
- Secondary skill to acquire/hire by Phase 3: GHG accounting / CSRD domain knowledge (or partner with an ESG/accounting firm rather than building in-house)
- Secondary skill for Phase 4 maritime: comfort with high-volume time-series data (AIS) — likely the first engagement requiring Azure Data Factory / a proper data warehouse rather than direct Power BI ingestion

## Milestones & Success Metrics

| Milestone | Target timing | Metric |
|---|---|---|
| SMV:Digital advisor status approved | Week 6 | Approved/not |
| First paid real estate pilot signed | Week 10 | 1 signed contract |
| Real estate template reusable v1 | Week 14 | Deployed to 2nd client without rebuild |
| First agrifood ESG pilot signed | Month 4 | 1 signed contract |
| Reference case study published | Month 5 | 1 public case study |
| Break-even on founder time | Month 6 | Revenue ≥ cost of 1 FTE |
| 3 concurrent sectors active | Month 9 | Real estate + agrifood + 1 more |
| First retainer/subscription client | Month 9–12 | 1 recurring contract |

## Key Risks & Mitigations

- **Grant dependency risk**: SMV:Digital funding could change/tighten — don't structure pricing so it only works with the subsidy; validate willingness-to-pay at full price with at least one client per sector.
- **Internal data quality risk**: client ERPs are often messy (per the strategic analysis) — always scope a paid "data foundation" phase (key standardization: CVR, BFE numbers) before promising integration timelines.
- **Single-founder bottleneck**: templates must be documented and reusable so delivery doesn't require the same person rebuilding logic each time.
- **Sector 4 (maritime) complexity risk**: AIS data volume/cost could erode margins — validate data costs with a real vendor quote before selling a fixed-price maritime engagement.

## Immediate Next Actions (This Week)

1. Register Datafordeler.dk and DMI API credentials
2. Draft SMV:Digital advisor application
3. Pull a CVR-code-filtered list of 15–20 real estate SMEs in Aarhus/Central Jutland as the first outbound target list
4. Build the public-data-only demo dashboard for real estate (no client data required) to use in first sales calls
