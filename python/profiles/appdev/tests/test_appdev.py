import os
import subprocess
import sys

import pytest

HAS_DISPLAY = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


@pytest.mark.skipif(not HAS_DISPLAY, reason="Kivy a besoin d'un affichage (bureau NexOS ou Xvfb)")
def test_kivy_and_kivymd_render_a_window(tmp_path):
    """Lance une vraie application KivyMD dans un sous-processus, capture la fenêtre."""
    shot = tmp_path / "kivy.png"
    code = f"""
import os
os.environ['KIVY_NO_ARGS'] = '1'
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel

class Demo(MDApp):
    def build(self):
        Clock.schedule_once(self.done, 1.5)
        return MDLabel(text='NexOS', halign='center')
    def done(self, *_):
        self.root.export_to_png({str(shot)!r})
        self.stop()

Demo().run()
"""
    app = tmp_path / "demo_app.py"   # KivyMD lit le fichier source de l'application
    app.write_text(code)
    r = subprocess.run([sys.executable, str(app)], check=False, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-1500:]
    assert shot.exists() and shot.stat().st_size > 500


def test_pyside6_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel
    app = QApplication.instance() or QApplication([])
    assert QLabel("NexOS").text() == "NexOS" and app


def test_quality_tools(tmp_path):
    f = tmp_path / "m.py"
    f.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    for cmd in (["ruff", "check", str(f)], ["mypy", str(f)]):
        r = subprocess.run([sys.executable, "-m", *cmd], check=False, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


def test_pyinstaller_builds_runnable_executable(tmp_path):
    """Distribution : construit un exécutable autonome puis l'exécute."""
    (tmp_path / "hello.py").write_text("print('Bonjour NexOS')\n")
    r = subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconfirm", "--log-level", "ERROR",
                        "--distpath", str(tmp_path / "dist"), "--workpath", str(tmp_path / "build"),
                        "--specpath", str(tmp_path), str(tmp_path / "hello.py")],
                       check=False, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-1500:]
    out = subprocess.run([str(tmp_path / "dist" / "hello")], check=False, capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == "Bonjour NexOS"
