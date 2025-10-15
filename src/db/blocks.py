from asyncio import sleep
from typing import AsyncIterator, List, Literal

from rusty_results import Empty, Option, Some
from sqlalchemy import Float, Integer, Result, String, cast, func
from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import Select

from db.clients import DbClient
from node.models.blocks import Block


def order_by_json(
    sql_expr, path: str, *, into_type: Literal["int", "float", "text"] = "text", descending: bool = False
):
    expression = jget(sql_expr, path, into_type=into_type)
    return expression.desc() if descending else expression.asc()


def jget(sql_expr, path: str, *, into_type: Literal["int", "float", "text"] = "text"):
    expression = func.json_extract(sql_expr, path)
    match into_type:
        case "int":
            expression = cast(expression, Integer)
        case "float":
            expression = cast(expression, Float)
        case "text":
            expression = cast(expression, String)
    return expression


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

    async def updates_stream(self, slot_from: int, *, timeout_seconds: int = 1) -> AsyncIterator[List[Block]]:
        slot_cursor = slot_from
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
        with self.client.session() as session:
            order = order_by_json(Block.header, "$.slot", into_type="int", descending=False)
            statement = select(Block).order_by(order).limit(1)
            results: Result[Block] = session.exec(statement)
            if (block := results.first()) is not None:
                return Some(block)
            else:
                return Empty()
