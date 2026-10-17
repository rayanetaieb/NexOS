"""NexOS Control Center — panneau centralisé (PySide6). Toutes les valeurs affichées
sont lues sur le système au moment de l'affichage (module probe)."""
from __future__ import annotations

import os
import subprocess
import sys

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import probe

ADMIN = "/usr/lib/nexos/nexos-admin"


def human(mb: float) -> str:
    return f"{mb / 1024:.1f} Go" if mb >= 1024 else f"{mb:.0f} Mio"


class Runner(QObject):
    done = Signal(int, str)

    def __init__(self, cmd):
        super().__init__(); self.cmd = cmd

    @Slot()
    def run(self):
        try:
            r = subprocess.run(self.cmd, capture_output=True, text=True, check=False)
            self.done.emit(r.returncode, (r.stdout + r.stderr)[-4000:])
        except FileNotFoundError as e:
            self.done.emit(127, str(e))


class Page(QWidget):
    title = ""
    def __init__(self, cc):
        super().__init__(); self.cc = cc
        self.lay = QVBoxLayout(self)
        h = QLabel(self.title); f = h.font(); f.setPointSize(f.pointSize() + 6); f.setBold(True); h.setFont(f)
        self.lay.addWidget(h)
    def refresh(self): ...


def table(headers):
    t = QTableWidget(0, len(headers)); t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setStretchLastSection(True); t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    return t


def fill(t, rows):
    t.setRowCount(0)
    for r, row in enumerate(rows):
        t.insertRow(r)
        for c, v in enumerate(row):
            t.setItem(r, c, QTableWidgetItem(str(v)))
    t.resizeColumnsToContents()


class Overview(Page):
    title = "Vue d'ensemble"
    def __init__(self, cc):
        super().__init__(cc)
        self.info = QLabel(); self.info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.cpu, self.ram, self.disk = QProgressBar(), QProgressBar(), QProgressBar()
        for lbl, bar in (("Processeur", self.cpu), ("Mémoire", self.ram), ("Disque /", self.disk)):
            self.lay.addWidget(QLabel(lbl)); self.lay.addWidget(bar)
        self.lay.addWidget(self.info)
        self.procs = table(["PID", "Processus", "Mémoire"]); self.lay.addWidget(QLabel("Processus les plus gourmands"))
        self.lay.addWidget(self.procs, 1)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh)
    def showEvent(self, e):
        self.timer.start(2000); self.refresh(); super().showEvent(e)
    def hideEvent(self, e):
        self.timer.stop(); super().hideEvent(e)   # aucune mesure quand la page n'est pas visible
    def refresh(self):
        m = probe.meminfo(); d = probe.disk_usage("/")
        used = m["MemTotal"] - m["MemAvailable"]
        self.cpu.setValue(int(probe.cpu_percent(0.2)))
        self.ram.setValue(int(100 * used / m["MemTotal"])); self.ram.setFormat(f"{human(used)} / {human(m['MemTotal'])}")
        self.disk.setValue(int(d["used_pct"])); self.disk.setFormat(f"{human(d['total_mb'] - d['free_mb'])} / {human(d['total_mb'])}")
        osr = probe.os_release(); up = probe.uptime_s()
        self.info.setText(f"{osr.get('PRETTY_NAME', '?')} · noyau {os.uname().release} · "
                          f"allumé depuis {up // 3600} h {up % 3600 // 60} min · racine : {probe.root_fs()}")
        fill(self.procs, [(p.pid, p.name, human(p.rss_mb)) for p in probe.top_processes(10)])


