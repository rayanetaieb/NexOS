#!/usr/bin/env python3
"""Schéma → PCB avec l'API Python de KiCad (pcbnew), comme « Mettre à jour le PCB depuis le schéma » :
lit la netlist exportée par kicad-cli, charge chaque empreinte depuis les bibliothèques
installées, crée les réseaux, relie les pastilles, enregistre une nouvelle carte.
Usage : kicad_sch_to_pcb.py netlist.net sortie.kicad_pcb"""
import re
import sys
from pathlib import Path

import pcbnew

net_txt = Path(sys.argv[1]).read_text()
comps = re.findall(r'\(comp \(ref "?([^")\s]+)"?\).*?\(footprint "?([^")\s]+)"?\)', net_txt, re.S)
board = pcbnew.BOARD()
# En script autonome, le registre de greffons n'est pas initialisé : greffon du format KiCad explicite.
io = pcbnew.PCB_IO_KICAD_SEXPR()
libroot = Path("/usr/share/kicad/footprints")
placed, missing = {}, []
for i, (ref, fpid) in enumerate(comps):
    lib, name = fpid.split(":", 1)
    try:
        fp = io.FootprintLoad(str(libroot / f"{lib}.pretty"), name)
    except Exception:  # noqa: BLE001 — empreinte absente des bibliothèques installées
        fp = None
    if fp is None:
        missing.append(fpid); continue
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20 + (i % 10) * 15), pcbnew.FromMM(20 + (i // 10) * 15)))
    board.Add(fp); placed[ref] = fp
nets = 0
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "?([^")]*)"?\)(.*?)(?=\(net \(code|\)\s*\)\s*$)', net_txt, re.S):
    name, body = m.group(1), m.group(2)
    ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); nets += 1
    for ref, pin in re.findall(r'\(node \(ref "?([^")\s]+)"?\) \(pin "?([^")\s]+)"?\)', body):
        fp = placed.get(ref)
        if fp:
            for pad in fp.Pads():
                if pad.GetNumber() == pin:
                    pad.SetNet(ni)
pcbnew.SaveBoard(sys.argv[2], board)
print(f"OK {len(placed)}/{len(comps)} empreintes placées, {nets} réseaux, empreintes manquantes : {len(missing)}")
