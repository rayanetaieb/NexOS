
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
