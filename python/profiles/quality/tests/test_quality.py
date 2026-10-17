import subprocess
import sys
import textwrap

from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.integers()))
def test_hypothesis_sort_idempotent(xs):
    assert sorted(sorted(xs)) == sorted(xs)


def _run(*args, cwd):
    return subprocess.run([sys.executable, "-m", *args], cwd=cwd, capture_output=True, text=True, check=False)


def test_ruff_and_mypy_find_real_problems(tmp_path):
    (tmp_path / "bad.py").write_text(textwrap.dedent("""
        import os
        def f(x: int) -> str:
            return x
    """))
    ruff = _run("ruff", "check", "bad.py", cwd=tmp_path)
    assert ruff.returncode == 1 and "F401" in ruff.stdout          # import inutilisé détecté
    mypy = _run("mypy", "bad.py", cwd=tmp_path)
    assert mypy.returncode == 1 and "Incompatible return value" in mypy.stdout


def test_pytest_coverage_report(tmp_path):
    (tmp_path / "mod.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "test_mod.py").write_text("from mod import add\n\ndef test_add():\n    assert add(2, 3) == 5\n")
    r = _run("pytest", "-q", "--cov=mod", "--cov-report=term", "-p", "no:cacheprovider", cwd=tmp_path)
    assert r.returncode == 0, r.stdout
    assert "mod.py" in r.stdout and "100%" in r.stdout
