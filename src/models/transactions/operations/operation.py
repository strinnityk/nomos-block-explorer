from core.models import NbeSchema
from models.transactions.operations.contents import NbeContent
from models.transactions.operations.proofs import OperationProof


class Operation(NbeSchema):
    content: NbeContent
    proof: OperationProof
