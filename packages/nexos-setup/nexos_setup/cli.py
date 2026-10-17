"""nexos-setup android|miktex|status : assistants d'installation (interface Qt, repli texte)."""
from __future__ import annotations

import subprocess
import shutil
import sys
from pathlib import Path

from . import android, miktex


def status() -> int:
    k = android.kvm_status()
    print(f"Android Studio : {'installé' if android.installed() else 'non installé'} ({android.base_dir()})")
    print(f"  {android.adb_version()}")
    print(f"  KVM (émulateur) : virtualisation CPU={k['cpu_virtualisation']} /dev/kvm={k['dev_kvm']} "
          f"accès={k['dev_kvm_rw']} groupe kvm={k['groupe_kvm']}")
    print(f"  mémoire IDE prévue : {android.ide_heap_mb(android.mem_total_mb())} Mio")
    print(f"MiKTeX : {'installé' if miktex.installed() else 'non installé'}")
    return 0


def android_gui() -> int:
    from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog
    app = QApplication.instance() or QApplication(sys.argv)
    if android.installed():
        subprocess.Popen([str(android.base_dir() / "bin/studio.sh")]); return 0
    k = android.kvm_status()
    try:
        rel = android.fetch_release()
    except Exception as e:  # noqa: BLE001 — frontière UI
        QMessageBox.warning(None, "Android Studio", f"Impossible de lire la page officielle :\n{e}"); return 1
    msg = (f"Android Studio {rel.version}\nArchive : {rel.filename}\nSHA-256 : {rel.sha256}\n\n"
           f"En continuant, vous acceptez les conditions de Google :\n{android.TERMS_URL}\n\n"
           f"Mémoire maximale de l'IDE : {android.ide_heap_mb(android.mem_total_mb())} Mio.\n"
           f"Émulateur : {'KVM disponible' if k['dev_kvm_rw'] else 'KVM indisponible → utilisez un téléphone en USB (adb)'}.")
    if QMessageBox.question(None, "Installer Android Studio", msg) != QMessageBox.StandardButton.Yes:
        return 2
    dlg = QProgressDialog("Téléchargement d'Android Studio…", None, 0, 100); dlg.show()
    def prog(done, total):
        dlg.setValue(int(100 * done / max(1, total))); app.processEvents()
    try:
        archive = android.download(rel, android.base_dir().parent / "downloads", prog)
        android.install(archive); archive.unlink()
    except Exception as e:  # noqa: BLE001
        QMessageBox.warning(None, "Android Studio", f"Échec : {e}"); return 1
    QMessageBox.information(None, "Android Studio", "Installé. Au premier lancement, l'assistant d'Android Studio "
                            "télécharge le SDK choisi (seulement les versions nécessaires).")
    subprocess.Popen([str(android.base_dir() / "bin/studio.sh")]); return 0


def miktex_gui() -> int:
    from PySide6.QtWidgets import QApplication, QMessageBox
    QApplication.instance() or QApplication(sys.argv)
    def confirm(fpr):
        return QMessageBox.question(None, "MiKTeX", f"Empreinte de la clé du dépôt MiKTeX :\n{fpr}\n\n"
                                    "Vérifiez-la sur https://miktex.org/download puis confirmez.") \
            == QMessageBox.StandardButton.Yes
    try:
        rc = miktex.install(confirm)
    except Exception as e:  # noqa: BLE001
        QMessageBox.warning(None, "MiKTeX", f"Échec : {e}"); return 1
    QMessageBox.information(None, "MiKTeX", "MiKTeX installé." if rc == 0 else f"Arrêté (code {rc}).")
    return rc


TEMPLATES = [Path("/usr/share/nexos/templates"), Path(__file__).resolve().parents[1] / "templates"]


def new_android_project(dest: Path | None = None) -> Path:
    """Copie le modèle Kotlin dans ~/AndroidStudioProjects/BonjourNexOS (sans écraser)."""
    src = next((t / "android-kotlin" for t in TEMPLATES if (t / "android-kotlin").is_dir()), None)
    if src is None:
        raise FileNotFoundError("modèle android-kotlin introuvable")
    dest = dest or Path.home() / "AndroidStudioProjects" / "BonjourNexOS"
    if dest.exists():
        raise FileExistsError(f"{dest} existe déjà")
    shutil.copytree(src, dest)
    return dest


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "status"
    if cmd == "android-project":
        print(new_android_project(Path(argv[1]) if len(argv) > 1 else None)); return 0
    return {"status": status, "android": android_gui, "miktex": miktex_gui}.get(cmd, status)()


if __name__ == "__main__":
    sys.exit(main())
