from flask import Flask, request, jsonify
import re

app = Flask(__name__)


def _split_tags(tags: str):
    if not tags:
        return set()
    arr = re.split(r"[,\s，]+", str(tags))
    return {t.strip() for t in arr if t and t.strip()}


def _tokenize(text: str):
    if not text:
        return set()
    s = str(text).lower()
    # 兼容中文：这里简单按非字母数字分割 + 中文字符保留
    parts = re.split(r"[^0-9a-zA-Z\u4e00-\u9fff]+", s)
    return {p.strip() for p in parts if p and p.strip()}


def _features(photo: dict):
    # 按需求：描述不作为推荐指标
    tags = _split_tags(photo.get("tags"))
    title = _tokenize(photo.get("title"))
    return tags, title


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


@app.post("/recommend")
def recommend():
    """
    期望输入：
    {
      "topK": 6,
      "target": {"id": 1, "title": "...", "description":"...", "tags":"游戏,数码"},
      "candidates": [
        {"id": 2, "title": "...", "description":"...", "tags":"..."},
        ...
      ]
    }
    返回：
    {"ids":[2,5,9]}
    """
    data = request.get_json(silent=True) or {}
    topk = int(data.get("topK") or 6)
    target = data.get("target") or {}
    candidates = data.get("candidates") or []

    target_id = target.get("id")
    t_tags, t_title = _features(target)

    scored = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        cid = c.get("id")
        if cid is None or cid == target_id:
            continue
        c_tags, c_title = _features(c)
        # 更稳的指标：标签优先，其次标题
        tag_sim = _jaccard(t_tags, c_tags)
        title_sim = _jaccard(t_title, c_title)
        inter_tags = len(t_tags & c_tags)

        if tag_sim > 0:
            bonus = 0.12 * min(inter_tags, 2) / 2.0  # 有共同标签会明显靠前
            s = 0.88 * tag_sim + 0.12 * title_sim + bonus
        else:
            # 没有共同标签时，只靠标题（且降低权重避免乱推荐）
            s = 0.45 * title_sim
        scored.append((s, cid))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    ids = [cid for _, cid in scored[: max(0, topk)]]
    return jsonify({"ids": ids})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

