"""Scénario piloté de l'interface (Qt hors écran) : liste des profils, installation
réelle du profil « base » par le bouton, création d'un projet, ajout d'un paquet."""
import os
import shutil
import time
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

from nexos_python import core

REPO_PROFILES = Path(__file__).resolve().parents[3] / "python" / "profiles"
NET = pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="intégration réseau")


@pytest.fixture
def window(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("NEXOS_PROJECTS", str(tmp_path / "projets"))
    monkeypatch.setenv("NEXOS_PYTHON_PROFILES", str(REPO_PROFILES))
    monkeypatch.setenv("NEXOS_PYTHON", shutil.which("python3.13") or "/usr/bin/python3")
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    from nexos_python.gui import CenterWindow
    app = QApplication.instance() or QApplication([])
    w = CenterWindow(); w.show()
    yield app, w
    w.close()


def wait_idle(app, w, timeout=600):
    t0 = time.time()
    while w._thread is not None and time.time() - t0 < timeout:
        app.processEvents(); time.sleep(0.05)
    app.processEvents()
    assert w._thread is None, "opération toujours en cours"


def test_profiles_listed(window):
    _app, w = window
    names = {w.profile_list.item(i).data(256) for i in range(w.profile_list.count())}
    assert {"base", "science", "ai", "vision", "electronics", "appdev"} <= names


def test_catalog_search_filters(window):
    app, w = window
    w.search.setText("série"); app.processEvents()
    assert w.cat_table.rowCount() >= 1 and w.cat_table.item(0, 0).text() == "pyserial"


@NET
def test_install_profile_via_button_then_project(window):
    app, w = window
    for i in range(w.profile_list.count()):
        if w.profile_list.item(i).data(256) == "base":
            w.profile_list.setCurrentRow(i)
    w.install_profile(); wait_idle(app, w)
    assert core.get_profile("base").installed
    assert "✔ Installation du profil base : terminé" in w.console.toPlainText()
    assert w.profile_list.currentItem() is not None, "sélection perdue après rafraîchissement"
    assert "✔ installé" in w.profile_list.currentItem().text()
    # projet + paquet
    w.start("Création", core.create_project, "demo", None, then=lambda r: w.refresh_projects())
    wait_idle(app, w)
    w.project_list.setCurrentRow(0); app.processEvents()
    w.pkg_input.setText("six"); w.add_pkg(); wait_idle(app, w)
    rows = [w.pkg_table.item(r, 0).text() for r in range(w.pkg_table.rowCount())]
    assert "six" in rows
