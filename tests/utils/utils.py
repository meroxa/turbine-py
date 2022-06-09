import json


def read_fixture(path: str):
    with open(path, "r") as f:
        data = json.load(f)
    return data
