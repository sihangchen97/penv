# penv

Generate `[feature.penv]` in `pixi.toml` based on environment tags.

## Quick Start

Add `bin/` to PATH:

```bash
export PATH="$PATH:/path/to/penv/bin"
```

Run from any project directory:

```bash
penv py311-pt2110-cu130
```

Optional flags:

```bash
penv py311-pt2110-cu130 --fvdb --natten
```

## Tag Format

| Tag | Meaning | Example | Resolves to |
|-----|---------|---------|-------------|
| `pyXYZ` | Python | `py311` | Python 3.11.* |
| `ptXYZ` / `ptXYYZ` | PyTorch | `pt2110` | PyTorch 2.11.0 |
| `cuXY` / `cuXXY` | CUDA | `cu130` | CUDA 13.0.* |
| `gccX` / `gccXX` | GCC | `gcc13` | GCC 13.* |

## Config

- `configs/_env.yaml` — base deps (python, gcc, cuda, torch)
- `configs/_tag_patterns.json` — tag → version mapping rules
- `configs/build.yaml` — build tools (cmake, ninja, etc.)
- `configs/_user.yaml` — machine-specific paths (gitignored, create your own)

## How It Works

1. Parse tags from env name (e.g. `py311-pt2110-cu130`)
2. Resolve version variables via tag patterns
3. Match dependency configs against tags
4. Merge configs, render templates, inject `PIXI_*` env vars
5. Write `[feature.penv]` + `[environments].default` to `pixi.toml`
