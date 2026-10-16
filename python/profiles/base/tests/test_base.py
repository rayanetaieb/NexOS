import sys


def test_python_version():
    assert sys.version_info[:2] == (3, 13)


def test_tools_import():
    import IPython, pytest, requests, rich  # noqa: F401,E401
    assert requests.__version__