class Startup(Page):
    title = "Démarrage et services"
    def __init__(self, cc):
        super().__init__(cc)
        self.lay.addWidget(QLabel("Programmes lancés à l'ouverture de session (désactivables sans droits admin) :"))
        self.auto = table(["Fichier", "Nom", "Actif"]); self.lay.addWidget(self.auto, 1)
        b = QPushButton("Activer / désactiver le programme sélectionné"); b.clicked.connect(self.toggle_auto)
        self.lay.addWidget(b)
        self.lay.addWidget(QLabel("Services système activés au démarrage :"))
        self.svc = table(["Unité"]); self.lay.addWidget(self.svc, 1)
        row = QHBoxLayout()
        for txt, act in (("Désactiver…", "service-disable"), ("Activer…", "service-enable")):
            bb = QPushButton(txt); bb.clicked.connect(lambda _=False, a=act: self.svc_action(a)); row.addWidget(bb)
        row.addStretch(); self.lay.addLayout(row)
    def refresh(self):
        fill(self.auto, [(f, n, "oui" if a else "non") for f, n, a in probe.autostart_entries()])
        fill(self.svc, [(u,) for u in probe.enabled_services()])
    def toggle_auto(self):
        r = self.auto.currentRow()
        if r < 0: return
        f, active = self.auto.item(r, 0).text(), self.auto.item(r, 2).text() == "oui"
        probe.set_user_autostart(f, not active); self.refresh()
    def svc_action(self, act):
        r = self.svc.currentRow()
        if r < 0: return
        unit = self.svc.item(r, 0).text()
        if QMessageBox.question(self, "Confirmation", f"{act.split('-')[1]} {unit} ? (droits administrateur requis)") \
                == QMessageBox.StandardButton.Yes:
            self.cc.admin([act, unit], self.refresh)


class Devices(Page):
    title = "Périphériques et matériel"
    def __init__(self, cc):
        super().__init__(cc); self.text = QPlainTextEdit(); self.text.setReadOnly(True)
        self.text.setFont(QFont("monospace", 9)); self.lay.addWidget(self.text, 1)
    def refresh(self):
        disks = "\n".join(f"  {d['name']:8} {d.get('size') or '':>7} {d.get('type') or '':5} {d.get('fstype') or '':6} "
                          f"{d.get('mountpoint') or '':12} {d.get('model') or ''}" for d in probe.block_devices())
        self.text.setPlainText(
            "Processeur graphique :\n  " + ("\n  ".join(probe.gpus()) or "non détecté (lspci absent ?)") +
            "\n\nStockage :\n" + disks +
            "\n\nUSB :\n  " + ("\n  ".join(probe.usb_devices()) or "aucun / lsusb absent") +
            "\n\nPorts série (Arduino, ESP32…) :\n  " + (", ".join(probe.serial_ports()) or "aucun") +
            "\n\nBluetooth :\n  " + probe.bluetooth())


class Network(Page):
    title = "Réseau et pare-feu"
    def __init__(self, cc):
        super().__init__(cc); self.t = table(["Interface", "Type", "État", "Connexion"]); self.lay.addWidget(self.t, 1)
        self.fw = QLabel(); self.lay.addWidget(self.fw)
        row = QHBoxLayout()
        for txt, act in (("Activer le pare-feu", "firewall-on"), ("Désactiver le pare-feu", "firewall-off")):
            b = QPushButton(txt); b.clicked.connect(lambda _=False, a=act: self.cc.admin([a], self.refresh)); row.addWidget(b)
        o = QPushButton("Paramètres réseau…"); o.clicked.connect(lambda: subprocess.Popen(["systemsettings", "kcm_networkmanagement"]))
        row.addWidget(o); row.addStretch(); self.lay.addLayout(row)
    def refresh(self):
        fill(self.t, [ln.split(":") for ln in probe.network()])
        self.fw.setText(f"Pare-feu (firewalld) : {probe.firewall_state()}")


class Updates(Page):
    title = "Mises à jour"
    def __init__(self, cc):
        super().__init__(cc)
        self.lay.addWidget(QLabel("Les mises à jour sont signées (APT vérifie les signatures). Sur Btrfs, un "
                                  "instantané est créé automatiquement avant et après chaque mise à jour."))
        self.out = QPlainTextEdit(); self.out.setReadOnly(True); self.lay.addWidget(self.out, 1)
        row = QHBoxLayout()
        for txt, act in (("Rechercher", "apt-update"), ("Installer les mises à jour", "apt-upgrade")):
            b = QPushButton(txt); b.clicked.connect(lambda _=False, a=act: self.go(a)); row.addWidget(b)
        row.addStretch(); self.lay.addLayout(row)
    def go(self, act):
        if act == "apt-upgrade" and QMessageBox.question(self, "Confirmation", "Installer toutes les mises à jour ?") \
                != QMessageBox.StandardButton.Yes:
            return
        self.cc.admin([act], self.refresh)
    def refresh(self):
        out = probe.sh(["apt", "list", "--upgradable"], timeout=30)
        lines = [ln for ln in out.splitlines() if "/" in ln]
        self.out.setPlainText(f"{len(lines)} mise(s) à jour disponible(s) (dernière recherche)\n\n" + "\n".join(lines))


