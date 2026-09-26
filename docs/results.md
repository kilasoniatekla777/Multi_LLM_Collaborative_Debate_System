# Experimental Results

## 1. Overview

Briefly explain:
- 25 benchmark questions
- 4 categories
- 3 systems compared
- same underlying model
- objective answer verification

## 2. Accuracy Comparison

Table:

| System | Correct | Total | Accuracy |
|---|---:|---:|---:|
| Single LLM | 12 | 25 | 48% |
| Majority Vote | 12 | 25 | 48% |
| Independent Solvers + Judge | 13 | 25 | 52% |
| Full Debate | 11 | 25 | 44% |

Explain what the numbers show.

Include:
`analysis/plots/accuracy_comparison.png`

## 3. Initial vs Refined Solutions

| Metric | Result |
|---|---:|
| Initial solver accuracy | 45.33% |
| Refined solver accuracy | 44.00% |
| Improvement rate | 2.44% |
| Damage rate | 5.88% |

Explain that refinement sometimes corrected an incorrect solution, but could also introduce an error into a correct solution.

Include the refinement plot.

## 4. Peer Review Performance

| Metric | Result |
|---|---:|
| Total reviews | 150 |
| Correct assessments | 115 |
| Incorrect assessments | 21 |
| Partially correct | 14 |
| Error detection rate | 32.93% |
| False criticism rate | 11.76% |

Explain that peer review was not perfectly reliable.

## 5. Consensus Analysis

| Metric | Result |
|---|---:|
| Consensus rate | 40% |
| Consensus accuracy | 90% |

Explain the difference between:
- how often agents agreed
- whether their agreement was correct

Include consensus plots.

## 6. Judge Performance

Compare:
- Independent Solvers + Judge: 52%
- Full Debate Judge: 44%

Explain what this means without claiming that one approach is universally better.

## 7. Computational Cost

### Token Usage

| System | Calls | Input | Output | Total |
|---|---:|---:|---:|---:|
| Single LLM | 25 | 3,207 | 9,272 | 12,479 |
| Independent + Judge | 100 | 49,386 | 34,318 | 83,704 |
| Full Debate | 325 | 269,545 | 85,762 | 355,307 |

### Latency

Compare average latency per question.

### Cost

Compare estimated API cost.

Explain the trade-off:
more collaboration → substantially more calls/tokens/cost.

## 8. Main Findings

Summarize the experimental observations.

For example:

- The Full Debate system did not achieve the highest accuracy in this experiment.
- Independent Solvers + Judge achieved 52%.
- Refinement produced both corrections and regressions.
- Consensus was relatively uncommon but highly accurate when it occurred.
- Peer review detected only a portion of genuine errors.
- Collaboration substantially increased computational cost and latency.

## 9. Limitations

Mention:

- only 25 questions
- one underlying LLM/model family
- results depend on prompts
- deterministic role assignment
- cost estimates depend on API pricing
- peer-review metrics use the implemented final-answer-level evaluation
- Stage 0 role-assessment token usage was not included in the recorded cost totals

## 10. Conclusion

A short factual conclusion connecting the results to the research question.