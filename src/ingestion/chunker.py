"""
Semantic Chunker for Alex Rivera's Ground Truth Experience.
Splits ground truth into atomic semantic chunks with metadata (source, category, technologies, is_gap).
Do NOT use naive fixed-character splitting.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
from src.data.seed_data import GROUND_TRUTH_DATA, CANDIDATE_INFO


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str         # resume_experience | project | achievement | explicit_gap | candidate_summary
    category: str       # technical | behavioral | achievement | gap
    technologies: List[str] = field(default_factory=list)
    is_gap: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "category": self.category,
            "technologies": self.technologies,
            "is_gap": self.is_gap,
            "metadata": self.metadata
        }


class SemanticChunker:
    """
    Parses seed dataset into atomic semantic units:
    - 1 experience bullet = 1 chunk
    - 1 project = 1 chunk (with sub-bullets attached)
    - 1 achievement = 1 chunk
    - 1 explicit gap = 1 chunk (is_gap = True)
    """

    def __init__(self):
        self.candidate_info = CANDIDATE_INFO
        self.ground_truth = GROUND_TRUTH_DATA

    def create_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []

        # 1. Candidate Summary Chunk
        summary_text = (
            f"{self.candidate_info['name']}, {self.candidate_info['degree']} "
            f"({self.candidate_info['institution']}, {self.candidate_info['graduation_years']}, {self.candidate_info['graduation_status']}). "
            f"{self.candidate_info['total_experience']}. Core Stack: {', '.join(self.candidate_info['core_stack'])}."
        )
        chunks.append(
            Chunk(
                chunk_id="SUMMARY-1",
                text=summary_text,
                source="candidate_summary",
                category="technical",
                technologies=self.candidate_info['core_stack'],
                is_gap=False,
                metadata={"title": "Candidate Summary"}
            )
        )

        # 2. Experience Bullets (1 bullet = 1 chunk)
        for item in self.ground_truth["experience"]:
            chunk_text = (
                f"{item['role']} at {item['company']} ({item['period']}, {item['location']}): "
                f"{item['text']}"
            )
            meta = {
                "role": item["role"],
                "company": item["company"],
                "period": item["period"],
                "location": item["location"]
            }
            if "note" in item:
                meta["note"] = item["note"]

            chunks.append(
                Chunk(
                    chunk_id=item["id"],
                    text=chunk_text,
                    source="resume_experience",
                    category=item.get("category", "technical"),
                    technologies=item.get("technologies", []),
                    is_gap=False,
                    metadata=meta
                )
            )

        # 3. Project Chunks (1 project = 1 chunk with sub-bullets attached)
        for proj in self.ground_truth["projects"]:
            bullets_str = " ".join([f"- {b}" for b in proj.get("bullets", [])])
            proj_text = (
                f"Project: {proj['name']} ({', '.join(proj['technologies'])}). "
                f"{proj['summary']} {bullets_str}"
            ).strip()

            chunks.append(
                Chunk(
                    chunk_id=proj["id"],
                    text=proj_text,
                    source="project",
                    category=proj.get("category", "technical"),
                    technologies=proj.get("technologies", []),
                    is_gap=False,
                    metadata={
                        "name": proj["name"],
                        "period": proj.get("period", ""),
                        "bullets": proj.get("bullets", []),
                        "is_portfolio_rebuild": proj.get("is_portfolio_rebuild", False)
                    }
                )
            )

        # 4. Achievement Chunks (1 achievement = 1 chunk)
        for ach in self.ground_truth["achievements"]:
            ach_text = f"Achievement: {ach['title']} - {ach['text']}"
            chunks.append(
                Chunk(
                    chunk_id=ach["id"],
                    text=ach_text,
                    source="achievement",
                    category=ach.get("category", "achievement"),
                    technologies=ach.get("technologies", []),
                    is_gap=False,
                    metadata={"title": ach["title"]}
                )
            )

        # 5. Explicit Gap Chunks (is_gap = True)
        for gap in self.ground_truth["explicit_known_gaps"]:
            gap_text = (
                f"EXPLICIT KNOWN GAP / UNORGANIZED EXPERIENCE: Candidate explicitly does NOT have professional "
                f"or production experience in {gap['name']} ({gap['description']})."
            )
            chunks.append(
                Chunk(
                    chunk_id=gap["id"],
                    text=gap_text,
                    source="explicit_gap",
                    category="gap",
                    technologies=[gap["name"]],
                    is_gap=True,
                    metadata={"gap_name": gap["name"], "gap_description": gap["description"]}
                )
            )

        return chunks
