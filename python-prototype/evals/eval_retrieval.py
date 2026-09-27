"""
Evaluation script for Phase 1 Retrieval Layer.
Calculates recall@3 and recall@5 against labeled test set of 15 job descriptions.
Target success criterion: recall@3 and recall@5 >= 70%.
"""

import json
import os
from typing import Dict, Any
from src.retrieval.retriever import Retriever


def run_retrieval_evaluation() -> Dict[str, Any]:
    dataset_path = os.path.join("evals", "datasets", "retrieval_test_set.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    retriever = Retriever()

    results = []
    total_recall_3 = 0.0
    total_recall_5 = 0.0

    for tc in test_cases:
        tc_id = tc["id"]
        query = tc["query"]
        expected_ids = set(tc["expected_chunk_ids"])

        # Retrieve top-3 and top-5
        retrieved_3 = retriever.retrieve(query, k=3, include_gaps=True)
        retrieved_5 = retriever.retrieve(query, k=5, include_gaps=True)

        r3_ids = set(c.chunk_id for c in retrieved_3)
        r5_ids = set(c.chunk_id for c in retrieved_5)

        hits_3 = expected_ids.intersection(r3_ids)
        hits_5 = expected_ids.intersection(r5_ids)

        recall_3 = len(hits_3) / len(expected_ids) if expected_ids else 1.0
        recall_5 = len(hits_5) / len(expected_ids) if expected_ids else 1.0

        total_recall_3 += recall_3
        total_recall_5 += recall_5

        results.append({
            "id": tc_id,
            "query": query,
            "expected_chunk_ids": list(expected_ids),
            "retrieved_k3": list(r3_ids),
            "retrieved_k5": list(r5_ids),
            "recall_at_3": round(recall_3, 4),
            "recall_at_5": round(recall_5, 4)
        })

    num_cases = len(test_cases)
    mean_recall_3 = total_recall_3 / num_cases if num_cases > 0 else 0.0
    mean_recall_5 = total_recall_5 / num_cases if num_cases > 0 else 0.0

    report = {
        "num_test_cases": num_cases,
        "mean_recall_at_3": round(mean_recall_3, 4),
        "mean_recall_at_5": round(mean_recall_5, 4),
        "passed_threshold": (mean_recall_3 >= 0.70 and mean_recall_5 >= 0.70),
        "case_details": results
    }

    return report


if __name__ == "__main__":
    report = run_retrieval_evaluation()
    print("=" * 60)
    print(" PHASE 1 RETRIEVAL EVALUATION REPORT")
    print("=" * 60)
    print(f"Test Cases Processed: {report['num_test_cases']}")
    print(f"Mean Recall@3: {report['mean_recall_at_3'] * 100:.2f}%")
    print(f"Mean Recall@5: {report['mean_recall_at_5'] * 100:.2f}%")
    print(f"Passed Criteria (>= 70%): {report['passed_threshold']}")
    print("=" * 60)
