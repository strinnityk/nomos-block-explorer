from typing import TYPE_CHECKING

from node.manager.base import NodeManager
from node.manager.docker import DockerModeManager
from node.manager.noop import NoopNodeManager

if TYPE_CHECKING:
    from core.app import NBESettings


def build_node_manager(settings: "NBESettings") -> NodeManager:
    match settings.node_manager:
        case "docker":
            return DockerModeManager(settings)
        case "noop":
            return NoopNodeManager(settings)
        case _:
            raise ValueError(f"Unknown Manager name: {settings.node_manager}. Available options are: 'docker', 'noop'.")
