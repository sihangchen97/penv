"""ocr_scan_result.json 1-10 号修复的回归测试。

无 pytest 依赖，直接跑：python tests/test_scan_fixes.py
"""
import contextlib
import inspect
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penv.config import load_config
from penv.matcher import _req_matches, merge_configs
from penv.template import render_template


def _capture_stderr(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        try:
            return fn(*a, **kw)
        finally:
            return_value = fn.__name__  # 仅占位，真正返回值在下面重新拿
    return buf.getvalue()


def test_yaml_list_validation():
    """空/非 list 的配置文件 → ValueError 并报文件名。"""
    import penv.config as cfg_mod
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "_bad.yaml")
        with open(p, "w") as f:
            f.write("just: a\nmapping: b\n")   # 合法 YAML 但是 mapping，不是 list
        orig = cfg_mod._CONFIG_DIR
        try:
            cfg_mod._CONFIG_DIR = d
            try:
                load_config()
                raise AssertionError("expected ValueError")
            except ValueError as e:
                assert "must contain a YAML list" in str(e), str(e)
                assert p in str(e), str(e)
        finally:
            cfg_mod._CONFIG_DIR = orig


def test_re_escape_in_matcher():
    """带正则元字符的 prefix 按字面匹配，不误中。"""
    assert _req_matches("py*", {"py311"})             # 简单前缀通配（现有 configs 的用法）不受影响
    assert _req_matches("cu*", {"cu130"})
    assert not _req_matches("py.3*", {"py311"})       # 字面点号不再当通配符
    assert _req_matches("py.3*", {"py.311"})


def test_unknown_config_key_warns():
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        merge_configs([{"name": "x", "config": {"pypi-deps": {"torch": "1"}}}])
    assert "unknown config key 'pypi-deps'" in buf.getvalue()


def test_template_render_warns():
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        r = render_template("{missing_var}", {})
    assert r == "{missing_var}"
    assert "template render failed" in buf.getvalue()


def test_update_toml_signature_and_file_error():
    from penv.toml_writer import update_toml
    assert "variables" not in inspect.signature(update_toml).parameters
    try:
        update_toml("/nonexistent/pixi.toml", {})
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass


def test_config_no_mutable_default():
    src = inspect.getsource(load_config)
    assert "flags=[]" not in src


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ok {name}")
    print("OK")


if __name__ == "__main__":
    main()
