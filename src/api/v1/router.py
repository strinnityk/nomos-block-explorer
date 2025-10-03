from fastapi import APIRouter

from . import blocks, health, index, transactions

router = APIRouter()
router.add_api_route("/", index.index, methods=["GET", "HEAD"])
router.add_api_route("/health", health.get, methods=["GET", "HEAD"])
router.add_api_route("/health/stream", health.stream, methods=["GET", "HEAD"])

router.add_api_route("/transactions/stream", transactions.stream, methods=["GET"])
router.add_api_route("/blocks/stream", blocks.stream, methods=["GET"])
