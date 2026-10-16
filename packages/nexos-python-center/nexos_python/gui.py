"""Centre Python NexOS — interface graphique (PySide6)."""
from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import core


class Job(QObject):
    line = Signal(str)
    finished = Signal(object)

    def __init__(self, fn, *args):
        super().__init__()
        self.fn, self.args = fn, args

    @Slot()
    def run(self):
        kwargs = {"on_line": self.line.emit} if "on_line" in inspect.signature(self.fn).parameters else {}
        try:
            res = self.fn(*self.args, **kwargs)
        except Exception as e:  # noqa: BLE001 — frontière UI
            res = core.OpResult(["?"], 1, str(e))
        self.finished.emit(res)


class Console(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("monospace", 9))
        self.setMaximumBlockCount(5000)


class CenterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Centre Python — NexOS")
        self.setWindowIcon(QIcon.fromTheme("nexos-python-center"))
        self.resize(1000, 680)
        self._thread: QThread | None = None
        tabs = QTabWidget()
        tabs.addTab(self._profiles_tab(), "Profils")
        tabs.addTab(self._projects_tab(), "Projets")
        tabs.addTab(self._catalog_tab(), "Catalogue")
        self.console = Console()
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(tabs); split.addWidget(self.console); split.setSizes([480, 200])
        self.status = QLabel()
        root = QWidget(); lay = QVBoxLayout(root); lay.addWidget(split); lay.addWidget(self.status)
        self.setCentralWidget(root)
        self.refresh_profiles(); self.refresh_projects()

    # --------------------------------------------------------- utilitaires
    def start(self, label: str, fn, *args, then=None):
        if self._thread is not None:
            QMessageBox.information(self, "Centre Python", "Une opération est déjà en cours.")
            return
        self.console.appendPlainText(f"▶ {label}")
        self.status.setText(f"En cours : {label}…")
        self._thread = QThread(self)
        self._job = Job(fn, *args)
        self._job.moveToThread(self._thread)
        self._thread.started.connect(self._job.run)
        self._job.line.connect(self.console.appendPlainText)
        self._job.finished.connect(self._done)
        self._then = then
        self._label = label
        self._thread.start()

    @Slot(object)
    def _done(self, res: core.OpResult):
        self._thread.quit(); self._thread.wait(); self._thread = None
        if res.ok:
            self.console.appendPlainText(f"✔ {self._label} : terminé")
            self.status.setText(f"Terminé : {self._label}")
        else:
            self.console.appendPlainText(f"✖ {self._label} : échec (code {res.returncode})")
            if res.output and res.output not in self.console.toPlainText()[-len(res.output):]:
                self.console.appendPlainText(res.output[-3000:])
            self.status.setText(f"Échec : {self._label} — détails dans le journal")
            QMessageBox.warning(self, "Centre Python", f"Échec : {self._label}\n\n{res.output[-800:]}")
        if self._then:
            self._then(res)

    # --------------------------------------------------------- profils
    def _profiles_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.addWidget(QLabel("Ensembles de bibliothèques testés ensemble, aux versions verrouillées. "
                             "Chaque profil s'installe dans son propre environnement."))
        self.profile_list = QListWidget()
        lay.addWidget(self.profile_list, 1)
        row = QHBoxLayout()
        for text, slot in (("Installer", self.install_profile), ("Tester", self.test_profile),
                           ("Noyau Jupyter", self.kernel_profile), ("Supprimer", self.remove_profile)):
            b = QPushButton(text); b.clicked.connect(slot); row.addWidget(b)
        row.addStretch(); lay.addLayout(row)
        return w

    def refresh_profiles(self):
        self.profile_list.clear()
        for p in core.list_profiles():
            state = f"✔ installé · {p.size_mb():.0f} Mio" if p.installed else "non installé"
            it = QListWidgetItem(f"{p.name}  —  {p.description}\n      {p.locked_packages} paquets verrouillés · {state}")
            it.setData(Qt.ItemDataRole.UserRole, p.name)
            self.profile_list.addItem(it)

    def _selected_profile(self) -> str | None:
        it = self.profile_list.currentItem()
        if not it:
            QMessageBox.information(self, "Centre Python", "Sélectionnez un profil.")
            return None
        return it.data(Qt.ItemDataRole.UserRole)

    def install_profile(self):
        if n := self._selected_profile():
            self.start(f"Installation du profil {n}", core.install_profile, n, then=lambda r: self.refresh_profiles())

    def test_profile(self):
        if n := self._selected_profile():
            self.start(f"Tests du profil {n}", core.test_profile, n)

    def kernel_profile(self):
        if n := self._selected_profile():
            self.start(f"Noyau Jupyter {n}", core.register_kernel, n)

    def remove_profile(self):
        if (n := self._selected_profile()) and QMessageBox.question(
                self, "Supprimer", f"Supprimer l'environnement du profil {n} ?") == QMessageBox.StandardButton.Yes:
            self.start(f"Suppression du profil {n}", core.remove_profile, n, then=lambda r: self.refresh_profiles())

    # --------------------------------------------------------- projets
    def _projects_tab(self) -> QWidget:
        w = QWidget(); lay = QHBoxLayout(w)
        left = QVBoxLayout()
        self.project_list = QListWidget(); self.project_list.currentItemChanged.connect(self.show_project)
        left.addWidget(QLabel(f"Projets dans {core.projects_root()}")); left.addWidget(self.project_list, 1)
        b_new = QPushButton("Nouveau projet…"); b_new.clicked.connect(self.new_project)
        b_open = QPushButton("Ouvrir le dossier"); b_open.clicked.connect(self.open_project)
        left.addWidget(b_new); left.addWidget(b_open)
        right = QVBoxLayout()
        self.pkg_table = QTableWidget(0, 2); self.pkg_table.setHorizontalHeaderLabels(["Paquet", "Version"])
        self.pkg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right.addWidget(self.pkg_table, 1)
        row = QHBoxLayout()
        self.pkg_input = QLineEdit(); self.pkg_input.setPlaceholderText("ex. requests ou numpy==2.1")
        for text, slot in (("Ajouter", self.add_pkg), ("Supprimer", self.rm_pkg),
                           ("Mettre à jour", self.upgrade_pkg), ("Dépendances", self.tree)):
            b = QPushButton(text); b.clicked.connect(slot); row.addWidget(b)
        right.addWidget(self.pkg_input); right.addLayout(row)
        lay.addLayout(left, 1); lay.addLayout(right, 2)
        return w

    def refresh_projects(self):
        self.project_list.clear()
        for p in core.list_projects():
            it = QListWidgetItem(p.name); it.setData(Qt.ItemDataRole.UserRole, str(p))
            self.project_list.addItem(it)

    def _project(self) -> Path | None:
        it = self.project_list.currentItem()
        return Path(it.data(Qt.ItemDataRole.UserRole)) if it else None

    def show_project(self, *_):
        self.pkg_table.setRowCount(0)
        if p := self._project():
            for i, pkg in enumerate(core.project_packages(p)):
                self.pkg_table.insertRow(i)
                self.pkg_table.setItem(i, 0, QTableWidgetItem(pkg["name"]))
                self.pkg_table.setItem(i, 1, QTableWidgetItem(pkg["version"]))

    def new_project(self):
        d = QDialog(self); d.setWindowTitle("Nouveau projet")
        form = QFormLayout(d); name = QLineEdit(); prof = QComboBox()
        prof.addItem("(aucun)", None)
        for p in core.list_profiles():
            prof.addItem(p.name, p.name)
        form.addRow("Nom", name); form.addRow("Partir du profil", prof)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept); bb.rejected.connect(d.reject); form.addRow(bb)
        if d.exec() and name.text().strip():
            self.start(f"Création du projet {name.text()}", core.create_project, name.text().strip(),
                       prof.currentData(), then=lambda r: self.refresh_projects())

    def open_project(self):
        if p := self._project():
            subprocess.Popen(["xdg-open", str(p)])

    def _need_project(self) -> Path | None:
        p = self._project()
        if not p:
            QMessageBox.information(self, "Centre Python", "Sélectionnez un projet.")
        return p

    def add_pkg(self):
        if (p := self._need_project()) and self.pkg_input.text().strip():
            self.start(f"Ajout de {self.pkg_input.text()}", core.add_packages, p,
                       self.pkg_input.text().split(), then=lambda r: self.show_project())

    def rm_pkg(self):
        p = self._need_project(); row = self.pkg_table.currentRow()
        if p and row >= 0:
            name = self.pkg_table.item(row, 0).text()
            self.start(f"Suppression de {name}", core.remove_packages, p, [name], then=lambda r: self.show_project())

    def upgrade_pkg(self):
        if p := self._need_project():
            row = self.pkg_table.currentRow()
            names = [self.pkg_table.item(row, 0).text()] if row >= 0 else None
            label = f"Mise à jour de {names[0]}" if names else "Mise à jour de tous les paquets"
            self.start(label, core.upgrade_packages, p, names, then=lambda r: self.show_project())

    def tree(self):
        if p := self._need_project():
            self.start("Arbre des dépendances", core.dependency_tree, p,
                       then=lambda r: self.console.appendPlainText(r.output))

    # --------------------------------------------------------- catalogue
    def _catalog_tab(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        self.search = QLineEdit(); self.search.setPlaceholderText("Rechercher (nom, usage, catégorie)…")
        self.search.textChanged.connect(self.fill_catalog)
        self.cat_table = QTableWidget(0, 3)
        self.cat_table.setHorizontalHeaderLabels(["Bibliothèque", "Catégorie", "Usage"])
        self.cat_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        row = QHBoxLayout()
        b_info = QPushButton("Fiche PyPI"); b_info.clicked.connect(self.pypi)
        b_add = QPushButton("Ajouter au projet sélectionné"); b_add.clicked.connect(self.add_from_catalog)
        row.addWidget(b_info); row.addWidget(b_add); row.addStretch()
        lay.addWidget(self.search); lay.addWidget(self.cat_table, 1); lay.addLayout(row)
        self.fill_catalog("")
        return w

    def fill_catalog(self, q: str):
        self.cat_table.setRowCount(0)
        for i, e in enumerate(core.search_catalog(q)):
            self.cat_table.insertRow(i)
            for j, v in enumerate((e.name, e.category, e.summary)):
                self.cat_table.setItem(i, j, QTableWidgetItem(v))
        if q and not self.cat_table.rowCount():
            self.cat_table.insertRow(0)
            self.cat_table.setItem(0, 0, QTableWidgetItem(q))
            self.cat_table.setItem(0, 2, QTableWidgetItem("Hors catalogue : « Fiche PyPI » pour vérifier"))

    def _cat_name(self) -> str | None:
        r = self.cat_table.currentRow()
        return self.cat_table.item(r, 0).text() if r >= 0 else None

    def pypi(self):
        if n := self._cat_name():
            info = core.pypi_info(n)
            QMessageBox.information(self, n, "\n".join(f"{k} : {v}" for k, v in info.items())
                                    if info else "Introuvable sur PyPI ou pas de connexion.")

    def add_from_catalog(self):
        p, n = self._need_project(), self._cat_name()
        if p and n:
            self.start(f"Ajout de {n}", core.add_packages, p, [n], then=lambda r: self.show_project())


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Centre Python")
    app.setDesktopFileName("org.nexos.PythonCenter")
    w = CenterWindow(); w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
