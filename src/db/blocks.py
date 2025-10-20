from asyncio import sleep
from typing import AsyncIterator, List, Optional

from rusty_results import Empty, Option, Some
from sqlalchemy import Result, Select
from sqlalchemy.orm import aliased
from sqlmodel import select

from core.db import jget, order_by_json
from db.clients import DbClient
from node.models.blocks import Block


def get_latest_statement(limit: int, latest_ascending: bool = True) -> Select:
    # Fetch latest
    descending = order_by_json(Block.header, "$.slot", into_type="int", descending=True)
    inner = select(Block).order_by(descending, Block.id.desc()).limit(limit).subquery()

    # Reorder
    latest = aliased(Block, inner)
    latest_order = order_by_json(latest.header, "$.slot", into_type="int", descending=(not latest_ascending))
    id_order = latest.id.asc() if latest_ascending else latest.id.desc()
    statement = select(latest).order_by(latest_order, id_order)  # type: ignore[arg-type]
    return statement


class BlockRepository:
    """
    FIXME: Assumes slots are sequential and one block per slot
    """

    def __init__(self, client: DbClient):
        self.client = client

    async def create(self, *blocks: Block) -> None:
        with self.client.session() as session:
            session.add_all(list(blocks))
            session.commit()

    async def get_latest(self, limit: int, *, ascending: bool = True) -> List[Block]:
        statement = get_latest_statement(limit, ascending)

        with self.client.session() as session:
            results: Result[Block] = session.exec(statement)
            return results.all()

    async def get_by_id(self, block_id: int) -> Option[Block]:
        statement = select(Block).where(Block.id == block_id)

        with self.client.session() as session:
            result: Result[Block] = session.exec(statement)
            if (block := result.first()) is not None:
                return Some(block)
            else:
                return Empty()

    async def updates_stream(
        self, block_from: Optional[Block], *, timeout_seconds: int = 1
    ) -> AsyncIterator[List[Block]]:
        # FIXME
        slot_cursor = block_from.slot + 1 if block_from is not None else 0
        block_slot_expression = jget(Block.header, "$.slot", into_type="int")
        order = order_by_json(Block.header, "$.slot", into_type="int", descending=False)

        while True:
            where_clause = block_slot_expression >= slot_cursor
            statement = select(Block).where(where_clause).order_by(order)

            with self.client.session() as session:
                blocks: List[Block] = session.exec(statement).all()

            if len(blocks) > 0:
                slot_cursor = blocks[-1].slot + 1
                yield blocks
            else:
                await sleep(timeout_seconds)

    async def get_earliest(self) -> Option[Block]:
        order = order_by_json(Block.header, "$.slot", into_type="int", descending=False)
        statement = select(Block).order_by(order).limit(1)

        with self.client.session() as session:
            results: Result[Block] = session.exec(statement)
            if (block := results.first()) is not None:
                return Some(block)
            else:
                return Empty()
