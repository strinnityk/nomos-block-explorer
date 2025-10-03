import random
from asyncio import TaskGroup, create_task, sleep
from contextlib import asynccontextmanager
from itertools import chain
from typing import TYPE_CHECKING, AsyncGenerator

from rusty_results import Option

from db.blocks import BlockRepository
from db.clients import SqliteClient
from db.transaction import TransactionRepository
from node.api.fake import FakeNodeApi
from node.api.http import HttpNodeApi
from node.manager.docker import DockerModeManager
from node.manager.fake import FakeNodeManager
from node.models.blocks import Block
from node.models.transactions import Transaction

if TYPE_CHECKING:
    from core.app import NBE


@asynccontextmanager
async def node_lifespan(app: "NBE") -> AsyncGenerator[None]:
    # app.state.node_manager = DockerModeManager()
    # app.state.node_api = HttpApi(host="127.0.0.1", port=3000)

    db_client = SqliteClient()

    app.state.node_manager = FakeNodeManager()
    app.state.node_api = FakeNodeApi()
    app.state.db_client = db_client
    app.state.block_repository = BlockRepository(db_client)
    app.state.transaction_repository = TransactionRepository(db_client)
    try:
        print("Starting node...")
        await app.state.node_manager.start()
        print("Node started.")

        app.state.subscription_to_updates_handle = create_task(subscription_to_updates(app))
        app.state.backfill = create_task(backfill(app))

        yield
    finally:
        print("Stopping node...")
        await app.state.node_manager.stop()
        print("Node stopped.")


# ================
# BACKFILLING
# ================
# Legend:
# BT = Block and/or Transaction
# Steps:
# 1. Subscribe to new BT and store them in the database.
# 2. Backfill gaps between the earliest received BT from subscription (step 1.) and the latest BT in the database.
# 3. Backfill gaps between the earliest BT in the database and genesis BT (slot 0).
# Assumptions:
# - BT are always filled correctly.
# - There's at most 1 gap in the BT sequence: From genesis to earliest received BT from subscription.
# - Slots are populated fully or not at all (no partial slots).
# Notes:
# - Upsert always.

# ================
# Fake
_SUBSCRIPTION_START_SLOT = 5  # Simplification for now.
# ================


async def subscription_to_updates(app: "NBE") -> None:
    print("✅ Subscription to new blocks and transactions started.")
    async with TaskGroup() as tg:
        tg.create_task(subscribe_to_new_blocks(app))
        tg.create_task(subscribe_to_new_transactions(app))
    print("Subscription to new blocks and transactions finished.")


async def subscribe_to_new_blocks(
    app: "NBE", interval: int = 5, subscription_start_slot: int = _SUBSCRIPTION_START_SLOT
):
    while app.state.is_running:
        try:
            new_block: Block = Block.from_random(slot_start=subscription_start_slot, slot_end=subscription_start_slot)
            print("> New Block")
            await app.state.block_repository.create((new_block,))
            subscription_start_slot += 1
        except Exception as e:
            print(f"Error while subscribing to new blocks: {e}")
        finally:
            await sleep(interval)


async def subscribe_to_new_transactions(app: "NBE", interval: int = 5):
    while app.state.is_running:
        try:
            new_transaction: Transaction = Transaction.from_random()
            print("> New TX")
            await app.state.transaction_repository.create((new_transaction,))
        except Exception as e:
            print(f"Error while subscribing to new transactions: {e}")
        finally:
            await sleep(interval)


async def backfill(app: "NBE", delay: int = 3) -> None:
    await sleep(delay)  # Wait for some data to be present: Simplification for now.s

    print("Backfilling started.")
    async with TaskGroup() as tg:
        tg.create_task(backfill_blocks(app))
        tg.create_task(backfill_transactions(app))
    print("✅ Backfilling finished.")


async def backfill_blocks(app: "NBE"):
    # Assuming at most one gap. This will be either genesis block (no gap) or the earliest received block from subscription.
    # If genesis, do nothing.
    # If earliest received block from subscription, backfill.
    print("Checking for block gaps to backfill...")
    earliest_block: Option[Block] = await app.state.block_repository.get_earliest()
    earliest_block: Block = earliest_block.expects("Subscription should have provided at least one block by now.")
    earliest_block_slot = earliest_block.slot
    if earliest_block_slot == 0:
        print("No need to backfill blocks, genesis block already present.")
        return

    print(f"Backfilling blocks from slot {earliest_block_slot - 1} down to 0...")

    def n_blocks():
        return random.choices((1, 2, 3), (6, 3, 1))[0]

    blocks = (
        (Block.from_random(slot_start=slot_index, slot_end=slot_index) for _ in range(n_blocks()))
        for slot_index in reversed(range(0, earliest_block_slot))
    )
    flattened = list(chain.from_iterable(blocks))
    await sleep(10)  # Simulate some backfilling delay
    await app.state.block_repository.create(flattened)
    print("Backfilling blocks completed.")


async def backfill_transactions(app: "NBE"):
    # Assume there's some TXs to backfill
    n = random.randint(0, 5)
    print(f"Backfilling {n} transactions...")
    transactions = (Transaction.from_random() for _ in range(n))
    await sleep(10)  # Simulate some backfilling delay
    await app.state.transaction_repository.create(transactions)
    print("Backfilling transactions completed.")
