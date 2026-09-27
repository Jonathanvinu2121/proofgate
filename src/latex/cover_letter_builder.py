"""
Phase 5 LaTeX Cover Letter Builder.
Populates matching LaTeX cover letter template dynamically using grounded text paragraphs.
Enforces grounding checker verification before writing file.
"""

import os
from typing import List, Dict, Any
from jinja2 import Environment
from src.data.seed_data import CANDIDATE_INFO
from src.ingestion.chunker import Chunk
from src.latex.template import COVER_LETTER_LATEX_TEMPLATE
from src.guardrails.grounding_checker import GroundingChecker


class CoverLetterBuilder:
    def __init__(self):
        self.candidate_info = CANDIDATE_INFO
        self.grounding_checker = GroundingChecker()

    def build_cover_letter_tex(
        self,
        approved_chunks: List[Chunk],
        draft_plan: Dict[str, Any],
        cover_letter_paragraph: str,
        company_name: str = "Company",
        output_dir: str = "./output"
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)

        p1 = f"I am writing to express my strong interest in joining {company_name} as a backend/software engineer."
        p2 = cover_letter_paragraph or (
            "In my recent engineering work, I delivered RESTful APIs connecting React frontends with high-throughput backend services (EXP-1) "
            "and optimized slow PostgreSQL queries from ~600ms to under 100ms through targeted indexing (EXP-2). "
            "I also personally designed and deployed a live production real-time kitchen order POS system processing 100+ daily orders (EXP-3)."
        )
        p3 = "I welcome the opportunity to discuss how my hands-on backend and system optimization experience aligns with your team's technical goals."

        full_text = f"{p1} {p2} {p3}"

        # Perform grounding check verification
        v_res = self.grounding_checker.verify_grounding([], full_text, approved_chunks)
        self.grounding_checker.assert_grounded(v_res)

        env = Environment(comment_start_string='/*=', comment_end_string='=*/*')
        template = env.from_string(COVER_LETTER_LATEX_TEMPLATE)
        rendered_tex = template.render(
            candidate_name=self.candidate_info["name"],
            phone=self.candidate_info["phone"],
            email=self.candidate_info["email"],
            linkedin=self.candidate_info["linkedin"],
            github=self.candidate_info["github"],
            company_name=company_name,
            paragraph_1=self._escape_latex(p1),
            paragraph_2=self._escape_latex(p2),
            paragraph_3=self._escape_latex(p3)
        )

        safe_company = "".join(c for c in company_name if c.isalnum() or c in "_-").lower()
        if not safe_company:
            safe_company = "custom"

        tex_filename = f"cover_letter_{safe_company}.tex"
        tex_path = os.path.join(output_dir, tex_filename)

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(rendered_tex)

        return tex_path

    def _escape_latex(self, text: str) -> str:
        replacements = [
            ("&", r"\&"),
            ("%", r"\%"),
            ("$", r"\$"),
            ("#", r"\#"),
            ("_", r"\_"),
            ("~", r"\textasciitilde{}"),
            ("^", r"\textasciicircum{}")
        ]
        res = text
        for old, new in replacements:
            res = res.replace(old, new)
        return res
