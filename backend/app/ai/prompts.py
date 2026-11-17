from __future__ import annotations

from typing import Dict, List, Any


SOCRATIC_HINTS: Dict[int, Dict[str, str]] = {
    0: {
        "tier0_eli5": "Think of this problem like a simple recipe. You have ingredients (variables) and steps (logic). What is the very first step you should take? Ignore complex tools - just focus on what you need right now.",
        "tier0_conceptual": "If you were telling a friend how to solve this, what would you say in one simple sentence? Start there.",
    },
    1: {
        "tier1_plus_guide": "You've got the basic ideas. Now, what's the specific piece that's tripping you up? Name exactly one thing you're unsure about, and we'll untangle it.",
        "tier1_analogy": "Picture a toolbox. Which tool feels right for this job? You don't need every tool - just the one that fits.",
    },
    2: {
        "tier2_specific": "Look at the line giving you trouble. What does it want to do and what's actually happening? Compare the two.",
        "tier2_breakdown": "Stop at the exact line number. What should the output be and what are you getting instead? That gap is your clue.",
    },
    3: {
        "tier3_refactor": "You're close. Can you extract one small piece into its own function? That often reveals the pattern.",
        "tier3_dry": "Is the same logic written in two places? Pull it out and name it clearly.",
    },
    4: {
        "tier4_arch": "Step back. Which responsibility should this code own, and which should it delegate? Draw the boundary.",
        "tier4_edge": "What edge case are you not handling? Trace through the unhappy path.",
    },
}


SENIOR_ENGINEER_PROMPT = "You are a Senior Engineering reviewer. Be constructive, specific, and educational.\n\nCode review guidelines:\n- Point to exact line numbers and show the relevant snippet.\n- Explain WHY a pattern is better, not just WHAT.\n- Suggest Pythonic alternatives with brief justification.\n- Flag potential bugs or edge cases.\n- Keep feedback concise - max 8 bullet points.\n\nFormat your review as:\n1. **Line X**: `...` - Comment\n2. **Line Y**: `...` - Comment\n...\nOverall: <one-paragraph summary>\nSuggested improvements:\n- <improvement 1>\n- <improvement 2>"


PROBLEM_GENERATOR_PROMPT = (
    "You are a mission generator for a coding practice platform."
    "Generate:"
    "1. A ticket markdown with title, description, and acceptance criteria."
    "2. Starter Python code that implements the core functionality."
    "3. A test file with at least 2 test cases."
    "4. The expected interface/signature."
    "Topic: {topic}"
    "Tier: {tier} (0=basic, 1=intermediate, 2=advanced, 3=expert, 4=master)"
    "Difficulty: {difficulty} (easy, medium, hard)"
    "Output JSON with keys: ticket_markdown, starter_code, test_file, expected_interface"
    "All code must be Python, runnable, and follow PEP 8."
    "Test file must use pytest."
    "expected_interface should describe the function/method signature."
)


def get_socratic_hint(tier: int, sub_type: str = "conceptual") -> str:
    """Get a socratic hint for the given tier and sub-type."""
    tier_data = SOCRATIC_HINTS.get(tier, SOCRATIC_HINTS[0])
    return tier_data.get(sub_type, tier_data[list(tier_data.keys())[0]])


def generate_review_prompt(code: str, grader_result: dict | None = None) -> str:
    """Generate the senior engineer review prompt with code and grade context."""
    base = SENIOR_ENGINEER_PROMPT
    if grader_result:
        base += f"\n\nGraded result: {grader_result.get('grade', '?')}"
        base += f"\nCode under review:\n```python\n{code}\n```"
    else:
        base += f"\n\nCode under review:\n```python\n{code}\n```"
    return base


def generate_problem_prompt(topic: str, tier: int, difficulty: str) -> str:
    """Generate the dynamic problem generator prompt."""
    return PROBLEM_GENERATOR_PROMPT.format(topic=topic, tier=tier, difficulty=difficulty)