import json
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD RESULTS
# ============================================================

with open(
    "results/final_experiment_results.json",
    "r",
    encoding="utf-8"
) as f:
    results = json.load(f)


systems = results["system_comparison"]

output_dir = Path("analysis/plots")
output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. ACCURACY COMPARISON
# ============================================================

names = [
    "Single LLM",
    "Independent\nSolvers + Judge",
    "Full Debate"
]

accuracy = [
    systems["single_llm"]["accuracy_percent"],
    systems["independent_solvers_judge"]["accuracy_percent"],
    systems["full_debate"]["accuracy_percent"]
]

plt.figure(figsize=(8, 5))

plt.bar(
    names,
    accuracy
)

plt.ylabel("Accuracy (%)")
plt.title("Accuracy Comparison")
plt.ylim(0, 100)

for i, value in enumerate(accuracy):
    plt.text(
        i,
        value + 2,
        f"{value:.0f}%",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "accuracy_comparison.png",
    dpi=300
)

plt.close()


# ============================================================
# 3. REFINEMENT IMPROVEMENT / DAMAGE
# ============================================================

refinement = results["refinement_analysis"]

labels = [
    "Improvement",
    "Damage"
]

values = [
    refinement["improvement_rate_percent"],
    refinement["damage_rate_percent"]
]

plt.figure(figsize=(7, 5))

plt.bar(
    labels,
    values
)

plt.ylabel("Rate (%)")
plt.title("Refinement Improvement vs Damage")

for i, value in enumerate(values):
    plt.text(
        i,
        value + 0.2,
        f"{value:.2f}%",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "refinement_improvement.png",
    dpi=300
)

plt.close()


# ============================================================
# 4. CONSENSUS ACCURACY
# ============================================================

consensus = results["consensus_analysis"]

labels = [
    "Consensus",
    "Non-consensus"
]

values = [
    consensus["consensus_accuracy_percent"],
    100 - consensus["consensus_accuracy_percent"]
]

plt.figure(figsize=(7, 5))

plt.bar(
    labels,
    values
)

plt.ylabel("Percentage (%)")
plt.title("Consensus Accuracy")

plt.ylim(0, 100)

for i, value in enumerate(values):
    plt.text(
        i,
        value + 2,
        f"{value:.0f}%",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "consensus_accuracy.png",
    dpi=300
)

plt.close()


# ============================================================
# 5. JUDGE ACCURACY
# ============================================================

judge_accuracy = [
    systems["independent_solvers_judge"]["accuracy_percent"],
    systems["full_debate"]["accuracy_percent"]
]

judge_names = [
    "Independent\nJudge",
    "Full Debate\nJudge"
]

plt.figure(figsize=(7, 5))

plt.bar(
    judge_names,
    judge_accuracy
)

plt.ylabel("Accuracy (%)")
plt.title("Judge Accuracy")

plt.ylim(0, 100)

for i, value in enumerate(judge_accuracy):
    plt.text(
        i,
        value + 2,
        f"{value:.0f}%",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "judge_accuracy.png",
    dpi=300
)

plt.close()


# ============================================================
# 6. COST AND LATENCY COMPARISON
# ============================================================

costs = [
    systems["single_llm"]["estimated_cost_usd"],
    systems["independent_solvers_judge"]["estimated_cost_usd"],
    systems["full_debate"]["estimated_cost_usd"]
]

latencies = [
    systems["single_llm"]["latency_seconds_per_question"],
    systems["independent_solvers_judge"]["latency_seconds_per_question"],
    systems["full_debate"]["latency_seconds_per_question"]
]


# Cost plot

plt.figure(figsize=(8, 5))

plt.bar(
    names,
    costs
)

plt.ylabel("Estimated Cost (USD)")
plt.title("Estimated Cost per 25-Question Experiment")

for i, value in enumerate(costs):
    plt.text(
        i,
        value + 0.002,
        f"${value:.5f}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "cost_comparison.png",
    dpi=300
)

plt.close()


# Latency plot

plt.figure(figsize=(8, 5))

plt.bar(
    names,
    latencies
)

plt.ylabel("Average Latency per Question (seconds)")
plt.title("Latency Comparison")

for i, value in enumerate(latencies):
    plt.text(
        i,
        value + 1,
        f"{value:.2f}s",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    output_dir / "latency_comparison.png",
    dpi=300
)

plt.close()


# ============================================================
# 7. COMPLETION MESSAGE
# ============================================================

print()
print("=" * 60)
print("PLOTS CREATED")
print("=" * 60)

print(
    f"Saved plots to: {output_dir}"
)

print()

for file in sorted(output_dir.iterdir()):
    print(file.name)