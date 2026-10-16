"""Fenêtre minimaliste de l'assistant (PySide6).

Le moteur n'est PAS démarré à l'ouverture de la fenêtre : seulement à la
première question. Fermer la fenêtre arrête le moteur.
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import models, sysinfo
from .config import Config
from .engine import GenerationStats
from .manager import AssistantManager
from .prompts import flag_risky_commands


class Worker(QObject):
    piece = Signal(str)
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, mgr: AssistantManager, question: str, history: list[dict]):
        super().__init__()
        self.mgr, self.question, self.history = mgr, question, history

    @Slot()
    def run(self):
        stats = GenerationStats()
        try:
            for p in self.mgr.ask(self.question, self.history, stats):
                self.piece.emit(p)
            self.done.emit(stats)
        except Exception as e:  # noqa: BLE001 — frontière UI
            self.failed.emit(str(e))


class Downloader(QObject):
    progress = Signal(int, int)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, info):
        super().__init__()
        self.info = info

    @Slot()
    def run(self):
        try:
            path = models.download(self.info, lambda d, t: self.progress.emit(d // 2**20, max(t, 1) // 2**20))
            self.done.emit(str(path))
        except Exception as e:  # noqa: BLE001 — frontière UI
            self.failed.emit(str(e))


class AssistantWindow(QMainWindow):
    def __init__(self, mgr: AssistantManager):
        super().__init__()
        self.mgr = mgr
        self.history: list[dict] = []
        self._answer = ""
        self._thread: QThread | None = None
        self.setWindowTitle("NexOS — Assistant")
        self.resize(560, 640)

        self.view = QTextBrowser(); self.view.setOpenExternalLinks(False)
        self.input = QPlainTextEdit(); self.input.setPlaceholderText("Posez votre question… (Ctrl+Entrée)")
        self.input.setMaximumHeight(90)
        self.send_btn = QPushButton("Envoyer")
        self.free_btn = QPushButton("Libérer la mémoire")
        self.free_btn.setToolTip("Arrête immédiatement le moteur IA et rend sa mémoire au système")
        self.status = QLabel(); self.status.setFont(QFont("monospace", 9))

        buttons = QHBoxLayout(); buttons.addWidget(self.free_btn); buttons.addStretch(); buttons.addWidget(self.send_btn)
        lay = QVBoxLayout(); lay.addWidget(self.view, 1); lay.addWidget(self.input); lay.addLayout(buttons); lay.addWidget(self.status)
        root = QWidget(); root.setLayout(lay); self.setCentralWidget(root)

        # Gestion du modèle : rien n'est téléchargé sans clic explicite.
        self.setup_box = QWidget(); sl = QVBoxLayout(self.setup_box)
        rec = models.recommended_model(sysinfo.mem_total_mb())
        self._rec = rec
        self.setup_label = QLabel(
            f"Aucun modèle IA installé.\n\nModèle recommandé pour cette machine : {rec.name} "
            f"({models.SIZES_MB.get(rec.key, '?')} Mio, licence {rec.license}).\n"
            "Le fichier est téléchargé une seule fois depuis Hugging Face puis vérifié (SHA-256).\n"
            "Ensuite, l'assistant fonctionne entièrement hors ligne.")
        self.setup_label.setWordWrap(True)
        self.dl_btn = QPushButton(f"Télécharger {rec.name}")
        self.pick_btn = QPushButton("Utiliser un fichier .gguf déjà téléchargé…")
        self.progress = QProgressBar(); self.progress.hide()
        for wdg in (self.setup_label, self.dl_btn, self.pick_btn, self.progress):
            sl.addWidget(wdg)
        lay.insertWidget(0, self.setup_box)
        self.dl_btn.clicked.connect(self.download_model)
        self.pick_btn.clicked.connect(self.pick_model)
        self._update_setup()

        self.send_btn.clicked.connect(self.send)
        self.free_btn.clicked.connect(self.free)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.send)
        QShortcut(QKeySequence("Escape"), self, self.close)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(2000)
        self.refresh()
        if not mgr.config.enabled:
            self.view.setPlainText("L'assistant est désactivé (nexai enable pour le réactiver).")
            self.send_btn.setEnabled(False)

    def _has_model(self) -> bool:
        import os
        return bool(self.mgr.config.model_path) and os.path.isfile(self.mgr.config.model_path)

    def _update_setup(self):
        ok = self._has_model()
        self.setup_box.setVisible(not ok)
        self.view.setVisible(ok); self.input.setVisible(ok)
        self.send_btn.setEnabled(ok and self.mgr.config.enabled)

    def _use_model(self, path: str):
        self.mgr.config.model_path = path
        self.mgr.config.save()
        self._update_setup()
        self.view.append("<p style='color:gray'>Modèle installé. Posez votre question.</p>")

    def download_model(self):
        self.dl_btn.setEnabled(False); self.pick_btn.setEnabled(False); self.progress.show()
        self._dl_thread = QThread(self)
        self._dl = Downloader(self._rec)
        self._dl.moveToThread(self._dl_thread)
        self._dl_thread.started.connect(self._dl.run)
        self._dl.progress.connect(self.on_progress)
        self._dl.done.connect(self.on_downloaded)
        self._dl.failed.connect(self.on_download_failed)
        self._dl_thread.start()

    @Slot(int, int)
    def on_progress(self, done: int, total: int):
        self.progress.setMaximum(total); self.progress.setValue(done)
        self.progress.setFormat(f"{done} / {total} Mio")

    def _end_download(self):
        self._dl_thread.quit(); self._dl_thread.wait()
        self.dl_btn.setEnabled(True); self.pick_btn.setEnabled(True); self.progress.hide()

    @Slot(str)
    def on_downloaded(self, path: str):
        self._end_download(); self._use_model(path)

    @Slot(str)
    def on_download_failed(self, msg: str):
        self._end_download()
        QMessageBox.warning(self, "Assistant", f"Échec du téléchargement :\n{msg}")

    def pick_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un modèle", "", "Modèles GGUF (*.gguf)")
        if path:
            try:
                dest, digest = models.import_local(path)
            except Exception as e:  # noqa: BLE001 — frontière UI
                QMessageBox.warning(self, "Assistant", str(e)); return
            self._use_model(str(dest))
            self.view.append(f"<p style='color:gray'>SHA-256 : {digest}</p>")

    def refresh(self):
        s = self.mgr.status()
        if s.engine_running:
            txt = f"Moteur actif · {s.engine_rss_mb:.0f} Mio · déchargement dans {s.unload_in_s:.0f} s"
        else:
            txt = "Moteur arrêté (aucune mémoire IA utilisée)"
        txt += f" · RAM dispo {s.mem_available_mb} Mio"
        if s.mem_available_mb < s.required_free_mb and not s.engine_running:
            txt += f" · ⚠ {s.required_free_mb} Mio requis"
        self.status.setText(txt)

    def send(self):
        q = self.input.toPlainText().strip()
        if not q or self._thread is not None:
            return
        self.input.clear()
        self.view.append(f"<p><b>Vous :</b> {q.replace('<', '&lt;')}</p><p><b>Assistant :</b></p>")
        self._answer = ""
        self._pending_q = q
        self.send_btn.setEnabled(False)
        self._thread = QThread(self)
        self._worker = Worker(self.mgr, q, list(self.history))
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.piece.connect(self.on_piece)
        # Slots liés à la fenêtre (thread principal) → connexion en file d'attente.
        # Un lambda s'exécuterait dans le thread du worker.
        self._worker.done.connect(self.on_done)
        self._worker.failed.connect(self.on_failed)
        self._thread.start()

    @Slot(str)
    def on_piece(self, p: str):
        self._answer += p
        self.view.moveCursor(self.view.textCursor().MoveOperation.End)
        self.view.insertPlainText(p)

    @Slot(object)
    def on_done(self, st: GenerationStats):
        q = self._pending_q
        self.history += [{"role": "user", "content": q}, {"role": "assistant", "content": self._answer}]
        for line in flag_risky_commands(self._answer):
            self.view.append(f"<p style='color:#c60'>⚠ Commande sensible : vérifiez avant de l'exécuter : <code>{line}</code></p>")
        if st.first_token_s is not None:
            self.view.append(f"<p style='color:gray;font-size:small'>1er mot {st.first_token_s:.1f} s · "
                             f"{st.tokens_per_s or 0:.1f} tokens/s</p>")
        self._finish()

    @Slot(str)
    def on_failed(self, msg: str):
        self.view.append(f"<p style='color:#c00'>Erreur : {msg}</p>")
        self._finish()

    def _finish(self):
        self._thread.quit(); self._thread.wait()
        self._thread = None
        self._worker = None
        self.send_btn.setEnabled(self.mgr.config.enabled)
        self.refresh()

    def free(self):
        if self._thread is not None:
            QMessageBox.information(self, "Assistant", "Une réponse est en cours ; réessayez après.")
            return
        self.mgr.unload()
        self.refresh()

    def closeEvent(self, ev):
        self.mgr.shutdown()
        super().closeEvent(ev)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("nexai")
    app.setDesktopFileName("org.nexos.Assistant")   # rattache la fenêtre à son icône (Wayland)
    w = AssistantWindow(AssistantManager(Config.load()))
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
