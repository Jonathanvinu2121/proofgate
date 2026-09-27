"""
CLI Entrypoint for Grounded Job-Application RAG Agent & LaTeX Compiler.
Command:
    python run_pipeline.py --jd path/to/jd.txt --output-dir ./output

Executes Phases 1-5 in order:
  1. Retrieval (semantic vector search over seed chunks)
  2. Agentic Reasoning (3-step hand-rolled state machine: fit, gaps, draft plan)
  3. Generation (grounded bullet & cover letter creation)
  4. Grounding Check Guardrail (HALTS if any claim is ungrounded)
  5. LaTeX Compilation (renders .tex & compiles 1-page PDF for resume and cover letter)
"""

import sys
import os
import time
import argparse
from typing import Dict, Any

from src.retrieval.retriever import Retriever
from src.agent.state_machine import ApplicationAgent
from src.agent.llm_client import LLMClient
from src.generation.generator import Generator
from src.guardrails.grounding_checker import GroundingChecker, GroundingValidationError
from src.latex.resume_builder import ResumeBuilder
from src.latex.cover_letter_builder import CoverLetterBuilder
from src.latex.compiler import LaTeXCompiler
from src.metrics.telemetry import TelemetryTracker


def run_pipeline(jd_file_path: str, output_dir: str = "./output", company_name: str = "Company") -> Dict[str, Any]:
    telemetry = TelemetryTracker()

    if not os.path.exists(jd_file_path):
        print(f"Error: Job description file not found at '{jd_file_path}'")
        sys.exit(1)

    with open(jd_file_path, "r", encoding="utf-8") as f:
        jd_text = f.read().strip()

    print("=" * 70)
    print(" GROUNDED JOB-APPLICATION RAG AGENT & LATEX COMPILER")
    print("=" * 70)
    print(f"Input JD File: {jd_file_path}")
    print(f"Target Output Directory: {output_dir}")
    print("=" * 70)

    # ----------------------------------------------------
    # Phase 1: Ingestion & Retrieval
    # ----------------------------------------------------
    t0 = time.time()
    retriever = Retriever()
    retrieved_with_scores = retriever.retrieve_with_scores(jd_text, k=6, include_gaps=True)
    retrieved_chunks = [c for c, _ in retrieved_with_scores]
    telemetry.record_phase("1_retrieval", time.time() - t0)

    print("\n[PHASE 1: RETRIEVAL RESULTS]")
    for chunk, score in retrieved_with_scores:
        gap_tag = " [EXPLICIT GAP]" if chunk.is_gap else ""
        print(f"  * [{chunk.chunk_id}] (score: {score:.4f}){gap_tag} - {chunk.source}: {chunk.text[:80]}...")

    # ----------------------------------------------------
    # Phase 2: Agentic Reasoning Layer (Hand-rolled State Machine)
    # ----------------------------------------------------
    t0 = time.time()
    llm_client = LLMClient(provider="mock")
    agent = ApplicationAgent(llm_client=llm_client)
    agent_output = agent.run(jd_text, retrieved_chunks)
    telemetry.record_phase("2_agentic_reasoning", time.time() - t0)

    fit = agent_output["fit_assessment"]
    gaps = agent_output["identified_gaps"]
    draft_plan = agent_output["draft_plan"]

    print("\n[PHASE 2: FIT ASSESSMENT]")
    print(f"  Fit Level: {fit.get('fit_level', 'unknown').upper()}")
    print(f"  Reasoning: {fit.get('reasoning')}")
    print(f"  Supporting Chunk IDs: {', '.join(fit.get('supporting_chunk_ids', []))}")

    print("\n[PHASE 2: PRE-GENERATION GAP IDENTIFICATION]")
    if gaps:
        for g in gaps:
            gap_chunk = f" ({g['associated_gap_chunk_id']})" if g.get("associated_gap_chunk_id") else ""
            print(f"  [GAP] Missing Requirement: {g['jd_requirement']}{gap_chunk}")
            print(f"        Reasoning: {g['reasoning']}")
    else:
        print("  [OK] No missing explicit technical gaps identified for this JD.")

    # ----------------------------------------------------
    # Phase 3: Generation Layer
    # ----------------------------------------------------
    t0 = time.time()
    generator = Generator(llm_client=llm_client)
    generation_output = generator.generate(fit, gaps, draft_plan, retrieved_chunks)
    telemetry.record_phase("3_generation", time.time() - t0)

    resume_bullets = generation_output["resume_bullets"]
    cover_letter_para = generation_output["cover_letter_paragraph"]

    print("\n[PHASE 3: GENERATED PROSE CANDIDATES]")
    print("  Tailored Resume Bullets:")
    for b in resume_bullets:
        print(f"    - [{b.get('source_chunk_id')}] {b.get('bullet')}")
    print("\n  Cover Letter Paragraph:")
    print(f"    \"{cover_letter_para}\"")

    # ----------------------------------------------------
    # Phase 4: Grounding Checker Guardrail
    # ----------------------------------------------------
    t0 = time.time()
    checker = GroundingChecker()
    verification = checker.verify_grounding(resume_bullets, cover_letter_para, retrieved_chunks)
    telemetry.record_phase("4_grounding_guardrail", time.time() - t0)

    print("\n[PHASE 4: GROUNDING CHECK RESULTS]")
    for claim_item in verification["claims"]:
        status_icon = "[PASS]" if claim_item["grounded"] else "[HALT - UNGROUNDED]"
        source = f"(Source: {claim_item['source_chunk_id']})" if claim_item["source_chunk_id"] else "(No Source)"
        print(f"  {status_icon} {source}: {claim_item['claim'][:85]}...")

    # CRITICAL GUARDRAIL HALT CHECK
    if not verification["all_grounded"]:
        print("\n" + "!" * 70)
        print(" GUARDRAIL HALT ACTIVATED: UNGROUNDED CLAIM DETECTED")
        print("!" * 70)
        for fc in verification["failed_claims"]:
            print(f"  [FAIL] Failing Claim: {fc}")
        print("\nPipeline execution halted BEFORE Phase 5 LaTeX generation to prevent hallucination bleed.")
        print("!" * 70)
        sys.exit(1)

    print("  [OK] All claims successfully verified against source chunk IDs!")

    # ----------------------------------------------------
    # Phase 5: LaTeX Resume & Cover Letter Generation
    # ----------------------------------------------------
    t0 = time.time()
    resume_builder = ResumeBuilder()
    cover_builder = CoverLetterBuilder()
    compiler = LaTeXCompiler()

    resume_tex = resume_builder.build_resume_tex(
        retrieved_chunks, draft_plan, resume_bullets, company_name=company_name, output_dir=output_dir
    )
    cover_tex = cover_builder.build_cover_letter_tex(
        retrieved_chunks, draft_plan, cover_letter_para, company_name=company_name, output_dir=output_dir
    )

    resume_compile_res = compiler.compile_pdf(resume_tex, output_dir=output_dir)
    cover_compile_res = compiler.compile_pdf(cover_tex, output_dir=output_dir)
    telemetry.record_phase("5_latex_generation_compile", time.time() - t0)

    print("\n[PHASE 5: LATEX & PDF OUTPUT FILES]")
    print(f"  * Resume TeX:        {resume_tex}")
    if resume_compile_res["compiled"]:
        print(f"  * Resume PDF:        {resume_compile_res['pdf_path']} (Pages: {resume_compile_res['page_count']})")
    else:
        print(f"  * Resume PDF Status: {resume_compile_res['warning']}")

    print(f"  * Cover Letter TeX:  {cover_tex}")
    if cover_compile_res["compiled"]:
        print(f"  * Cover Letter PDF:  {cover_compile_res['pdf_path']} (Pages: {cover_compile_res['page_count']})")
    else:
        print(f"  * Cover Letter PDF Status: {cover_compile_res['warning']}")

    if resume_compile_res.get("overfull_warnings"):
        print("\n  [WARNING] Resume Layout Overfull Warnings:")
        for w in resume_compile_res["overfull_warnings"]:
            print(f"     - {w}")

    # ----------------------------------------------------
    # Telemetry Breakdown
    # ----------------------------------------------------
    t_summary = telemetry.get_summary()
    print("\n[PER-PHASE LATENCY & TELEMETRY BREAKDOWN]")
    for phase_name, lat in t_summary["phase_latencies_seconds"].items():
        print(f"  * {phase_name:<30}: {lat:.4f}s")
    print(f"  * Total Pipeline Execution Time: {t_summary['total_latency_seconds']:.4f}s")
    print(f"  * Estimated Token Cost:        {t_summary['estimated_cost_usd']}")

    print("=" * 70)
    print(" PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return {
        "status": "success",
        "resume_tex": resume_tex,
        "cover_tex": cover_tex,
        "resume_pdf": resume_compile_res.get("pdf_path"),
        "cover_pdf": cover_compile_res.get("pdf_path"),
        "telemetry": t_summary
    }


def main():
    parser = argparse.ArgumentParser(
        description="Grounded Job-Application RAG Agent & LaTeX Resume Compiler CLI"
    )
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--output-dir", default="./output", help="Directory to save generated .tex and .pdf files")
    parser.add_argument("--company", default="Company", help="Company name for file naming and customization")

    args = parser.parse_args()
    run_pipeline(args.jd, output_dir=args.output_dir, company_name=args.company)


if __name__ == "__main__":
    main()
