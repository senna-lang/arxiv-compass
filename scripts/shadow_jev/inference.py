"""Qwen3-4B + E2 LoRA の推論専用順位付け。学習用 loader は使わない。"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import torch

LETTERS = "ABCDEFGHIJKLMNOPQRST"


@dataclass
class Branch:
    kind: str
    instructions: str
    options: list[str]


@dataclass
class PackedRequest:
    state: str
    branches: list[Branch]


@dataclass
class BranchSpan:
    start: int
    decision_index: int


@dataclass
class PackedSequence:
    input_ids: list[int]
    state_len: int
    branch_spans: list[BranchSpan]



def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inference_model(base_dir: Path, adapter_dir: Path, expected_adapter_sha256: str | None = None):
    """bf16 / SDPA / eval。gradient checkpointing と trainable adapter は有効にしない。"""
    if expected_adapter_sha256 is not None:
        actual = sha256_file(adapter_dir / "adapter_model.safetensors")
        if actual != expected_adapter_sha256:
            raise RuntimeError("adapter SHA-256 does not match the configured E2 checkpoint")
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(base_dir)
    base = AutoModelForCausalLM.from_pretrained(base_dir, dtype=torch.bfloat16, attn_implementation="sdpa")
    base.config.use_cache = False
    model = PeftModel.from_pretrained(base, adapter_dir, is_trainable=False)
    model.eval()
    return model, tokenizer


def scoring_text(state: str, branch: Branch) -> str:
    answers = "\n".join(f"{LETTERS[index]}. {option}" for index, option in enumerate(branch.options))
    return (
        "Read the record and answer the question. Respond with exactly one listed letter and no other text.\n\n"
        f"Record:\n{state}\n\nQuestion: {branch.instructions}\nAnswers:\n{answers}\n\nAnswer:"
    )


def _chat_ids(tokenizer, state: str, branch: Branch) -> list[int]:
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": scoring_text(state, branch)}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    input_ids = rendered.input_ids if hasattr(rendered, "input_ids") else rendered
    return input_ids[0] if input_ids and isinstance(input_ids[0], list) else input_ids


def _pack(request: PackedRequest, tokenizer) -> PackedSequence:
    prompts = [_chat_ids(tokenizer, request.state, branch) for branch in request.branches]
    state_len = 0
    for tokens in zip(*prompts):
        if len(set(tokens)) != 1:
            break
        state_len += 1
    if state_len == 0 or any(state_len == len(prompt) for prompt in prompts):
        raise ValueError("chat prompts do not have a shared state prefix")
    input_ids = prompts[0][:state_len]
    spans = []
    for prompt in prompts:
        start = len(input_ids)
        input_ids.extend(prompt[state_len:])
        spans.append(BranchSpan(start=start, decision_index=len(input_ids) - 1))
    return PackedSequence(input_ids=input_ids, state_len=state_len, branch_spans=spans)


def _tree_mask(packed: PackedSequence) -> torch.Tensor:
    branch_ids = torch.full((len(packed.input_ids),), -1, dtype=torch.long)
    for index, span in enumerate(packed.branch_spans):
        branch_ids[span.start:span.decision_index + 1] = index
    size = branch_ids.shape[0]
    causal = torch.tril(torch.ones(size, size, dtype=torch.bool))
    state = branch_ids == -1
    same = branch_ids.unsqueeze(1) == branch_ids.unsqueeze(0)
    return causal & (state.unsqueeze(0) | same)


def _position_ids(packed: PackedSequence) -> list[int]:
    positions = list(range(packed.state_len))
    for span in packed.branch_spans:
        length = span.decision_index - span.start + 1
        positions.extend(range(packed.state_len, packed.state_len + length))
    return positions


def _label_ids(tokenizer, count: int, device: torch.device) -> torch.Tensor:
    tokens = [tokenizer.encode(letter, add_special_tokens=False) for letter in LETTERS[:count]]
    if any(len(token) != 1 for token in tokens):
        raise ValueError("answer labels must each be one token")
    return torch.tensor([token[0] for token in tokens], device=device)


@torch.inference_mode()
def _predict(model, tokenizer, state: str, branches: list[Branch], orders: list[list[list[int]]], device) -> list[list[float]]:
    expanded = []
    for index, (branch, branch_orders) in enumerate(zip(branches, orders)):
        for order in branch_orders:
            expanded.append((index, order, Branch(branch.kind, branch.instructions, [branch.options[i] for i in order])))
    packed = _pack(PackedRequest(state, [branch for _, _, branch in expanded]), tokenizer)
    decisions = torch.tensor([span.decision_index for span in packed.branch_spans], device=device)
    output = model(
        input_ids=torch.tensor([packed.input_ids], device=device),
        attention_mask=_tree_mask(packed).to(device)[None, None],
        position_ids=torch.tensor([_position_ids(packed)], device=device),
        logits_to_keep=decisions,
        use_cache=False,
    ).logits[0]
    predictions: list[list[list[float]]] = [[] for _ in branches]
    for logits, (index, order, _) in zip(output, expanded):
        labels = _label_ids(tokenizer, len(order), device)
        ordered = torch.softmax(logits[labels].float(), dim=-1).tolist()
        canonical = [0.0] * len(order)
        for position, original in enumerate(order):
            canonical[original] = ordered[position]
        predictions[index].append(canonical)
    return [[sum(values) / len(values) for values in zip(*per_order)] for per_order in predictions]


@torch.inference_mode()
def rank_papers(model, tokenizer, state: str, papers: list[dict], question: str, options: list[str], batch_size: int, device) -> dict[str, float]:
    """2論文ずつ、Noul の正順・逆順を平均した Yes 確率を返す。"""
    if options != ["No", "Yes"]:
        raise ValueError("shadow predicate options must be No, Yes")
    yes_index = options.index("Yes")
    probabilities = {}
    for offset in range(0, len(papers), batch_size):
        batch = papers[offset:offset + batch_size]
        branches = [
            Branch(
                "noul",
                f"Paper title: {paper['title']}\nAbstract: {paper['abstract']}\n\n{question}",
                options,
            )
            for paper in batch
        ]
        orders = [[[0, 1], [1, 0]] for _ in batch]
        for paper, distribution in zip(batch, _predict(model, tokenizer, state, branches, orders, device)):
            probabilities[paper["id"]] = distribution[yes_index]
    return probabilities
