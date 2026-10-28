import os


def update_toml(toml_path, merged, variables=None):
    """Apply merged config to existing pixi.toml using tomlkit."""
    import tomlkit

    assert os.path.exists(toml_path), f"pixi.toml not found: {toml_path}"
    with open(toml_path, "r") as f:
        doc = tomlkit.load(f)

    # Remove old penv sections if they exist
    if "feature" in doc and "penv" in doc["feature"]:
        del doc["feature"]["penv"]
    if "environments" in doc and "penv" in doc["environments"]:
        del doc["environments"]["penv"]

    # Build [feature.penv]
    penv = tomlkit.table()

    if "dependencies" in merged:
        penv["dependencies"] = tomlkit.table()
        for k, v in merged["dependencies"].items():
            penv["dependencies"][k] = v

    if "activation.env" in merged:
        act = tomlkit.table()
        act["env"] = tomlkit.table()
        for k, v in merged["activation.env"].items():
            act["env"][k] = v
        penv["activation"] = act

    if "pypi-options" in merged:
        pypi_opts = tomlkit.table()
        for k, v in merged["pypi-options"].items():
            if isinstance(v, list):
                arr = tomlkit.array()
                arr.multiline(True)
                if k == "find-links":
                    for item in v:
                        it = tomlkit.inline_table()
                        it["url"] = item
                        arr.append(it)
                else:
                    for item in v:
                        arr.append(item)
                pypi_opts[k] = arr
            else:
                pypi_opts[k] = v
        penv["pypi-options"] = pypi_opts

    if "pypi-dependencies" in merged:
        penv["pypi-dependencies"] = tomlkit.table()
        for k, v in merged["pypi-dependencies"].items():
            penv["pypi-dependencies"][k] = v

    if "feature" not in doc:
        doc["feature"] = tomlkit.table()
    doc["feature"]["penv"] = penv
    doc["feature"].add(tomlkit.nl())

    # Ensure [feature.custom] exists with empty dependency tables
    if "feature" not in doc:
        doc["feature"] = tomlkit.table()
    if "custom" not in doc.get("feature", {}):
        custom = tomlkit.table()
        custom["dependencies"] = tomlkit.table()
        custom["pypi-dependencies"] = tomlkit.table()
        doc["feature"]["custom"] = custom

    # Create or update [environments].default
    if "environments" not in doc:
        doc["environments"] = tomlkit.table()

    if "default" in doc["environments"]:
        existing_default = doc["environments"]["default"]
        features = existing_default.get("features")
        if features is None:
            features = tomlkit.array()
            existing_default["features"] = features
        for f in ("penv", "custom"):
            if f not in features:
                features.append(f)
    else:
        env_table = tomlkit.inline_table()
        env_table["features"] = ["penv", "custom"]
        doc["environments"]["default"] = env_table

    with open(toml_path, "w") as f:
        tomlkit.dump(doc, f)
