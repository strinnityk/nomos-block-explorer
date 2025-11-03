import logging
from typing import TYPE_CHECKING

from python_on_whales import DockerException
from python_on_whales.docker_client import DockerClient
from rusty_results import Err, Ok, Result

from node.manager.base import NodeManager

if TYPE_CHECKING:
    from core.app import NBESettings


logger = logging.getLogger(__name__)


class DockerModeManager(NodeManager):
    def __init__(self, settings: "NBESettings"):
        self.client: DockerClient = DockerClient(
            client_type="docker",
            compose_files=[settings.node_compose_filepath],
        )

        match self.ps():
            case Err(1):
                logger.error("Docker compose services are not running.")
                exit(21)  # FIXME: There's too much output here: Don't exit here, raise error and exit outside.
            case Err(_):
                logger.error("Failed to run docker compose.")
                exit(20)

    def ps(self, only_running: bool = True) -> Result:
        try:
            services = self.client.compose.ps(all=(not only_running))  # TODO: Filter compose services.
        except DockerException as e:
            return Err(e.return_code)
        return Ok(services)

    async def start(self):
        services = self.ps().map(lambda _services: len(_services)).expect("Failed to get compose services.")
        if services > 0:
            logger.warning("Compose services are already running.")
            return

        self.client.compose.up(
            detach=True,
            build=False,
            remove_orphans=True,
        )

    async def stop(self):
        self.client.compose.down(remove_orphans=True, volumes=True)
