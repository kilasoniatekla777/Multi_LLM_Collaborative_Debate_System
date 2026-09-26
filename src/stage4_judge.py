import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# --------------------------------------------------
# 2. Load Stage 1 original solutions
# --------------------------------------------------

with open(
    "results/initial_solutions.json",
    "r",
    encoding="utf-8"
) as f:
    initial_solutions = json.load(f)


# --------------------------------------------------
# 3. Load Stage 2 peer reviews
# --------------------------------------------------

with open(
    "results/peer_reviews.json",
    "r",
    encoding="utf-8"
) as f:
    peer_reviews = json.load(f)


# --------------------------------------------------
# 4. Load Stage 3 refined solutions
# --------------------------------------------------

with open(
    "results/refined_solutions.json",
    "r",
    encoding="utf-8"
) as f:
    refined_solutions = json.load(f)


# --------------------------------------------------
# 5. Load Stage 0.5 role assignments
# --------------------------------------------------

with open(
    "results/role_assignments.json",
    "r",
    encoding="utf-8"
) as f:
    role_assignments = json.load(f)


# --------------------------------------------------
# 6. Function: Judge one question
# --------------------------------------------------

def judge_question(
    judge_id,
    question_text,
    original_solutions,
    reviews,
    refined_solutions
):

    # --------------------------------------------------
    # Format original solutions
    # --------------------------------------------------

    original_text = ""

    for solution in original_solutions:

        original_text += f"""
MODEL: {solution["model_id"]}

Original reasoning:
{solution["reasoning"]}

Original final answer:
{solution["final_answer"]}

--------------------------------
"""


    # --------------------------------------------------
    # Format peer reviews
    # --------------------------------------------------

    reviews_text = ""

    for review in reviews:

        reviews_text += f"""
Reviewer: {review["reviewer_id"]}
Target Solver: {review["target_id"]}

Correctness assessment:
{review.get("correctness_assessment")}

Strengths:
{review.get("strengths")}

Weaknesses:
{review.get("weaknesses")}

Errors:
{review.get("errors")}

Suggested changes:
{review.get("suggested_changes")}

Overall comment:
{review.get("overall_comment")}

--------------------------------
"""


    # --------------------------------------------------
    # Format refined solutions
    # --------------------------------------------------

    refined_text = ""

    for solution in refined_solutions:

        refined_text += f"""
MODEL: {solution["model_id"]}

Changes made:
{solution.get("changes_made")}

Responses to reviews:
{solution.get("review_responses")}

Refined reasoning:
{solution.get("refined_reasoning")}

Refined final answer:
{solution.get("refined_final_answer")}

Confidence:
{solution.get("confidence")}

--------------------------------
"""


    # --------------------------------------------------
    # Judge prompt
    # --------------------------------------------------

    prompt = f"""
You are the Final Judge in a multi-LLM collaborative reasoning system.

Your task is to determine the most accurate final answer to the
problem using the complete debate evidence.

You are reviewing:

1. The original solutions from the three Solvers.
2. The peer reviews of those solutions.
3. The refined solutions after the Solvers responded to feedback.

IMPORTANT:

- Do NOT simply choose the majority answer.
- Do NOT assume that a peer review is correct.
- Independently check the mathematical, logical, scientific,
  or strategic reasoning.
- Identify incorrect criticisms when necessary.
- Compare the reasoning, not just the final answers.
- Select the answer that is best supported by the actual problem.
- Give a clear explanation for your decision.
- Return ONLY valid JSON.
- Do not use markdown code fences.

Problem:

{question_text}


==============================
ORIGINAL SOLUTIONS
==============================

{original_text}


==============================
PEER REVIEWS
==============================

{reviews_text}


==============================
REFINED SOLUTIONS
==============================

{refined_text}


Return exactly this JSON structure:

{{
    "selected_solver": "model_id",
    "final_answer": "the final correct answer",
    "reasoning": "explain why this answer is correct and why the other solutions were rejected or accepted",
    "confidence": 0.0
}}

The confidence must be a number between 0 and 1.
"""


    # --------------------------------------------------
    # Start timer
    # --------------------------------------------------

    start_time = time.time()


    # --------------------------------------------------
    # Send request to Judge
    # --------------------------------------------------

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    # --------------------------------------------------
    # Calculate latency
    # --------------------------------------------------

    elapsed = time.time() - start_time


    # --------------------------------------------------
    # Get Judge response
    # --------------------------------------------------

    answer = response.choices[0].message.content


    # --------------------------------------------------
    # Get token usage
    # --------------------------------------------------

    usage = response.usage

    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens


    # --------------------------------------------------
    # Parse Judge response
    # --------------------------------------------------

    try:

        judgment_data = json.loads(answer)

        return {
            "judge_id": judge_id,

            "selected_solver": judgment_data[
                "selected_solver"
            ],

            "final_answer": judgment_data[
                "final_answer"
            ],

            "reasoning": judgment_data[
                "reasoning"
            ],

            "confidence": judgment_data[
                "confidence"
            ],

            # Performance
            "latency_seconds": round(
                elapsed,
                2
            ),

            # Token usage
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }


    except (json.JSONDecodeError, KeyError) as error:

        print(
            f"WARNING: {judge_id} returned invalid "
            f"Judge JSON."
        )

        return {
            "judge_id": judge_id,

            "selected_solver": None,

            "final_answer": None,

            "reasoning": answer,

            "confidence": None,

            # Performance
            "latency_seconds": round(
                elapsed,
                2
            ),

            # Token usage is still saved
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,

            "parse_error": True,

            "error": str(error)
        }


