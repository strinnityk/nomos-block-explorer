from abc import ABC, abstractmethod
from typing import Iterator

from sqlmodel.ext.asyncio.session import AsyncSession


class DbClient(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def session(self) -> Iterator[AsyncSession]:
        pass

    @abstractmethod
    def disconnect(self):
        pass
