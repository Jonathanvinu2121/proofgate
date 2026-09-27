"""
Vector Store implementation supporting PostgreSQL pgvector and standalone In-Memory fallback.
Computes embeddings via sentence-transformers (all-MiniLM-L6-v2) and performs cosine similarity search.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from src.ingestion.chunker import Chunk

# Model instance holder to avoid repeated reload
_EMBEDDER_MODEL = None


def get_embedder():
    global _EMBEDDER_MODEL
    if _EMBEDDER_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDER_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDER_MODEL


def embed_text(text: str) -> List[float]:
    model = get_embedder()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedder()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


class VectorStore:
    """
    In-memory and PostgreSQL pgvector store manager.
    """

    def __init__(self, use_postgres_if_available: bool = True):
        self.chunks: Dict[str, Chunk] = {}
        self.chunk_ids: List[str] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.postgres_enabled = False

        if use_postgres_if_available:
            from src.db.database import get_db_engine
            _, self.postgres_enabled = get_db_engine()

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts)

        for chunk, emb in zip(chunks, embeddings):
            self.chunks[chunk.chunk_id] = chunk
            if chunk.chunk_id not in self.chunk_ids:
                self.chunk_ids.append(chunk.chunk_id)

        emb_array = np.array(embeddings, dtype=np.float32)
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        norm_emb = emb_array / norms

        if self.embeddings_matrix is None:
            self.embeddings_matrix = norm_emb
        else:
            self.embeddings_matrix = np.vstack([self.embeddings_matrix, norm_emb])

    def similarity_search(
        self, query: str, k: int = 5, include_gaps: bool = True
    ) -> List[Tuple[Chunk, float]]:
        """
        Performs cosine similarity search against stored chunks.
        Returns list of tuples (Chunk, similarity_score).
        """
        if not self.chunk_ids or self.embeddings_matrix is None:
            return []

        query_emb = np.array(embed_text(query), dtype=np.float32)
        q_norm = np.linalg.norm(query_emb)
        if q_norm == 0:
            q_norm = 1e-10
        query_norm = query_emb / q_norm

        # Cosine similarity dot product
        scores = np.dot(self.embeddings_matrix, query_norm)

        # Filter indices based on gap inclusion
        valid_indices = []
        for idx, chunk_id in enumerate(self.chunk_ids):
            chunk = self.chunks[chunk_id]
            if not include_gaps and chunk.is_gap:
                continue
            valid_indices.append(idx)

        if not valid_indices:
            return []

        filtered_scores = scores[valid_indices]
        top_k_sub_indices = np.argsort(filtered_scores)[::-1][:k]

        results = []
        for sub_idx in top_k_sub_indices:
            orig_idx = valid_indices[sub_idx]
            chunk_id = self.chunk_ids[orig_idx]
            score = float(filtered_scores[sub_idx])
            results.append((self.chunks[chunk_id], score))

        return results
