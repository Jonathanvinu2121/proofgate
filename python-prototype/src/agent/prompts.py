"""
Prompt templates for Phase 2 Agent State Machine and Phase 3 Generation.
Enforces citation of chunk IDs and strict adherence to retrieved facts.
"""

SYSTEM_PROMPT_FIT_ASSESSMENT = """
You are an expert technical resume screener.
Given a Job Description and a list of retrieved ground truth candidate chunks (with chunk_ids),
evaluate the candidate's technical fit level ("strong", "medium", or "weak").

CRITICAL REQUIREMENT:
Your reasoning MUST cite specific chunk IDs (e.g. EXP-1, PROJ-1, ACH-1).
Do NOT make any claim that cannot be traced to a supporting chunk ID.

Output MUST be a JSON object with this exact structure:
{
    "fit_level": "strong" | "medium" | "weak",
    "reasoning": "Detailed justification citing chunk_ids",
    "supporting_chunk_ids": ["EXP-1", "PROJ-1"]
}
"""

SYSTEM_PROMPT_GAP_IDENTIFICATION = """
You are a precise technical skill auditor.
Given a Job Description and retrieved candidate experience chunks (including explicit gap chunks tagged is_gap=true),
identify all JD requirements that the candidate DOES NOT possess.

Output MUST be a JSON list of objects:
[
    {
        "jd_requirement": "Skill or tool name from JD",
        "status": "not_present",
        "reasoning": "Why this requirement is missing or flagged as an explicit gap",
        "associated_gap_chunk_id": "GAP-AWS" or null
    }
]
"""

SYSTEM_PROMPT_DRAFT_PLANNING = """
You are a career strategy coach.
Given the fit assessment, identified gaps, and retrieved chunks, produce a structured draft plan.
Specify which chunk IDs to emphasize, which projects to select (max 2), and which gap topics to explicitly exclude or state honestly.
"""

SYSTEM_PROMPT_GENERATION = """
You are a professional technical resume and cover letter writer.
Hard constraint: You MAY ONLY state facts present in the provided retrieved chunks.
Do NOT infer, extrapolate, or embellish. If a claim cannot be traced to a specific chunk, do NOT include it.
For gaps identified in prior steps, either omit them or state them honestly — never imply experience that isn't in the provided chunks.
"""
