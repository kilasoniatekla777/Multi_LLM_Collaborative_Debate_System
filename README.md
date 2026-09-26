# Multi-LLM Collaborative Debate & Evaluation System

A research project that experimentally evaluates whether **iterative multi-agent collaboration improves LLM problem-solving accuracy** compared with a single LLM and simpler multi-agent approaches.

The system uses multiple LLM agents that independently solve problems, review each other's solutions, refine their answers, and use a final Judge to select the strongest solution.

---

## Research Question

> **Does iterative multi-agent debate improve LLM problem-solving accuracy compared with a single LLM and simpler multi-agent approaches?**

The project also investigates:

* Can agents detect genuine errors in other agents' solutions?
* Can peer feedback correct incorrect solutions?
* Can peer feedback make correct solutions worse?
* Does consensus correspond to correctness?
* How accurately can a Judge select the strongest solution?
* What are the token, latency, and cost trade-offs of collaboration?
* Does adaptive role assignment provide useful information?

---

## System Architecture

The full collaborative system consists of four LLM agents:

* **3 Solver agents**
* **1 Judge agent**

The pipeline is:

```text
                    User Question
                         │
                         ▼
                Stage 0: Role
                Self-Assessment
                         │
                         ▼
             Stage 0.5: Deterministic
                 Role Assignment
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Solver 1    Solver 2    Solver 3
             │           │           │
             └───────┬───┴───┬───────┘
                     ▼
              Stage 2: Peer Review
                 6 Reviews
                     │
                     ▼
             Stage 3: Refinement
              3 Refined Answers
                     │
                     ▼
              Stage 4: Final Judge
                     │
                     ▼
                Final Answer
                     │
                     ▼
              Evaluation & Analysis
```

### Stage 0 — Role Self-Assessment

Each available model evaluates whether it is better suited to the role of:

* Solver
* Judge

The model provides confidence scores and a short explanation.

The model does **not** make the final assignment.

### Stage 0.5 — Role Assignment

A deterministic Python algorithm uses the self-assessment scores to assign:

* 1 Judge
* 3 Solvers

The assignment is reproducible and does not require another LLM call.

### Stage 1 — Independent Solving

The three Solvers independently solve the problem without seeing the other solutions.

### Stage 2 — Peer Review

Every Solver reviews the other two Solvers.

This produces:

```text
3 Solvers × 2 Reviews = 6 Reviews
```

### Stage 3 — Refinement

Each Solver receives the two reviews of its solution and decides whether to:

* accept a criticism and correct the solution
* reject a criticism and defend the original solution

### Stage 4 — Final Judge

The Judge receives the original solutions, peer reviews, and refined solutions.

The Judge selects the strongest final solution based primarily on correctness and reasoning quality.

---

## Benchmark

The final benchmark contains **25 objectively verifiable problems**.

| Category                        | Problems |
| ------------------------------- | -------: |
| Mathematics / Logical Reasoning |        7 |
| Physics / Scientific Reasoning  |        6 |
| Logic / Constraint Satisfaction |        6 |
| Strategic Game Theory           |        6 |
| **Total**                       |   **25** |

Each problem contains:

* question
* category
* difficulty
* correct answer
* reference solution

Reference answers are hidden from the LLM agents during the experiments.

---

## Experimental Systems

The project compares several approaches.

### 1. Single LLM

```text
Question → LLM → Answer
```

One model independently answers each question.

### 2. Majority Vote

```text
Question
   ↓
3 Independent Solvers
   ↓
Majority Vote
   ↓
Answer
```

The three Solvers do not communicate.

### 3. Independent Solvers + Judge

```text
Question
   ↓
3 Independent Solvers
   ↓
Judge
   ↓
Answer
```

The Judge sees the three independent solutions but does not receive peer reviews or refinements.

### 4. Full Collaborative Debate

```text
Question
   ↓
3 Solvers
   ↓
6 Peer Reviews
   ↓
3 Refinements
   ↓
Judge
   ↓
Answer
```

This is the main experimental system.

---

## Evaluation Metrics

### Accuracy

Measures the percentage of questions answered correctly.

### Refinement Improvement Rate

Measures how often an initially incorrect solution becomes correct after refinement.

### Refinement Damage Rate

Measures how often an initially correct solution becomes incorrect after refinement.

### Peer Review Error Detection Rate

Measures how often reviewers correctly identify genuine errors.

### False Criticism Rate

Measures how often reviewers incorrectly criticize a correct solution.

### Consensus Rate

Measures how often the independent Solvers agree.

### Consensus Accuracy

Measures how often consensus answers are correct.

### Judge Accuracy

Measures how often the Judge produces a correct final answer.

### Efficiency

The system records:

* input tokens
* output tokens
* total tokens
* latency
* estimated API cost

---

## Experimental Results

The experiment produced the following overall accuracy results:

| System                      | Correct | Total | Accuracy |
| --------------------------- | ------: | ----: | -------: |
| Single LLM                  |      12 |    25 |  **48%** |
| Majority Vote               |      12 |    25 |  **48%** |
| Independent Solvers + Judge |      13 |    25 |  **52%** |
| Full Debate                 |      11 |    25 |  **44%** |

Other findings:

