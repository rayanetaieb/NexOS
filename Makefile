# Points d'entrée NexOS. Tout est écrit dans out/ ; rien n'est modifié sur l'hôte.
SUITE  ?= trixie
MIRROR ?= http://deb.debian.org/debian
KERNEL ?= linux-image-amd64
OUT    ?= $(CURDIR)/out
# Hôte non-Debian (ex. Ubuntu 24.04) : trousseau récupéré par chaîne de confiance.
KEYRING ?= $(if $(wildcard $(OUT)/debian-archive-keyring.gpg),$(OUT)/debian-archive-keyring.gpg,)
export SUITE MIRROR KERNEL OUT KEYRING APT_PROXY APT_CAINFO

.PHONY: keyring rootfs disk boot-test vm test-nexai clean

keyring:
	./build/fetch-debian-keyring.sh

rootfs:
	./build/build-rootfs.sh

disk:
	./build/make-disk.sh

boot-test:
	./tests/boot/test-boot.sh

vm:
	qemu-system-x86_64 -machine q35,accel=kvm:tcg -m 1024 -smp 2 -nographic \
	  -kernel $(OUT)/vmlinuz -initrd $(OUT)/initrd.img -append "root=/dev/vda rw console=ttyS0" \
	  -drive file=$(OUT)/nexos.img,format=raw,if=virtio,snapshot=on -nic user,model=virtio-net-pci

test-nexai:
	cd packages/nexai && python -m pytest -q && ruff check nexai tests

clean:
	rm -rf out
