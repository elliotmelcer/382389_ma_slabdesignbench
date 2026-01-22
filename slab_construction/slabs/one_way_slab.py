from abc import ABC, abstractmethod

from structuralcodes.sections import GenericSection

from slab_construction.slabs.slab import Slab


class OneWaySlab(Slab, ABC):

    @property
    @abstractmethod
    def L(self) -> float:
        pass

    @property
    @abstractmethod
    def B(self) -> float:
        pass

    @abstractmethod
    def section_at(self, x: float) -> GenericSection:
        r"""
        This method returns the section of a one-way-slab at x.
        Note: Input domain must be normalized to the following model:
        # x = 0 at first support, x = 1 at second support, etc.
        #
        #   |-> x
        #   0      0.5      1      1.5      2
        #
        #   ====================================|...
        #  /_\             /_\             /_\
        #
        :param x:
        :return:
        """
        pass
