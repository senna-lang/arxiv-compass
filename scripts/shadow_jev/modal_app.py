"""SPECTER とは別の Modal app。日次 publish からは直接呼ばない。"""
from __future__ import annotations

from pathlib import Path

import modal

app = modal.App("arxiv-jev-shadow")
weights = modal.Volume.from_name("arxiv-jev-weights", create_if_missing=True)
WEIGHTS = "/weights"
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", extra_index_url="https://download.pytorch.org/whl/cu124")
    .pip_install("transformers", "peft", "huggingface_hub", "numpy")
    .add_local_python_source("shadow_jev")
)

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
MODEL_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
ADAPTER_ID = "e2-lr-1e-4-epoch-3-quarter-3"


@app.function(image=image, volumes={WEIGHTS: weights}, timeout=1800)
def bootstrap_weights() -> str:
    """Volume へ pin 済み base を一度だけ置く。adapter はローカルから batch_upload する。"""
    from huggingface_hub import snapshot_download

    base_dir = Path(WEIGHTS) / "base" / MODEL_REVISION
    snapshot_download(MODEL_ID, revision=MODEL_REVISION, local_dir=base_dir)
    weights.commit()
    return str(base_dir)


@app.cls(
    gpu="L4",
    image=image,
    volumes={WEIGHTS: weights},
    timeout=180,
    startup_timeout=600,
    retries=0,
)
class JevRanker:
    @modal.enter()
    def load(self) -> None:
        import torch
        from shadow_jev.inference import load_inference_model

        torch.set_num_threads(4)
        self.device = torch.device("cuda")
        self.model, self.tokenizer = load_inference_model(
            Path(WEIGHTS) / "base" / MODEL_REVISION,
            Path(WEIGHTS) / "adapters" / ADAPTER_ID,
        )
        self.model.to(self.device)
        torch.cuda.reset_peak_memory_stats()

    @modal.method()
    def rank(self, papers: list[dict], state: str, question: str, options: list[str], batch_size: int, expected_adapter_sha256: str) -> dict:
        import time

        import torch
        from shadow_jev.inference import rank_papers, sha256_file

        started = time.perf_counter()
        adapter = Path(WEIGHTS) / "adapters" / ADAPTER_ID / "adapter_model.safetensors"
        if sha256_file(adapter) != expected_adapter_sha256:
            raise RuntimeError("adapter SHA-256 does not match the configured E2 checkpoint")
        probabilities = rank_papers(self.model, self.tokenizer, state, papers, question, options, batch_size, self.device)
        return {
            "probabilities": probabilities,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
            "execution_time_ms": round((time.perf_counter() - started) * 1000),
            "gpu": "L4",
        }


@app.local_entrypoint()
def bootstrap(adapter_dir: str = "/Users/senna/Documents/Repos/jeb-scratch/checkpoints/e2/lr-1e-4/epoch-3-quarter-3") -> None:
    print(bootstrap_weights.remote())
    adapter = Path(adapter_dir)
    with weights.batch_upload() as batch:
        batch.put_file(adapter / "adapter_config.json", f"/adapters/{ADAPTER_ID}/adapter_config.json")
        batch.put_file(adapter / "adapter_model.safetensors", f"/adapters/{ADAPTER_ID}/adapter_model.safetensors")
    print(f"uploaded adapter to /adapters/{ADAPTER_ID}")


@app.local_entrypoint()
def smoke(daily_json: str = "data/20260911.json") -> None:
    import json

    from core.config import load_config
    from shadow_jev.predicate import canonical_predicate, shared_state

    config = load_config()
    papers = json.loads(Path(daily_json).read_text())["papers"]
    predicate = canonical_predicate(config)
    result = JevRanker().rank.remote(
        papers,
        shared_state(config),
        predicate["question"],
        predicate["options"],
        config["shadow_jev"]["batch_size"],
        config["shadow_jev"]["model"]["adapter_sha256"],
    )
    print({
        "count": len(result["probabilities"]),
        "execution_time_ms": result["execution_time_ms"],
        "peak_cuda_memory_bytes": result["peak_cuda_memory_bytes"],
        "gpu": result["gpu"],
    })
