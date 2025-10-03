import json


def ndjson(json_data: dict | list) -> bytes:
    return (json.dumps(json_data) + "\n").encode("utf-8")
