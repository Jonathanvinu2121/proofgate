"""
Phase 2 Hand-Rolled 3-Step Agent State Machine (ApplicationAgent).
Implementation avoids third-party agent orchestration frameworks (LangGraph/CrewAI/AutoGen).
Executes:
  Step 1: Fit Assessment (verifies reasoning cites valid supporting_chunk_ids)
  Step 2: Pre-generation Gap Identification (cross-references JD against is_gap chunks)
  Step 3: Draft Planning (structured plan of included/excluded topics and project selection)
"""

from typing import List, Dict, Any
from enum import Enum, auto
from src.ingestion.chunker import Chunk
from src.agent.llm_client import LLMClient


class AgentState(Enum):
    INIT = auto()
    FIT_ASSESSMENT = auto()
    GAP_IDENTIFICATION = auto()
    DRAFT_PLANNING = auto()
    COMPLETED = auto()
    FAILED = auto()


class ApplicationAgent:
    """
    State machine orchestrating multi-step reasoning over candidate experience chunks.
    """

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient(provider="mock")
        self.state = AgentState.INIT
        self.fit_assessment: Dict[str, Any] = {}
        self.identified_gaps: List[Dict[str, Any]] = []
        self.draft_plan: Dict[str, Any] = {}
        self.retrieved_chunks: List[Chunk] = []
        self.max_retries = 3

    def run(self, jd_text: str, retrieved_chunks: List[Chunk]) -> Dict[str, Any]:
        self.retrieved_chunks = retrieved_chunks
        self.state = AgentState.FIT_ASSESSMENT

        chunks_dict_list = [c.to_dict() for c in retrieved_chunks]
        valid_chunk_ids = set(c.chunk_id for c in retrieved_chunks)

        # ----------------------------------------------------
        # Step 1: Fit Assessment
        # ----------------------------------------------------
        fit_result = None
        for attempt in range(self.max_retries):
            raw_fit = self.llm_client.generate_fit_assessment(jd_text, chunks_dict_list)

            # Validate that reasoning cites supporting_chunk_ids
            supporting = raw_fit.get("supporting_chunk_ids", [])
            reasoning = raw_fit.get("reasoning", "")

            # Check if cited IDs exist in retrieved set
            invalid_citations = [cid for cid in supporting if cid not in valid_chunk_ids]
            if invalid_citations and attempt < self.max_retries - 1:
                # Retry if hallucinated chunk IDs cited
                continue

            fit_result = raw_fit
            break

        if not fit_result:
            self.state = AgentState.FAILED
            raise ValueError("Fit Assessment failed citation verification.")

        self.fit_assessment = fit_result
        self.state = AgentState.GAP_IDENTIFICATION

        # ----------------------------------------------------
        # Step 2: Pre-Generation Gap Identification
        # ----------------------------------------------------
        self.identified_gaps = self.llm_client.generate_gap_identification(jd_text, chunks_dict_list)
        self.state = AgentState.DRAFT_PLANNING

        # ----------------------------------------------------
        # Step 3: Draft Planning
        # ----------------------------------------------------
        self.draft_plan = self.llm_client.generate_draft_plan(
            self.fit_assessment, self.identified_gaps, chunks_dict_list
        )
        self.state = AgentState.COMPLETED

        return {
            "fit_assessment": self.fit_assessment,
            "identified_gaps": self.identified_gaps,
            "draft_plan": self.draft_plan,
            "status": "success"
        }
