from abc import ABC, abstractmethod
from random import choice
from typing import Self


class FromRandom(ABC):
    @classmethod
    @abstractmethod
    def from_random(cls, *args, **kwargs) -> Self:
        raise NotImplementedError


# TODO: Unnecessarily complex.
class EnforceSubclassFromRandom(FromRandom, ABC):
    @classmethod
    def from_random(cls, *args, **kwargs) -> Self:
        subclasses = cls.__subclasses__()
        if len(subclasses) == 0:
            raise TypeError("No subclasses were found.")
        return choice(subclasses).from_random(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Distance to the base in the MRO
        try:
            distance = cls.mro().index(EnforceSubclassFromRandom)
        except ValueError:
            return  # Not a descendant (shouldn't happen here)

        # Require override only for grandchildren (exactly two levels below)
        if distance >= 2 and not hasattr(cls, "from_random"):
            raise TypeError(
                f"Class {cls.__name__} is a grandchild of EnforceSubclassFromRandom. Therefore, it must implement `from_random()`."
            )
