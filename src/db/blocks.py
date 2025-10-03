from typing import AsyncIterator, Iterable, List

from rusty_results import Empty, Option, Some
from sqlalchemy import Result
from sqlmodel import select

from db.clients import DbClient
from node.models.blocks import Block


class BlockRepository:
    def __init__(self, client: DbClient):
        self.client = client

    async def create(self, block: Iterable[Block]) -> None:
        with self.client.session() as session:
            session.add_all(block)
            session.commit()

    async def get_latest(self, limit: int, descending: bool = True) -> List[Block]:
        statement = select(Block).limit(limit)
        if descending:
            statement = statement.order_by(Block.slot.desc())
        else:
            statement = statement.order_by(Block.slot.asc())

        with self.client.session() as session:
            results: Result[Block] = session.exec(statement)
            return results.all()

    async def updates_stream(self, slot_from: int) -> AsyncIterator[List[Block]]:
        _slot_from = slot_from
        while True:
            statement = select(Block).where(Block.slot >= _slot_from).order_by(Block.slot.asc())

            with self.client.session() as session:
                blocks: List[Block] = session.exec(statement).all()

            if len(blocks) > 0:
                # POC: Assumes slots are sequential and one block per slot
                _slot_from = blocks[-1].slot + 1

            yield blocks

    async def get_earliest(self) -> Option[Block]:
        with self.client.session() as session:
            statement = select(Block).order_by(Block.slot.asc()).limit(1)
            results: Result[Block] = session.exec(statement)
            if (block := results.first()) is not None:
                return Some(block)
            else:
                return Empty()
