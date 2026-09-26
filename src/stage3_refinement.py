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
# 2. Load Stage 1 solutions
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
# 4. Function: refine one Solver's solution
# --------------------------------------------------

def refine_solution(
    model_id,
    question_text,
    original_reasoning,
    original_final_answer,
    reviews
):

    # --------------------------------------------------
    # Format the two peer reviews
    # --------------------------------------------------

    reviews_text = ""

    for i, review in enumerate(reviews, start=1):

        reviews_text += f"""
Review {i}

Reviewer:
{review["reviewer_id"]}

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

------------------------------
"""


    # --------------------------------------------------
    # Build refinement prompt
    # --------------------------------------------------

    prompt = f"""
You are a Solver in a multi-LLM collaborative reasoning system.

You originally solved the problem below.

Other Solvers have now reviewed your solution.

Your task is to reconsider your original solution using
their feedback.

IMPORTANT:

1. Carefully check each criticism.
2. Do NOT automatically accept a review.
3. If a reviewer is wrong, explain why and defend your
   original reasoning.
4. If a reviewer identifies a genuine mistake, correct it.
5. Produce a complete refined solution.
6. Clearly state the final answer.
7. Return ONLY valid JSON.
8. Do not use markdown code fences.

Problem:
{question_text}


Your original solution:

Reasoning:
{original_reasoning}

Final answer:
{original_final_answer}


Peer reviews:

{reviews_text}


Return exactly this JSON structure:

{{
    "changes_made": [
        "describe each change made to the original solution"
    ],
    "review_responses": [
        "explain how each important criticism was addressed"
    ],
    "refined_reasoning": "complete step-by-step refined solution",
    "refined_final_answer": "final answer",
    "confidence": 0.0
}}

The confidence must be between 0 and 1.
"""


    # --------------------------------------------------
    # 5. Call the LLM
    # --------------------------------------------------

    start_time = time.time()

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
    # Get model response
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
    # 6. Parse JSON response
    # --------------------------------------------------

    try:

        refinement_data = json.loads(answer)

        return {
            "model_id": model_id,

            "changes_made": refinement_data[
                "changes_made"
            ],

            "review_responses": refinement_data[
                "review_responses"
            ],

            "refined_reasoning": refinement_data[
                "refined_reasoning"
            ],

            "refined_final_answer": refinement_data[
                "refined_final_answer"
            ],

            "confidence": refinement_data[
                "confidence"
            ],

            # Performance
            "latency_seconds": round(elapsed, 2),

            # Token usage
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }


    except (json.JSONDecodeError, KeyError) as error:

        print(
            f"WARNING: {model_id} returned invalid "
            f"refinement JSON."
        )

        return {
            "model_id": model_id,

            "changes_made": [],

            "review_responses": [],

            "refined_reasoning": answer,

            "refined_final_answer": None,

            "confidence": None,

            # Performance
            "latency_seconds": round(elapsed, 2),

            # Token usage is still saved
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,

            "parse_error": True,

            "error": str(error)
        }


# --------------------------------------------------
# 7. Process all questions
# --------------------------------------------------

all_results = []


for initial_question, review_question in zip(
    initial_solutions,
    peer_reviews
):

    question_id = initial_question["question_id"]
    question_text = initial_question["question"]

    solutions = initial_question["solutions"]
    reviews = review_question["reviews"]


    print()
    print("=" * 60)
    print(f"Question {question_id}")
    print("=" * 60)


    refined_solutions = []


    # --------------------------------------------------
    # 8. Refine each Solver's solution
    # --------------------------------------------------

    for solution in solutions:

        model_id = solution["model_id"]


        # Find reviews written ABOUT this Solver
        model_reviews = [
            review
            for review in reviews
            if review["target_id"] == model_id
        ]


        print(
            f"Refining {model_id}..."
        )


        result = refine_solution(
            model_id=model_id,
            question_text=question_text,
            original_reasoning=solution["reasoning"],
            original_final_answer=solution["final_answer"],
            reviews=model_reviews
        )


        refined_solutions.append(result)


    # --------------------------------------------------
    # 9. Save refined solutions for this question
    # --------------------------------------------------

    question_result = {
        "question_id": question_id,
        "question": question_text,
        "refined_solutions": refined_solutions
    }


    all_results.append(question_result)


# --------------------------------------------------
# 10. Save all refined solutions
# --------------------------------------------------

with open(
    "results/refined_solutions.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# 11. Summary
# --------------------------------------------------

total_refined = 0
parse_errors = 0

total_input_tokens = 0
total_output_tokens = 0
total_tokens = 0


for question in all_results:

    for solution in question["refined_solutions"]:

        total_refined += 1

        if solution.get("parse_error", False):
            parse_errors += 1

        total_input_tokens += solution.get(
            "input_tokens",
            0
        )

        total_output_tokens += solution.get(
            "output_tokens",
            0
        )

        total_tokens += solution.get(
            "total_tokens",
            0
        )


# --------------------------------------------------
# 12. Final summary
# --------------------------------------------------

print()
print("=" * 60)
print("STAGE 3 COMPLETED")
print("=" * 60)

print(
    f"Questions processed: {len(all_results)}"
)

print(
    f"Total refined solutions: {total_refined}"
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
    "Saved to results/refined_solutions.json"
)