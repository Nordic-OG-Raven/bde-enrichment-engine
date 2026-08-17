from dataclasses import dataclass


@dataclass
class ResolvedAddress:
    query: str
    display_name: str
    adgangsadresse_id: str
    kommunekode: str
    postnummer: str
    vejnavn: str
    husnr: str


@dataclass
class BuildingProfile:
    bbr_building_id: str
    use_code: str | None
    year_built: int | None
    wall_material: str | None
    roof_material: str | None
    total_area_sqm: float | None
    footprint_sqm: float | None
    floors: int | None
    heating_type: str | None
    registered_from: str | None


@dataclass
class PropertyProfile:
    address: ResolvedAddress
    building: BuildingProfile | None
