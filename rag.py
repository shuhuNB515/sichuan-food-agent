import json
import os
import sys

from dish_data import DISH_DB
from llm import embedding_client, EMBEDDING_MODEL

CACHE_FILE = "embeddings_cache.json"
DOCS_DIR = "knowledge/docs"


def build_corpus() -> list[dict]:
    corpus = []
    for name, info in DISH_DB.items():
        text = (
            f"{name}（{info['类别']}）：{info['流派']}。"
            f"风味：{info['风味']}。做法关键：{info['关键']}。"
            f"食材：{'、'.join(info['食材'])}。标签：{'、'.join(info['标签'])}。"
        )
        corpus.append({"标题": name, "来源": f"dishes.json#{name}", "text": text})
    if os.path.isdir(DOCS_DIR):
        for fname in os.listdir(DOCS_DIR):
            if fname.endswith(".md"):
                with open(os.path.join(DOCS_DIR, fname), "r", encoding="utf-8") as f:
                    corpus += _chunk_markdown(f.read(), fname)
    return corpus


def _chunk_markdown(text: str, source: str) -> list[dict]:
    chunks = []
    for section in text.split("## "):
        section = section.strip()
        if not section or len(section) < 15:   # ← 过滤孤块和超短碎片
            continue
        title = section.splitlines()[0].strip()[:20]
        chunks.append({"标题": title, "来源": source, "text": section})
    return chunks


def _load_cache() -> dict:
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    cache = _load_cache()
    result: list = [None] * len(texts)
    missing_idx = [i for i, t in enumerate(texts) if t not in cache]
    if missing_idx:
        missing_texts = [texts[i] for i in missing_idx]
        resp = embedding_client.embeddings.create(model=EMBEDDING_MODEL, input=missing_texts)
        for i, item in zip(missing_idx, resp.data):
            result[i] = item.embedding
            cache[texts[i]] = item.embedding
        _save_cache(cache)
    for i, t in enumerate(texts):
        if result[i] is None:
            result[i] = cache[t]
    return result


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b)


def semantic_search(query: str, top_k: int = 3) -> list[dict]:
    corpus = build_corpus()
    vectors = get_embeddings([c["text"] for c in corpus] + [query])
    q = vectors[-1]
    scored = [
        {
            "标题": c["标题"],
            "来源": c["来源"],
            "相似度": round(cosine(q, vectors[i]), 4),
            "摘要": c["text"][:60],
        }
        for i, c in enumerate(corpus)
    ]
    scored.sort(key=lambda x: x["相似度"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "适合下酒的凉菜"
    print(f"查询：{question}")
    for row in semantic_search(question, top_k=3):
        print(f"  {row['相似度']}  {row['标题']}（{row['来源']}）——{row['摘要']}")
