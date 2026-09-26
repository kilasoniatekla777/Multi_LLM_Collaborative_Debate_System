import json


# =============================================================
# LOAD DATA
# =============================================================

with open("data/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

with open("results/initial_solutions.json", "r", encoding="utf-8") as f:
    initial_solutions = json.load(f)

with open("results/refined_solutions.json", "r", encoding="utf-8") as f:
    refined_solutions = json.load(f)

with open("results/final_judgments.json", "r", encoding="utf-8") as f:
    final_judgments = json.load(f)

with open("results/baseline_results.json", "r", encoding="utf-8") as f:
    baseline_results = json.load(f)

with open("results/majority_vote_results.json", "r", encoding="utf-8") as f:
    majority_results = json.load(f)

with open("results/independent_judge_results.json", "r", encoding="utf-8") as f:
    independent_judge_results = json.load(f)

with open("results/peer_reviews.json", "r", encoding="utf-8") as f:
    peer_reviews = json.load(f)


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def normalize_answer(answer):
    """
    Normalize an answer so simple formatting differences
    do not affect comparison.
    """

    if answer is None:
        return None

    return str(answer).strip().lower()


def is_correct(answer, correct_answer):
    """
    Check whether an answer matches the ground-truth answer.
    """

    return (
        normalize_answer(answer)
        == normalize_answer(correct_answer)
    )


# =============================================================
# 1. SINGLE-LLM ACCURACY
# =============================================================

single_llm_correct = 0

for result in baseline_results:

    predicted = result["baseline_solution"]["final_answer"]
    correct = result["correct_answer"]

    if is_correct(predicted, correct):
        single_llm_correct += 1


total_questions = len(questions)

single_llm_accuracy = (
    single_llm_correct / total_questions
)


# =============================================================
# 2. MAJORITY VOTE ACCURACY
# =============================================================

majority_correct = 0

for result in majority_results:

    if result["is_correct"]:
        majority_correct += 1


majority_accuracy = (
    majority_correct / total_questions
)


# =============================================================
# 3. INDEPENDENT SOLVERS + JUDGE ACCURACY
# =============================================================

independent_judge_correct = 0

for result, question in zip(
    independent_judge_results,
    questions
):

    final_answer = result["judge"]["final_answer"]
    correct_answer = question["correct_answer"]

    if is_correct(final_answer, correct_answer):
        independent_judge_correct += 1


independent_judge_accuracy = (
    independent_judge_correct / total_questions
)


# =============================================================
# 4. FULL DEBATE / FINAL JUDGE ACCURACY
# =============================================================

judge_correct = 0

for judgment, question in zip(
    final_judgments,
    questions
):

    final_answer = judgment["judge"]["final_answer"]
    correct_answer = question["correct_answer"]

    if is_correct(final_answer, correct_answer):
        judge_correct += 1


judge_accuracy = (
    judge_correct / total_questions
)


# =============================================================
# 5. REFINEMENT IMPROVEMENT RATE
# =============================================================

initial_wrong = 0
improved_to_correct = 0

for initial_question, refined_question, question in zip(
    initial_solutions,
    refined_solutions,
    questions
):

    correct_answer = question["correct_answer"]

    for initial_solution, refined_solution in zip(
        initial_question["solutions"],
        refined_question["refined_solutions"]
    ):

        initial_answer = initial_solution["final_answer"]
        refined_answer = refined_solution["refined_final_answer"]

        initial_is_correct = is_correct(
            initial_answer,
            correct_answer
        )

        refined_is_correct = is_correct(
            refined_answer,
            correct_answer
        )

        if not initial_is_correct:

            initial_wrong += 1

            if refined_is_correct:
                improved_to_correct += 1


if initial_wrong > 0:
    improvement_rate = (
        improved_to_correct / initial_wrong
    )
else:
    improvement_rate = 0.0


# =============================================================
# 6. REFINEMENT DAMAGE RATE
# =============================================================

initial_correct_for_damage = 0
damaged_to_wrong = 0

for initial_question, refined_question, question in zip(
    initial_solutions,
    refined_solutions,
    questions
):

    correct_answer = question["correct_answer"]

    for initial_solution, refined_solution in zip(
        initial_question["solutions"],
        refined_question["refined_solutions"]
    ):

        initial_answer = initial_solution["final_answer"]
        refined_answer = refined_solution["refined_final_answer"]

        initial_is_correct = is_correct(
            initial_answer,
            correct_answer
        )

        refined_is_correct = is_correct(
            refined_answer,
            correct_answer
        )

        if initial_is_correct:

            initial_correct_for_damage += 1

            if not refined_is_correct:
                damaged_to_wrong += 1


if initial_correct_for_damage > 0:
    damage_rate = (
        damaged_to_wrong / initial_correct_for_damage
    )
else:
    damage_rate = 0.0


# =============================================================
# 7. CONSENSUS RATE
# =============================================================

consensus_questions = 0

for initial_question in initial_solutions:

    answers = [
        normalize_answer(solution["final_answer"])
        for solution in initial_question["solutions"]
    ]

    if len(set(answers)) == 1:
        consensus_questions += 1


consensus_rate = (
    consensus_questions / total_questions
)


# =============================================================
# 8. CONSENSUS ACCURACY
# =============================================================

consensus_correct = 0

for initial_question, question in zip(
    initial_solutions,
    questions
):

    answers = [
        normalize_answer(solution["final_answer"])
        for solution in initial_question["solutions"]
    ]

    if len(set(answers)) == 1:

        consensus_answer = answers[0]
        correct_answer = normalize_answer(
            question["correct_answer"]
        )

        if consensus_answer == correct_answer:
            consensus_correct += 1


if consensus_questions > 0:
    consensus_accuracy = (
        consensus_correct / consensus_questions
    )
else:
    consensus_accuracy = 0.0


# =============================================================
# 9. INITIAL VS REFINED SOLVER ACCURACY
# =============================================================

initial_correct = 0
refined_correct = 0

total_initial_solver_answers = 0
total_refined_solver_answers = 0

for initial_question, refined_question, question in zip(
    initial_solutions,
    refined_solutions,
    questions
):

    correct_answer = question["correct_answer"]

    for solution in initial_question["solutions"]:

        total_initial_solver_answers += 1

        if is_correct(
            solution["final_answer"],
            correct_answer
        ):
            initial_correct += 1

    for solution in refined_question["refined_solutions"]:

        total_refined_solver_answers += 1

        if is_correct(
            solution["refined_final_answer"],
            correct_answer
        ):
            refined_correct += 1


initial_solver_accuracy = (
    initial_correct / total_initial_solver_answers
)

refined_solver_accuracy = (
    refined_correct / total_refined_solver_answers
)


# =============================================================
# 10. PEER REVIEW ERROR DETECTION
# =============================================================

genuine_errors_reviewed = 0
genuine_errors_detected = 0

correct_solutions_reviewed = 0
false_criticisms = 0

review_assessment_counts = {
    "Correct": 0,
    "Incorrect": 0,
    "Partially Correct": 0,
    "Other": 0
}

for review_question, initial_question, question in zip(
    peer_reviews,
    initial_solutions,
    questions
):

    correct_answer = question["correct_answer"]

    # Map solver ID -> actual initial answer
    solver_answers = {}

    for solution in initial_question["solutions"]:

        solver_answers[solution["model_id"]] = (
            solution["final_answer"]
        )

    for review in review_question["reviews"]:

        target_id = review["target_id"]

        target_answer = solver_answers.get(target_id)

        target_is_correct = is_correct(
            target_answer,
            correct_answer
        )

        assessment = review.get(
            "correctness_assessment",
            ""
        )

        # Normalize assessment
        assessment = assessment.strip()

        if assessment in review_assessment_counts:
            review_assessment_counts[assessment] += 1
        else:
            review_assessment_counts["Other"] += 1

        # -----------------------------------------------------
        # Target solution was actually correct
        # -----------------------------------------------------

        if target_is_correct:

            correct_solutions_reviewed += 1

            # Reviewer incorrectly criticized it
            if assessment in [
                "Incorrect",
                "Partially Correct"
            ]:
                false_criticisms += 1

        # -----------------------------------------------------
        # Target solution was actually incorrect
        # -----------------------------------------------------

        else:

            genuine_errors_reviewed += 1

            # Reviewer detected the error
            if assessment in [
                "Incorrect",
                "Partially Correct"
            ]:
                genuine_errors_detected += 1


# Calculate error detection rate

if genuine_errors_reviewed > 0:
    peer_review_error_detection_rate = (
        genuine_errors_detected /
        genuine_errors_reviewed
    )
else:
    peer_review_error_detection_rate = 0.0


# Calculate false criticism rate

if correct_solutions_reviewed > 0:
    false_criticism_rate = (
        false_criticisms /
        correct_solutions_reviewed
    )
else:
    false_criticism_rate = 0.0


# =============================================================
# 11. STORE RESULTS
# =============================================================

evaluation_results = {

    "total_questions": total_questions,

    "single_llm": {
        "correct": single_llm_correct,
        "total": total_questions,
        "accuracy": single_llm_accuracy
    },

    "majority_vote": {
        "correct": majority_correct,
        "total": total_questions,
        "accuracy": majority_accuracy
    },

    "independent_judge": {
        "correct": independent_judge_correct,
        "total": total_questions,
        "accuracy": independent_judge_accuracy
    },

    "full_debate": {
        "judge_correct": judge_correct,
        "total": total_questions,
        "judge_accuracy": judge_accuracy
    },

    "solver_performance": {
        "initial_correct": initial_correct,
        "initial_total": total_initial_solver_answers,
        "initial_accuracy": initial_solver_accuracy,

        "refined_correct": refined_correct,
        "refined_total": total_refined_solver_answers,
        "refined_accuracy": refined_solver_accuracy
    },

    "improvement": {
        "initially_wrong": initial_wrong,
        "improved_to_correct": improved_to_correct,
        "improvement_rate": improvement_rate
    },

    "damage": {
        "initially_correct": initial_correct_for_damage,
        "damaged_to_wrong": damaged_to_wrong,
        "damage_rate": damage_rate
    },

    "consensus": {
        "consensus_questions": consensus_questions,
        "total_questions": total_questions,
        "consensus_rate": consensus_rate,
        "consensus_correct": consensus_correct,
        "consensus_accuracy": consensus_accuracy
    },

    "peer_review": {
        "total_reviews": sum(review_assessment_counts.values()),
        "genuine_errors_reviewed": genuine_errors_reviewed,
        "genuine_errors_detected": genuine_errors_detected,
        "error_detection_rate": peer_review_error_detection_rate,
        "correct_solutions_reviewed": correct_solutions_reviewed,
        "false_criticisms": false_criticisms,
        "false_criticism_rate": false_criticism_rate,
        "assessment_counts": review_assessment_counts
    }
}


# =============================================================
# SAVE RESULTS
# =============================================================

with open(
    "results/evaluation_results.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        evaluation_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# =============================================================
# PRINT SUMMARY
# =============================================================

print()
print("=" * 60)
print("EVALUATION COMPLETED")
print("=" * 60)

print()

print("SINGLE-LLM BASELINE")
print(
    f"Accuracy: {single_llm_accuracy:.2%} "
    f"({single_llm_correct}/{total_questions})"
)

print()

print("MAJORITY VOTE BASELINE")
print(
    f"Accuracy: {majority_accuracy:.2%} "
    f"({majority_correct}/{total_questions})"
)

print()

print("INDEPENDENT SOLVERS + JUDGE")
print(
    f"Accuracy: {independent_judge_accuracy:.2%} "
    f"({independent_judge_correct}/{total_questions})"
)

print()

print("INITIAL SOLVERS")
print(
    f"Accuracy: {initial_solver_accuracy:.2%} "
    f"({initial_correct}/{total_initial_solver_answers})"
)

print()

print("REFINED SOLVERS")
print(
    f"Accuracy: {refined_solver_accuracy:.2%} "
    f"({refined_correct}/{total_refined_solver_answers})"
)

print()

print("FULL DEBATE / FINAL JUDGE")
print(
    f"Accuracy: {judge_accuracy:.2%} "
    f"({judge_correct}/{total_questions})"
)

print()

print("REFINEMENT IMPROVEMENT RATE")
print(
    f"Rate: {improvement_rate:.2%} "
    f"({improved_to_correct}/{initial_wrong})"
)

print()

print("REFINEMENT DAMAGE RATE")
print(
    f"Rate: {damage_rate:.2%} "
    f"({damaged_to_wrong}/{initial_correct_for_damage})"
)

print()

print("CONSENSUS RATE")
print(
    f"Rate: {consensus_rate:.2%} "
    f"({consensus_questions}/{total_questions})"
)

print()

print("CONSENSUS ACCURACY")
print(
    f"Accuracy: {consensus_accuracy:.2%} "
    f"({consensus_correct}/{consensus_questions})"
)

print()

print("PEER REVIEW ERROR DETECTION")
print(
    f"Rate: {peer_review_error_detection_rate:.2%} "
    f"({genuine_errors_detected}/{genuine_errors_reviewed})"
)

print()

print("FALSE CRITICISM RATE")
print(
    f"Rate: {false_criticism_rate:.2%} "
    f"({false_criticisms}/{correct_solutions_reviewed})"
)

print()

print("PEER REVIEW ASSESSMENTS")
print(
    f"Correct: {review_assessment_counts['Correct']}"
)

print(
    f"Incorrect: {review_assessment_counts['Incorrect']}"
)

print(
    f"Partially Correct: "
    f"{review_assessment_counts['Partially Correct']}"
)

print(
    f"Other: {review_assessment_counts['Other']}"
)

print()

print("Saved to results/evaluation_results.json")

