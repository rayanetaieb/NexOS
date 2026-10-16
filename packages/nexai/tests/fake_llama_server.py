#!/usr/bin/env python3
"""Faux llama-server pour les tests : même API HTTP minimale (/health,
/v1/chat/completions en SSE), alloue une quantité de mémoire paramétrable pour
simuler le poids d'un modèle, et enregistre ses arguments.
Ce n'est PAS un modèle : il renvoie une réponse fixe."""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

args = sys.argv[1:]
port = int(args[args.index("--port") + 1])
host = args[args.index("--host") + 1]
alloc_mb = int(os.environ.get("FAKE_ALLOC_MB", "64"))
delay = float(os.environ.get("FAKE_TOKEN_DELAY", "0.01"))
if os.environ.get("FAKE_ARGV_FILE"):
    with open(os.environ["FAKE_ARGV_FILE"], "w") as f:
        json.dump(args, f)

ballast = bytearray(alloc_mb * 1024 * 1024)
for i in range(0, len(ballast), 4096):   # toucher les pages : RSS réel
    ballast[i] = 1

WORDS = ["Utilisez", " la", " commande", " df", " -h", "."]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        n = min(body.get("max_tokens", 16), len(WORDS))
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream"); self.end_headers()
        for w in WORDS[:n]:
            time.sleep(delay)
            chunk = {"choices": [{"delta": {"content": w}}]}
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode()); self.wfile.flush()
        final = {"choices": [], "usage": {"prompt_tokens": 42, "completion_tokens": n},
                 "timings": {"predicted_per_second": 99.0}}
        self.wfile.write(f"data: {json.dumps(final)}\n\ndata: [DONE]\n\n".encode())


ThreadingHTTPServer((host, port), H).serve_forever()
