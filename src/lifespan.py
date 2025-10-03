import typing
from contextlib import AsyncExitStack, asynccontextmanager

from node.lifespan import node_lifespan

if typing.TYPE_CHECKING:
    from core.app import NBE


@asynccontextmanager
async def lifespan(app: "NBE"):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(node_lifespan(app))
        yield
