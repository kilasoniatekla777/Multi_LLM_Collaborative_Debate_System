import json

# Load the original Solver answers
with open("results/initial_solutions.json", "r", encoding="utf-8") as f:
    initial_solutions = json.load(f)

# Load the ground-truth answers
with open("data/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


def normalize_answer(answer):
    """
    Normalize answers slightly so that simple formatting
    differences do not prevent matching.
    """

    if answer is None:
        return None

    return str(answer).strip().lower()


all_results = []


for solution_data, question_data in zip(
    initial_solutions,
    questions
):

    question_id = solution_data["question_id"]
    question_text = solution_data["question"]

    correct_answer = question_data["correct_answer"]

    solutions = solution_data["solutions"]

    answers = []

    for solution in solutions:
        answer = solution.get("final_answer")

        if answer is not None:
            answers.append(answer)

    # ---------------------------------------------------------
    # Count answers
    # ---------------------------------------------------------

    answer_counts = {}

    for answer in answers:

        normalized = normalize_answer(answer)

        if normalized not in answer_counts:
            answer_counts[normalized] = 0

        answer_counts[normalized] += 1

    # ---------------------------------------------------------
    # Select majority answer
    # ---------------------------------------------------------

    if answer_counts:

        majority_normalized = max(
            answer_counts,
            key=answer_counts.get
        )

        # Recover original formatting
        majority_answer = next(
            answer
            for answer in answers
            if normalize_answer(answer) == majority_normalized
        )

    else:
        majority_answer = None

    # ---------------------------------------------------------
    # Check correctness
    # ---------------------------------------------------------

    is_correct = (
        normalize_answer(majority_answer)
        == normalize_answer(correct_answer)
    )

    question_result = {
        "question_id": question_id,
        "question": question_text,
        "correct_answer": correct_answer,
        "solver_answers": answers,
        "answer_counts": answer_counts,
        "majority_answer": majority_answer,
        "is_correct": is_correct
    }

    all_results.append(question_result)

    print()
    print("=" * 60)
    print(f"Question {question_id}")
    print("=" * 60)

    print(f"Solver answers: {answers}")
    print(f"Majority answer: {majority_answer}")
    print(f"Correct answer: {correct_answer}")
    print(f"Correct: {is_correct}")


# =============================================================
# SAVE RESULTS
# =============================================================

with open(
    "results/majority_vote_results.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# =============================================================
# SUMMARY
# =============================================================

correct_count = sum(
    1
    for result in all_results
    if result["is_correct"]
)

total_questions = len(all_results)

accuracy = correct_count / total_questions


print()
print("=" * 60)
print("MAJORITY VOTE BASELINE COMPLETED")
print("=" * 60)

print(f"Questions processed: {total_questions}")
print(f"Correct: {correct_count}")
print(f"Accuracy: {accuracy:.2%}")
print("Saved to results/majority_vote_results.json")