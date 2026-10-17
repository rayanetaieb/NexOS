#!/usr/bin/env python3
"""Vérifie chaque bibliothèque candidate sur son dépôt Git officiel et produit catalog.json.

Pour chaque dépôt : dernière version publiée (tag semver le plus élevé), clone superficiel
à ce tag, lecture de library.properties (nom exact, version, auteur, description,
architectures, dépendances), détection de la licence (fichier LICENSE/COPYING), date du
dernier commit de la branche principale (maintenance), exemples disponibles.
Usage : fetch_catalog.py <dossier_de_travail> <catalog.json>
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from candidates import CANDIDATES, CATEGORIES

LICENSES = [  # (motif, identifiant SPDX) — ordre : du plus spécifique au plus général
    (r"GNU LESSER GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 2\.1", "LGPL-2.1"),
    (r"GNU LESSER GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 3", "LGPL-3.0"),
    (r"GNU AFFERO GENERAL PUBLIC LICENSE", "AGPL-3.0"),
    (r"GNU GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 3", "GPL-3.0"),
    (r"GNU GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 2", "GPL-2.0"),
    (r"Apache License[\s\S]{0,100}Version 2\.0", "Apache-2.0"),
    (r"Mozilla Public License[\s\S]{0,50}2\.0", "MPL-2.0"),
    (r"Permission is hereby granted, free of charge", "MIT"),
    (r"Redistribution and use in source and binary forms[\s\S]{0,1500}Neither the name", "BSD-3-Clause"),
    (r"Redistribution and use in source and binary forms", "BSD-2-Clause"),
    (r"This is free and unencumbered software released into the public domain", "Unlicense"),
    (r"Creative Commons Attribution[- ]ShareAlike|CC BY-SA", "CC-BY-SA"),
    (r"Creative Commons Attribution", "CC-BY"),
    (r"\bGPL\s*V?3\b", "GPL-3.0"),
    (r"Lesser General Public\s+License", "LGPL (version non précisée)"),
    (r"GNU General Public\s+License", "GPL (version non précisée)"),
    (r"\bMIT [Ll]icen[sc]e\b", "MIT"),
    (r"\bBSD [Ll]icen[sc]e\b", "BSD"),
    (r"public domain", "domaine public"),
]


def git(*args, cwd=None, timeout=300) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-300:])
    return r.stdout


def version_key(tag: str):
    nums = re.findall(r"\d+", tag)
    return [int(n) for n in nums[:4]] + [0] * (4 - len(nums[:4]))


def latest_tag(url: str) -> str | None:
    tags = [ln.split("refs/tags/")[1] for ln in git("ls-remote", "--tags", "--refs", url).splitlines()]
    tags = [t for t in tags if re.match(r"^v?\d+(\.\d+)*$", t)]
    return max(tags, key=version_key) if tags else None


def parse_properties(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def detect_license(repo: Path) -> str:
    lj = repo / "library.json"
    if lj.exists():
        try:
            lic = json.loads(lj.read_text(errors="replace")).get("license")
            if isinstance(lic, str) and lic.strip():
                return lic.strip() + " (library.json)"
        except ValueError:
            pass
    return _detect_license_files(repo)


def _detect_license_files(repo: Path) -> str:
    for f in sorted(repo.glob("*")):
        if re.match(r"(?i)^(license|licence|copying)(\.|$|-)", f.name) and f.is_file():
            txt = f.read_text(errors="replace")
            for pat, spdx in LICENSES:
                if re.search(pat, txt, re.IGNORECASE):
                    return spdx
            return f"voir {f.name}"
    # en-têtes des sources principales et library.properties / README
    cands = (sorted(repo.glob("src/*.h")) + sorted(repo.glob("src/*.cpp")) + sorted(repo.glob("*.h"))
             + sorted(repo.glob("*.cpp")) + sorted(repo.glob("README*")))
    for f in cands[:12]:
        txt = f.read_text(errors="replace")[:8000]
        for pat, spdx in LICENSES:
            if re.search(pat, txt, re.IGNORECASE):
                return spdx + " (en-tête)"
    return "non indiquée"


def check(category: str, slug: str, work: Path) -> dict:
    url = f"https://github.com/{slug}.git"
    entry = {"category": category, "category_name": CATEGORIES[category], "repository": f"https://github.com/{slug}"}
    try:
        tag = latest_tag(url)
        dest = work / slug.replace("/", "__")
        if not dest.exists():
            args = ["clone", "--depth", "1", "--quiet"] + (["--branch", tag] if tag else []) + [url, str(dest)]
            git(*args)
        props = parse_properties(dest / "library.properties")
        head = work / (slug.replace("/", "__") + "__head")
        if not head.exists():
            git("clone", "--depth", "1", "--quiet", "--no-checkout", url, str(head))
        last_commit = git("log", "-1", "--format=%cs", cwd=head).strip()
        tag_date = git("log", "-1", "--format=%cs", cwd=dest).strip()
        examples = sorted(str(p.relative_to(dest)) for p in dest.glob("examples/**/*.ino"))
        entry.update({
            "name": props.get("name") or slug.split("/")[1], "version": props.get("version") or tag or "(aucune version publiée)",
            "tag": tag, "release_date": tag_date, "author": props.get("author", ""),
            "maintainer": props.get("maintainer", ""), "description": props.get("sentence", ""),
            "paragraph": props.get("paragraph", ""), "architectures": props.get("architectures", "non déclarées"),
            "depends": [d.strip() for d in props.get("depends", "").split(",") if d.strip()],
            "license": detect_license(dest), "last_commit": last_commit, "examples": examples[:5],
            "library_properties": (dest / "library.properties").exists(), "path": str(dest), "ok": True,
        })
        age_days = (date.today() - date.fromisoformat(last_commit)).days
        entry["maintenance"] = ("active" if age_days < 365 else "modérée" if age_days < 3 * 365 else "faible (> 3 ans)")
    except Exception as e:  # noqa: BLE001 — l'échec est enregistré, pas masqué
        entry.update({"ok": False, "error": str(e)})
    return entry


def main(work: Path, out: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda c: check(c[0], c[1], work), CANDIDATES))
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [r for r in results if r["ok"]]
    print(f"{len(ok)}/{len(results)} dépôts vérifiés ; échecs : "
          + ", ".join(r["repository"].split("github.com/")[1] for r in results if not r["ok"]))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
