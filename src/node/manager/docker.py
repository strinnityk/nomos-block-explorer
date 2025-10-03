from os import environ
from pathlib import Path

from python_on_whales.docker_client import DockerClient

from node.manager.base import NodeManager


class DockerModeManager(NodeManager):
    COMPOSE_FILE: Path = Path(environ["NODE_COMPOSE_FILEPATH"])

    def __init__(self):
        self.client: DockerClient = DockerClient(
            client_type="docker",
            compose_files=[
                self.COMPOSE_FILE,
            ],
        )

    async def start(self):
        self.client.compose.up(
            detach=True,
            build=False,
            remove_orphans=True,
        )

    async def stop(self):
        self.client.compose.down(remove_orphans=True, volumes=True)
