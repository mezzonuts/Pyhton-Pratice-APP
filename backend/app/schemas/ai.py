from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.ai.provider import ProviderType


class ProviderConfigWrite(BaseModel):
    id: str = Field(..., description="Unique provider identifier")
    type: str = Field(..., description="Provider type: nine_router, ollama, lm_studio, openai, anthropic, custom")
    name: str = Field(..., description="Human-readable provider name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key (encrypted at rest)")
    model: str = Field(..., description="Default model name")
    fallback_models: List[str] = Field(
        default_factory=list,
        description="Fallback model names in order",
    )
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default provider",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Lower priority = higher preference",
    )


class ProviderConfigRead(BaseModel):
    id: str
    type: ProviderType
    name: str
    base_url: str
    model: str
    fallback_models: List[str] = []
    timeout: float
    max_retries: int
    is_default: bool
    priority: int

    class Config:
        from_attributes = True


class AIHintRequest(BaseModel):
    mission_id: str = Field(..., description="Mission identifier")
    user_code: str = Field(..., description="User's submitted code")
    error_type: str = Field(
        default="conceptual",
        description="Type of hint needed: conceptual/analogy/ELI5",
    )


class AIHintResponse(BaseModel):
    hint: str = Field(..., description="Hint text (no code)")
    hint_type: str = Field(..., description="Conceptual/analogy/ELI5")
    mission_id: str
    tier: int = Field(default=0, description="Problem tier")


class AIReviewRequest(BaseModel):
    mission_id: str = Field(..., description="Mission identifier")
    code: str = Field(..., description="Code to review")
    grader_result: Dict[str, Any] = Field(
        default={},
        description="Grading result with grade, etc.",
    )


class AIReviewResponse(BaseModel):
    review: str = Field(..., description="Senior engineer review with line references")
    mission_id: str
    provider: str = Field(default="", description="Provider name")


class AIProblemGenerateRequest(BaseModel):
    topic: str = Field(..., description="Problem topic/title")
    tier: int = Field(
        default=0,
        ge=0,
        le=4,
        description="Tier: 0=basic, 1=intermediate, 2=advanced, 3=expert, 4=master",
    )
    difficulty: str = Field(
        default="medium",
        description="Difficulty: easy, medium, hard",
    )


class AIProblemGenerateResponse(BaseModel):
    ticket_markdown: str = Field(..., description="Ticket markdown with title, description, acceptance criteria")
    starter_code: str = Field(..., description="Starter Python code")
    test_file: str = Field(..., description="Pytest test file")
    expected_interface: str = Field(
        ..., description="Expected function/method signature"
    )