#!/usr/bin/env python3
"""penv - Generate [feature.penv] in pixi.toml based on environment name."""

import argparse
import os
import shutil
import subprocess
import sys

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import (
    load_config,
    load_tag_patterns,
    tag_resolve,
    render_template,
    match_deps,
    merge_configs,
    update_toml,
    variables_to_env,
)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    if cwd == script_dir:
        print("Error: do not run penv.py from its own directory. Run from a project directory.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate [feature.penv] in pixi.toml")
    parser.add_argument("env_name", help="Environment name, e.g. py311-pt2110-cu130")
    parser.add_argument("--fvdb", action="store_true", help="Add fvdb-core dependency")
    parser.add_argument("--natten", action="store_true", help="Add natten dependency")
    args = parser.parse_args()

    tags = set(args.env_name.split("-"))
    flags = set()
    if args.fvdb:
        flags.add("fvdb")
    if args.natten:
        flags.add("natten")

    config = load_config(flags)
    patterns = load_tag_patterns()
    variables = tag_resolve(patterns, tags)
    matched = match_deps(config, tags)

    if not matched:
        print(f"Error: no dependencies matched for environment {args.env_name}", file=sys.stderr)
        sys.exit(1)

    merged = merge_configs(matched)
    merged = render_template(merged, variables)

    # Build activation.env
    merged["activation.env"] = {**merged.get("activation.env", {}), **variables_to_env(variables)}

    toml_path = os.path.join(cwd, "pixi.toml")
    if not os.path.exists(toml_path):
        print("No pixi.toml found, running pixi init...")
        if not shutil.which("pixi"):
            print("Error: pixi not found in PATH", file=sys.stderr)
            sys.exit(1)
        subprocess.run(["pixi", "init"], check=True)

    update_toml(toml_path, merged, variables)
    print(f"Updated {toml_path} with [feature.penv] and [environments].default for {args.env_name}")


if __name__ == "__main__":
    main()
