"""
Phase 1 Retrieval Layer.
Provides high-level retrieval interface over ground truth chunks.
"""

from typing import List, Tuple
from src.ingestion.chunker import SemanticChunker, Chunk
from src.db.vector_store import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore = None):
        if vector_store is None:
            self.vector_store = VectorStore(use_postgres_if_available=False)
            self._ingest_seed_data()
        else:
            self.vector_store = vector_store

    def _ingest_seed_data(self):
        chunker = SemanticChunker()
        chunks = chunker.create_chunks()
        self.vector_store.add_chunks(chunks)

    def retrieve(self, query: str, k: int = 5, include_gaps: bool = True) -> List[Chunk]:
        """
        Retrieves top-k relevant chunks for a query, ensuring baseline summary chunk is present.
        """
        results = self.vector_store.similarity_search(query, k=k, include_gaps=include_gaps)
        chunks = [chunk for chunk, _ in results]

        # Ensure SUMMARY-1 candidate summary chunk is present in chunk list
        if "SUMMARY-1" in self.vector_store.chunks:
            if not any(c.chunk_id == "SUMMARY-1" for c in chunks):
                chunks.append(self.vector_store.chunks["SUMMARY-1"])

        return chunks

    def retrieve_with_scores(self, query: str, k: int = 5, include_gaps: bool = True) -> List[Tuple[Chunk, float]]:
        """
        Retrieves top-k relevant chunks alongside similarity score floats.
        """
        return self.vector_store.similarity_search(query, k=k, include_gaps=include_gaps)
