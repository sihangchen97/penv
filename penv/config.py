import glob
import json
import os

import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")


def load_config(flags=None):
    if flags is None:
        flags = []
    result = []
    files = sorted(glob.glob(os.path.join(_CONFIG_DIR, "*.yaml")))
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        if name.startswith("_") or name in flags:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, list):
                raise ValueError(f"Config file {path} must contain a YAML list, got {type(data).__name__}")
            result.extend(data)
    return result


def load_tag_patterns():
    with open(os.path.join(_CONFIG_DIR, "_tag_patterns.json"), "r") as f:
        return json.load(f)
