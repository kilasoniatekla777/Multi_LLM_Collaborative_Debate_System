import json
from pathlib import Path

import matplotlib.pyplot as plt


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = BASE_DIR / "analysis" / "plots"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Load evaluation results
# --------------------------------------------------

with open(RESULTS_DIR / "evaluation_results.json", "r") as f:
    results = json.load(f)


# --------------------------------------------------
# Extract metrics
# --------------------------------------------------

single_llm_accuracy = results["single_llm"]["accuracy"]
majority_vote_accuracy = results["majority_vote"]["accuracy"]
full_debate_accuracy = results["full_debate"]["judge_accuracy"]

initial_solver_accuracy = results["solver_performance"]["initial_accuracy"]
refined_solver_accuracy = results["solver_performance"]["refined_accuracy"]

improvement_rate = results["improvement"]["improvement_rate"]

total_questions = results["total_questions"]

consensus_rate = (
    results["consensus"]["consensus_questions"]
    / total_questions
)


# --------------------------------------------------
# Calculate degradation
# --------------------------------------------------

with open(RESULTS_DIR / "initial_solutions.json", "r") as f:
    initial_solutions = json.load(f)

with open(RESULTS_DIR / "refined_solutions.json", "r") as f:
    refined_solutions = json.load(f)

with open(BASE_DIR / "data" / "questions.json", "r") as f:
    questions = json.load(f)


ground_truth = {
    str(q["id"]): str(q["correct_answer"]).strip().lower()
    for q in questions
}

initial_correct_to_wrong = 0
initial_correct = 0

for initial_q, refined_q in zip(initial_solutions, refined_solutions):

    question_id = str(initial_q["question_id"])
    correct_answer = ground_truth[question_id]

    initial_by_model = {
        solution["model_id"]: str(solution["final_answer"]).strip().lower()
        for solution in initial_q["solutions"]
        if "final_answer" in solution
    }

    refined_by_model = {
        solution["model_id"]: str(solution["refined_final_answer"]).strip().lower()
        for solution in refined_q["refined_solutions"]
        if "refined_final_answer" in solution
    }

    for model_id in initial_by_model:

        if model_id not in refined_by_model:
            continue

        initial_answer = initial_by_model[model_id]
        refined_answer = refined_by_model[model_id]

        if initial_answer == correct_answer:
            initial_correct += 1

            if refined_answer != correct_answer:
                initial_correct_to_wrong += 1


degradation_rate = (
    initial_correct_to_wrong / initial_correct
    if initial_correct > 0
    else 0
)


# --------------------------------------------------
# Print summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("DEBATE SYSTEM ANALYSIS")
print("=" * 60)

print(f"Single LLM Accuracy:       {single_llm_accuracy:.2%}")
print(f"Majority Vote Accuracy:    {majority_vote_accuracy:.2%}")
print(f"Full Debate Accuracy:      {full_debate_accuracy:.2%}")

print()

print(f"Initial Solver Accuracy:    {initial_solver_accuracy:.2%}")
print(f"Refined Solver Accuracy:    {refined_solver_accuracy:.2%}")

print()

print(f"Improvement Rate:           {improvement_rate:.2%}")
print(f"Degradation Rate:           {degradation_rate:.2%}")
print(f"Consensus Rate:             {consensus_rate:.2%}")

print("=" * 60)


# --------------------------------------------------
# Plot 1: Accuracy comparison
# --------------------------------------------------

models = [
    "Single LLM",
    "Majority Vote",
    "Full Debate"
]

accuracies = [
    single_llm_accuracy,
    majority_vote_accuracy,
    full_debate_accuracy
]

plt.figure(figsize=(8, 5))

plt.bar(models, accuracies)

plt.ylabel("Accuracy")
plt.title("Accuracy Comparison")

plt.ylim(0, 1)

for i, value in enumerate(accuracies):
    plt.text(
        i,
        value + 0.02,
        f"{value:.1%}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "accuracy_comparison.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Plot 2: Initial vs Refined Solver
# --------------------------------------------------

solver_stages = [
    "Initial Solver",
    "Refined Solver"
]

solver_accuracies = [
    initial_solver_accuracy,
    refined_solver_accuracy
]

plt.figure(figsize=(7, 5))

plt.bar(solver_stages, solver_accuracies)

plt.ylabel("Accuracy")
plt.title("Initial vs Refined Solver Accuracy")

plt.ylim(0, 1)

for i, value in enumerate(solver_accuracies):
    plt.text(
        i,
        value + 0.02,
        f"{value:.1%}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "solver_refinement.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Plot 3: Improvement vs Degradation
# --------------------------------------------------

change_types = [
    "Improved\nWrong → Correct",
    "Degraded\nCorrect → Wrong"
]

change_rates = [
    improvement_rate,
    degradation_rate
]

plt.figure(figsize=(8, 5))

plt.bar(change_types, change_rates)

plt.ylabel("Rate")
plt.title("Effect of Refinement")

plt.ylim(0, max(0.1, degradation_rate + 0.05))

for i, value in enumerate(change_rates):
    plt.text(
        i,
        value + 0.005,
        f"{value:.1%}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "improvement_vs_degradation.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Plot 4: Consensus Rate
# --------------------------------------------------

consensus_values = [
    consensus_rate,
    1 - consensus_rate
]

labels = [
    "Consensus",
    "No Consensus"
]

plt.figure(figsize=(7, 5))

plt.bar(labels, consensus_values)

plt.ylabel("Proportion of Questions")
plt.title("Solver Consensus Rate")

plt.ylim(0, 1)

for i, value in enumerate(consensus_values):
    plt.text(
        i,
        value + 0.02,
        f"{value:.1%}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "consensus_rate.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Finished
# --------------------------------------------------

print("\nPlots generated successfully!")

print(f"Saved to: {PLOTS_DIR}")
print()
print("Files:")

for file in sorted(PLOTS_DIR.glob("*.png")):
    print(f"  - {file.name}")
    