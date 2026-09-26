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
# 3. Load Stage 0.5 role assignments
# --------------------------------------------------

with open(
    "results/role_assignments.json",
    "r",
    encoding="utf-8"
) as f:
    role_assignments = json.load(f)


# --------------------------------------------------
# 4. Function: ask one Solver to solve one question
# --------------------------------------------------

def solve_question(model_id, question_text):

    prompt = f"""
You are a Solver in a multi-LLM collaborative reasoning system.

Your task is to independently solve the following problem.

Provide a complete step-by-step solution.

At the end, clearly state your final answer.

Return ONLY valid JSON in this exact format:

{{
    "reasoning": "your complete step-by-step solution",
    "final_answer": "your final answer"
}}

Important:
- Do not assume that another Solver has solved the problem.
- Do not discuss the other agents.
- Solve the problem independently.
- Your response must contain ONLY the JSON object.
- Do not use markdown code fences.
- Do not write anything before or after the JSON.

Problem:
{question_text}
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
    # Calculate response time
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
    # Try to parse the response as JSON
    # --------------------------------------------------

    try:

        solution_data = json.loads(answer)

        return {
            "model_id": model_id,
            "reasoning": solution_data["reasoning"],
            "final_answer": solution_data["final_answer"],
            "latency_seconds": round(elapsed, 2),

            # Token usage
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

    except json.JSONDecodeError:

        print(
            f"WARNING: {model_id} returned invalid JSON."
        )

        return {
            "model_id": model_id,
            "reasoning": answer,
            "final_answer": None,
            "latency_seconds": round(elapsed, 2),

            # Token usage is still saved
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,

            "parse_error": True
        }

    except KeyError as error:

        print(
            f"WARNING: {model_id} returned JSON "
            f"but is missing field: {error}"
        )

        return {
            "model_id": model_id,
            "reasoning": answer,
            "final_answer": None,
            "latency_seconds": round(elapsed, 2),

            # Token usage is still saved
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,

            "parse_error": True,
            "error": f"Missing field: {error}"
        }


# --------------------------------------------------
# 5. Run Stage 1 for all 25 questions
# --------------------------------------------------

all_results = []


for question, assignment in zip(
    questions,
    role_assignments
):

    print()
    print("=" * 60)
    print(f"Question {question['id']}")
    print("=" * 60)

    solutions = []

    # --------------------------------------------------
    # Find the 3 Solvers for this question
    # --------------------------------------------------

    for model_id, role in assignment["assignments"].items():

        if role == "Solver":

            print(
                f"Running {model_id} as Solver..."
            )

            result = solve_question(
                model_id,
                question["question"]
            )

            solutions.append(result)

    # --------------------------------------------------
    # Store results for this question
    # --------------------------------------------------

    question_result = {
        "question_id": question["id"],
        "question": question["question"],
        "solutions": solutions
    }

    all_results.append(question_result)


# --------------------------------------------------
# 6. Save all Stage 1 results
# --------------------------------------------------

with open(
    "results/initial_solutions.json",
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
# 7. Final summary
# --------------------------------------------------

total_solutions = 0
parse_errors = 0

total_input_tokens = 0
total_output_tokens = 0
total_tokens = 0


for question in all_results:

    for solution in question["solutions"]:

        total_solutions += 1

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
# 8. Print final summary
# --------------------------------------------------

print()
print("=" * 60)
print("PHASE 1 COMPLETED")
print("=" * 60)

print(
    f"Questions processed: {len(all_results)}"
)

print(
    f"Total Solver responses: {total_solutions}"
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
    "Saved to results/initial_solutions.json"
)