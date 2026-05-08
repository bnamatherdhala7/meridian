"""
Two RAG layers:
  - SPLKnowledgeRAG  : retrieves SPL patterns before query execution
  - IncidentMemoryRAG: retrieves past incidents during investigation
"""
from dataclasses import dataclass
from openai import OpenAI
from pinecone import Pinecone
from vigil.config import (
    OPENAI_API_KEY, PINECONE_API_KEY,
    PINECONE_SPL_INDEX, PINECONE_INCIDENT_INDEX
)

EMBED_MODEL = "text-embedding-3-small"


@dataclass
class RAGHit:
    id:       str
    score:    float
    title:    str
    text:     str
    metadata: dict


class _BaseRAG:
    def __init__(self, index_name: str):
        self._oai = OpenAI(api_key=OPENAI_API_KEY)
        self._pc  = Pinecone(api_key=PINECONE_API_KEY)
        self._idx = self._pc.Index(index_name)

    def _embed(self, text: str) -> list[float]:
        resp = self._oai.embeddings.create(model=EMBED_MODEL, input=[text])
        return resp.data[0].embedding

    def query(self, text: str, top_k: int = 3, filter: dict = None) -> list[RAGHit]:
        vec = self._embed(text)
        kwargs: dict = {"vector": vec, "top_k": top_k, "include_metadata": True}
        if filter:
            kwargs["filter"] = filter
        results = self._idx.query(**kwargs)
        hits = []
        for m in results.matches:
            md = m.metadata or {}
            hits.append(RAGHit(
                id       = m.id,
                score    = round(m.score, 3),
                title    = md.get("title", m.id),
                text     = md.get("spl") or md.get("summary") or md.get("description", ""),
                metadata = md
            ))
        return hits


class SPLKnowledgeRAG(_BaseRAG):
    """Retrieve SPL patterns relevant to an alert. Feeds TRIAGE state."""
    def __init__(self):
        super().__init__(PINECONE_SPL_INDEX)

    def get_patterns(self, alert_text: str, phase: str = None, top_k: int = 3) -> list[RAGHit]:
        f = {"phase": phase} if phase else None
        return self.query(alert_text, top_k=top_k, filter=f)


class IncidentMemoryRAG(_BaseRAG):
    """Retrieve past incidents similar to current alert. Feeds HYPOTHESIZING state."""
    def __init__(self):
        super().__init__(PINECONE_INCIDENT_INDEX)

    def get_similar_incidents(self, alert_text: str, top_k: int = 3) -> list[RAGHit]:
        return self.query(alert_text, top_k=top_k)
