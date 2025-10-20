from fastapi import APIRouter

from . import blocks, health, index, transactions


def create_v1_router() -> APIRouter:
    router = APIRouter()

    router.add_api_route("/", index.index, methods=["GET", "HEAD"])

    router.add_api_route("/health", health.get, methods=["GET", "HEAD"])
    router.add_api_route("/health/stream", health.stream, methods=["GET", "HEAD"])

    router.add_api_route("/transactions/{transaction_id:int}", transactions.get, methods=["GET"])
    router.add_api_route("/transactions/stream", transactions.stream, methods=["GET"])

    router.add_api_route("/blocks/{block_id:int}", blocks.get, methods=["GET"])
    router.add_api_route("/blocks/stream", blocks.stream, methods=["GET"])

    return router
