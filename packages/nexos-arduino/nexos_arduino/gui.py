"""Centre Arduino NexOS — bibliothèques (catalogue de 100) et diagnostic (PySide6)."""
from __future__ import annotations

import subprocess
import sys

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import core

TEST_LABEL = {"ok": "✔ compile (AVR)", "non testable": "— autre carte", "échec": "✖ échec"}


class Job(QObject):
    done = Signal(bool, str)
    def __init__(self, fn, *args):
        super().__init__(); self.fn, self.args = fn, args
    @Slot()
    def run(self):
        try:
            r = self.fn(*self.args)
            self.done.emit(True, "\n".join(r) if isinstance(r, list) else str(r))
        except Exception as e:  # noqa: BLE001 — frontière UI : l'erreur est affichée
            self.done.emit(False, str(e))


class ArduinoCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Centre Arduino — NexOS"); self.resize(1150, 700)
        self.cat = core.catalog(); self._th = None
        tabs = QTabWidget(); tabs.addTab(self._libs_tab(), "Bibliothèques (100)"); tabs.addTab(self._diag_tab(), "Diagnostic")
        self.setCentralWidget(tabs); self.fill()

    # ---------------------------------------------------------------- bibliothèques
    def _libs_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        row = QHBoxLayout()
        self.q = QLineEdit(); self.q.setPlaceholderText("Rechercher (nom, usage, auteur)…"); self.q.textChanged.connect(self.fill)
        self.catbox = QComboBox(); self.catbox.addItem("Toutes les catégories", "")
        for k in sorted({e["category"] for e in self.cat["libraries"]}):
            name = next(e["category_name"] for e in self.cat["libraries"] if e["category"] == k)
            self.catbox.addItem(f"{k[:2]}. {name}", k)
        self.catbox.currentIndexChanged.connect(self.fill)
        row.addWidget(self.q, 2); row.addWidget(self.catbox, 1); lay.addLayout(row)
        split = QSplitter(Qt.Orientation.Horizontal)
        self.t = QTableWidget(0, 6); self.t.setHorizontalHeaderLabels(["Bibliothèque", "Version", "Catégorie", "Licence", "Compilation", "État"])
        self.t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.t.itemSelectionChanged.connect(self.details)
        self.info = QTextBrowser(); self.info.setOpenExternalLinks(True)
        split.addWidget(self.t); split.addWidget(self.info); split.setSizes([700, 420]); lay.addWidget(split, 1)
        b = QHBoxLayout()
        for txt, fn in (("Installer", core.install), ("Mettre à jour", core.update), ("Supprimer", core.remove)):
            btn = QPushButton(txt); btn.clicked.connect(lambda _=False, f=fn, n=txt: self.act(f, n)); b.addWidget(btn)
        ide = QPushButton("Ouvrir l'Arduino IDE"); ide.clicked.connect(lambda: subprocess.Popen(["arduino"])); b.addStretch(); b.addWidget(ide)
        lay.addLayout(b)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(110); lay.addWidget(self.log)
        return w

    def fill(self):
        self.rows = core.search(self.q.text(), self.catbox.currentData() or "")
        self.t.setRowCount(0)
        for r, e in enumerate(self.rows):
            self.t.insertRow(r)
            for c, v in enumerate((e["name"], e["version"], e["category_name"], e["license"], TEST_LABEL.get(e.get("test", {}).get("status"), "?"), core.status(e))):
                self.t.setItem(r, c, QTableWidgetItem(v))

    def current(self):
        r = self.t.currentRow()
        return self.rows[r] if 0 <= r < len(self.rows) else None

    def details(self):
        e = self.current()
        if not e:
            return
        maint = e.get("maintenance", "?") + (f" — {e['note']}" if e.get("note") else "")
        self.info.setHtml(
            f"<h3>{e['name']} {e['version']}</h3><p>{e.get('description','')}</p><p>{e.get('paragraph','') if e.get('paragraph') != e.get('description') else ''}</p>"
            f"<p><b>Dépôt :</b> <a href='{e['repository']}'>{e['repository']}</a><br><b>Auteur :</b> {e.get('author','')}"
            f"<br><b>Licence :</b> {e['license']}<br><b>Architectures :</b> {e['architectures']}"
            f"<br><b>Dépendances :</b> {', '.join(e['depends']) or 'aucune'}<br><b>Dernière version :</b> {e.get('release_date','?')}"
            f"<br><b>Maintenance :</b> {maint} (dernier commit {e.get('last_commit','?')})"
            f"<br><b>Exemples :</b> {', '.join(x.split('/')[-1] for x in e['examples']) or 'aucun'}</p>"
            f"<p><b>Test NexOS :</b> {TEST_LABEL.get(e.get('test', {}).get('status'), 'non vérifié')} — "
            f"{e.get('test', {}).get('example', '')} {e.get('test', {}).get('detail', '')[:160]}<br>"
            f"<i>Compilation vérifiée, pas d'essai sur carte réelle.</i></p>"
            f"<p><b>Installation :</b> <code>{e['install']}</code></p>")

    def act(self, fn, label):
        e = self.current()
        if not e or self._th:
            return
        if fn is core.remove and QMessageBox.question(self, "Supprimer", f"Supprimer {e['name']} ?") != QMessageBox.StandardButton.Yes:
            return
        self.log.appendPlainText(f"▶ {label} : {e['name']}")
        self._th = QThread(self); self._job = Job(fn, e); self._job.moveToThread(self._th)
        self._th.started.connect(self._job.run); self._job.done.connect(self.finished); self._th.start()

    @Slot(bool, str)
    def finished(self, ok, text):
        self._th.quit(); self._th.wait(); self._th = None
        self.log.appendPlainText(("✔ " if ok else "✖ ") + text); self.fill()

    # ---------------------------------------------------------------- diagnostic
    def _diag_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        self.diag = QLabel(); self.diag.setWordWrap(True); self.diag.setTextFormat(Qt.TextFormat.RichText); lay.addWidget(self.diag)
        row = QHBoxLayout()
        b1 = QPushButton("Actualiser"); b1.clicked.connect(self.refresh_diag)
        b2 = QPushButton("Tester la compilation (Blink, Uno)"); b2.clicked.connect(self.test_compile)
        row.addWidget(b1); row.addWidget(b2); row.addStretch(); lay.addLayout(row); lay.addStretch()
        self.refresh_diag(); return w

    def refresh_diag(self):
        d = core.diagnose()
        yes = lambda v: "✔" if v else "✖"
        tips = "" if d["groupe_dialout"] else ("<p style='color:#e5484d'>Votre compte n'est pas dans le groupe <b>dialout</b> : "
                                               "le téléversement échouera. Le Control Center peut corriger (déconnexion requise).</p>")
        self.diag.setText(
            f"<h3>Chaîne Arduino</h3>Arduino IDE {yes(d['arduino_ide'])} · arduino-builder {yes(d['arduino_builder'])} · "
            f"avr-gcc {yes(d['avr_gcc'])} · avrdude {yes(d['avrdude'])} · esptool {yes(d['esptool'])}"
            f"<h3>Accès aux ports série</h3>Groupe dialout : {yes(d['groupe_dialout'])}{tips}"
            f"<h3>Cartes détectées (USB)</h3>{'<br>'.join(d['cartes']) or 'aucune carte reconnue'}"
            f"<h3>Ports série</h3>{', '.join(d['ports']) or 'aucun (branchez la carte, câble de données et non de charge seule)'}")

    def test_compile(self):
        ok, msg = core.compile_test()
        QMessageBox.information(self, "Compilation", ("Réussie : " if ok else "Échec : ") + msg)


def main() -> int:
    app = QApplication(sys.argv); app.setDesktopFileName("org.nexos.ArduinoCenter")
    w = ArduinoCenter(); w.show(); return app.exec()


if __name__ == "__main__":
    sys.exit(main())
