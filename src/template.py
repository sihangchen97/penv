from typing import Any


def render_template(obj: Any, variables: dict) -> Any:
    """Recursively replace {var} placeholders in strings."""
    if isinstance(obj, str):
        try:
            return obj.format(**variables)
        except (KeyError, IndexError):
            return obj
    elif isinstance(obj, dict):
        return {k: render_template(v, variables) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_template(item, variables) for item in obj]
    return obj
