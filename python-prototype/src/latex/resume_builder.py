"""
Phase 5 LaTeX Resume Builder.
Populates Alex's exact working LaTeX resume template dynamically based on approved grounded chunks.
Features:
  - Reorders technical skill lines to surface JD-relevant technologies first.
  - Selects top relevant projects based on Phase 1 similarity retrieval.
  - Inserts verified grounded bullets into \resumeItem{} calls (falling back to original ground truth text if ungrounded).
"""

import os
from typing import List, Dict, Any
from jinja2 import Environment
from src.data.seed_data import CANDIDATE_INFO, GROUND_TRUTH_DATA
from src.ingestion.chunker import Chunk
from src.latex.template import RESUME_LATEX_TEMPLATE
from src.guardrails.grounding_checker import GroundingChecker


class ResumeBuilder:
    def __init__(self):
        self.candidate_info = CANDIDATE_INFO
        self.grounding_checker = GroundingChecker()

    def build_resume_tex(
        self,
        approved_chunks: List[Chunk],
        draft_plan: Dict[str, Any],
        generated_bullets: List[Dict[str, Any]],
        company_name: str = "Company",
        output_dir: str = "./output"
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        approved_chunk_map = {c.chunk_id: c for c in approved_chunks if not c.is_gap}

        # ----------------------------------------------------
        # 1. Technical Skills Reordering
        # ----------------------------------------------------
        priority_skills = draft_plan.get("skills_priority", [])

        line1_skills = ["Node.js", "Express.js", "Python", "FastAPI", "Java", "Spring Boot", "React"]
        line2_skills = ["PostgreSQL", "MongoDB", "Redis", "Docker"]
        line3_skills = ["Git", "GitHub", "Postman", "Selenium", "Jira", "Notion"]

        # Sort skills so JD priority skills appear first
        def reorder_skills(skill_list):
            sorted_list = sorted(
                skill_list,
                key=lambda s: 0 if any(p.lower() in s.lower() for p in priority_skills) else 1
            )
            return ", ".join(sorted_list)

        skills_line_1 = reorder_skills(line1_skills)
        skills_line_2 = reorder_skills(line2_skills)
        skills_line_3 = reorder_skills(line3_skills)

        # ----------------------------------------------------
        # 2. Experience Bullets Assembly
        # ----------------------------------------------------
        # Map generated bullets to experiences
        exp_groups = {}
        for item in GROUND_TRUTH_DATA["experience"]:
            company = item["company"]
            if company not in exp_groups:
                exp_groups[company] = {
                    "company": company,
                    "role": item["role"],
                    "period": item["period"],
                    "location": item["location"],
                    "bullets": []
                }

            # Find matching generated or ground-truth bullet
            matching_gen = [b for b in generated_bullets if b.get("source_chunk_id") == item["id"]]
            bullet_text = item["text"]

            if matching_gen:
                candidate_bullet = matching_gen[0].get("bullet", item["text"])
                # Grounding validation check
                v_res = self.grounding_checker.verify_grounding(
                    [{"bullet": candidate_bullet, "source_chunk_id": item["id"]}], "", approved_chunks
                )
                if v_res["all_grounded"]:
                    bullet_text = candidate_bullet
                else:
                    bullet_text = item["text"]  # Fallback to unmodified ground truth

            # Escape LaTeX special characters
            tex_bullet = self._escape_latex(bullet_text)
            exp_groups[company]["bullets"].append(tex_bullet)

        experience_items = list(exp_groups.values())

        # ----------------------------------------------------
        # 3. Dynamic Project Selection (Top 2 projects)
        # ----------------------------------------------------
        selected_proj_ids = draft_plan.get("selected_project_ids", ["PROJ-1", "PROJ-2"])
        if not selected_proj_ids:
            selected_proj_ids = ["PROJ-1", "PROJ-2"]

        project_items = []
        for p in GROUND_TRUTH_DATA["projects"]:
            if p["id"] in selected_proj_ids or len(project_items) < 2:
                proj_bullets = []
                for b in p.get("bullets", []):
                    proj_bullets.append(self._escape_latex(b))

                project_items.append({
                    "name": p["name"],
                    "tech_stack": ", ".join(p["technologies"]),
                    "period": p["period"],
                    "bullets": proj_bullets
                })

        # ----------------------------------------------------
        # 4. Achievements
        # ----------------------------------------------------
        achievement_items = []
        for ach in GROUND_TRUTH_DATA["achievements"]:
            achievement_items.append({
                "title": self._escape_latex(ach["title"]),
                "text": self._escape_latex(ach["text"])
            })

        # Render Jinja2 Template (custom comment tags to avoid conflict with LaTeX {#1} parameters)
        env = Environment(comment_start_string='/*=', comment_end_string='=*/*')
        template = env.from_string(RESUME_LATEX_TEMPLATE)
        rendered_tex = template.render(
            candidate_name=self.candidate_info["name"],
            phone=self.candidate_info["phone"],
            email=self.candidate_info["email"],
            linkedin=self.candidate_info["linkedin"],
            github=self.candidate_info["github"],
            leetcode=self.candidate_info["leetcode"],
            education_institution=self.candidate_info["institution"],
            education_location=self.candidate_info["location"],
            education_degree=f"{self.candidate_info['degree']} ({self.candidate_info['graduation_status']})",
            education_years=self.candidate_info["graduation_years"],
            skills_line_1=skills_line_1,
            skills_line_2=skills_line_2,
            skills_line_3=skills_line_3,
            experience_items=experience_items,
            project_items=project_items,
            achievement_items=achievement_items
        )

        safe_company = "".join(c for c in company_name if c.isalnum() or c in "_-").lower()
        if not safe_company:
            safe_company = "custom"

        tex_filename = f"resume_{safe_company}.tex"
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
