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
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

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

        self.send_btn.clicked.connect(self.send)
        self.free_btn.clicked.connect(self.free)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.send)
        QShortcut(QKeySequence("Escape"), self, self.close)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(2000)
        self.refresh()
        if not mgr.config.enabled:
            self.view.setPlainText("L'assistant est désactivé (nexai enable pour le réactiver).")
            self.send_btn.setEnabled(False)

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
    w = AssistantWindow(AssistantManager(Config.load()))
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
