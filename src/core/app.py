from asyncio import Task, gather
from typing import Optional

from fastapi import FastAPI
from starlette.datastructures import State

from db.blocks import BlockRepository
from db.clients import DbClient
from db.transaction import TransactionRepository
from node.api.base import NodeApi
from node.manager.base import NodeManager


class NBEState(State):
    signal_exit: bool = False
    node_manager: Optional[NodeManager]
    node_api: Optional[NodeApi]
    db_client: DbClient
    block_repository: BlockRepository
    transaction_repository: TransactionRepository
    subscription_to_updates_handle: Task
    backfill_handle: Task

    @property
    def is_running(self) -> bool:
        return not self.signal_exit

    async def stop(self):
        self.signal_exit = True
        await self._wait_tasks_finished()

    async def _wait_tasks_finished(self):
        await gather(
            self.subscription_to_updates_handle,
            self.backfill_handle,
            return_exceptions=True,
        )


class NBE(FastAPI):
    state: NBEState

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = NBEState()
