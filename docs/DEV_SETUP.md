# Environnement de développement NexOS

Tout se fait **sans modifier le système hôte** au-delà de l'installation d'outils :
la construction écrit uniquement dans `out/`, la VM démarre l'image en mode
`snapshot=on` (aucune écriture sur le disque image).

## Hôte recommandé
Debian 13 ou Ubuntu 24.04, x86_64, 8 Go de RAM, 20 Go libres. KVM fortement
conseillé (`ls /dev/kvm`) : sans KVM, QEMU émule le CPU (≈ 10× plus lent).

## Installation des outils
```bash
sudo apt install git mmdebstrap qemu-system-x86 qemu-utils xorriso \
                 squashfs-tools e2fsprogs python3-venv cmake build-essential
# accès KVM pour votre utilisateur (puis se reconnecter)
sudo usermod -aG kvm "$USER"
```

## Construire et tester le prototype (phase 2)
```bash
git clone <dépôt> nexos && cd nexos
make rootfs          # Debian trixie par défaut (mmdebstrap)
make disk            # image ext4 + noyau + initramfs dans out/
make boot-test       # démarre dans QEMU, attend NEXOS-BOOT-OK, vérifie 0 unité en échec
make vm              # session interactive (console série, Ctrl+A puis X pour quitter)
```
Sans accès à `deb.debian.org`, on peut valider la chaîne avec Ubuntu :
`make rootfs SUITE=noble MIRROR=http://archive.ubuntu.com/ubuntu KERNEL=linux-image-virtual`
(c'est ainsi qu'elle a été validée dans l'environnement de développement initial).

## Assistant IA (nexai)
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e "packages/nexai[test,gui]" ruff
make test-nexai                      # pytest + ruff

# Moteur llama.cpp (CPU)
git clone --depth 1 https://github.com/ggml-org/llama.cpp
cmake -S llama.cpp -B llama.cpp/build -DGGML_NATIVE=ON -DLLAMA_CURL=OFF
cmake --build llama.cpp/build -j --target llama-server
nexai config --set server_binary "$PWD/llama.cpp/build/bin/llama-server"

# Modèle : fichier GGUF que vous avez téléchargé et vérifié vous-même
nexai models import ~/Téléchargements/qwen2.5-0.5b-instruct-q4_k_m.gguf
nexai models use ~/.local/share/nexos/nexai/models/qwen2.5-0.5b-instruct-q4_k_m.gguf
nexai ask "Quelle commande affiche l'espace disque ?"
nexai bench -o bench.json            # mesures section G
nexai gui                            # fenêtre (nécessite PySide6)
```

## Git
Commits logiques, un sujet par commit. `out/` est ignoré.