class Backups(Page):
    title = "Sauvegardes et récupération"
    def __init__(self, cc):
        super().__init__(cc)
        self.lay.addWidget(QLabel("Instantanés Btrfs (snapper) : retour à un état antérieur du système."))
        self.out = QPlainTextEdit(); self.out.setReadOnly(True); self.out.setFont(QFont("monospace", 9))
        self.lay.addWidget(self.out, 1)
        row = QHBoxLayout()
        b1 = QPushButton("Lister les instantanés"); b1.clicked.connect(lambda: self.cc.admin(["snapshot-list"], None, self.out))
        b2 = QPushButton("Créer un instantané…"); b2.clicked.connect(self.create)
        b4 = QPushButton("Revenir à un instantané…"); b4.clicked.connect(self.undo)
        b3 = QPushButton("Btrfs Assistant (restauration)…"); b3.clicked.connect(lambda: subprocess.Popen(["btrfs-assistant-launcher"]))
        for b in (b1, b2, b4, b3): row.addWidget(b)
        row.addStretch(); self.lay.addLayout(row)
        self.lay.addWidget(QLabel("Récupération : au démarrage, menu GRUB → « Options avancées » ; en cas de panne "
                                  "grave, démarrer la clé NexOS → « console de diagnostic ». Voir docs/RECOVERY.md."))
    def refresh(self):
        self.out.setPlainText(f"Système de fichiers racine : {probe.root_fs()}")
    def undo(self):
        n, ok = QInputDialog.getInt(self, "Revenir à un instantané", "Numéro de l'instantané (voir la liste) :", 1, 1, 999999)
        if not ok:
            return
        msg = (f"Les fichiers système modifiés depuis l'instantané {n} vont être remis dans leur état d'alors "
               "(paquets installés ou mis à jour, configuration dans /etc…).\n\nVos documents (/home) ne sont pas touchés. "
               "Un instantané de l'état actuel est créé d'abord, pour pouvoir annuler.\n\nRedémarrez ensuite. Continuer ?")
        if QMessageBox.question(self, "Confirmer le retour arrière", msg) == QMessageBox.StandardButton.Yes:
            self.cc.admin(["snapshot-undo", str(n)], None, self.out)
    def create(self):
        desc, ok = QInputDialog.getText(self, "Instantané", "Description :", text="Avant modification")
        if ok:
            self.cc.admin(["snapshot-create", desc], None, self.out)


class Security(Page):
    title = "Sécurité"
    def __init__(self, cc):
        super().__init__(cc); self.text = QLabel(); self.text.setWordWrap(True); self.lay.addWidget(self.text); self.lay.addStretch()
    def refresh(self):
        self.text.setText(
            f"Pare-feu : {probe.firewall_state()}\n"
            f"AppArmor : {'actif' if probe.apparmor_enabled() else 'inactif'}\n"
            f"Démarrage sécurisé : {probe.secure_boot()}\n"
            f"Système de fichiers racine : {probe.root_fs()}\n"
            "Mises à jour : signées et vérifiées par APT ; voir la page « Mises à jour ».")


