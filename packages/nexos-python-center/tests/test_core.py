"""Tests du cœur du Centre Python avec le VRAI uv (réseau PyPI requis pour l'intégration)."""
import os
import shutil
from pathlib import Path

import pytest

from nexos_python import core

REPO_PROFILES = Path(__file__).resolve().parents[3] / "python" / "profiles"


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("NEXOS_PROJECTS", str(tmp_path / "projets"))
    monkeypatch.setenv("NEXOS_PYTHON_PROFILES", str(REPO_PROFILES))
    monkeypatch.setenv("NEXOS_PYTHON", shutil.which("python3.13") or "/usr/bin/python3")


def test_profiles_are_listed_with_locks():
    names = {p.name for p in core.list_profiles()}
    assert {"base", "science", "ai", "vision", "electronics", "appdev"} <= names
    for p in core.list_profiles():
        assert p.locked_packages > 0, f"{p.name} sans uv.lock"
        assert not p.installed


def test_locked_versions_parse():
    pins = core.locked_versions(core.get_profile("base"))
    assert "pytest" in pins and pins["pytest"][0].isdigit()


def test_catalog_search():
    assert any(e.name == "pyserial" for e in core.search_catalog("série"))
    assert any(e.name == "opencv-python" for e in core.search_catalog("vision"))


def test_unknown_profile():
    with pytest.raises(KeyError):
        core.get_profile("inexistant")


@pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="intégration réseau (NEXOS_NET_TESTS=1)")
def test_install_test_remove_base_profile():
    lines = []
    r = core.install_profile("base", on_line=lines.append)
    assert r.ok, r.output
    p = core.get_profile("base")
    assert p.installed and p.size_mb() > 1
    t = core.test_profile("base")
    assert t.ok, t.output
    assert core.remove_profile("base").ok and not p.installed


@pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="intégration réseau (NEXOS_NET_TESTS=1)")
def test_project_lifecycle():
    r = core.create_project("demo")
    assert r.ok, r.output
    proj = core.projects_root() / "demo"
    assert core.add_packages(proj, ["six==1.16.0"]).ok
    assert any(p["name"] == "six" and p["version"] == "1.16.0" for p in core.project_packages(proj))
    up = core.upgrade_packages(proj, ["six"])
    assert up.ok, up.output
    assert any(p["name"] == "six" and p["version"] != "1.16.0" for p in core.project_packages(proj))
    tree = core.dependency_tree(proj)
    assert tree.ok and "six" in tree.output
    assert core.remove_packages(proj, ["six"]).ok
    assert not any(p["name"] == "six" for p in core.project_packages(proj))
    bad = core.add_packages(proj, ["ce-paquet-nexiste-pas-nexos-1234"])
    assert not bad.ok and bad.output  # l'erreur d'uv est bien remontée


@pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="intégration réseau (NEXOS_NET_TESTS=1)")
def test_project_from_profile_uses_locked_versions():
    r = core.create_project("depuis-base", profile="base")
    assert r.ok, r.output
    proj = core.projects_root() / "depuis-base"
    pins = core.locked_versions(core.get_profile("base"))
    installed = {p["name"].lower(): p["version"] for p in core.project_packages(proj)}
    assert installed["pytest"] == pins["pytest"]


@pytest.mark.skipif(not os.environ.get("NEXOS_NET_TESTS"), reason="intégration réseau (NEXOS_NET_TESTS=1)")
def test_failed_upgrade_restores_previous_constraint(monkeypatch):
    assert core.create_project("restaure").ok
    proj = core.projects_root() / "restaure"
    assert core.add_packages(proj, ["six==1.16.0"]).ok
    real_add = core.add_packages
    calls = {"n": 0}

    def flaky_add(project, pkgs, on_line=None):
        calls["n"] += 1
        if calls["n"] == 1:   # le ré-ajout « dernière version » échoue (ex. hors ligne)
            return core.OpResult(["uv", "add"], 1, "simulé")
        return real_add(project, pkgs, on_line)
    monkeypatch.setattr(core, "add_packages", flaky_add)
    assert not core.upgrade_packages(proj, ["six"]).ok
    assert core._current_spec(proj, "six") == "six==1.16.0"
