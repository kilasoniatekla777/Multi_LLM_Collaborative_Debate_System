# Multi-LLM Collaborative Debate System — Architecture & Build Guide

This is the complete build order for the assignment: three Solver LLMs answer
independently, cross-review each other, refine based on feedback, and a Judge
picks the best final answer. Every stage below maps directly to the
assignment's Phase 1/2/3 structure.

**How to use this doc:** build top to bottom. Don't skip ahead to Stage 2
before Stage 1 actually works end-to-end on a real problem — each stage's
input is the previous stage's real output, not a placeholder.

---

## 1. Architecture

```
                        problems.json (25 problems)
                                |
                                v
                    ┌───────────────────────┐
                    │   Stage 0: Self-       │
                    │   Assessment (4 LLMs)  │
                    └───────────┬───────────┘
                                v
                    ┌───────────────────────┐
                    │  Stage 0.5: Algorithmic│
                    │  Role Assignment       │  (plain Python, no LLM call)
                    └───────────┬───────────┘
                                v
              ┌─────────────────┼─────────────────┐
              v                 v                 v
        ┌─────────┐       ┌─────────┐       ┌─────────┐
        │Solver 1 │       │Solver 2 │       │Solver 3 │   Stage 1:
        │(indep.) │       │(indep.) │       │(indep.) │   Independent solving
        └────┬────┘       └────┬────┘       └────┬────┘
             │                 │                 │
             └────────┬────────┴────────┬────────┘
                       v                 v
              ┌─────────────────────────────────┐
              │   Stage 2: Peer Review           │   6 review calls total
              │   (each solver reviews 2 peers)  │   (3 solvers x 2 peers)
              └────────────────┬─────────────────┘
                                v
              ┌─────────────────────────────────┐
              │   Stage 3: Refinement            │   3 calls
              │   (each solver revises based on  │
              │    the 2 reviews it received)    │
              └────────────────┬─────────────────┘
                                v
              ┌─────────────────────────────────┐
              │   Stage 4: Final Judgment        │   1 call
              │   (sees everything: originals,   │
              │    reviews, refined solutions)   │
              └────────────────┬─────────────────┘
                                v
                         Final Answer
                                |
                                v
                  ┌───────────────────────────┐
                  │  Evaluation & Logging      │  pandas + matplotlib
                  │  (accuracy, consensus,     │
                  │   improvement, judge acc.) │
                  └───────────────────────────┘
```

Three separate pipelines get run against the same 25 problems, for comparison:
1. **Single-LLM baseline** — one call, no debate.
2. **Simple voting baseline** — Stage 1's three independent answers, majority vote, no review/refinement/judge.
3. **Full system** — all five stages above.

---

## 2. Tech stack

| Need | Tool |
|---|---|
| LLM calls | `openai`, `google-generativeai` SDKs (native, not litellm — see rationale in `app/llm/client.py`) |
| Structured output | `pydantic` |
| Concurrency (parallel solver/review calls) | `asyncio` |
| Secrets | `python-dotenv`, `.env` (never committed) |
| Logging results | `pandas` |
| Plots | `matplotlib` |
| Tests | `pytest` |
| Notebooks (required deliverable) | `jupyter` / `jupyterlab` |
| Version control | `git` + GitHub, incremental commits |

---

## 3. Target repo structure

