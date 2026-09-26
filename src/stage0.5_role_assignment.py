import json


# Load Phase 0 results
with open("results/role_assessments.json", "r", encoding="utf-8") as f:
    role_assessments = json.load(f)


all_assignments = []


# Process every question
for question in role_assessments:

    assessments = question["assessments"]

    candidate_scores = {}


    # Try each model as the Judge
    for candidate_judge in assessments:

        judge_id = candidate_judge["model_id"]

        total_score = 0


        # Calculate how good this assignment would be
        for model in assessments:

            model_data = json.loads(model["raw_response"])

            if model["model_id"] == judge_id:

                # This model becomes Judge
                total_score += model_data["confidence_by_role"]["Judge"]

            else:

                # All other models become Solvers
                total_score += model_data["confidence_by_role"]["Solver"]


        # Avoid floating-point precision problems
        candidate_scores[judge_id] = round(total_score, 6)


    # Choose the best Judge
    #
    # Tie-break rules:
    # 1. Highest total score
    # 2. Highest Judge confidence
    # 3. Lowest model number
    selected_judge = max(
        assessments,
        key=lambda model: (
            candidate_scores[model["model_id"]],
            json.loads(model["raw_response"])["confidence_by_role"]["Judge"],
            -int(model["model_id"].split("_")[1])
        )
    )["model_id"]


    # Assign roles
    assignments = {
        model["model_id"]:
            ("Judge" if model["model_id"] == selected_judge else "Solver")
        for model in assessments
    }


    # Save this question's result
    all_assignments.append({
        "question_id": question["question_id"],
        "candidate_scores": candidate_scores,
        "selected_judge": selected_judge,
        "assignments": assignments
    })


# Save all 25 assignments
with open("results/role_assignments.json", "w", encoding="utf-8") as f:
    json.dump(
        all_assignments,
        f,
        indent=4,
        ensure_ascii=False
    )


print("Phase 0.5 completed.")
print(f"Processed {len(all_assignments)} questions.")


# Print a simple summary
for result in all_assignments:

    print(
        f"Q{result['question_id']}: "
        f"Judge = {result['selected_judge']}"
    )