class Components(Page):
    title = "Composants facultatifs"
    def __init__(self, cc):
        super().__init__(cc)
        self.lay.addWidget(QLabel("Installés uniquement à votre demande : rien n'est téléchargé ni lancé automatiquement."))
        self.t = table(["Composant", "État", "Taille indicative"]); self.lay.addWidget(self.t, 1)
        b = QPushButton("Installer le composant sélectionné…"); b.clicked.connect(self.install); self.lay.addWidget(b)
    def items(self):
        try:
            from nexos_setup import android, miktex
            a_ok, m_ok = android.installed(), miktex.installed()
        except ImportError:
            a_ok = m_ok = False
        return [
            ("android-studio", "Android Studio (licence Google, téléchargement vérifié)", a_ok, "≈ 1,3 Go + SDK"),
            ("miktex", "MiKTeX (dépôt officiel MiKTeX)", m_ok, "≈ 300 Mo + paquets à la demande"),
            ("kicad-3d", "Modèles 3D KiCad", os.path.isdir("/usr/share/kicad/3dmodels"), "≈ 6 Go"),
            ("texlive-full-extra", "Polices et classes TeX supplémentaires", False, "≈ 1 Go"),
            ("flathub", "Dépôt d'applications Flathub", "flathub" in probe.sh(["flatpak", "remotes"]), "—"),
        ]
    def refresh(self):
        fill(self.t, [(name, "installé" if ok else "non installé", size) for _, name, ok, size in self.items()])
    def install(self):
        r = self.t.currentRow()
        if r < 0: return
        key = self.items()[r][0]
        if key == "android-studio":
            subprocess.Popen(["nexos-setup", "android"])
        elif key == "miktex":
            subprocess.Popen(["nexos-setup", "miktex"])
        elif key == "flathub":
            self.cc.admin(["flathub-enable"], self.refresh)
        else:
            self.cc.admin(["install-optional", key], self.refresh)


class AI(Page):
    title = "Assistant IA et Python"
    def __init__(self, cc):
        super().__init__(cc); self.text = QLabel(); self.text.setWordWrap(True); self.lay.addWidget(self.text)
        row = QHBoxLayout()
        b1 = QPushButton("Arrêter le moteur IA (libérer la mémoire)"); b1.clicked.connect(self.stop_ai)
        b2 = QPushButton("Ouvrir le Centre Python"); b2.clicked.connect(lambda: subprocess.Popen(["nexos-python", "gui"]))
        row.addWidget(b1); row.addWidget(b2); row.addStretch(); self.lay.addLayout(row); self.lay.addStretch()
    def refresh(self):
        eng = probe.nexai_engines()
        ai = (f"Moteur IA actif : {len(eng)} processus, {human(sum(p.rss_mb for p in eng))}" if eng
              else "Moteur IA arrêté : aucune mémoire utilisée")
        prof = probe.python_profiles_installed()
        self.text.setText(f"{ai}\nProfils Python installés : {', '.join(prof) or 'aucun'}")
    def stop_ai(self):
        for p in probe.nexai_engines():
            try:
                os.kill(p.pid, 15)
            except PermissionError:
                pass
        QTimer.singleShot(800, self.refresh)


class ControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NexOS Control Center"); self.setWindowIcon(QIcon.fromTheme("nexos-control-center"))
        self.resize(1100, 720)
        self.nav = QListWidget(); self.nav.setFixedWidth(230); self.stack = QStackedWidget()
        self.pages = [Overview(self), Startup(self), Devices(self), Network(self), Updates(self),
                      Backups(self), Security(self), Components(self), AI(self)]
        for p in self.pages:
            self.nav.addItem(QListWidgetItem(p.title)); self.stack.addWidget(p)
        self.nav.currentRowChanged.connect(self.show_page)
        root = QWidget(); lay = QHBoxLayout(root); lay.addWidget(self.nav); lay.addWidget(self.stack, 1)
        self.setCentralWidget(root); self.nav.setCurrentRow(0)
        self._threads = []

    def show_page(self, i):
        self.stack.setCurrentIndex(i); self.pages[i].refresh()

    def admin(self, args, then=None, output: QPlainTextEdit | None = None):
        """Action administrateur : pkexec (authentification polkit) + nexos-admin (liste fermée)."""
        th = QThread(self); job = Runner(["pkexec", ADMIN, *args]); job.moveToThread(th)
        th.started.connect(job.run)
        def finished(code, text):
            th.quit(); th.wait()
            if output is not None:
                output.setPlainText(text)
            elif code != 0:
                QMessageBox.warning(self, "Échec", f"Action « {' '.join(args)} » : code {code}\n{text[-1500:]}")
            if then:
                then()
        job.done.connect(finished); th.start(); self._threads.append((th, job))


def main() -> int:
    app = QApplication(sys.argv); app.setApplicationName("NexOS Control Center")
    app.setDesktopFileName("org.nexos.ControlCenter")
    w = ControlCenter(); w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
