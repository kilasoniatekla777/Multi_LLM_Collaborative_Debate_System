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
# 2. Load questions
# --------------------------------------------------

with open(
    "data/questions.json",
    "r",
    encoding="utf-8"
) as f:
    questions = json.load(f)


# --------------------------------------------------
# 3. Function: solve one question
# --------------------------------------------------

def solve_question(question_text):

    prompt = f"""
Solve the following problem independently.

Provide a clear step-by-step solution.

At the end, clearly state the final answer.

Return ONLY valid JSON in this exact format:

{{
    "reasoning": "your complete step-by-step solution",
    "final_answer": "your final answer"
}}

Do not use markdown code fences.
Do not write anything before or after the JSON.

Problem:
{question_text}
"""

    # --------------------------------------------------
    # Start timer
    # --------------------------------------------------

    start_time = time.time()


    # --------------------------------------------------
    # Send request
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
    # Parse JSON response
    # --------------------------------------------------

    try:

        result = json.loads(answer)

        return {
            "reasoning": result["reasoning"],
            "final_answer": result["final_answer"],

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
            "WARNING: Model returned invalid JSON."
        )

        return {
            "reasoning": answer,
            "final_answer": None,

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
# 4. RUN BASELINE
# ============================================================

all_results = []


for question in questions:

    print()
    print("=" * 60)
    print(f"Question {question['id']}")
    print("=" * 60)

    print(
        "Running single LLM..."
    )


    result = solve_question(
        question["question"]
    )


    question_result = {
        "question_id": question["id"],
        "question": question["question"],
        "correct_answer": question["correct_answer"],
        "reference_solution": question["reference_solution"],
        "baseline_solution": result
    }


    all_results.append(
        question_result
    )


# ============================================================
# 5. SAVE RESULTS
# ============================================================

with open(
    "results/baseline_results.json",
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
# 6. SUMMARY
# ============================================================

parse_errors = sum(
    1
    for result in all_results
    if result[
        "baseline_solution"
    ].get(
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

    baseline = result[
        "baseline_solution"
    ]

    total_input_tokens += baseline.get(
        "input_tokens",
        0
    )

    total_output_tokens += baseline.get(
        "output_tokens",
        0
    )

    total_tokens += baseline.get(
        "total_tokens",
        0
    )


# ============================================================
# 7. PRINT SUMMARY
# ============================================================

print()
print("=" * 60)
print("SINGLE-LLM BASELINE COMPLETED")
print("=" * 60)

print(
    f"Questions processed: {len(all_results)}"
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
    "Saved to results/baseline_results.json"
)