
import pytest
from nexos_cc import admin, probe


def test_admin_refuses_unknown_and_protected(capsys):
    assert admin.main(["rm", "-rf", "/"]) == 2
    assert admin.main(["service-disable", "sddm.service"]) == 3
    assert admin.main(["service-disable", "dbus.service"]) == 3
    assert admin.main(["service-enable", "../../evil"]) == 2
    assert admin.main(["install-optional", "paquet-arbitraire"]) == 2
    assert admin.main(["snapshot-create", "x; rm -rf /"]) == 2


def test_protected_matching():
    assert admin.protected("getty@tty1.service") and not admin.protected("cups.service")


def test_probe_reads_real_values():
    m = probe.meminfo()
    assert m["MemTotal"] > 0 and 0 < m["MemAvailable"] <= m["MemTotal"]
    assert 0 <= probe.cpu_percent(0.1) <= 100
    d = probe.disk_usage("/")
    assert d["total_mb"] > 0 and 0 <= d["used_pct"] <= 100
    assert probe.uptime_s() > 0 and probe.top_processes(3)
    assert "PRETTY_NAME" in probe.os_release()


def test_user_autostart_toggle(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".config/autostart").mkdir(parents=True)
    (tmp_path / ".config/autostart/demo.desktop").write_text("[Desktop Entry]\nName=Démo\nExec=true\n")
    probe.set_user_autostart("demo.desktop", False)
    assert ("demo.desktop", "Démo", False) in probe.autostart_entries()
    probe.set_user_autostart("demo.desktop", True)
    assert ("demo.desktop", "Démo", True) in probe.autostart_entries()


def test_gui_all_pages_render(monkeypatch):
    pytest.importorskip("PySide6")
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from nexos_cc.gui import ControlCenter
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    w = ControlCenter(); w.show()
    for i in range(len(w.pages)):
        w.nav.setCurrentRow(i); app.processEvents()
    assert w.pages[0].ram.value() > 0
    w.close()


def test_snapshot_undo_rejects_invalid_numbers(capsys):
    from nexos_cc import admin
    for bad in ("", "0", "-1", "1;rm", "1..0", "abc"):
        assert admin.main(["snapshot-undo", bad]) == 2


def test_gaming_actions_are_restricted(capsys):
    from nexos_cc import admin
    assert admin.main(["install-app", "org.evil.App"]) == 2          # hors liste autorisée
    assert admin.main(["install-app"]) == 2


def test_mok_import_validates_password(monkeypatch, capsys):
    import io
    from nexos_cc import admin
    monkeypatch.setattr("sys.stdin", io.StringIO("court\n"))
    assert admin.main(["mok-import"]) == 2                            # trop court
    monkeypatch.setattr("sys.stdin", io.StringIO("assezlong123\n"))
    monkeypatch.setattr(admin, "MOK_PUB", "/nonexistent/mok.pub")
    assert admin.main(["mok-import"]) == 3                            # pas de clé DKMS


def test_nvidia_detection(monkeypatch):
    from nexos_cc import probe
    monkeypatch.setattr(probe, "sh", lambda cmd, timeout=10: "01:00.0 0300: 10de:2484 (rev a1)\n00:02.0 0300: 8086:9bc4\n")
    assert probe.nvidia_gpu() is True
    monkeypatch.setattr(probe, "sh", lambda cmd, timeout=10: "00:02.0 0300: 8086:9bc4\n02:00.0 0200: 10de:0001\n")
    assert probe.nvidia_gpu() is False                                # 10de mais pas une carte graphique
