# Methodology

## 1. Research Question

The main research question is:

> Does iterative multi-agent debate improve LLM problem-solving accuracy compared with a single LLM and simpler multi-agent approaches?

Secondary research questions:

- Can agents detect genuine errors in other agents' solutions?
- Can peer feedback turn incorrect solutions into correct ones?
- Can peer feedback make correct solutions worse?
- Does consensus correspond to correctness?
- How accurately can a Judge select the strongest solution?
- What are the latency, token, and cost trade-offs?
- Does dynamic role assignment provide useful information?

---

## 2. System Architecture

The system consists of four LLM agents:

- 3 Solver agents
- 1 Judge agent

The experiment follows these stages:

1. Stage 0 — Role Self-Assessment
2. Stage 0.5 — Deterministic Role Assignment
3. Stage 1 — Independent Solution Generation
4. Stage 2 — Peer Review
5. Stage 3 — Solution Refinement
6. Stage 4 — Final Judge

Overall pipeline:

Question
→ Role Assessment
→ Role Assignment
→ 3 Independent Solvers
→ 6 Peer Reviews
→ 3 Refinements
→ Final Judge
→ Final Answer
→ Evaluation

---

## 3. Benchmark Dataset

The final benchmark contains 25 problems.

| Category | Number |
|---|---:|
| Mathematics / Logical Reasoning | 7 |
| Physics / Scientific Reasoning | 6 |
| Logic / Constraint Satisfaction | 6 |
| Strategic Game Theory | 6 |
| **Total** | **25** |

Each problem contains:

- question
- category
- difficulty
- objectively verifiable correct answer
- reference solution

The reference answers are hidden from the LLM agents during problem solving.

The benchmark was designed to contain problems that:

- require meaningful reasoning
- can produce objectively verifiable answers
- are difficult enough to produce occasional model errors
- do not require current internet information

---

## 4. Stage 0 — Role Self-Assessment

Each available model receives the original problem and evaluates whether it is better suited to:

- Solver
- Judge

The model provides:

- preferred roles
- confidence for each role
- short reasoning summary

The model does not make the final assignment.

This stage provides information used by the deterministic assignment algorithm.

---

## 5. Stage 0.5 — Deterministic Role Assignment

A Python algorithm converts the self-assessment results into a reproducible assignment.

For each candidate Judge `j`:

score(j) =
JudgeConfidence(j)
+
sum(SolverConfidence(i))

for all other models `i`.

The model with the highest score becomes the Judge.

The remaining three models become Solvers.

Tie-breaking is deterministic:

1. highest total score
2. highest Judge confidence
3. lowest model number

This guarantees exactly:

- 1 Judge
- 3 Solvers

for every question.

No LLM call is made during this stage.

---

## 6. Stage 1 — Independent Solving

The three Solvers independently receive the original question.

They do not see:

- other solutions
- peer reviews
- reference answers
- other agents' reasoning

Each Solver produces:

- reasoning
- final answer

The system records:

- response
- latency
- input tokens
- output tokens
- total tokens

This stage establishes the initial solver performance.

---

## 7. Stage 2 — Peer Review

Each Solver reviews the other two Solvers.

Therefore, each question produces:

3 × 2 = 6 reviews.

The reviewers evaluate:

- correctness
- logical validity
- calculations
- assumptions
- edge cases
- completeness
- whether the conclusion follows from the reasoning

Each review contains structured fields such as:

- correctness assessment
- strengths
- weaknesses
- errors
- suggested changes
- overall assessment

The reviewer does not have access to the hidden reference answer.

---

## 8. Stage 3 — Refinement

Each Solver receives:

- the original question
- its original solution
- the two reviews written about that solution

The Solver must evaluate the criticisms rather than automatically accepting them.

For each important criticism, it can:

- accept and correct the solution
- reject the criticism and defend the original solution

The refined response contains:

- changes made
- responses to critiques
- refined reasoning
- refined final answer
- confidence

This stage allows measurement of whether peer feedback improves or damages solutions.

---

## 9. Stage 4 — Final Judge

The Judge receives:

