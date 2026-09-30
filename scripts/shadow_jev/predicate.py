"""shadow Jev の評価基準を、再現できる identity と共有 state に変換する。"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_predicate(config: dict[str, Any]) -> dict[str, Any]:
    """出力に影響する設定だけを安定した順で返す。SPECTER の地図設定は含めない。"""
    predicate = config["shadow_jev"]["predicate"]
    return {
        "id": predicate["id"],
        "version": predicate["version"],
        "interests": list(config["interest_profile"]),
        "current_project_context": list(predicate["current_project_context"]),
        "preference": predicate["preference"],
        "question": predicate["question"],
        "options": list(predicate["options"]),
        "order_averaging": "noul-canonical-and-reverse",
    }


def context_sha256(config: dict[str, Any]) -> str:
    payload = json.dumps(canonical_predicate(config), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def shared_state(config: dict[str, Any]) -> str:
    predicate = canonical_predicate(config)
    interests = "\n".join(f"- {item}" for item in predicate["interests"])
    project = "\n".join(f"- {item}" for item in predicate["current_project_context"])
    return (
        "User research interests:\n"
        f"{interests}\n\n"
        "Current project:\n"
        f"{project}\n\n"
        "Preference:\n"
        f"{predicate['preference']}\n"
    )
