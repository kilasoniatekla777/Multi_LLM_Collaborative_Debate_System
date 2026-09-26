import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI


# =============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# =============================================================
# 2. LOAD ORIGINAL INDEPENDENT SOLVER RESULTS
# =============================================================

with open(
    "results/initial_solutions.json",
    "r",
    encoding="utf-8"
) as f:
    initial_solutions = json.load(f)


# =============================================================
# 3. JUDGE FUNCTION
# =============================================================

def judge_question(
    question_text,
    original_solutions
):
    """
    Ask a Judge to select the strongest answer from
    three independent solver answers.

    No peer reviews or refinements are provided.
    """

    # ---------------------------------------------------------
    # Format the three independent solutions
    # ---------------------------------------------------------

    solutions_text = ""

    for solution in original_solutions:

        solutions_text += f"""
MODEL: {solution["model_id"]}

Reasoning:
{solution["reasoning"]}

Final answer:
{solution["final_answer"]}

--------------------------------
"""


    # ---------------------------------------------------------
    # Judge prompt
    # ---------------------------------------------------------

    prompt = f"""
You are the Final Judge in an independent multi-LLM
problem-solving experiment.

Three independent Solvers attempted the problem below.

Your task is to determine which answer is most accurate.

IMPORTANT:

- Do NOT simply choose the majority answer.
- Independently check the reasoning.
- Check calculations, logical steps, assumptions,
  edge cases, and the final conclusion.
- Compare the actual reasoning and answer.
- Select the solution that is best supported by the problem.
- If all solutions are incorrect, determine the correct answer
  yourself.
- Return ONLY valid JSON.
- Do not use markdown code fences.

Problem:

{question_text}


==============================
INDEPENDENT SOLUTIONS
==============================

{solutions_text}


Return exactly this JSON structure:

{{
    "selected_solver": "model_id",
    "final_answer": "the final answer",
    "reasoning": "explain why this answer is correct and why the other solutions were accepted or rejected",
    "confidence": 0.0
}}

The confidence must be a number between 0 and 1.
"""


    # ---------------------------------------------------------
    # Start timer
    # ---------------------------------------------------------

    start_time = time.time()


    # ---------------------------------------------------------
    # Send request
    # ---------------------------------------------------------

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    # ---------------------------------------------------------
    # Calculate latency
    # ---------------------------------------------------------

    elapsed = time.time() - start_time


    # ---------------------------------------------------------
    # Get model response
    # ---------------------------------------------------------

    answer = response.choices[0].message.content


    # ---------------------------------------------------------
    # Get token usage
    # ---------------------------------------------------------

    usage = response.usage

    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens


    # ---------------------------------------------------------
    # Parse Judge response
    # ---------------------------------------------------------

    try:

        judgment_data = json.loads(answer)

        return {
            "selected_solver": judgment_data["selected_solver"],
            "final_answer": judgment_data["final_answer"],
            "reasoning": judgment_data["reasoning"],
            "confidence": judgment_data["confidence"],

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
            "WARNING: Judge returned invalid JSON."
        )

        return {
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


# =============================================================
# 4. RUN INDEPENDENT JUDGE EXPERIMENT
# =============================================================

all_results = []


for question_data in initial_solutions:

    question_id = question_data["question_id"]
    question_text = question_data["question"]

    print()
    print("=" * 60)
    print(f"Question {question_id}")
    print("=" * 60)

    print(
        "Running Independent Judge..."
    )


    result = judge_question(
        question_text=question_text,
        original_solutions=question_data["solutions"]
    )


    question_result = {
        "question_id": question_id,
        "question": question_text,
        "judge": result
    }


    all_results.append(
        question_result
    )


# =============================================================
# 5. SAVE RESULTS
# =============================================================

with open(
    "results/independent_judge_results.json",
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
# 6. CALCULATE SUMMARY
# =============================================================

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


# ---------------------------------------------------------
# Calculate token totals
# ---------------------------------------------------------

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


# =============================================================
# 7. PRINT SUMMARY
# =============================================================

print()
print("=" * 60)
print("INDEPENDENT JUDGE EXPERIMENT COMPLETED")
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
    "Saved to results/independent_judge_results.json"
)