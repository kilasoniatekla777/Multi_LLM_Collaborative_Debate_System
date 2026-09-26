
import json
from pathlib import Path
from statistics import mean


RESULTS_DIR = Path("results")


def load_json(filename):
    with open(RESULTS_DIR / filename, "r") as f:
        return json.load(f)


def summarize(name, latencies):
    if not latencies:
        print(f"\n{name}")
        print("No latency data found.")
        return None

    result = {
        "calls": len(latencies),
        "total_seconds": round(sum(latencies), 2),
        "average_seconds": round(mean(latencies), 2),
        "min_seconds": round(min(latencies), 2),
        "max_seconds": round(max(latencies), 2),
    }

    print(f"\n{name}")
    print("-" * 50)
    print(f"Calls: {result['calls']}")
    print(f"Total: {result['total_seconds']} seconds")
    print(f"Average: {result['average_seconds']} seconds")
    print(f"Minimum: {result['min_seconds']} seconds")
    print(f"Maximum: {result['max_seconds']} seconds")

    return result


# ---------------------------------------------------------
# Load results
# ---------------------------------------------------------

initial = load_json("initial_solutions.json")
reviews = load_json("peer_reviews.json")
refined = load_json("refined_solutions.json")
final_judgments = load_json("final_judgments.json")
baseline = load_json("baseline_results.json")
independent_judge = load_json("independent_judge_results.json")


# ---------------------------------------------------------
# Extract latency
# ---------------------------------------------------------

initial_latencies = [
    solver["latency_seconds"]
    for item in initial
    for solver in item["solutions"]
    if "latency_seconds" in solver
]

review_latencies = [
    review["latency_seconds"]
    for item in reviews
    for review in item["reviews"]
    if "latency_seconds" in review
]

refined_latencies = [
    refinement["latency_seconds"]
    for item in refined
    for refinement in item["refined_solutions"]
    if "latency_seconds" in refinement
]

judge_latencies = [
    item["judge"]["latency_seconds"]
    for item in final_judgments
    if "latency_seconds" in item["judge"]
]

baseline_latencies = [
    item["baseline_solution"]["latency_seconds"]
    for item in baseline
    if "latency_seconds" in item["baseline_solution"]
]

independent_judge_latencies = [
    item["judge"]["latency_seconds"]
    for item in independent_judge
    if "latency_seconds" in item["judge"]
]


# ---------------------------------------------------------
# Print analysis
# ---------------------------------------------------------

print("=" * 60)
print("LATENCY ANALYSIS")
print("=" * 60)

initial_stats = summarize(
    "INITIAL SOLVERS",
    initial_latencies
)

review_stats = summarize(
    "PEER REVIEWS",
    review_latencies
)

refined_stats = summarize(
    "REFINEMENT",
    refined_latencies
)

judge_stats = summarize(
    "FULL-DEBATE JUDGE",
    judge_latencies
)

baseline_stats = summarize(
    "SINGLE-LLM BASELINE",
    baseline_latencies
)

independent_judge_stats = summarize(
    "INDEPENDENT SOLVERS + JUDGE",
    independent_judge_latencies
)


# ---------------------------------------------------------
# Full debate latency per question
# ---------------------------------------------------------

full_debate_totals = []

for q_initial, q_reviews, q_refined, q_judge in zip(
    initial,
    reviews,
    refined,
    final_judgments
):

    total = 0

    # 3 initial solvers
    for solver in q_initial["solutions"]:
        total += solver.get("latency_seconds", 0)

    # 6 peer reviews
    for review in q_reviews["reviews"]:
        total += review.get("latency_seconds", 0)

    # 3 refinements
    for refinement in q_refined["refined_solutions"]:
        total += refinement.get("latency_seconds", 0)

    # Final judge
    total += q_judge["judge"].get("latency_seconds", 0)

    full_debate_totals.append(total)


full_debate_stats = summarize(
    "FULL DEBATE TOTAL PER QUESTION",
    full_debate_totals
)


# ---------------------------------------------------------
# Save results
# ---------------------------------------------------------

latency_results = {
    "initial_solvers": initial_stats,
    "peer_reviews": review_stats,
    "refinement": refined_stats,
    "full_debate_judge": judge_stats,
    "single_llm_baseline": baseline_stats,
    "independent_solvers_judge": independent_judge_stats,
    "full_debate_per_question": full_debate_stats,
}


with open(RESULTS_DIR / "latency_results.json", "w") as f:
    json.dump(latency_results, f, indent=4)


print("\nSaved to results/latency_results.json")