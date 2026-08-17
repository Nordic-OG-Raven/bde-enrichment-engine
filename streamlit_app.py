import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enrichment_engine.engine import property_profile
from enrichment_engine.exceptions import AddressLookupError, AddressNotFoundError, BBRLookupError

st.set_page_config(page_title="Ejendomsopslag", page_icon="🏠")

st.title("🏠 Ejendomsopslag")
st.caption(
    "Slå en adresse op og få bygningsdata fra BBR øjeblikkeligt — "
    "i stedet for manuelt opslag på tværs af flere portaler."
)

query = st.text_input("Adresse", placeholder="fx Ryesgade 1, 8000 Aarhus")
submitted = st.button("Slå op", type="primary") or query

if submitted and query:
    with st.spinner("Slår op..."):
        try:
            profile = property_profile(query)
        except AddressNotFoundError:
            st.error(f"Kunne ikke finde en adresse, der matcher \"{query}\". Tjek stavning og prøv igen.")
        except (AddressLookupError, BBRLookupError):
            st.error("Der opstod en fejl under opslaget. Prøv igen om lidt.")
        else:
            st.subheader(profile.address.display_name)
            if profile.address.ambiguous:
                st.warning(
                    "Adressen matcher flere forskellige bygninger — viser resultatet "
                    "for det bedste match."
                )

            if profile.building is None:
                st.info("Adressen blev fundet, men vi har ingen BBR-oplysninger for denne bygning.")
            else:
                b = profile.building
                col1, col2, col3 = st.columns(3)
                col1.metric("Opførelsesår", b.year_built or "Ukendt")
                col2.metric("Samlet areal", f"{b.total_area_sqm} m²" if b.total_area_sqm else "Ukendt")
                col3.metric("Etager", b.floors or "Ukendt")

                st.markdown("&nbsp;")
                detail_rows = [
                    ("Anvendelse", b.use_label),
                    ("Ydervæg", b.wall_material_label),
                    ("Tag", b.roof_material_label),
                    ("Varmeinstallation", b.heating_type_label),
                ]
                for label, value in detail_rows:
                    dcol1, dcol2 = st.columns([1, 2])
                    dcol1.markdown(f"**{label}**")
                    dcol2.write(value or "Ukendt")

            if profile.energy_label is not None:
                st.markdown("&nbsp;")
                el = profile.energy_label
                ecol1, ecol2 = st.columns([1, 2])
                ecol1.metric("Energimærke", el.energy_class)
                status = "udløbet" if el.is_historic else "gyldigt"
                ecol2.caption(f"{status.capitalize()} {el.valid_from} – {el.valid_to} (nr. {el.energimaerkenr})")

            if profile.address.lat is not None and profile.address.lon is not None:
                st.markdown("&nbsp;")
                st.map([{"lat": profile.address.lat, "lon": profile.address.lon}], size=30)

            if profile.units:
                st.markdown("&nbsp;")
                st.subheader(f"Enheder ({len(profile.units)})")
                st.dataframe(
                    [
                        {
                            "Anvendelse": u.use_label or "Ukendt",
                            "Boligareal": f"{u.living_area_sqm} m²" if u.living_area_sqm else "Ukendt",
                            "Samlet areal": f"{u.total_area_sqm} m²" if u.total_area_sqm else "Ukendt",
                            "Værelser": u.num_rooms if u.num_rooms is not None else "Ukendt",
                        }
                        for u in profile.units
                    ],
                    hide_index=True,
                    use_container_width=True,
                )

st.divider()
st.caption("Big Data Energy — ekstern databerigelse for danske SME'er. Nordic Raven Solutions.")
