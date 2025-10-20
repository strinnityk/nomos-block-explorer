from asyncio import sleep
from typing import AsyncIterator, Iterable, List, Optional

from rusty_results import Empty, Option, Some
from sqlalchemy import Result, Select
from sqlalchemy.orm import aliased, selectinload
from sqlmodel import select

from core.db import jget, order_by_json
from db.clients import DbClient
from node.models.transactions import Transaction


def get_latest_statement(
    limit: int, output_ascending: bool = True, preload_relationships: bool = False, **kwargs
) -> Select:
    from node.models.blocks import Block

    # Join with Block to order by Block's slot
    slot_expr = jget(Block.header, "$.slot", into_type="int").label("slot")
    slot_desc = order_by_json(Block.header, "$.slot", into_type="int", descending=True)
    inner = (
        select(Transaction, slot_expr)
        .join(Block, Transaction.block_id == Block.id, isouter=False)
        .order_by(slot_desc, Block.id.desc())
        .limit(limit)
        .subquery()
    )

    # Reorder
    latest = aliased(Transaction, inner)
    output_slot_order = inner.c.slot.asc() if output_ascending else inner.c.slot.desc()
    output_id_order = (
        latest.id.asc() if output_ascending else latest.id.desc()
    )  # TODO: Double check it's Transaction.id
    statement = select(latest).order_by(output_slot_order, output_id_order)
    if preload_relationships:
        statement = statement.options(selectinload(latest.block))
    return statement


class TransactionRepository:
    def __init__(self, client: DbClient):
        self.client = client

    async def create(self, transaction: Iterable[Transaction]) -> None:
        with self.client.session() as session:
            session.add_all(transaction)
            session.commit()

    async def get_latest(self, limit: int, *, ascending: bool = True, **kwargs) -> List[Transaction]:
        statement = get_latest_statement(limit, ascending, **kwargs)

        with self.client.session() as session:
            results: Result[Transaction] = session.exec(statement)
            return results.all()

    async def get_by_id(self, transaction_id: int) -> Option[Transaction]:
        statement = select(Transaction).where(Transaction.id == transaction_id)

        with self.client.session() as session:
            result: Result[Transaction] = session.exec(statement)
            if (transaction := result.first()) is not None:
                return Some(transaction)
            else:
                return Empty()

    async def updates_stream(
        self, transaction_from: Optional[Transaction], *, timeout_seconds: int = 1
    ) -> AsyncIterator[List[Transaction]]:
        from node.models.blocks import Block

        slot_cursor: int = transaction_from.block.slot + 1 if transaction_from is not None else 0
        slot_expression = jget(Block.header, "$.slot", into_type="int")
        slot_order = order_by_json(Block.header, "$.slot", into_type="int", descending=False)

        while True:
            where_clause_slot = slot_expression >= slot_cursor
            where_clause_id = Transaction.id > transaction_from.id if transaction_from is not None else True

            statement = (
                select(Transaction)
                .options(selectinload(Transaction.block))
                .join(Block, Transaction.block_id == Block.id)
                .where(where_clause_slot, where_clause_id)
                .order_by(slot_order, Block.id.asc(), Transaction.id.asc())
            )

            with self.client.session() as session:
                transactions: List[Transaction] = session.exec(statement).all()

            if len(transactions) > 0:
                slot_cursor = transactions[-1].block.slot + 1
                yield transactions
            else:
                await sleep(timeout_seconds)
