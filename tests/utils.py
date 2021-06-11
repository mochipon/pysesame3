import json
import os


def load_fixture(filename):
    """Load a fixture."""
    with open(
        os.path.join(os.path.dirname(__file__), "fixtures", filename), encoding="utf-8"
    ) as fp:
        data = json.load(fp)
    return data
