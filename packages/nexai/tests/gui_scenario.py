"""Scénario GUI piloté (hors écran) : mesure la RAM de la fenêtre seule, puis
question → réponse → bouton « Libérer la mémoire ». Imprime des mesures réelles."""
import json
import os
import sys
import time

from PySide6.QtWidgets import QApplication

from nexai import sysinfo
from nexai.config import Config
from nexai.gui import AssistantWindow
from nexai.manager import AssistantManager

app = QApplication(sys.argv)
mgr = AssistantManager(Config.load())
w = AssistantWindow(mgr); w.show()
t_end = time.monotonic() + 2
while time.monotonic() < t_end: app.processEvents(); time.sleep(0.02)
me = os.getpid()
res = {"gui_rss_mb_model_not_loaded": round(sysinfo.rss_mb(me), 1),
       "gui_anon_mb_model_not_loaded": round(sysinfo.smaps_mb(me, "Pss_Anon"), 1),
       "engine_running_after_open": mgr.status().engine_running}
w.input.setPlainText("Quelle commande affiche l'espace disque ?"); w.send()
t_end = time.monotonic() + 120
while w._thread is not None and time.monotonic() < t_end: app.processEvents(); time.sleep(0.02)
res["answer_chars"] = len(w._answer)
res["engine_running_after_answer"] = mgr.status().engine_running
res["engine_rss_mb_after_answer"] = mgr.status().engine_rss_mb
w.free_btn.click(); app.processEvents()
res["engine_running_after_free_button"] = mgr.status().engine_running
res["status_label"] = w.status.text()
w.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
