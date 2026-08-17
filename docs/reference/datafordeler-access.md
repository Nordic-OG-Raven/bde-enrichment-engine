# Datafordeler.dk — Data Access Guide (captured 2026-08-17)

Source: "Vejledning og bilag til ansøgning", inside Datafordeler Administration
(authenticated portal — not independently re-fetchable, so captured here in full
rather than just linked). Original Danish preserved for register names/terms where
translation could lose precision.

## Key takeaway for this project

**CVR: only the `CVRPerson` entity requires an access request.** All other CVR
entities (company name, address, status, industry code, etc.) are **unrestricted**
— fetchable directly with the existing `bde-enrichment-engine` credentials, no
Dataadgang request needed. This resolves the open question from the 2026-08-17
engine review/log: we do NOT need to wait on any approval to build basic CVR company
lookup — only ownership/participant data (`CVRPerson`) needs the request in flight now.

## General rules (apply across all registers)

- Access requests are per-environment — Production and Test04 need separate requests.
- **IPv6 addresses can never be whitelisted**, for any register, any path.
- Registers with restricted services on Datafordeler: CPR, CVR, VUR, EJF, SVR.
- The legacy Webbruger/Tjenestebruger + REST path is being phased out across the
  board (various end-2026 dates per register) in favor of Datafordeler
  Administration + MitID Erhverv + OAuth/API-key.

## Per register

### CVR (Det Centrale Virksomhedsregister) — the one relevant to BDE now

- Registry authority: Erhvervsstyrelsen.
- **Only `CVRPerson` is access-restricted.** Everything else is open.
- `CVRPerson` access (via CVR Fildownload HTTPS or CVR GraphQL): request through
  Datafordeler Administration; requires MitID Erhverv + an OAuth-authenticated
  IT-system (we have the IT-system + OAuth Shared Secret already — MitID Erhverv
  itself not yet confirmed as attached to the Administration login used).
- **No CVR-specific bilag document is called out** in the guidance, unlike EJF/SVR
  below — the on-screen Dataadgang form's contact fields may be sufficient on their
  own. Consistent with the UI: "Bilag til ansøgning" isn't marked required (no `*`),
  unlike Register* and Vælg entiteter og tjenester*.
- Legacy REST path (phasing out): separate email request to cvrselvbetjening@erst.dk
  + mandatory IP whitelisting. Superseded by the Administration path above.

### CPR (Det Centrale Personregister) — not currently needed by BDE

- Registry authority: CPR-kontoret.
- Modern path needs MitID Erhverv + OAuth via Administration, **plus** a *separate*
  application to CPR directly: open a support ticket at CPR's servicedesk, then
  apply via virk.dk (with MitID Erhverv), referencing the servicedesk ticket number.
  Public bodies get the `CustomPublicSectorPerson` service; private entities get
  `CustomPrivateSectorPerson`.
- **Private companies must pay** for CPR service usage on Datafordeler (see
  Datafordeler's pricing page) — unlike CVR/BBR which are free.

### EJF (Ejerfortegnelsen) — ownership register, includes real-estate transaction data

- Registry authority: Geodatastyrelsen.
- **Relevant to the separate `aarhus_re` project**, not BDE directly: that project
  hit a dead end trying to get EJF "Handelsoplysning" (sale price) data via an ad-hoc
  REST call — blocked on IP whitelisting for a Zone-5 cert-services endpoint (see
  `aarhus_re/price_scraping_log.md`, section 5). This guidance shows the actual
  intended path, which wasn't tried at the time.
- Modern path: via Datafordeler Administration, MitID Erhverv + OAuth IT-system,
  **plus a specific required attachment** — "Bilag Anmodning om adgang til
  Ejerfortegnelsen" (downloadable from Geodatastyrelsen's own site) must be filled
  out and included with the request. Unlike CVR, this one is not optional.
- Legacy path (phasing out end of 2026): web user + service user (REST cert or FTP
  SSH2 key), IP whitelist ordered via a specific EJF document on GST's site, sent to
  services@gst.dk.

### VUR (Ejendomsvurdering) — property valuation — not currently needed by BDE

- Registry authority: Vurderingsstyrelsen.
- **The access-request process itself is being phased out 30 June 2026** with no
  replacement process specified in this guidance — check Vurderingsstyrelsen's own
  site directly if this is ever needed.
- Legacy path: web user + service user (password auth), email
  datafordeler@vurdst.dk stating services wanted, environment, user names, and the
  *purpose* of the extract, plus company contact details.

### SVR (Skatteforvaltningens Virksomhedsregister) — not currently needed by BDE

- Registry authority: Skatteforvaltningen.
- Modern path: via Administration, MitID Erhverv + OAuth, plus a bilag stating
  company/authority name, CVR, contact person, email, phone, **and the legal basis
  (lovhjemmel)** under which you're entitled to use the requested services.
  Approval results in a formal data exchange agreement ("dataudvekslingsaftale") and
  a welcome package.
- Legacy path: web user + service user, IP whitelist, email to
  dataudstilling@ufst.dk with the same information.

## Practical UI notes (Datafordeler Administration)

- Dataadgang form: "Bilag til ansøgning" is not marked required (no `*`) — only
  Register* and Vælg entiteter og tjenester* are. For CVR specifically, try
  submitting without an attachment first; EJF and SVR explicitly do need one, per
  above.
- **An IT-system needs at least one registered IP before it can create a Dataadgang
  request at all** — not documented in the guidance text above, discovered via the
  UI's own error: *"IT-systemet skal have en registreret IP for at oprette en
  dataadgangsanmodning."* Register one under the IT-system's **IP-adresser** tab
  first. Note home/broadband IPs are often dynamic — a changed IP later is a
  plausible silent-failure cause worth checking if a previously-working request
  stops working.