| Metric                           | Result |
| -------------------------------- | -----: |
| Initial Solver Accuracy          | 45.33% |
| Refined Solver Accuracy          | 44.00% |
| Refinement Improvement Rate      |  2.44% |
| Refinement Damage Rate           |  5.88% |
| Consensus Rate                   | 40.00% |
| Consensus Accuracy               | 90.00% |
| Peer Review Error Detection Rate | 32.93% |
| False Criticism Rate             | 11.76% |

The results show that collaboration did **not automatically improve accuracy** in this experiment. The full debate system produced lower final accuracy than the single-LLM and independent-solver baselines, while requiring substantially more computation.

These findings are specific to this benchmark, model, prompts, and experimental configuration.

---

## Computational Cost

Recorded token usage for the main systems:

| System                      | Calls | Input Tokens | Output Tokens | Total Tokens |
| --------------------------- | ----: | -----------: | ------------: | -----------: |
| Single LLM                  |    25 |        3,207 |         9,272 |       12,479 |
| Independent Solvers + Judge |   100 |       49,386 |        34,318 |       83,704 |
| Full Debate                 |   325 |      269,545 |        85,762 |      355,307 |

The Full Debate system therefore requires substantially more model calls and tokens than the simpler approaches.

The recorded cost comparison covers the main problem-solving stages. Stage 0 role-assessment token usage was not included because it was not recorded in the current experiment.

---

## Project Structure

```text
multi_llm_debate/
│
├── data/
│   └── questions.json
│
├── src/
│   ├── stage0_role_assessment.py
│   ├── stage05_role_assignment.py
│   ├── stage1_solve.py
│   ├── stage2_peer_review.py
│   ├── stage3_refinement.py
│   ├── stage4_judge.py
│   ├── baseline.py
│   ├── majority_vote.py
│   └── evaluation.py
│
├── results/
│   ├── role_assessments.json
│   ├── role_assignments.json
│   ├── initial_solutions.json
│   ├── peer_reviews.json
│   ├── refined_solutions.json
│   ├── final_judgments.json
│   ├── baseline_results.json
│   ├── majority_vote_results.json
│   ├── independent_judge_results.json
│   ├── evaluation_results.json
│   ├── latency_results.json
│   ├── cost_results.json
│   └── final_experiment_results.json
│
├── analysis/
│   ├── analyze_results.py
│   ├── create_plots.py
│   └── plots/
│       ├── accuracy_comparison.png
│       ├── consensus_accuracy.png
│       ├── consensus_rate.png
│       ├── cost_comparison.png
│       ├── improvement_vs_degradation.png
│       ├── judge_accuracy.png
│       ├── latency_comparison.png
│       ├── refinement_improvement.png
│       └── solver_refinement.png
│
├── notebooks/
│   └── results_analysis.ipynb
│
├── docs/
│   ├── methodology.md
│   ├── results.md
│   ├── research_question.md
│   └── evaluation_rubric.md
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd multi_llm_debate
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

---

## Running the Experiment

### 1. Role Assessment

```bash
python3 src/stage0_role_assessment.py
```

### 2. Role Assignment

```bash
python3 src/stage05_role_assignment.py
```

### 3. Independent Solving

```bash
python3 src/stage1_solve.py
```

### 4. Peer Review

```bash
python3 src/stage2_peer_review.py
```

### 5. Refinement

```bash
python3 src/stage3_refinement.py
```

### 6. Final Judge

```bash
python3 src/stage4_judge.py
```

### 7. Baselines

```bash
python3 src/baseline.py
python3 src/majority_vote.py
python3 src/independent_judge.py
```

### 8. Evaluation

```bash
python3 src/evaluation.py
```

### 9. Generate Plots

```bash
python3 analysis/create_plots.py
```

---

## Reproducibility

Intermediate outputs are saved after each stage.

This allows the experiment to be inspected at multiple levels:

```text
Role Assessment
      ↓
Role Assignment
      ↓
Initial Solutions
      ↓
Peer Reviews
      ↓
Refined Solutions
      ↓
Final Judgments
      ↓
Evaluation
```

The system also records token usage and latency for the main LLM stages.

---

## Limitations

This experiment has several limitations:

* The benchmark contains only 25 questions.
* Only one underlying LLM model was used.
* Results depend on prompt design.
* Results depend on the selected benchmark.
* Role assignment is only one possible adaptive assignment strategy.
* Peer-review evaluation uses an answer-level operationalization rather than complete human claim-level annotation.
* API cost estimates depend on the pricing assumptions used.
* Stage 0 token usage was not included in the recorded cost totals.

Therefore, the results should be interpreted as findings from this particular experimental configuration rather than as evidence that multi-agent debate universally improves or harms LLM reasoning.

---

## Detailed Documentation

For the complete experimental design:

* [`docs/methodology.md`](docs/methodology.md)

For detailed experimental findings:

* [`docs/results.md`](docs/results.md)

For the research question:

* [`docs/research_question.md`](docs/research_question.md)

For the evaluation criteria:

* [`docs/evaluation_rubric.md`](docs/evaluation_rubric.md)

---

## Project Goal

The purpose of this project is not to assume that multi-agent collaboration works.

Instead, it experimentally evaluates **when collaboration helps, when it fails, and what computational cost it introduces**.

The system therefore treats multi-agent debate as an empirical question rather than an assumption.
