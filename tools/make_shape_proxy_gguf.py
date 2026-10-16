#!/usr/bin/env python3
"""Génère un GGUF « proxy de forme » : architecture et dimensions d'un vrai
modèle (par défaut Qwen2.5-0.5B), tokenizer réel copié d'un GGUF de vocabulaire,
mais POIDS ALÉATOIRES.

Usage : mesurer RAM, temps de chargement et vitesse d'inférence d'un modèle de
cette taille quand le vrai fichier n'est pas téléchargeable. Les réponses sont
du charabia : AUCUNE conclusion sur la qualité ne doit être tirée de ce fichier.

  python make_shape_proxy_gguf.py VOCAB.gguf OUT-f16.gguf
"""
import sys

import numpy as np
from gguf import GGUFReader, GGUFValueType, GGUFWriter

# Dimensions publiées de Qwen2.5-0.5B (config.json du dépôt Qwen).
CFG = dict(hidden=896, layers=24, heads=14, kv_heads=2, ffn=4864,
           ctx=32768, rope_theta=1_000_000.0, eps=1e-6)


def copy_tokenizer(reader: GGUFReader, w: GGUFWriter) -> int:
    n_vocab = 0
    for name, field in reader.fields.items():
        if not name.startswith("tokenizer."):
            continue
        vtype = field.types[0]
        value = field.contents()
        if vtype == GGUFValueType.ARRAY:
            sub = field.types[1]
            w.add_key_value(name, value, vtype, sub_type=sub)
            if name == "tokenizer.ggml.tokens":
                n_vocab = len(value)
        else:
            w.add_key_value(name, value, vtype)
    return n_vocab


def main(vocab_path: str, out_path: str) -> None:
    rng = np.random.default_rng(0)
    reader = GGUFReader(vocab_path)
    w = GGUFWriter(out_path, "qwen2")
    w.add_name("NexOS shape proxy (Qwen2.5-0.5B dims, RANDOM WEIGHTS)")
    n_vocab = copy_tokenizer(reader, w)
    c = CFG
    head_dim = c["hidden"] // c["heads"]
    w.add_context_length(c["ctx"])
    w.add_embedding_length(c["hidden"])
    w.add_block_count(c["layers"])
    w.add_feed_forward_length(c["ffn"])
    w.add_head_count(c["heads"])
    w.add_head_count_kv(c["kv_heads"])
    w.add_rope_freq_base(c["rope_theta"])
    w.add_layer_norm_rms_eps(c["eps"])
    w.add_file_type(1)  # F16

    def rnd(*shape):
        return (rng.standard_normal(shape, dtype=np.float32) * 0.02).astype(np.float16)

    h, kv = c["hidden"], c["kv_heads"] * head_dim
    w.add_tensor("token_embd.weight", rnd(n_vocab, h))
    w.add_tensor("output_norm.weight", np.ones(h, dtype=np.float32))
    for i in range(c["layers"]):
        p = f"blk.{i}."
        w.add_tensor(p + "attn_norm.weight", np.ones(h, dtype=np.float32))
        w.add_tensor(p + "attn_q.weight", rnd(h, h))
        w.add_tensor(p + "attn_q.bias", np.zeros(h, dtype=np.float32))
        w.add_tensor(p + "attn_k.weight", rnd(kv, h))
        w.add_tensor(p + "attn_k.bias", np.zeros(kv, dtype=np.float32))
        w.add_tensor(p + "attn_v.weight", rnd(kv, h))
        w.add_tensor(p + "attn_v.bias", np.zeros(kv, dtype=np.float32))
        w.add_tensor(p + "attn_output.weight", rnd(h, h))
        w.add_tensor(p + "ffn_norm.weight", np.ones(h, dtype=np.float32))
        w.add_tensor(p + "ffn_gate.weight", rnd(c["ffn"], h))
        w.add_tensor(p + "ffn_up.weight", rnd(c["ffn"], h))
        w.add_tensor(p + "ffn_down.weight", rnd(h, c["ffn"]))
    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()
    print(f"écrit : {out_path} (vocab={n_vocab})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
