def test_native_c_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "Compiling custom module: hello", timeout=60)
    s.wait_log("obbyircd", "third/hello.so", timeout=30)
    conf = s.read_container_file("obbyircd", "/home/obbyircd/obby/conf/custom-modules.conf")
    assert 'loadmodule "third/hello";' in conf


def test_obbyscript_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "Loaded JavaScript script: hello.js", timeout=60)


def test_obbypy_autoloads(stack_factory):
    s = stack_factory("modules")
    s.wait_log("obbyircd", "Loaded /home/obbyircd/obby/conf/scripts/python/hello.py", timeout=60)