```
multi-llm-debate/
├── app/
│   ├── llm/
│   │   └── client.py           # provider wrappers + call_llm dispatcher
│   ├── config/
│   │   └── schemas.py          # all Pydantic models
│   ├── agents/
│   │   ├── role_assignment.py  # Stage 0 + 0.5
│   │   ├── solver.py           # Stage 1 + 3 (independent solve, refine)
│   │   ├── reviewer.py         # Stage 2 (peer review)
│   │   └── judge.py            # Stage 4
│   ├── evaluation/
│   │   ├── grading.py          # check_answer() — grades against ground truth
│   │   └── metrics.py          # accuracy, consensus rate, improvement rate, judge accuracy
│   └── orchestrator.py         # ties all 5 stages together for one problem
├── data/
│   └── problems.json           # 25 verifiable problems
├── experiments/
│   ├── single_llm_baseline.py
│   ├── simple_voting_baseline.py
│   └── full_system_run.py
├── notebooks/
│   └── results_analysis.ipynb  # loads experiment CSVs, makes required plots
├── tests/
│   ├── test_grading.py
│   ├── test_role_assignment.py
│   └── test_orchestrator.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 4. Build order, step by step

### Step 1 — Environment + skeleton
Create the folder structure above. Add `requirements.txt`, `.env.example`,
`.gitignore`. Commit. This is infrastructure, not logic — get it out of the
way first so every later step has somewhere to live.

```
pip install openai google-generativeai pydantic python-dotenv pandas matplotlib pytest jupyter
```

### Step 2 — Problem dataset
Build `data/problems.json`: 25 problems across the four suggested categories,
each with `id`, `category`, `question`, `correct_answer`, `answer_type`,
`solution_notes`. Verify every answer yourself (by hand or brute-force script)
before trusting it — an unverified "verifiable" answer defeats the entire
point of this dataset.

**Hard rule going forward: `correct_answer` and `solution_notes` are never
sent in a prompt to any Solver/Reviewer/Judge.** Only your own grading code
reads them.

### Step 3 — LLM client wrapper (`app/llm/client.py`)
One function per provider (`call_openai`, `call_gemini`), same signature:
`(model, system_prompt, user_prompt) -> str`. Then one dispatcher,
`call_llm(provider, model, system_prompt, user_prompt)`, that every agent
calls — never the provider-specific functions directly. This is the seam
that lets you assign different models to different roles later without
touching agent code.

Test each wrapper in isolation with a trivial prompt before building
anything on top of it.

### Step 4 — Pydantic schemas (`app/config/schemas.py`)
Define the shape of every stage's output, matching the assignment's example
JSON (you can adapt field names, but keep the assignment's intent):

- `SolverAnswer` — `reasoning`, `final_answer` (used by Stage 1 and the
  single-LLM baseline)
- `RoleSelfAssessment` — `role_preferences`, `confidence_by_role`, `reasoning`
  (Stage 0)
- `PeerReview` — `solution_id`, `strengths`, `weaknesses`, `errors`,
  `suggested_changes`, `overall_assessment` (Stage 2)
- `RefinedSolution` — `changes_made`, `refined_solution`, `refined_answer`,
  `confidence` (Stage 3)
- `JudgeVerdict` — `winner`, `confidence`, `reasoning` (Stage 4)

Why now, before any agent code: every agent function is going to be "build
prompt → call LLM → parse JSON → validate against schema → retry on
failure." Writing the schema first means every agent you write after this
follows the same shape.

### Step 5 — Grading module (`app/evaluation/grading.py`)
`check_answer(correct_answer, model_answer, answer_type) -> (bool | None, str)`.
Handle `integer`, `decimal`, `fraction`, `percentage`, `string` differently —
don't force one comparison strategy on all types. Return `None` (not `False`)
for free-text answers your automatic grader genuinely can't judge with
confidence.

**Test this against your own dataset's correct answers before using it on
any LLM output.** Run every problem's `correct_answer` through the grader as
if it were the model's answer — if any of those fail, the grader is broken,
independent of anything an LLM does.

### Step 6 — Single-LLM baseline (`experiments/single_llm_baseline.py`)
The simplest possible pipeline: one problem in, one `call_llm`, parse the
`SolverAnswer` JSON, grade it, log the row. Run this on all 25 problems.

This does double duty: it's your Phase 3 "Single-LLM Baseline" metric, *and*
it's how you empirically check whether your dataset is actually hard enough
(the assignment requires problems where single-LLM attempts "often fail" —
verify that, don't assume it).

### Step 7 — Simple voting baseline (`experiments/simple_voting_baseline.py`)
Call the same model 3 times independently on the same problem (or 3 different
models/prompts), take the majority answer, grade it. No review, no
refinement, no judge. This is your second Phase 3 baseline, and it's cheap to
build once Step 6 exists — mostly a loop around it.

### Step 8 — Stage 0 + 0.5: role assignment (`app/agents/role_assignment.py`)
- Stage 0: one LLM call per candidate model, asking it to self-assess
  confidence across roles (`RoleSelfAssessment` schema).
- Stage 0.5: **plain Python, no LLM call.** Given 4 candidates' confidence
  scores across roles, assign roles to maximize total confidence without
  double-assigning anyone. At this scale (4 candidates, 4 roles), a
  greedy highest-confidence-first assignment is defensible and simple; the
  formal version of this problem is called the "assignment problem" (solved
  properly by the Hungarian algorithm) if you want to note the connection.

Write this as a pure function you can unit test with fabricated confidence
scores — no API calls needed to verify the logic is correct.

### Step 9 — Stage 1: independent solving (`app/agents/solver.py`)
Three concurrent calls (`asyncio.gather`), each with only `problem['question']`
in the prompt — no communication between them, no correct answer, no
solution notes. Parse each into `SolverAnswer`.

### Step 10 — Stage 2: peer review (`app/agents/reviewer.py`)
6 concurrent calls: each solver reviews each of the other two solutions,
producing a `PeerReview`. Each review call needs: the peer's full solution
text, but NOT the ground-truth answer.

### Step 11 — Stage 3: refinement (`app/agents/solver.py`, extend)
3 calls: each solver receives its own original solution plus the 2 reviews
it received about it, and produces a `RefinedSolution`. It must address each
critique (accept or defend), not just silently rewrite.

### Step 12 — Stage 4: judgment (`app/agents/judge.py`)
1 call: the Judge receives all 3 original solutions, all 6 reviews, and all
3 refined solutions, and produces a `JudgeVerdict` naming a winner. Map the
winner back to that solver's `refined_answer` — that's the system's final
answer for the problem.

### Step 13 — Orchestration (`app/orchestrator.py`)
One function, `run_full_pipeline(problem) -> dict`, that calls Steps 8–12 in
order for a single problem and returns everything: role assignment, all
three original solutions, all reviews, all refined solutions, the verdict,
and the final answer. This is the function `experiments/full_system_run.py`
will call in a loop over all 25 problems.

Build and manually inspect this on **one problem** before running it on all
25 — read the Critic's actual reviews. Are they substantive, or generic
agreement? That's a real signal about whether Stage 2 is working as intended.

### Step 14 — Full run + logging (`experiments/full_system_run.py`)
Loop `run_full_pipeline` over all 25 problems. For each, log to a row:
problem id, category, each stage's answer, whether Stage 1 solvers agreed
(consensus), whether refinement changed each solver's answer (improvement),
whether the Judge's pick was correct, tokens/latency per call, final
correctness. Save to CSV.

### Step 15 — Metrics (`app/evaluation/metrics.py`)
Compute, from the logged CSV via pandas groupby/apply:
- **Overall Accuracy** — % where final answer is correct
- **Improvement Rate** — % where a solver's refined answer became correct
  when its Stage-1 answer wasn't
- **Consensus Rate** — % where all 3 Stage-1 answers matched before any
  debate happened
- **Judge Accuracy** — restricted to problems where solvers disagreed, %
  where the Judge picked the correct one

### Step 16 — Plots (required deliverable)
At minimum: accuracy comparison bar chart across the three pipelines
(single-LLM / voting / full system), and a breakdown of the four metrics
above by problem category. Build this in `notebooks/results_analysis.ipynb`
so it's inspectable, not just a script that dumps PNGs.

### Step 17 — README + submission polish
README needs: what this is, architecture diagram (can reuse the one above),
setup/run instructions, and a results summary. Commit incrementally as you
complete each step above — don't batch everything into one commit at the end,
since the assignment explicitly checks for that in group submissions.

---

## 5. What to build first, concretely

Given nothing exists yet: **Step 1 (skeleton) → Step 2 (dataset) → Step 3
(LLM client) → Step 5 (grading) → Step 6 (single-LLM baseline)**, in that
order, before touching Stage 0. Those five give you a working, testable,
loggable pipeline on the simplest possible case — everything from Stage 0
onward is just adding more calls and more structure around that same core
loop.
