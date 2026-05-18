def test_native_c_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "Compiling custom module: hello", timeout=60)
    s.wait_log("obbyircd", "third/hello.so", timeout=30)
    conf = (s.data_root / "conf" / "custom-modules.conf").read_text()
    assert 'loadmodule "third/hello";' in conf


def test_obbyscript_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "Loaded JavaScript script: hello.js", timeout=60)


def test_obbypy_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "hello.py", timeout=60)
    assert "E2E_PY_LOADED" in s.logs("obbyircd") or "Loaded" in s.logs("obbyircd")
