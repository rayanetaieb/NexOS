"""Interface en ligne de commande : nexai {status,ask,enable,disable,config,models,bench,gui}."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import models
from .config import Config
from .engine import GenerationStats
from .manager import AssistantManager
from .prompts import flag_risky_commands


def _print_status(mgr: AssistantManager) -> None:
    for k, v in asdict(mgr.status()).items():
        print(f"{k:18} {v}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="nexai", description="Assistant IA local de NexOS")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="état et mémoire")
    a = sub.add_parser("ask", help="pose une question (le moteur s'arrête ensuite)")
    a.add_argument("question", nargs="+")
    a.add_argument("--stats", action="store_true")
    sub.add_parser("enable")
    sub.add_parser("disable", help="désactive complètement l'assistant")
    c = sub.add_parser("config", help="affiche ou modifie la configuration")
    c.add_argument("--set", nargs=2, action="append", metavar=("CLÉ", "VALEUR"), default=[])
    m = sub.add_parser("models", help="gestion des modèles")
    msub = m.add_subparsers(dest="mcmd", required=True)
    msub.add_parser("catalog")
    msub.add_parser("list")
    mi = msub.add_parser("import"); mi.add_argument("file", type=Path)
    md = msub.add_parser("download"); md.add_argument("key")
    mu = msub.add_parser("use"); mu.add_argument("file", type=Path)
    mr = msub.add_parser("remove"); mr.add_argument("file", type=Path)
    b = sub.add_parser("bench", help="mesures RAM/latence/vitesse (section G)")
    b.add_argument("-o", "--output", type=Path)
    e = sub.add_parser("eval", help="évalue la qualité des réponses (notation automatique)")
    e.add_argument("-o", "--output", type=Path)
    e.add_argument("--model", type=Path, help="modèle à évaluer (défaut : modèle actif)")
    sub.add_parser("gui", help="ouvre la fenêtre de l'assistant")
    args = p.parse_args(argv)

    cfg = Config.load()

    if args.cmd == "status":
        _print_status(AssistantManager(cfg))
    elif args.cmd in ("enable", "disable"):
        cfg.enabled = args.cmd == "enable"
        print(f"Assistant {'activé' if cfg.enabled else 'désactivé'} ({cfg.save()})")
    elif args.cmd == "config":
        for key, value in args.set:
            if not hasattr(cfg, key):
                p.error(f"clé inconnue : {key}")
            cur = getattr(cfg, key)
            setattr(cfg, key, value.lower() in ("1", "true", "oui") if isinstance(cur, bool) else type(cur)(value))
        if args.set:
            cfg.validate(); cfg.save()
        print(json.dumps(asdict(cfg), ensure_ascii=False, indent=2))
    elif args.cmd == "ask":
        mgr = AssistantManager(cfg)
        stats = GenerationStats()
        text = []
        try:
            for piece in mgr.ask(" ".join(args.question), stats=stats):
                text.append(piece)
                print(piece, end="", flush=True)
            print()
            for line in flag_risky_commands("".join(text)):
                print(f"⚠ Commande sensible, vérifiez avant d'exécuter : {line}", file=sys.stderr)
            if args.stats:
                print(json.dumps(asdict(stats), ensure_ascii=False, indent=2), file=sys.stderr)
        except Exception as e:  # noqa: BLE001 — frontière UI : message lisible
            print(f"Erreur : {e}", file=sys.stderr)
            return 1
        finally:
            mgr.shutdown()
    elif args.cmd == "models":
        if args.mcmd == "catalog":
            for mi_ in models.CATALOG:
                ok = "téléchargeable" if (mi_.url and mi_.sha256) else "NON VALIDÉ"
                print(f"{mi_.key:20} {mi_.name:32} {mi_.license:20} [{ok}] {mi_.notes}")
        elif args.mcmd == "list":
            for path in models.installed():
                mark = "*" if str(path) == cfg.model_path else " "
                print(f"{mark} {path}  ({path.stat().st_size / 2**20:.0f} Mio)")
        elif args.mcmd == "import":
            dest, digest = models.import_local(args.file)
            print(f"Importé : {dest}\nSHA-256 : {digest}")
        elif args.mcmd == "download":
            info = next((x for x in models.CATALOG if x.key == args.key), None)
            if not info:
                p.error("modèle inconnu (voir « nexai models catalog »)")
            print(f"Téléchargement de {info.name} — {info.url}")
            dest = models.download(info, lambda d, t: print(f"\r{d/2**20:.0f}/{t/2**20:.0f} Mio", end=""))
            print(f"\nVérifié : {dest}")
        elif args.mcmd == "use":
            cfg.model_path = str(args.file.resolve()); cfg.save()
            print(f"Modèle actif : {cfg.model_path}")
        elif args.mcmd == "remove":
            models.remove(args.file)
            if cfg.model_path == str(args.file.resolve()):
                cfg.model_path = ""; cfg.save()
            print("Supprimé")
    elif args.cmd == "bench":
        from .bench import run
        report = run(cfg, args.output)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == "eval":
        from .evaluate import evaluate
        if args.model:
            cfg.model_path = str(args.model.resolve())
        r = evaluate(cfg, out=args.output)
        print(f"{r['model']} : {r['score']}/{r['total']} réussites "
              f"({r['score_french_and_pass']} réussies ET en français) · {r['by_category']} · "
              f"1er token médian {r['median_first_token_s']} s · {r['median_tokens_per_s']} tokens/s · "
              f"RAM anonyme pic {r['engine_anon_peak_mb']} Mio")
    elif args.cmd == "gui":
        from .gui import main as gui_main
        return gui_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
