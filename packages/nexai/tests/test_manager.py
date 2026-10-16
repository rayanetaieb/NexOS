"""Tests du cycle de vie de nexai avec un faux moteur (aucun vrai modèle)."""
import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from nexai import sysinfo
from nexai.config import Config
from nexai.engine import GenerationStats, LlamaServerEngine
from nexai.manager import (
    AssistantDisabled,
    AssistantManager,
    Busy,
    NoModel,
    NotEnoughMemory,
)
from nexai.prompts import flag_risky_commands

FAKE = Path(__file__).with_name("fake_llama_server.py")


@pytest.fixture
def model(tmp_path):
    m = tmp_path / "tiny.gguf"
    m.write_bytes(b"GGUF" + b"\0" * 1024)
    return m


@pytest.fixture
def fake_binary(tmp_path):
    wrapper = tmp_path / "llama-server"
    wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {FAKE} \"$@\"\n")
    wrapper.chmod(0o755)
    return str(wrapper)


def make_cfg(model, fake_binary, **kw):
    cfg = Config(model_path=str(model), server_binary=fake_binary, idle_unload_seconds=5,
                 startup_timeout_s=20, min_free_ram_mb=1)
    for k, v in kw.items():
        setattr(cfg, k, v)
    return cfg


def test_no_engine_process_until_first_question(model, fake_binary):
    mgr = AssistantManager(make_cfg(model, fake_binary))
    st = mgr.status()
    assert not st.engine_running and st.engine_pid is None and st.engine_rss_mb == 0


def test_ask_streams_and_unload_frees_process(model, fake_binary, tmp_path, monkeypatch):
    argv_file = tmp_path / "argv.json"
    monkeypatch.setenv("FAKE_ARGV_FILE", str(argv_file))
    monkeypatch.setenv("FAKE_ALLOC_MB", "100")
    mgr = AssistantManager(make_cfg(model, fake_binary))
    stats = GenerationStats()
    text = "".join(mgr.ask("espace disque ?", stats=stats))
    assert text == "Utilisez la commande df -h."
    assert stats.completion_tokens == 6 and stats.first_token_s is not None
    st = mgr.status()
    assert st.engine_running and st.engine_rss_mb > 90       # mémoire du « modèle » chargée
    pid = st.engine_pid
    args = json.loads(argv_file.read_text())
    assert args[args.index("--host") + 1] == "127.0.0.1"     # jamais d'écoute externe
    assert args[args.index("--parallel") + 1] == "1"
    assert args[args.index("-ngl") + 1] == "0"               # GPU non utilisé par défaut
    assert "--no-repack" in args                             # profil économe en RAM par défaut
    assert mgr.unload() is True
    assert not mgr.status().engine_running
    assert not Path(f"/proc/{pid}").exists() or "zombie" in Path(f"/proc/{pid}/status").read_text()


def test_idle_unload(model, fake_binary):
    mgr = AssistantManager(make_cfg(model, fake_binary, idle_unload_seconds=5))
    "".join(mgr.ask("bonjour"))
    assert mgr.status().engine_running
    deadline = time.monotonic() + 15
    while mgr.status().engine_running and time.monotonic() < deadline:
        time.sleep(0.5)
    assert not mgr.status().engine_running


def test_single_request_at_a_time(model, fake_binary, monkeypatch):
    monkeypatch.setenv("FAKE_TOKEN_DELAY", "0.3")
    mgr = AssistantManager(make_cfg(model, fake_binary))
    started = threading.Event()

    def slow():
        for _ in mgr.ask("long"):
            started.set()
    t = threading.Thread(target=slow); t.start()
    assert started.wait(20)
    with pytest.raises(Busy):
        next(mgr.ask("second"))
    t.join(); mgr.unload()


def test_disabled(model, fake_binary):
    mgr = AssistantManager(make_cfg(model, fake_binary, enabled=False))
    with pytest.raises(AssistantDisabled):
        next(mgr.ask("x"))
    assert not mgr.status().engine_running


def test_no_model(fake_binary):
    mgr = AssistantManager(Config(server_binary=fake_binary))
    with pytest.raises(NoModel):
        next(mgr.ask("x"))


def test_low_memory_refuses_to_start(model, fake_binary):
    cfg = make_cfg(model, fake_binary, min_free_ram_mb=0, ram_margin_mb=4096)
    mgr = AssistantManager(cfg, mem_available=lambda: 1000)    # simule un PC chargé
    with pytest.raises(NotEnoughMemory):
        next(mgr.ask("x"))
    assert not mgr.status().engine_running


def test_engine_crash_reports_error(model, tmp_path):
    bad = tmp_path / "bad-server"; bad.write_text("#!/bin/sh\necho boom >&2\nexit 3\n"); bad.chmod(0o755)
    eng = LlamaServerEngine(str(bad), str(model), 512, 1, startup_timeout_s=5)
    with pytest.raises(Exception, match="boom"):
        eng.start()


def test_config_roundtrip_and_validation(tmp_path):
    p = tmp_path / "c.toml"
    cfg = Config(model_path='/m/a "b".gguf', idle_unload_seconds=30)
    cfg.save(p)
    assert Config.load(p) == cfg
    with pytest.raises(ValueError):
        Config(gpu="cuda").validate()
    with pytest.raises(ValueError):
        Config(max_tokens=99999).validate()


def test_risky_command_flagging():
    hits = flag_risky_commands("Faites :\nsudo rm -rf /tmp/x\nls -l\ndd if=/dev/zero of=/dev/sda")
    assert len(hits) == 2 and "ls -l" not in hits


def test_sysinfo_reads_proc():
    assert sysinfo.mem_available_mb() > 0
    assert sysinfo.rss_mb(os.getpid()) > 0
    assert sysinfo.physical_cores() >= 1


def test_strip_think_removes_leading_block():
    from nexai.manager import strip_think
    assert "".join(strip_think(iter(["<th", "ink>\n\n</th", "ink>\n\nBon", "jour"]))) == "Bonjour"
    assert "".join(strip_think(iter(["<think>raisonnement</think>", " Oui"]))) == "Oui"
    assert "".join(strip_think(iter(["Salut ", "<think> reste"]))) == "Salut <think> reste"
    assert "".join(strip_think(iter(["  ", "Ok"]))) == "  Ok"


def test_qwen3_disables_thinking():
    from nexai.manager import model_request_options
    assert model_request_options("/m/Qwen3-0.6B-Q8_0.gguf") == {"chat_template_kwargs": {"enable_thinking": False}}
    assert model_request_options("/m/qwen2.5-0.5b.gguf") == {}


def test_knowledge_injection():
    from nexai.knowledge import augment, relevant_facts
    assert any("Centre Python" in f for f in relevant_facts("Comment installer pandas ?"))
    assert any("Centre de mises à jour" in f for f in relevant_facts("Comment mettre à jour le système ?"))
    assert augment("Combien font 2+2 ?") == "Combien font 2+2 ?"


def test_french_detector_is_neutral_on_code():
    from nexai.evaluate import is_french
    assert is_french("```python\ndef f():\n    return 1\n```")
    assert is_french("12 multiplié par 15 fait 180.")
    assert not is_french("You can use the command df to show the free space of your file system and it is easy.")
