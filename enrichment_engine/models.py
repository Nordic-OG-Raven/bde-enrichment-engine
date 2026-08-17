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
    lon: float | None = None
    lat: float | None = None
    ambiguous: bool = False


@dataclass
class BuildingProfile:
    bbr_building_id: str
    use_code: str | None
    use_label: str | None
    year_built: int | None
    wall_material: str | None
    wall_material_label: str | None
    roof_material: str | None
    roof_material_label: str | None
    total_area_sqm: int | None
    footprint_sqm: int | None
    floors: int | None
    heating_type: str | None
    heating_type_label: str | None
    registered_from: str | None


@dataclass
class Unit:
    bbr_unit_id: str
    use_code: str | None
    use_label: str | None
    living_area_sqm: int | None
    total_area_sqm: int | None
    num_rooms: int | None


@dataclass
class EnergyLabel:
    energy_class: str
    energimaerkenr: str
    valid_from: str
    valid_to: str
    is_historic: bool


@dataclass
class SaleRecord:
    price_dkk: int
    sale_date: str
    sale_type: str


@dataclass
class PropertyProfile:
    address: ResolvedAddress
    building: BuildingProfile | None
    units: list[Unit]
    energy_label: EnergyLabel | None
    last_sale: SaleRecord | None
