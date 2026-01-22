from abc import ABC, abstractmethod

class Slab(ABC):
    """Abstract base class for slab elements."""

    @abstractmethod
    def self_load(self) -> float:
        """
        Returns the self-weight load of the slab [kN/m²]
        """
        pass

    @abstractmethod
    def infill_load(self) -> float:
        """
        Returns the load due to infill on the slab [kN/m²]
        """
        pass

