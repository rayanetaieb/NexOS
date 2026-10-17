import os

import pytest
from nexos_arduino import core


def test_catalog_has_100_libraries_in_20_categories():
    c = core.catalog()
    assert c["count"] == 100 and len(c["libraries"]) == 100
    assert len({e["category"] for e in c["libraries"]}) == 20
    for e in c["libraries"]:
        for k in ("name", "repository", "version", "license", "architectures", "category_name", "install", "maintenance"):
            assert e.get(k), (e["name"], k)
    assert len({e["name"] for e in c["libraries"]}) == 100      # aucun doublon


def test_search_and_filter():
    assert any(e["name"] == "ArduinoJson" for e in core.search("json"))
    assert all(e["category"] == "11-rtc" for e in core.search("", "11-rtc"))


@pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="réseau requis")
def test_install_with_dependency_update_remove(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXOS_ARDUINO_LIBS", str(tmp_path / "libs"))
    bme = next(e for e in core.catalog()["libraries"] if e["name"] == "Adafruit BME280 Library")
    log = core.install(bme)
    names = {i.name for i in core.installed()}
    assert "Adafruit BME280 Library" in names and "Adafruit Unified Sensor" in names, log
    assert core.status(bme) == "installée"
    assert "supprimée" in core.remove(bme)
    assert core.status(bme) == "non installée"


def test_conflict_detected(tmp_path, monkeypatch):
    """Même bibliothèque déjà présente dans un autre dossier : installation refusée (pas de doublon)."""
    monkeypatch.setenv("NEXOS_ARDUINO_LIBS", str(tmp_path / "libs"))
    e = next(x for x in core.catalog()["libraries"] if x["name"] == "ArduinoJson")
    other = tmp_path / "libs/ancienne_copie"; other.mkdir(parents=True)
    (other / "library.properties").write_text("name=ArduinoJson\nversion=5.0.0\n")
    assert core.status(e).startswith("installée (5.0.0")
    with pytest.raises(RuntimeError, match="conflit"):
        core.install(e)


def test_diagnose_reports_real_state():
    d = core.diagnose()
    assert set(d) >= {"ports", "cartes", "groupe_dialout", "arduino_builder", "avr_gcc"}
