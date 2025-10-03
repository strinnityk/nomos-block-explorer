from datetime import datetime, timedelta
from typing import AsyncIterator, Iterable, List

from rusty_results import Empty, Option, Some
from sqlalchemy import Result
from sqlmodel import select

from db.clients import DbClient
from node.models.transactions import Transaction
from utils.datetime import increment_datetime


class TransactionRepository:
    def __init__(self, client: DbClient):
        self.client = client

    async def create(self, transaction: Iterable[Transaction]) -> None:
        with self.client.session() as session:
            session.add_all(transaction)
            session.commit()

    async def get_latest(self, limit: int, descending: bool = True) -> List[Transaction]:
        statement = select(Transaction).limit(limit)
        if descending:
            statement = statement.order_by(Transaction.timestamp.desc())
        else:
            statement = statement.order_by(Transaction.timestamp.asc())

        with self.client.session() as session:
            results: Result[Transaction] = session.exec(statement)
            return results.all()

    async def updates_stream(self, timestamp_from: datetime) -> AsyncIterator[List[Transaction]]:
        _timestamp_from = timestamp_from
        while True:
            statement = (
                select(Transaction)
                .where(Transaction.timestamp >= _timestamp_from)
                .order_by(Transaction.timestamp.asc())
            )

            with self.client.session() as session:
                transactions: List[Transaction] = session.exec(statement).all()

            if len(transactions) > 0:
                # POC: Assumes transactions are inserted in order and with a minimum 1 of second difference
                _timestamp_from = increment_datetime(transactions[-1].timestamp)

            yield transactions

    async def get_earliest(self) -> Option[Transaction]:
        with self.client.session() as session:
            statement = select(Transaction).order_by(Transaction.slot.asc()).limit(1)
            results: Result[Transaction] = session.exec(statement)
            if (transaction := results.first()) is not None:
                return Some(transaction)
            else:
                return Empty()
