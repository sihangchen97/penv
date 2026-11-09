import sys
from typing import Any


def render_template(obj: Any, variables: dict) -> Any:
    """Recursively replace {var} placeholders in strings."""
    if isinstance(obj, str):
        try:
            return obj.format(**variables)
        except (KeyError, IndexError, ValueError, AttributeError, TypeError) as e:
            # 部分变量缺失/格式符错误时保留原串（有意设计），但打 warning 便于诊断
            print(f"Warning: template render failed for {obj!r}: {type(e).__name__}: {e}",
                  file=sys.stderr)
            return obj
    elif isinstance(obj, dict):
        return {k: render_template(v, variables) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_template(item, variables) for item in obj]
    return obj
