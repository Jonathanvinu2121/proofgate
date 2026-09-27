"""
Phase 3 Generation Layer.
Produces tailored resume bullets and cover letter paragraph using ONLY approved retrieved chunks.
Enforces system prompt hard constraints prohibiting extrapolation or embellishment.
"""

from typing import List, Dict, Any
from src.ingestion.chunker import Chunk
from src.agent.llm_client import LLMClient


class Generator:
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient(provider="mock")

    def generate(
        self,
        fit_assessment: Dict[str, Any],
        identified_gaps: List[Dict[str, Any]],
        draft_plan: Dict[str, Any],
        approved_chunks: List[Chunk]
    ) -> Dict[str, Any]:
        """
        Generates grounded resume bullets and cover letter prose.
        """
        chunks_dict = [c.to_dict() for c in approved_chunks if not c.is_gap]

        generated_result = self.llm_client.generate_grounded_content(
            draft_plan, chunks_dict
        )

        return {
            "resume_bullets": generated_result.get("resume_bullets", []),
            "cover_letter_paragraph": generated_result.get("cover_letter_paragraph", ""),
            "approved_chunk_ids": [c.chunk_id for c in approved_chunks if not c.is_gap]
        }
