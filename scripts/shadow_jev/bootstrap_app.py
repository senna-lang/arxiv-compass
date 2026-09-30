"""L4 を定義しない CPU bootstrap。支払い方法なしでも base weight を置ける。"""
from pathlib import Path

import modal

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
MODEL_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
ADAPTER_ID = "e2-lr-1e-4-epoch-3-quarter-3"
WEIGHTS = "/weights"
weights = modal.Volume.from_name("arxiv-jev-weights", create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.11").pip_install("huggingface_hub")
app = modal.App("arxiv-jev-bootstrap", image=image)


@app.function(volumes={WEIGHTS: weights}, timeout=1800)
def bootstrap_weights() -> str:
    from huggingface_hub import snapshot_download

    base_dir = Path(WEIGHTS) / "base" / MODEL_REVISION
    snapshot_download(MODEL_ID, revision=MODEL_REVISION, local_dir=base_dir)
    weights.commit()
    return str(base_dir)


@app.local_entrypoint()
def main(adapter_dir: str = "/Users/senna/Documents/Repos/jeb-scratch/checkpoints/e2/lr-1e-4/epoch-3-quarter-3") -> None:
    print(bootstrap_weights.remote())
    adapter = Path(adapter_dir)
    with weights.batch_upload() as batch:
        batch.put_file(adapter / "adapter_config.json", f"/adapters/{ADAPTER_ID}/adapter_config.json")
        batch.put_file(adapter / "adapter_model.safetensors", f"/adapters/{ADAPTER_ID}/adapter_model.safetensors")
    print(f"uploaded adapter to /adapters/{ADAPTER_ID}")
