"""
Evaluation script for Phase 4 Grounding Checker & Regression Test Suite.
Executes 15 regression & adversarial test cases, verifying:
1. No ungrounded claims pass the grounding checker.
2. Artificial hallucination injections trigger GroundingValidationError (guardrail halt).
3. Adversarial skill requests (Golang, AWS, Stripe) are correctly identified as gaps and NOT claimed in output.
"""

import json
import os
from typing import Dict, Any
from src.retrieval.retriever import Retriever
from src.agent.state_machine import ApplicationAgent
from src.generation.generator import Generator
from src.guardrails.grounding_checker import GroundingChecker, GroundingValidationError


def run_grounding_evaluation() -> Dict[str, Any]:
    dataset_path = os.path.join("evals", "datasets", "regression_test_suite.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    retriever = Retriever()
    agent = ApplicationAgent()
    generator = Generator()
    checker = GroundingChecker()

    results = []
    passed_count = 0

    for tc in test_cases:
        tc_id = tc["id"]
        jd_text = tc["jd"]
        should_halt = tc.get("should_halt_guardrail", False)

        retrieved_chunks = retriever.retrieve(jd_text, k=5, include_gaps=True)
        agent_out = agent.run(jd_text, retrieved_chunks)

        gen_out = generator.generate(
            agent_out["fit_assessment"],
            agent_out["identified_gaps"],
            agent_out["draft_plan"],
            retrieved_chunks
        )

        bullets = gen_out["resume_bullets"]
        cover_letter = gen_out["cover_letter_paragraph"]

        # If test specifies artificial hallucination injection, inject it
        if "test_hallucination_injection" in tc:
            bullets.append({
                "bullet": tc["test_hallucination_injection"],
                "source_chunk_id": None
            })

        verification = checker.verify_grounding(bullets, cover_letter, retrieved_chunks)

        case_passed = False
        halt_triggered = False

        try:
            checker.assert_grounded(verification)
            if not should_halt:
                case_passed = True
        except GroundingValidationError as e:
            halt_triggered = True
            if should_halt:
                case_passed = True

        # Check must_flag_gap requirement if present
        if "must_flag_gap" in tc:
            gap_names = [g["jd_requirement"] for g in agent_out["identified_gaps"]]
            if tc["must_flag_gap"] not in gap_names:
                case_passed = False

        if case_passed:
            passed_count += 1
        else:
            print(f"[FAIL] {tc_id} ({tc['description']}): should_halt={should_halt}, halt_triggered={halt_triggered}, all_grounded={verification['all_grounded']}")
            print(f"       Failed claims: {verification['failed_claims']}")

        results.append({
            "id": tc_id,
            "description": tc["description"],
            "should_halt_guardrail": should_halt,
            "halt_triggered": halt_triggered,
            "all_grounded": verification["all_grounded"],
            "case_passed": case_passed
        })

    num_cases = len(test_cases)
    pass_rate = (passed_count / num_cases) * 100 if num_cases > 0 else 0.0

    return {
        "num_test_cases": num_cases,
        "passed_cases": passed_count,
        "pass_rate_pct": round(pass_rate, 2),
        "passed_suite": (passed_count == num_cases),
        "case_details": results
    }


if __name__ == "__main__":
    report = run_grounding_evaluation()
    print("=" * 60)
    print(" PHASE 4 GROUNDING & REGRESSION EVALUATION REPORT")
    print("=" * 60)
    print(f"Test Cases Processed: {report['num_test_cases']}")
    print(f"Passed Cases: {report['passed_cases']}/{report['num_test_cases']}")
    print(f"Pass Rate: {report['pass_rate_pct']}%")
    print(f"Suite Success: {report['passed_suite']}")
    print("=" * 60)
