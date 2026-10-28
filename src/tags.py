import itertools
import re


def _parse_format(format_str):
    """'XYYZ' -> ['X', 'YY', 'Z']"""
    return [''.join(g) for _, g in itertools.groupby(format_str)]


def _resolve_digits(digits, format_str):
    """digits='2110', format='XYYZ' -> {'X':'2', 'YY':'11', 'Z':'0'}"""
    groups = _parse_format(format_str)
    result = {}
    pos = 0
    for i, name in enumerate(groups):
        if i == len(groups) - 1:
            result[name] = digits[pos:]
        else:
            length = len(name)
            result[name] = digits[pos:pos + length]
            pos += length
    return result


def _eval_expr(expr, fields):
    """'XX.Y.*' with {XX:'13', Y:'0'} -> '13.0.*'"""
    parts = expr.split(".")
    resolved = []
    for part in parts:
        if part.endswith("*"):
            field_val = fields.get(part[:-1], part[:-1])
            resolved.append(f"{field_val}*")
        else:
            resolved.append(fields.get(part, part))
    return ".".join(resolved)


def tag_resolve(patterns, tags):
    """Generate template variable mapping from tag_patterns + tags."""
    variables = {}
    for tag in tags:
        for prefix, formats in patterns.items():
            m = re.match(rf"^{prefix}(\d+)$", tag)
            if not m:
                continue
            digits = m.group(1)
            target = None
            for fmt_str, version_expr in formats.items():
                if len(fmt_str) == len(digits):
                    target = (fmt_str, version_expr)
                    break
            if not target:
                continue
            fmt_str, version_expr = target
            fields = _resolve_digits(digits, fmt_str)
            version = _eval_expr(version_expr, fields)
            variables[f"{prefix}_version"] = version
            variables[f"{prefix}_tag"] = digits
            variables[f"{prefix}_tag_xy"] = digits[:-1]
            variables[f"{prefix}_tag_x"] = digits[:-2]
    return variables


def variables_to_env(variables):
    return {
        f"PIXI_{k.upper()}": v.replace(".*", "")
        for k, v in variables.items()
        if k.endswith(("_tag", "_version"))
    }
