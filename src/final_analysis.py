import json
import os


# =============================================================
# 1. LOAD RESULTS
# =============================================================

with open(
    "results/evaluation_results.json",
    "r",
    encoding="utf-8"
) as f:
    evaluation = json.load(f)


with open(
    "results/latency_results.json",
    "r",
    encoding="utf-8"
) as f:
    latency = json.load(f)


with open(
    "results/cost_results.json",
    "r",
    encoding="utf-8"
) as f:
    cost = json.load(f)


# =============================================================
# 2. BUILD FINAL COMPARISON
# =============================================================

systems = {
    "single_llm": {
        "name": "Single LLM",
        "accuracy_percent": 48.0,
        "correct": 12,
        "questions": 25,

        "total_tokens": cost["systems"]["single_llm"]["total_tokens"],
        "input_tokens": cost["systems"]["single_llm"]["input_tokens"],
        "output_tokens": cost["systems"]["single_llm"]["output_tokens"],

        "estimated_cost_usd":
            cost["systems"]["single_llm"]["estimated_total_cost_usd"],

        "latency_seconds_per_question":
            latency["single_llm_baseline"]["average_seconds"]
    },

    "independent_solvers_judge": {
        "name": "Independent Solvers + Judge",
        "accuracy_percent": 52.0,
        "correct": 13,
        "questions": 25,

        "total_tokens":
            cost["systems"]["independent_solvers_judge"]["total_tokens"],

        "input_tokens":
            cost["systems"]["independent_solvers_judge"]["input_tokens"],

        "output_tokens":
            cost["systems"]["independent_solvers_judge"]["output_tokens"],

        "estimated_cost_usd":
            cost["systems"]["independent_solvers_judge"]["estimated_total_cost_usd"],

        "latency_seconds_per_question": 13.8
    },

    "full_debate": {
        "name": "Full Debate",
        "accuracy_percent": 44.0,
        "correct": 11,
        "questions": 25,

        "total_tokens":
            cost["systems"]["full_debate"]["total_tokens"],

        "input_tokens":
            cost["systems"]["full_debate"]["input_tokens"],

        "output_tokens":
            cost["systems"]["full_debate"]["output_tokens"],

        "estimated_cost_usd":
            cost["systems"]["full_debate"]["estimated_total_cost_usd"],

        "latency_seconds_per_question":
            latency["full_debate_per_question"]["average_seconds"]
    }
}


# =============================================================
# 3. ADD REFINEMENT RESULTS
# =============================================================

refinement_analysis = {
    "initial_solver_accuracy_percent": 45.33,
    "initial_solver_correct": 34,
    "initial_solver_total": 75,

    "refined_solver_accuracy_percent": 44.0,
    "refined_solver_correct": 33,
    "refined_solver_total": 75,

    "improvement_rate_percent": 2.44,
    "improvements": 1,

    "damage_rate_percent": 5.88,
    "damaged_answers": 2
}


# =============================================================
# 4. ADD PEER REVIEW RESULTS
# =============================================================

peer_review_analysis = {
    "error_detection_rate_percent": 32.93,
    "genuine_errors_detected": 27,
    "genuine_errors": 82,

    "false_criticism_rate_percent": 11.76,
    "false_criticisms": 8,
    "reviews_of_correct_solutions": 68,

    "correct_assessments": 115,
    "incorrect_assessments": 21,
    "partially_correct_assessments": 14
}


# =============================================================
# 5. ADD CONSENSUS RESULTS
# =============================================================

consensus_analysis = {
    "consensus_rate_percent": 40.0,
    "consensus_questions": 10,
    "total_questions": 25,

    "consensus_accuracy_percent": 90.0,
    "correct_consensus": 9
}


# =============================================================
# 6. BUILD FINAL RESULT
# =============================================================

final_results = {
    "experiment": {
        "benchmark_size": 25,
        "model": "gpt-4o-mini",
        "architecture": "3 Solvers + Peer Review + Refinement + Judge"
    },

    "system_comparison": systems,

    "refinement_analysis": refinement_analysis,

    "peer_review_analysis": peer_review_analysis,

    "consensus_analysis": consensus_analysis
}


# =============================================================
# 7. SAVE FINAL RESULTS
# =============================================================

with open(
    "results/final_experiment_results.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# =============================================================
# 8. PRINT FINAL TABLE
# =============================================================

print()
print("=" * 80)
print("FINAL EXPERIMENT RESULTS")
print("=" * 80)

print()

print(
    f"{'System':<30}"
    f"{'Accuracy':<12}"
    f"{'Tokens':<15}"
    f"{'Latency':<15}"
    f"{'Cost':<12}"
)

print("-" * 80)


for system in systems.values():

    print(
        f"{system['name']:<30}"
        f"{system['accuracy_percent']:<12.2f}"
        f"{system['total_tokens']:<15}"
        f"{system['latency_seconds_per_question']:<15.2f}"
        f"${system['estimated_cost_usd']:<11.5f}"
    )


print()
print("=" * 80)
print("REFINEMENT")
print("=" * 80)

print(
    f"Initial accuracy: "
    f"{refinement_analysis['initial_solver_accuracy_percent']}%"
)

print(
    f"Refined accuracy: "
    f"{refinement_analysis['refined_solver_accuracy_percent']}%"
)

print(
    f"Improvement rate: "
    f"{refinement_analysis['improvement_rate_percent']}%"
)

print(
    f"Damage rate: "
    f"{refinement_analysis['damage_rate_percent']}%"
)


print()
print("=" * 80)
print("PEER REVIEW")
print("=" * 80)

print(
    f"Error detection rate: "
    f"{peer_review_analysis['error_detection_rate_percent']}%"
)

print(
    f"False criticism rate: "
    f"{peer_review_analysis['false_criticism_rate_percent']}%"
)


print()
print("=" * 80)
print("CONSENSUS")
print("=" * 80)

print(
    f"Consensus rate: "
    f"{consensus_analysis['consensus_rate_percent']}%"
)

print(
    f"Consensus accuracy: "
    f"{consensus_analysis['consensus_accuracy_percent']}%"
)


print()
print(
    "Saved to results/final_experiment_results.json"
)