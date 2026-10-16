#!/usr/bin/env bash
# Compile llama-server (llama.cpp) pour l'image NexOS, dans un environnement Debian 13
# propre (mmdebstrap), en version PORTABLE : aucune optimisation propre à la machine
# de build (GGML_NATIVE=OFF) ; toutes les variantes CPU x86-64 sont compilées et la
# bonne est choisie au lancement (GGML_BACKEND_DL + GGML_CPU_ALL_VARIANTS).
# Résultat : $OUT/llama-dist/ (llama-server + bibliothèques, RPATH=$ORIGIN)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$PWD/out}"
SRC="${LLAMA_SRC:?chemin des sources llama.cpp (clone git)}"
SUITE="${SUITE:-trixie}"; MIRROR="${MIRROR:-http://deb.debian.org/debian}"
COMMIT="$(git -C "$SRC" rev-parse --short HEAD)"
DIST="$OUT/llama-dist"; rm -rf "$DIST"; mkdir -p "$DIST"

aptopts=()
[ -n "${KEYRING:-}" ] && aptopts+=(--keyring="$KEYRING")
[ -n "${APT_PROXY:-}" ] && aptopts+=(--aptopt="Acquire::http::Proxy \"$APT_PROXY\"" --aptopt="Acquire::https::Proxy \"$APT_PROXY\"")
[ -n "${APT_CAINFO:-}" ] && aptopts+=(--aptopt="Acquire::https::CaInfo \"$APT_CAINFO\"" --aptopt="APT::Sandbox::User \"root\"")

echo ">> compilation de llama.cpp $COMMIT dans Debian $SUITE"
mmdebstrap --variant=minbase --include=build-essential,cmake,ca-certificates "${aptopts[@]}" \
  --customize-hook="mkdir -p \"\$1/src\" && cp -a '$SRC/.' \"\$1/src/llama.cpp\" && rm -rf \"\$1/src/llama.cpp/build\"" \
  --customize-hook='chroot "$1" sh -c "cd /src/llama.cpp && cmake -B build -DCMAKE_BUILD_TYPE=Release \
      -DGGML_NATIVE=OFF -DGGML_BACKEND_DL=ON -DGGML_CPU_ALL_VARIANTS=ON -DLLAMA_CURL=OFF \
      -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DCMAKE_INSTALL_RPATH=\$ORIGIN \
      -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON >/tmp/cmake.log && \
      cmake --build build -j$(nproc) --target llama-server >/tmp/build.log 2>&1 || (tail -40 /tmp/build.log; exit 1)"' \
  --customize-hook="cp -a \"\$1/src/llama.cpp/build/bin/.\" '$DIST/'" \
  "$SUITE" /dev/null "$MIRROR"

cp "$SRC/LICENSE" "$DIST/LICENSE.llama.cpp"
echo "$COMMIT" > "$DIST/VERSION"
find "$DIST" -maxdepth 1 -type f ! -name 'llama-server' ! -name '*.so*' ! -name 'LICENSE*' ! -name VERSION -delete
echo ">> $DIST : $(ls "$DIST" | wc -l) fichiers, $(du -sh "$DIST" | cut -f1)"
ls "$DIST"
