"""nexos-python : Centre Python en ligne de commande (même cœur que l'interface)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import core


def _p(line: str) -> None:
    print(line, flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="nexos-python", description="Centre Python NexOS")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("profiles", help="liste les profils et leur état")
    for c in ("install", "test", "remove", "kernel"):
        s = sub.add_parser(c, help=f"{c} d'un profil"); s.add_argument("profile")
    n = sub.add_parser("new", help="nouveau projet"); n.add_argument("name"); n.add_argument("--profile")
    sub.add_parser("projects", help="liste les projets")
    for c in ("add", "rm", "upgrade"):
        s = sub.add_parser(c); s.add_argument("project", type=Path); s.add_argument("packages", nargs="*")
    t = sub.add_parser("tree"); t.add_argument("project", type=Path)
    q = sub.add_parser("search"); q.add_argument("query", nargs="?", default="")
    i = sub.add_parser("info"); i.add_argument("name")
    gui = sub.add_parser("gui", help="ouvre l'interface graphique")  # noqa: F841
    a = ap.parse_args(argv)

    if a.cmd == "profiles":
        for p in core.list_profiles():
            state = f"installé ({p.size_mb()} Mio)" if p.installed else "non installé"
            print(f"{p.name:12} {p.locked_packages:4} paquets verrouillés  {state:22} {p.description}")
        return 0
    if a.cmd == "gui":
        from .gui import main as gui_main
        return gui_main()
    if a.cmd == "search":
        for e in core.search_catalog(a.query):
            print(f"{e.name:16} [{e.category}] {e.summary}")
        return 0
    if a.cmd == "info":
        info = core.pypi_info(a.name)
        print(info if info else "Introuvable sur PyPI (ou hors ligne).")
        return 0 if info else 1
    if a.cmd == "projects":
        for p in core.list_projects():
            print(p)
        return 0

    ops = {
        "install": lambda: core.install_profile(a.profile, on_line=_p),
        "test": lambda: core.test_profile(a.profile, on_line=_p),
        "remove": lambda: core.remove_profile(a.profile),
        "kernel": lambda: core.register_kernel(a.profile, on_line=_p),
        "new": lambda: core.create_project(a.name, a.profile, on_line=_p),
        "add": lambda: core.add_packages(a.project, a.packages, on_line=_p),
        "rm": lambda: core.remove_packages(a.project, a.packages, on_line=_p),
        "upgrade": lambda: core.upgrade_packages(a.project, a.packages or None, on_line=_p),
        "tree": lambda: core.dependency_tree(a.project),
    }
    r = ops[a.cmd]()
    if a.cmd in ("remove", "tree"):
        print(r.output)
    if not r.ok:
        print(f"ÉCHEC (code {r.returncode}) : {' '.join(r.command)}", file=sys.stderr)
    return 0 if r.ok else 1


if __name__ == "__main__":
    sys.exit(main())
