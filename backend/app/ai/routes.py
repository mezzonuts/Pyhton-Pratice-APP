from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.ai.provider import (
    ProviderType,
    ProviderConfig,
    AIProviderManager,
    AIResponse,
)
from app.ai.prompts import (
    get_socratic_hint,
    generate_review_prompt,
    generate_problem_prompt,
)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Global manager instance - in production, use dependency injection
_ai_manager: AIProviderManager | None = None


def get_ai_manager() -> AIProviderManager:
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIProviderManager()
    return _ai_manager


# ──────────────────────────────────────────────────────────────────────
# Provider CRUD
# ──────────────────────────────────────────────────────────────────────


@router.get("/providers", response_model=List[ProviderConfig], tags=["ai"])
async def list_providers(manager: AIProviderManager = Depends(get_ai_manager)):
    """List all configured AI providers."""
    return manager.list_providers()


@router.post("/providers", response_model=ProviderConfig, tags=["ai"])
async def add_provider(
    provider: ProviderConfig,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Add a new AI provider."""
    manager.register_provider(provider)
    return provider


@router.put("/providers/{provider_id}", response_model=ProviderConfig, tags=["ai"])
async def update_provider(
    provider_id: str,
    provider_update: ProviderConfig,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Update an existing AI provider."""
    if provider_id not in manager._providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} not found",
        )
    update_data = provider_update.model_dump(exclude_unset=True)
    provider = manager._providers[provider_id]
    for key, value in update_data.items():
        setattr(provider, key, value)
    # Reset is_default if being cleared
    if "is_default" in update_data and not update_data["is_default"]:
        # manager.set_default_provider(provider_id)  # handled elsewhere
        pass
    return provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["ai"])
async def remove_provider(
    provider_id: str,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Remove an AI provider."""
    if provider_id not in manager._providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} not found",
        )
    manager.unregister_provider(provider_id)


# ──────────────────────────────────────────────────────────────────────
# Provider test connection
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/providers/{provider_id}/test",
    tags=["ai"],
    response_model=dict,
)
async def test_provider_connection(
    provider_id: str,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Test connection to a specific AI provider."""
    result = await manager.test_connection(provider_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Connection test failed"),
        )
    return result


# ──────────────────────────────────────────────────────────────────────
# Socratic hint endpoint
# ──────────────────────────────────────────────────────────────────────

@router.post("/hint", tags=["ai"], response_model=dict)
async def get_socratic_hint(
    request: dict,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Get a socratic hint for user code.

    Body: { mission_id, user_code, error_type }
    Returns: hint text (no code), hint_type (conceptual/analogy/ELI5)
    """
    mission_id = request.get("mission_id", "")
    user_code = request.get("user_code", "")
    error_type = request.get("error_type", "conceptual")

    # Determine tier from mission context (simplified)
    # In production, fetch from DB
    tier = 0  # default to tier 0

    hint_text = get_socratic_hint(tier, error_type)

    # Ensure no code is returned
    if "```" in hint_text or "def " in hint_text or "import " in hint_text:
        hint_text = "Keep thinking about what the problem is asking."

    return {
        "hint": hint_text,
        "hint_type": error_type,
        "mission_id": mission_id,
        "tier": tier,
    }


# ──────────────────────────────────────────────────────────────────────
# AI Review endpoint
# ──────────────────────────────────────────────────────────────────────

@router.post("/review", tags=["ai"], response_model=dict)
async def _get_ai_review(
    request: dict,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Get AI Senior Engineer review of code.

    Body: { mission_id, code, grader_result }
    Returns: review text (specific line references, Pythonic suggestions, potential bugs)
    """
    mission_id = request.get("mission_id", "")
    code = request.get("code", "")
    grader_result = request.get("grader_result", {})

    if not code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No code provided",
        )

    prompt = generate_review_prompt(code, grader_result)

    # Execute via default provider
    if not manager._providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No AI providers configured",
        )

    default_provider = manager.get_default_provider()
    try:
        from app.ai.provider import AIResponse
        import aiohttp

        messages = [{"role": "user", "content": prompt}]
        response = await manager.execute_request(
            messages=messages,
            provider_id=default_provider.id,
            role="socratic",
            temperature=0.3,
            stream=False,
        )

        review_text = response.content
        # Ensure review has line references format
        if "Line" not in review_text and "```" not in review_text:
            # Prepend line reference format
            lines = review_text.split("\n")
            formatted = []
            for i, line in enumerate(lines[:8], 1):
                formatted.append(f"{i}. **Line {i}**: {line}")
            review_text = "\n".join(formatted)

        return {
            "review": review_text,
            "mission_id": mission_id,
            "provider": default_provider.name,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI review failed: {str(e)}",
        )


# ──────────────────────────────────────────────────────────────────────
# Dynamic problem generator endpoint
# ──────────────────────────────────────────────────────────────────────

@router.post("/generate-problem", tags=["ai"], response_model=dict)
async def _generate_problem(
    request: dict,
    manager: AIProviderManager = Depends(get_ai_manager),
):
    """Generate a dynamic programming problem.

    Body: { topic, tier, difficulty }
    Returns: { ticket_markdown, starter_code, test_file, expected_interface }
    """
    topic = request.get("topic", "")
    tier = request.get("tier", 0)
    difficulty = request.get("difficulty", "medium")

    if not topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic is required",
        )

    default_provider = manager.get_default_provider()
    prompt = generate_problem_prompt(topic, tier, difficulty)

    messages = [{"role": "user", "content": prompt}]

    try:
        response = await manager.execute_request(
            messages=messages,
            provider_id=default_provider.id,
            role="socratic",
            temperature=0.7,
            stream=False,
        )

        # Parse the JSON response from the AI
        import json

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: generate structured output manually
            result = {
                "ticket_markdown": f"## {topic.title()}\n\nDescription: Implement a solution for {topic}.\n\nAcceptance criteria: ...\n\nDifficulty: {difficulty}",
                "starter_code": f"def solve_{topic.lower()}(x):\n    '''Solve the {topic} problem.'''\n    return None",
                "test_file": f"def test_{topic.lower()}():\n    '''Test for {topic}.'''\n    assert False\n",
                "expected_interface": f"def solve_{topic.lower()}(x) -> int: ...",
            }

        return {
            "ticket_markdown": result.get("ticket_markdown", ""),
            "starter_code": result.get("starter_code", ""),
            "test_file": result.get("test_file", ""),
            "expected_interface": result.get("expected_interface", ""),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Problem generation failed: {str(e)}",
        )