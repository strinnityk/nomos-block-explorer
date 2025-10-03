import asyncio

import uvicorn

from app import create_app
from logs import setup_logging


async def main():
    app = create_app()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        loop="asyncio",
        log_config=None,
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        # Swallow debugger’s SIGINT
        pass


# Pycharm-Debuggable Uvicorn Server
if __name__ == "__main__":
    try:
        setup_logging()
        asyncio.run(main())
    except KeyboardInterrupt:
        # Graceful stop triggered by debugger/CTRL-C
        pass
