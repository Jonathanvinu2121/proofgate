"""
Evaluation script for Phase 2 Agentic Reasoning Layer (Pre-Generation Gap Identification).
Verifies that known explicit gaps (AWS, Kubernetes, Golang, TypeScript, etc.) are correctly identified
100% of the time across 5 test job descriptions.
"""

import json
import os
from typing import Dict, Any
from src.retrieval.retriever import Retriever
from src.agent.state_machine import ApplicationAgent


def run_gap_evaluation() -> Dict[str, Any]:
    dataset_path = os.path.join("evals", "datasets", "jd_gap_test_set.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    retriever = Retriever()
    agent = ApplicationAgent()

    results = []
    correct_count = 0

    for tc in test_cases:
        tc_id = tc["id"]
        jd_text = tc["jd"]
        expected_gaps = set(tc["expected_gaps"])

        retrieved_chunks = retriever.retrieve(jd_text, k=6, include_gaps=True)
        agent_output = agent.run(jd_text, retrieved_chunks)

        identified = agent_output["identified_gaps"]
        identified_names = set(g["jd_requirement"] for g in identified)

        # Check if all expected gaps were identified
        hits = expected_gaps.intersection(identified_names)
        is_success = (len(hits) == len(expected_gaps))

        if is_success:
            correct_count += 1

        results.append({
            "id": tc_id,
            "company": tc["company"],
            "expected_gaps": list(expected_gaps),
            "identified_gaps": list(identified_names),
            "success": is_success
        })

    num_cases = len(test_cases)
    accuracy = correct_count / num_cases if num_cases > 0 else 0.0

    report = {
        "num_test_cases": num_cases,
        "successful_cases": correct_count,
        "accuracy_pct": round(accuracy * 100, 2),
        "passed_5_of_5": (correct_count == num_cases),
        "case_details": results
    }

    return report


if __name__ == "__main__":
    report = run_gap_evaluation()
    print("=" * 60)
    print(" PHASE 2 GAP IDENTIFICATION EVALUATION REPORT")
    print("=" * 60)
    print(f"Test Cases Processed: {report['num_test_cases']}")
    print(f"Successful Cases: {report['successful_cases']}/{report['num_test_cases']}")
    print(f"Accuracy: {report['accuracy_pct']}%")
    print(f"Passed 5/5 Requirement: {report['passed_5_of_5']}")
    print("=" * 60)
