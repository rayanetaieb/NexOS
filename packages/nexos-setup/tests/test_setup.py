import tarfile

import pytest
from nexos_setup import android

PAGE = """<table><tr><td>Linux (64-bit)</td>
<td><button>android-studio-2025.1.3.7-linux.tar.gz</button></td><td>1.4 GB</td>
<td>4b2c5c0d1d7f1f1e0a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021</td></tr></table>
<a href="https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2025.1.3.7/android-studio-2025.1.3.7-linux.tar.gz">dl</a>"""


def test_parse_release_from_official_page_layout():
    rel = android.parse_release(PAGE)
    assert rel.version == "2025.1.3.7"
    assert rel.sha256.startswith("4b2c5c0d") and len(rel.sha256) == 64
    assert rel.url.endswith("android-studio-2025.1.3.7-linux.tar.gz")


def test_parse_release_without_hash_is_refused():
    with pytest.raises(ValueError):
        android.parse_release(PAGE.replace("4b2c5c0d1d7f1f1e0a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021", "x"))


@pytest.mark.parametrize("ram,expected", [(2048, 1024), (8192, 2048), (16384, 4096), (65536, 4096)])
def test_ide_heap_is_bounded(ram, expected):
    assert android.ide_heap_mb(ram) == expected


def test_install_from_archive_creates_launcher(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("HOME", str(tmp_path))
    src = tmp_path / "src/android-studio/bin"; src.mkdir(parents=True)
    (src / "studio.sh").write_text("#!/bin/sh\n"); (src / "studio.svg").write_text("<svg/>")
    arc = tmp_path / "a.tar.gz"
    with tarfile.open(arc, "w:gz") as t:
        t.add(tmp_path / "src/android-studio", arcname="android-studio")
    target = android.install(arc)
    assert (target / "bin/studio.sh").exists() and android.installed()
    desktop = (tmp_path / "data/applications/android-studio.desktop").read_text()
    assert "STUDIO_VM_OPTIONS" in desktop and "Xmx" in (target.parent / "studio64.vmoptions").read_text()


def test_kvm_status_reads_real_system():
    st = android.kvm_status()
    assert set(st) == {"cpu_virtualisation", "dev_kvm", "dev_kvm_rw", "groupe_kvm"}