# ============================================================
# 7. RUN STAGE 4
# ============================================================

all_results = []


for (
    initial_question,
    review_question,
    refined_question,
    assignment
) in zip(
    initial_solutions,
    peer_reviews,
    refined_solutions,
    role_assignments
):

    question_id = initial_question["question_id"]
    question_text = initial_question["question"]


    # --------------------------------------------------
    # Find model assigned as Judge
    # --------------------------------------------------

    judge_id = None

    for model_id, role in assignment[
        "assignments"
    ].items():

        if role == "Judge":

            judge_id = model_id

            break


    print()
    print("=" * 60)
    print(f"Question {question_id}")
    print("=" * 60)

    print(
        f"Running {judge_id} as Final Judge..."
    )


    # --------------------------------------------------
    # Run Judge
    # --------------------------------------------------

    result = judge_question(
        judge_id=judge_id,
        question_text=question_text,
        original_solutions=initial_question[
            "solutions"
        ],
        reviews=review_question[
            "reviews"
        ],
        refined_solutions=refined_question[
            "refined_solutions"
        ]
    )


    # --------------------------------------------------
    # Save question result
    # --------------------------------------------------

    question_result = {
        "question_id": question_id,
        "question": question_text,
        "judge": result
    }


    all_results.append(
        question_result
    )


# ============================================================
# 8. SAVE RESULTS
# ============================================================

with open(
    "results/final_judgments.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# 9. SUMMARY
# ============================================================

total_judgments = len(
    all_results
)

parse_errors = sum(
    1
    for result in all_results
    if result["judge"].get(
        "parse_error",
        False
    )
)


# --------------------------------------------------
# Calculate token totals
# --------------------------------------------------

total_input_tokens = 0
total_output_tokens = 0
total_tokens = 0


for result in all_results:

    judge = result["judge"]

    total_input_tokens += judge.get(
        "input_tokens",
        0
    )

    total_output_tokens += judge.get(
        "output_tokens",
        0
    )

    total_tokens += judge.get(
        "total_tokens",
        0
    )


# ============================================================
# 10. PRINT SUMMARY
# ============================================================

print()
print("=" * 60)
print("STAGE 4 COMPLETED")
print("=" * 60)

print(
    f"Questions processed: {total_judgments}"
)

print(
    f"Parse errors: {parse_errors}"
)

print()
print("TOKEN USAGE")
print("-" * 60)

print(
    f"Input tokens:  {total_input_tokens}"
)

print(
    f"Output tokens: {total_output_tokens}"
)

print(
    f"Total tokens:   {total_tokens}"
)

print()
print(
    "Saved to results/final_judgments.json"
)