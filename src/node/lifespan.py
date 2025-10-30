import logging
from asyncio import TaskGroup, create_task, sleep
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, AsyncIterator, List

from rusty_results import Option

from db.blocks import BlockRepository
from db.clients import SqliteClient
from db.transaction import TransactionRepository
from models.block import Block
from models.transactions.transaction import Transaction
from node.api.fake import FakeNodeApi
from node.api.http import HttpNodeApi
from node.api.serializers.block import BlockSerializer
from node.manager.docker import DockerModeManager
from node.manager.fake import FakeNodeManager

if TYPE_CHECKING:
    from core.app import NBE

logger = logging.getLogger(__name__)


@asynccontextmanager
async def node_lifespan(app: "NBE") -> AsyncGenerator[None]:
    db_client = SqliteClient()

    app.state.node_manager = FakeNodeManager()
    # app.state.node_manager = DockerModeManager(app.settings.node_compose_filepath)
    app.state.node_api = FakeNodeApi()
    # app.state.node_api = HttpNodeApi(host="127.0.0.1", port=18080)

    app.state.db_client = db_client
    app.state.block_repository = BlockRepository(db_client)
    app.state.transaction_repository = TransactionRepository(db_client)
    try:
        logger.info("Starting node...")
        await app.state.node_manager.start()
        logger.info("Node started.")

        app.state.subscription_to_updates_handle = create_task(subscribe_to_updates(app))
        app.state.backfill = create_task(backfill(app))

        yield
    finally:
        logger.info("Stopping node...")
        await app.state.node_manager.stop()
        logger.info("Node stopped.")


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


async def subscribe_to_updates(app: "NBE") -> None:
    logger.info("✅ Subscription to new blocks and transactions started.")
    async with TaskGroup() as tg:
        tg.create_task(subscribe_to_new_blocks(app))
        tg.create_task(subscribe_to_new_transactions(app))
    logger.info("Subscription to new blocks and transactions finished.")


async def _gracefully_close_stream(stream: AsyncIterator) -> None:
    aclose = getattr(stream, "aclose", None)
    if aclose is not None:
        try:
            await aclose()
        except Exception as e:
            logger.error(f"Error while closing the new blocks stream: {e}")


async def subscribe_to_new_blocks(app: "NBE"):
    blocks_stream: AsyncGenerator[BlockSerializer] = app.state.node_api.get_blocks_stream()  # type: ignore[call-arg]
    try:
        while app.state.is_running:
            try:
                block_serializer = await anext(blocks_stream)  # TODO: Use anext's Sentinel?
            except TimeoutError:
                continue
            except StopAsyncIteration:
                import traceback

                traceback.print_exc()
                logger.error("Subscription to the new blocks stream ended unexpectedly. Please restart the node.")
                break
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.error(f"Error while fetching new blocks: {e}")
                continue

            try:
                block = block_serializer.into_block()
                await app.state.block_repository.create(block)
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.error(f"Error while saving new block: {e}")
    finally:
        await _gracefully_close_stream(blocks_stream)


async def subscribe_to_new_transactions(_app: "NBE"):
    pass


async def backfill(app: "NBE") -> None:
    logger.info("Backfilling started.")
    async with TaskGroup() as tg:
        tg.create_task(backfill_blocks(app, db_hit_interval_seconds=3))
        tg.create_task(backfill_transactions(app))
    logger.info("✅ Backfilling finished.")


async def get_earliest_block_slot(app: "NBE") -> Option[int]:
    earliest_block: Option[Block] = await app.state.block_repository.get_earliest()
    return earliest_block.map(lambda block: block.slot)


async def backfill_blocks(app: "NBE", *, db_hit_interval_seconds: int, batch_size: int = 50):
    """
    FIXME: This is a very naive implementation:
      - One block per slot.
      - There's at most one gap to backfill (from genesis to earliest block).
    FIXME: First block received is slot=2
    """
    logger.info("Checking for block gaps to backfill...")
    # Hit the database until we get a block
    while (earliest_block_slot_option := await get_earliest_block_slot(app)).is_empty:
        logger.debug("No blocks were found in the database yet. Waiting...")
        await sleep(db_hit_interval_seconds)
    earliest_block_slot: int = earliest_block_slot_option.unwrap()

    if earliest_block_slot == 0:
        logger.info("No blocks to backfill.")
        return

    slot_to = earliest_block_slot - 1
    logger.info(f"Backfilling blocks from slot {slot_to} down to 0...")
    while slot_to > 0:
        slot_from = max(0, slot_to - batch_size)
        blocks_serializers: List[BlockSerializer] = await app.state.node_api.get_blocks(
            slot_from=slot_from, slot_to=slot_to
        )
        blocks: List[Block] = [block_serializer.into_block() for block_serializer in blocks_serializers]
        logger.debug(f"Backfilling {len(blocks)} blocks from slot {slot_from} to {slot_to}...")
        await app.state.block_repository.create(*blocks)
        slot_to = slot_from - 1
    logger.info("Backfilling blocks completed.")


async def backfill_transactions(_app: "NBE"):
    pass