- original question
- all three initial solutions
- all six peer reviews
- all three refined solutions

The Judge selects the strongest final solution.

The Judge is instructed to prioritize:

1. correctness
2. logical validity
3. quality of reasoning
4. consistency between reasoning and conclusion

Style and response length are not intended to determine the selection.

The Judge produces:

- selected solver
- final answer
- reasoning summary
- confidence

---

## 10. Baseline Systems

Three comparison approaches are evaluated.

### Baseline A — Single LLM

Question
→ Single LLM
→ Answer

One model produces one answer.

---

### Baseline B — Majority Vote

Question
→ 3 Independent Solvers
→ Majority Vote
→ Answer

The Solvers do not communicate.

Their final answers are compared and the majority answer is selected.

---

### Baseline C — Independent Solvers + Judge

Question
→ 3 Independent Solvers
→ Judge
→ Answer

The Judge receives the three independent solutions but no peer reviews or refinements.

This isolates the effect of the collaborative debate stages.

---

### Full Collaborative Debate

Question
→ 3 Solvers
→ Peer Review
→ Refinement
→ Judge
→ Answer

The main comparison is therefore between independent multi-agent solving and the full collaborative system.

---

## 11. Evaluation

All final answers are compared against the hidden reference answers.

### Primary Metric

#### Overall Accuracy

Accuracy is:

correct answers / total questions

---

### Solver Metrics

#### Initial Solver Accuracy

Measures how often the initial Solver answers are correct.

#### Refinement Improvement Rate

Measures the proportion of initially incorrect solutions that become correct after refinement.

#### Refinement Damage Rate

Measures the proportion of initially correct solutions that become incorrect after refinement.

---

### Peer Review Metrics

#### Error Detection Rate

Measures how often reviewers correctly identify genuine errors in incorrect solutions.

#### False Criticism Rate

Measures how often reviewers criticize a solution that is actually correct.

---

### Consensus Metrics

#### Consensus Rate

Measures how often the independent Solvers produce the same answer.

#### Consensus Accuracy

Measures how often consensus answers are correct.

---

### Judge Accuracy

Measures how often the final Judge produces a correct answer.

---

## 12. Efficiency Metrics

The experiment records:

- input tokens
- output tokens
- total tokens
- response latency
- estimated API cost

These measurements allow comparison between accuracy and computational resources.

---

## 13. Experimental Controls

To make the comparison meaningful:

- the same benchmark is used for all systems
- the same underlying model is used
- reference answers are hidden from agents
- independent Solvers do not communicate before peer review
- role assignment is deterministic
- structured outputs are used
- all systems are evaluated against the same ground truth

---

## 14. Error Classification

Observed failures are categorized as:

- calculation error
- logical error
- incorrect assumption
- missed edge case
- incomplete solution
- unsupported conclusion
- peer review missed genuine error
- peer review false criticism
- refinement failed to correct
- refinement introduced error
- Judge selected incorrect solution
- consensus incorrect

These categories are used for qualitative error analysis.

---

## 15. Experimental Reproducibility

The experiment stores intermediate results separately:

- `role_assessments.json`
- `role_assignments.json`
- `initial_solutions.json`
- `peer_reviews.json`
- `refined_solutions.json`
- `final_judgments.json`
- `baseline_results.json`
- `majority_vote_results.json`
- `independent_judge_results.json`
- `evaluation_results.json`

This makes it possible to inspect each stage independently rather than evaluating only the final answer.

---

## 16. Limitations

The methodology has several limitations:

- The benchmark contains only 25 questions.
- The experiment uses one underlying LLM model.
- Results can depend on prompt design.
- Results can depend on the particular benchmark questions.
- The role-assessment mechanism is only one possible assignment strategy.
- Token-based cost estimates depend on the pricing assumptions used.
- Peer-review evaluation is based on the implemented answer-level comparison rather than a complete claim-by-claim human annotation.
- Stage 0 role-assessment token usage was not included in the recorded problem-solving cost totals.

Therefore, the experiment measures the behavior of this particular system configuration rather than establishing a universal property of multi-agent LLM systems.