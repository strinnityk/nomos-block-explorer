from typing import Literal

from sqlalchemy import Float, Integer, String, cast, func


def order_by_json(
    sql_expr, path: str, *, into_type: Literal["int", "float", "text"] = "text", descending: bool = False
):
    expression = jget(sql_expr, path, into_type=into_type)
    return expression.desc() if descending else expression.asc()


def jget(sql_expr, path: str, *, into_type: Literal["int", "float", "text"] = "text"):
    expression = func.json_extract(sql_expr, path)
    match into_type:
        case "int":
            expression = cast(expression, Integer)
        case "float":
            expression = cast(expression, Float)
        case "text":
            expression = cast(expression, String)
    return expression
