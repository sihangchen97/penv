import re


def _req_matches(req, tags):
    """Check if a require is satisfied by tags (supports wildcard "cu*" and OR "cu128|cu130")."""
    if "|" in req:
        return any(_req_matches(part, tags) for part in req.split("|"))
    if req.endswith("*"):
        prefix = req[:-1]
        return any(re.match(rf"^{prefix}\d+$", t) for t in tags)
    return req in tags


def merge_configs(deps) -> dict:
    """Merge multiple config dicts into one result."""
    result = {}
    for dep in deps:
        cfg = dep["config"]
        for key, value in cfg.items():
            if key == "pypi-options":
                if key not in result:
                    result[key] = {}
                for sub_key, sub_value in value.items():
                    if sub_key not in result[key]:
                        result[key][sub_key] = []
                    existing = result[key][sub_key]
                    for item in sub_value:
                        if item not in existing:
                            existing.append(item)
            elif key in ("dependencies", "pypi-dependencies", "activation.env"):
                if key not in result:
                    result[key] = {}
                result[key].update(value)
    return result


def match_deps(deps, tags):
    """Match dependencies against tags."""
    matched = []
    for dep in deps:
        requires = dep.get("requires", [])
        if not all(_req_matches(req, tags) for req in requires):
            continue
        matched.append(dep)
    return matched
