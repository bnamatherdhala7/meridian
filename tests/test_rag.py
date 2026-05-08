"""Integration tests for RAG corpus loading — validates JSONL format only (no Pinecone needed)."""
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def test_spl_corpus_count():
    path = Path(__file__).parent.parent / "data" / "spl_knowledge" / "patterns.jsonl"
    records = load_jsonl(path)
    assert len(records) == 20


def test_spl_corpus_fields():
    path = Path(__file__).parent.parent / "data" / "spl_knowledge" / "patterns.jsonl"
    records = load_jsonl(path)
    for r in records:
        assert "id" in r
        assert "spl" in r
        assert "phase" in r
        assert r["phase"] in ("TRIAGE", "INVESTIGATING", "HYPOTHESIZING")


def test_incident_corpus_count():
    path = Path(__file__).parent.parent / "data" / "incidents" / "incidents.jsonl"
    records = load_jsonl(path)
    assert len(records) == 30


def test_incident_corpus_fields():
    path = Path(__file__).parent.parent / "data" / "incidents" / "incidents.jsonl"
    records = load_jsonl(path)
    for r in records:
        assert "id" in r
        assert "summary" in r
        assert "outcome" in r
        assert r["outcome"] in ("REMEDIATING", "ESCALATING")
