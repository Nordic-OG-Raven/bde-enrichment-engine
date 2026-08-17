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
- **Sale price gap — checked 2026-08-17, does not exist.** Initially thought their
  marketing didn't mention historical sale/transaction price data. Wrong — only
  checked their overview page, not their dedicated Tinglysning API docs, which
  return `købspris_dkk` (purchase price) straight from deed registration data.
  That's arguably *more* authoritative than our OIS/SVUR route (a legally-registered
  deed price vs. an aggregator database entry). No real differentiator here — this
  was a research gap on our side, not a real gap in their product. Didn't need to
  sign up for their trial to settle it; their own public docs answered it directly.

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

## Reconsideration prompted by the corrected finding (2026-08-17)

With the sale-price "edge" gone, BoligIQ is ahead of our own engine on essentially
every data-breadth axis (Tinglysning, EJF, CVR ownership, Plandata zoning,
Vurderingsstyrelsen valuations, ejendomsskat — none of which we have). Worth being
honest about what that implies rather than quietly ignoring it:

- **Our own engine's real job was always the free demo/prospecting tool (PRD 02),
  not a production data backbone to compete on completeness** — that's exactly
  what it was scoped for, and it still does that job well and at zero cost while
  pre-revenue.
- **Once there's an actual paying client, ~833 DKK/month for BoligIQ's full
  coverage is trivial next to a single consulting engagement's value.** Worth
  seriously considering *buying* BoligIQ as the production data source for real
  engagements rather than continuing to build/maintain our own scrapers —
  especially the two unofficial ones (`energimaerke.py`, `ois.py`) that could break
  without warning, a real liability in front of a paying client, not just a demo.
  Free demo stays ours (zero cost matters most pre-revenue); paid delivery could
  reasonably lean on BoligIQ instead of reinventing what they already sell cheaply.
- **A sharper differentiation angle than generic BI, given the corrected picture**:
  the CSRD/ESG compliance wedge from the original strategic analysis (Phase 3,
  originally scoped for agrifood) applies just as directly to commercial real
  estate — building energy performance/emissions reporting is an EU-taxonomy/CSRD
  compliance requirement, not just a nice-to-have dashboard. Neither Accobat nor
  BoligIQ appears to position around this specifically. We already have the energy
  certificate data; the gap is the compliance-reporting framing and Scope
  1-2-3-style emissions modeling on top of it — a regulatory deadline sells faster
  than a BI dashboard does, per the original analysis's own conclusion.
