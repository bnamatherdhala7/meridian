"""
Embed and upload both RAG corpora to Pinecone.
Run once: python scripts/seed_pinecone.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from vigil.config import (
    OPENAI_API_KEY, PINECONE_API_KEY,
    PINECONE_SPL_INDEX, PINECONE_INCIDENT_INDEX,
    PINECONE_ENVIRONMENT
)

EMBED_MODEL = "text-embedding-3-small"
DIMENSION   = 1536

oai = OpenAI(api_key=OPENAI_API_KEY)
pc  = Pinecone(api_key=PINECONE_API_KEY)


def embed(texts: list[str]) -> list[list[float]]:
    resp = oai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [r.embedding for r in resp.data]


def ensure_index(name: str) -> None:
    existing = [i.name for i in pc.list_indexes()]
    if name not in existing:
        print(f"Creating index: {name}")
        pc.create_index(
            name=name,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
        )
    else:
        print(f"Index exists: {name}")


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def upsert_corpus(index_name: str, records: list[dict], text_field: str) -> None:
    ensure_index(index_name)
    idx = pc.Index(index_name)

    texts = [
        r[text_field] + " " + r.get("title", "") + " " + " ".join(r.get("tags", []))
        for r in records
    ]
    print(f"Embedding {len(texts)} documents for {index_name}...")
    vectors = embed(texts)

    upserts = []
    for record, vec in zip(records, vectors):
        upserts.append({
            "id":       record["id"],
            "values":   vec,
            "metadata": {k: v for k, v in record.items() if k != "id"}
        })

    idx.upsert(vectors=upserts)
    print(f"Upserted {len(upserts)} vectors to {index_name}")


if __name__ == "__main__":
    base = Path(__file__).parent.parent / "data"
    spl_records      = load_jsonl(base / "spl_knowledge" / "patterns.jsonl")
    incident_records = load_jsonl(base / "incidents"     / "incidents.jsonl")
    upsert_corpus(PINECONE_SPL_INDEX,      spl_records,      "description")
    upsert_corpus(PINECONE_INCIDENT_INDEX, incident_records, "summary")
    print("\nDone. Both corpora seeded.")
