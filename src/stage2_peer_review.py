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
# 3. Function: review one Solver's solution
# --------------------------------------------------

def review_solution(
    reviewer_id,
    target_id,
    question_text,
    target_reasoning,
    target_final_answer
):

    prompt = f"""
You are participating in a multi-LLM collaborative reasoning system.

You are acting as a Peer Reviewer.

Your task is to critically evaluate another Solver's solution
to the problem below.

Do NOT solve the problem from scratch unless necessary to verify
the proposed solution.

Evaluate whether the reasoning is logically valid and whether
the final answer is correct.

Return ONLY valid JSON in exactly this format:

{{
    "correctness_assessment": "Correct / Incorrect / Partially Correct",
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2"
    ],
    "errors": [
        "error 1"
    ],
    "suggested_changes": [
        "suggested change 1"
    ],
    "overall_comment": "brief overall assessment"
}}

Important:
- Be critical and specific.
- Do not assume the proposed answer is correct.
- Check the reasoning carefully.
- Identify mathematical, logical, factual, or computational errors.
- If there are no errors, say so explicitly.
- Do not discuss other agents.
- Do not write anything outside the JSON object.
- Do not use markdown code fences.

Problem:
{question_text}

Solution being reviewed:

Reasoning:
{target_reasoning}

Final answer:
{target_final_answer}
"""

    # --------------------------------------------------
    # Start timer
    # --------------------------------------------------

    start_time = time.time()

    # --------------------------------------------------
    # Send request to the LLM
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
    # Try to parse JSON
    # --------------------------------------------------

    try:

        review_data = json.loads(answer)

        return {
            "reviewer_id": reviewer_id,
            "target_id": target_id,

            "correctness_assessment": review_data[
                "correctness_assessment"
            ],

            "strengths": review_data["strengths"],

            "weaknesses": review_data["weaknesses"],

            "errors": review_data["errors"],

            "suggested_changes": review_data[
                "suggested_changes"
            ],

            "overall_comment": review_data[
                "overall_comment"
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
            f"WARNING: {reviewer_id} returned invalid "
            f"review JSON for {target_id}."
        )

        return {
            "reviewer_id": reviewer_id,
            "target_id": target_id,

            "correctness_assessment": None,

            "strengths": [],

            "weaknesses": [],

            "errors": [],

            "suggested_changes": [],

            "overall_comment": answer,

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
# 4. Process every question
# --------------------------------------------------

all_reviews = []


for question_data in initial_solutions:

    question_id = question_data["question_id"]
    question_text = question_data["question"]
    solutions = question_data["solutions"]

    print()
    print("=" * 60)
    print(f"Question {question_id}")
    print("=" * 60)

    question_reviews = []

    # --------------------------------------------------
    # Every Solver reviews the other two
    # --------------------------------------------------

    for reviewer in solutions:

        reviewer_id = reviewer["model_id"]

        for target in solutions:

            target_id = target["model_id"]

            # Don't review your own solution
            if reviewer_id == target_id:
                continue

            print(
                f"{reviewer_id} reviewing {target_id}..."
            )

            review = review_solution(
                reviewer_id=reviewer_id,
                target_id=target_id,
                question_text=question_text,
                target_reasoning=target["reasoning"],
                target_final_answer=target["final_answer"]
            )

            question_reviews.append(review)

    # --------------------------------------------------
    # Save reviews for this question
    # --------------------------------------------------

    question_result = {
        "question_id": question_id,
        "question": question_text,
        "reviews": question_reviews
    }

    all_reviews.append(question_result)


# --------------------------------------------------
# 5. Save all reviews
# --------------------------------------------------

with open(
    "results/peer_reviews.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_reviews,
        f,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# 6. Summary
# --------------------------------------------------

total_reviews = 0
parse_errors = 0

total_input_tokens = 0
total_output_tokens = 0
total_tokens = 0


for question in all_reviews:

    for review in question["reviews"]:

        total_reviews += 1

        if review.get("parse_error", False):
            parse_errors += 1

        total_input_tokens += review.get(
            "input_tokens",
            0
        )

        total_output_tokens += review.get(
            "output_tokens",
            0
        )

        total_tokens += review.get(
            "total_tokens",
            0
        )


# --------------------------------------------------
# 7. Final summary
# --------------------------------------------------

print()
print("=" * 60)
print("STAGE 2 COMPLETED")
print("=" * 60)

print(
    f"Questions processed: {len(all_reviews)}"
)

print(
    f"Total peer reviews: {total_reviews}"
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
    "Saved to results/peer_reviews.json"
)