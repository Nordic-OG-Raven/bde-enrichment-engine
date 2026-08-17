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
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Opførelsesår", b.year_built or "Ukendt")
                    st.metric("Samlet areal", f"{b.total_area_sqm} m²" if b.total_area_sqm else "Ukendt")
                    st.metric("Etager", b.floors or "Ukendt")
                with col2:
                    st.metric("Anvendelse", b.use_label or "Ukendt")
                    st.metric("Ydervæg", b.wall_material_label or "Ukendt")
                    st.metric("Tag", b.roof_material_label or "Ukendt")
                st.metric("Varmeinstallation", b.heating_type_label or "Ukendt")

st.divider()
st.caption("Big Data Energy — ekstern databerigelse for danske SME'er. Nordic Raven Solutions.")
