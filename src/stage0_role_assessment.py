import os
import json
import time

from dotenv import load_dotenv
from openai import OpenAI


# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Load questions
with open("data/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)


question = questions[0]["question"]

print(question)

agents = [
    {
        "id": "model_1",
        "model": "gpt-4o-mini"
    },
    {
        "id": "model_2",
        "model": "gpt-4o-mini"
    },
    {
        "id": "model_3",
        "model": "gpt-4o-mini"
    },
    {
        "id": "model_4",
        "model": "gpt-4o-mini"
    }
]

def create_role_assessment_prompt(question):
    return f"""
You are participating in a multi-LLM collaborative reasoning system.

There are two possible roles:

1. Solver
   Independently solve the problem with detailed reasoning.

2. Judge
   Evaluate multiple proposed solutions later and determine which solution is correct.

For the following problem, assess which role you are better suited for.

Do NOT solve the problem.

Return ONLY valid JSON in exactly this format:

{{
    "role_preferences": ["Solver", "Judge"],
    "confidence_by_role": {{
        "Solver": 0.0,
        "Judge": 0.0
   }},
    "reason": "brief explanation"
}}

Important:
- Always include BOTH "Solver" and "Judge" in role_preferences.
- Put the role you prefer first.
- Always provide confidence scores for BOTH roles.
- Do NOT solve the problem.

The confidence scores must be numbers between 0 and 1.

Problem:
{question}
"""

def assess_role(agent, question):
    prompt = create_role_assessment_prompt(question)

    start_time = time.time()

    response = client.chat.completions.create(
        model=agent["model"],
        messages=[
            {
                "role": "system",
                "content": "You are an agent participating in a collaborative reasoning experiment."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    elapsed = time.time() - start_time

    answer = response.choices[0].message.content

    return {
        "model_id": agent["id"],
        "raw_response": answer,
        "latency_seconds": round(elapsed, 2)
    }

all_results = []

for question in questions:

    print(f"\nProcessing question {question['id']}...")

    question_result = {
        "question_id": question["id"],
        "question": question["question"],
        "assessments": []
    }

    for agent in agents:

        result = assess_role(
            agent,
            question["question"]
        )

        question_result["assessments"].append(result)

    all_results.append(question_result)


# Save results
with open(
    "results/role_assessments.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\nPhase 0 completed.")
print("Saved to results/role_assessments.json")