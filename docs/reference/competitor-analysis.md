# Competitor Analysis — Accobat & BoligIQ (2026-08-17)

Prompted by re-examining the earlier build-vs-buy question from
[PRD 01](../prd/01-external-data-enrichment-engine.md) now that there's a working
demo to compare against. Two names came up repeatedly in the original strategic
analysis; actually checked their current products rather than assuming.

## Key finding: these are two different product categories, not one competitive set

### Accobat — "Datadrevet Ejendom" (DDE) — NOT a direct competitor

- **What it is**: a BI-as-a-Service platform that connects a property administrator's
  *own internal* systems (UNIK Bolig, EG Bolig, Boligflow, Business Central, D365
  Finance) and builds P&L, budget, and DCF-valuation reporting in Power BI. External
  data (e.g. BBR) is a secondary enrichment, not the core product.
- **Target**: mid-to-large property administrators. Implementation takes "several
  weeks" per their own marketing — an enterprise sales/onboarding motion.
- **Relevance to BDE**: this is closer to what BDE could become in a *later-stage*,
  deep client engagement (join external + internal ERP data — Phase 2+ of the
  original strategic analysis), not a threat to the current public-data-only demo.
  Worth revisiting this comparison once BDE has an actual paying client wanting that
  kind of integration.

### BoligIQ — a real, direct competitor at our layer

- **What it is**: public-registry aggregation via API and web UI. Address or BFE
  number in, structured JSON out. Sources: BBR, CVR, Tinglysningen, EJF, energy
  certificates, Vurderingsstyrelsen, Plandata, DAR, Matrikel, ejendomsskat — 20+
  registries.
- **Pricing**: 14-day free trial, then 833 DKK/month (~10,000 DKK/year) flat,
  "one transparent price," API access included.
- **Broader than us**: includes Tinglysning (liens/mortgages/easements) and EJF
  ownership data — the exact sources we already know are gated behind MitID Erhverv
  + a bilag application (see [datafordeler-access.md](datafordeler-access.md)).
- **Possible gap in their offering**: their product pages make no mention of
  historical sale/transaction price data — something we have via the OIS route
  (`ois.py`). Not independently confirmed (haven't tried their trial) — worth
  verifying before leaning on this as a real differentiator in a sales conversation.

## What this resolves

**PRD 01's old "build vs. buy" open question now has a real number attached to
it.** At ~10k DKK/year for full registry coverage including Tinglysning/EJF,
*buying* BoligIQ API access as a component — rather than independently chasing the
MitID Erhverv/bilag process ourselves — is a legitimate option worth considering
if a specific client engagement ever needs that breadth. Not a decision to make
now (no client needs it yet), but no longer a guess.

## Strategic takeaway

Don't compete with BoligIQ on data breadth — it's commoditized and they're already
ahead there. **The actual differentiation was never the data, it's the integration
labor**: neither competitor sells a finished, integrated solution to a small/
independent operator. BoligIQ sells raw API access (someone still has to build the
Power BI layer on top). Accobat sells an enterprise platform with a weeks-long
onboarding motion, clearly aimed above small operators. A fast, low-friction
integration service for Aarhus-area property administrators too small for Accobat
and not equipped to build their own layer on BoligIQ's API is a real gap — and
matches what the original strategic analysis already concluded ("sell automated
workflows, not isolated dashboards, and don't be another portal to log into").

Also still true, unaddressed by either competitor as far as their marketing shows:
an **AI-native angle** (LLM-assisted classification, natural-language portfolio
queries) — nothing in Accobat's or BoligIQ's positioning suggests they lean into
this.
