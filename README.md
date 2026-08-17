# AI Research Debate

A multi-agent system that debates AI/ML research questions (Researcher, ML
Engineer, Critical Reviewer, Judge), and empirically tests whether that
debate actually improves answer quality over a single LLM.

## Status: early scaffolding (Phase 1 in progress)

What exists so far:
- `app/llm/client.py` -- provider wrappers (OpenAI and Gemini implemented)
- `data/debate_problems_25.json` -- the Phase 1 problem set: 25 verifiable
  problems across math/logic, physics, logic puzzles, and game theory, each
  with a `correct_answer` and `solution_notes` for scoring the Judge later
- `tests/test_llm_client.py` -- smoke tests for the LLM client

Not yet built: agents (Solver/Judge roles), structured output schemas,
evaluation harness (accuracy, consensus rate, judge accuracy, plots).

Note: `data/research_questions_25.json` is a leftover from an earlier framing
of this project (open-ended AI/ML research questions, not verifiable
problems) and is no longer used -- `debate_problems_25.json` is the real
Phase 1 dataset.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in your API keys
pytest  # runs whatever tests have keys available for them
```
