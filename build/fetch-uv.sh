#!/usr/bin/env bash
# Récupère le binaire uv officiel (roue PyPI manylinux x86_64, MIT/Apache-2.0) → $OUT/uv-dist/
# pip vérifie l'empreinte publiée par PyPI ; on note version et SHA-256 du binaire.
set -euo pipefail
OUT="${OUT:-$PWD/out}"; UV_VERSION="${UV_VERSION:-0.13.1}"
D="$OUT/uv-dist"; rm -rf "$D"; mkdir -p "$D"; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
python3 -m pip download --quiet --no-deps --only-binary=:all: --platform manylinux_2_17_x86_64 \
  --python-version 3.13 "uv==$UV_VERSION" -d "$tmp"
python3 - "$tmp"/uv-*.whl "$D" <<'PY'
import sys, zipfile, os
whl, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(whl) as z:
    for n in z.namelist():
        if n.endswith("/scripts/uv") or n.endswith(".data/scripts/uv"):
            open(os.path.join(out, "uv"), "wb").write(z.read(n))
        if n.endswith("LICENSE-MIT") or n.endswith("LICENSE-APACHE"):
            open(os.path.join(out, os.path.basename(n)), "wb").write(z.read(n))
PY
chmod 755 "$D/uv"
echo "$UV_VERSION $(sha256sum "$D/uv" | cut -d' ' -f1)" > "$D/VERSION"
"$D/uv" --version && cat "$D/VERSION"
