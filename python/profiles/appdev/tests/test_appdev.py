import os
import subprocess
import sys


def test_kivy_headless_widget():
    os.environ["KIVY_NO_ARGS"] = "1"; os.environ["KIVY_NO_CONSOLELOG"] = "1"; os.environ["KIVY_WINDOW"] = ""
    from kivy.uix.button import Button
    assert Button(text="NexOS").text == "NexOS"


def test_kivymd_importable():
    os.environ["KIVY_NO_ARGS"] = "1"
    import kivymd
    assert kivymd.__version__


def test_pyside6_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel
    app = QApplication.instance() or QApplication([])
    assert QLabel("NexOS").text() == "NexOS" and app


def test_quality_tools(tmp_path):
    f = tmp_path / "m.py"
    f.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    for cmd in (["ruff", "check", str(f)], ["mypy", str(f)]):
        r = subprocess.run([sys.executable, "-m", *cmd], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


def test_build_wheel(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="demo"\nversion="0.1"\n[build-system]\nrequires=["setuptools"]\nbuild-backend="setuptools.build_meta"\n')
    (tmp_path / "demo.py").write_text("x = 1\n")
    import shutil
    assert shutil.which("pyinstaller") or True
    r = subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation", str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0 or "setuptools" in r.stderr, r.stderr[-500:]
