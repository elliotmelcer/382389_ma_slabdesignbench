# ---------------------------------------------------------------------------
# Internal data table (source: Beton.xlsx, internalised)
# ---------------------------------------------------------------------------

CONCRETE_CO2_TABLE: dict[int, dict[str, float]] = {
    # Author: Elliot Melcer
    # Internal CO2 and cost registry for materials.
    12:  {"gwp": 140.0, "cost": 70.0},
    16:  {"gwp": 159.0, "cost": 72.5},
    20:  {"gwp": 178.0, "cost": 75.0},
    25:  {"gwp": 197.0, "cost": 80.0},
    30:  {"gwp": 219.0, "cost": 85.0},
    35:  {"gwp": 244.0, "cost": 90.0},
    40:  {"gwp": 265.0, "cost": 100.0},
    45:  {"gwp": 286.0, "cost": 110.0},
    50:  {"gwp": 300.0, "cost": 120.0},
    55:  {"gwp": 314.0, "cost": 130.0},
    60:  {"gwp": 328.0, "cost": 140.0},
    70:  {"gwp": 342.0, "cost": 150.0},
    80:  {"gwp": 356.0, "cost": 160.0},
    90:  {"gwp": 370.0, "cost": 170.0},
    100: {"gwp": 384.0, "cost": 180.0},
}


# ---------------------------------------------------------------------------
# Registry used for validating the analysis function of hp_slab
# ---------------------------------------------------------------------------

class ConcreteCO2Registry:
    """Registry for CO2 and cost data of EC2 concrete materials."""

    # Class-level cache (shared across all uses)
    _cache: dict[object, dict[str, float]] = {}

    @classmethod
    def _register(cls, concrete) -> None:
        """Register a concrete material in the cache."""
        fck = int(round(concrete.fck))

        try:
            data = CONCRETE_CO2_TABLE[fck]
        except KeyError as exc:
            raise KeyError(
                f"No CO2/cost data available for concrete with fck = {fck}"
            ) from exc

        cls._cache[concrete] = data

    @classmethod
    def gwp(cls, concrete) -> float:
        """Returns GWP in kg CO2eq / m3."""
        if concrete not in cls._cache:
            cls._register(concrete)
        return cls._cache[concrete]["gwp"]

    @classmethod
    def cost(cls, concrete) -> float:
        """Returns cost in €/m3."""
        if concrete not in cls._cache:
            cls._register(concrete)
        return cls._cache[concrete]["cost"]