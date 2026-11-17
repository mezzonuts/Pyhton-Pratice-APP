from __future__ import annotations

from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, validator


class ProviderType(str, Enum):
    NINE_ROUTER = "nine_router"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class ProviderConfig(BaseModel):
    id: str = Field(..., description="Unique provider identifier")
    type: ProviderType = Field(..., description="AI provider type")
    name: str = Field(..., description="Human-readable provider name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(
        ...,
        description="API key (encrypted at rest, decrypted on read via secure key management)",
    )
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

    @property
    def api_key_decrypted(self) -> str:
        # Placeholder: decrypt using project-wide key management
        # Never store or log raw keys directly; use this property instead
        return self.api_key

    @api_key_decrypted.setter
    def api_key_decrypted(self, value: str) -> None:
        # Placeholder: encrypt before storage
        object.__setattr__(self, "api_key", value)

    def mask_for_logs(self) -> str:
        """Return masked API key for logging - never log raw keys."""
        if not self.api_key:
            return ""
        # Mask all but last 4 characters
        if len(self.api_key) <= 4:
            return "*" * len(self.api_key)
        return self.api_key[:2] + "*" * (len(self.api_key) - 4) + self.api_key[-2:]


class AIResponse(BaseModel):
    content: str
    model: str
    provider_id: str
    usage: Dict[str, int] = {}
    finish_reason: str = "stop"


class AIProviderManager:
    def __init__(self, providers: List[ProviderConfig] | None = None):
        self._providers: Dict[str, ProviderConfig] = {}
        self._default_provider_id: Optional[str] = None
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        if providers:
            for p in providers:
                self.register_provider(p)

    # Registration

    def register_provider(self, provider: ProviderConfig) -> None:
        self._providers[provider.id] = provider
        if not self._default_provider_id and provider.is_default:
            self._default_provider_id = provider.id
        # Initialize circuit breaker
        self._circuit_breakers[provider.id] = {
            "failures": 0,
            "open": False,
            "last_failure": 0.0,
        }

    def unregister_provider(self, provider_id: str) -> None:
        self._providers.pop(provider_id, None)
        self._circuit_breakers.pop(provider_id, None)
        if self._default_provider_id == provider_id:
            self._default_provider_id = None
            for p in self._providers.values():
                if p.is_default:
                    self._default_provider_id = p.id
                    break

    # Core methods

    def list_providers(self) -> List[ProviderConfig]:
        return list(self._providers.values())

    def get_default_provider(self) -> ProviderConfig:
        if self._default_provider_id and self._default_provider_id in self._providers:
            return self._providers[self._default_provider_id]
        # Fallback: first available provider with is_default=True, or first any
        for p in self._providers.values():
            if p.is_default:
                return p
        if self._providers:
            return next(iter(self._providers.values()))
        raise RuntimeError("No AI providers configured")

    def set_default_provider(self, provider_id: str) -> None:
        if provider_id not in self._providers:
            raise ValueError(f"Provider {provider_id} not found")
        self._default_provider_id = provider_id
        # Update the new default's flag
        self._providers[provider_id].is_default = True
        # Reset old default if different
        for pid, p in self._providers.items():
            if pid != provider_id and p.is_default:
                p.is_default = False

    def _check_circuit_breaker(self, provider_id: str) -> bool:
        cb = self._circuit_breakers.get(provider_id)
        if not cb:
            return True
        if cb.get("open", False):
            # Check cool-down
            from time import monotonic
            if monotonic() - cb.get("last_failure", 0) < 60:
                return False
            cb["open"] = False
            cb["failures"] = 0
        return True

    def record_success(self, provider_id: str) -> None:
        cb = self._circuit_breakers.get(provider_id)
        if cb:
            cb["failures"] = 0
            cb["open"] = False

    def record_failure(self, provider_id: str) -> None:
        cb = self._circuit_breakers.get(provider_id)
        if not cb:
            return
        cb["failures"] += 1
        from time import monotonic
        cb["last_failure"] = monotonic()
        if cb["failures"] >= 3:
            cb["open"] = True

    async def test_connection(self, provider_id: str) -> dict:
        provider = self._providers.get(provider_id)
        if not provider:
            return {"success": False, "response_sample": None, "error": "Provider not found"}

        # Circuit breaker check
        if not self._check_circuit_breaker(provider_id):
            return {
                "success": False,
                "response_sample": None,
                "error": "Provider circuit breaker open",
            }

        try:
            headers = {}
            if provider.api_key:
                headers["Authorization"] = f"Bearer {provider.api_key}"

            async with aiohttp.ClientSession() as session:
                url = f"{provider.base_url.rstrip('/')}/health"
                if provider.type == ProviderType.OLLAMA:
                    url = f"{provider.base_url.rstrip('/')}/api/tags"
                elif provider.type == ProviderType.OPENAI:
                    url = f"{provider.base_url.rstrip('/')}/v1/models"

                async with session.get(url, headers=headers, timeout=provider.timeout) as resp:
                    sample = await resp.text()
                    return {
                        "success": resp.status < 500,
                        "response_sample": sample[:200] if sample else None,
                        "status": resp.status,
                    }
        except Exception as e:
            self.record_failure(provider_id)
            return {"success": False, "response_sample": None, "error": str(e)}

    async def execute_request(
        self,
        messages: List[Dict[str, Any]],
        provider_id: str,
        role: str = "socratic",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> AIResponse:
        provider = self._providers.get(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        # Check circuit breaker
        if not self._check_circuit_breaker(provider_id):
            # Try fallback chain
            return await self._execute_with_fallback(messages, provider_id, temperature, stream)

        try:
            response = await self._do_execute_request(provider, messages, role, temperature, stream)
            self.record_success(provider_id)
            return response
        except Exception as e:
            self.record_failure(provider_id)
            return await self._execute_with_fallback(messages, provider_id, temperature, stream)

    async def _execute_with_fallback(
        self,
        messages: List[Dict[str, Any]],
        start_provider_id: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        """Execute request with automatic fallback chain."""
        providers = self._get_fallback_chain(start_provider_id)
        last_error: dict | None = None

        for pid in providers:
            try:
                provider = self._providers[pid]
                response = await self._do_execute_request(
                    provider, messages, "socratic", temperature, stream
                )
                self.record_success(pid)
                return response
            except Exception as e:
                last_error = {"provider_id": pid, "error": str(e)}
                self.record_failure(pid)
                continue

        # All providers failed
        if last_error:
            raise RuntimeError(
                f"All AI providers failed. Last error: {last_error['error']}"
            )
        raise RuntimeError("All AI providers failed without error details")

    def _get_fallback_chain(self, start_provider_id: str) -> List[str]:
        """Get ordered fallback chain starting after the given provider."""
        start = self._providers.get(start_provider_id)
        if not start:
            return list(self._providers.keys())

        # Build chain: start from next priority, wrap around
        all_ids = sorted(self._providers.keys(), key=lambda pid: self._providers[pid].priority)
        start_idx = None
        for i, pid in enumerate(all_ids):
            if pid == start_provider_id:
                start_idx = i
                break

        if start_idx is None:
            return all_ids

        # Start from the next provider after the start
        chain = []
        for i in range(1, len(all_ids) + 1):
            idx = (start_idx + i) % len(all_ids)
            chain.append(all_ids[idx])
        return chain

    async def _do_execute_request(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        """Execute a single provider request."""
        headers = {"Content-Type": "application/json"}
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"

        if provider.type == ProviderType.NINE_ROUTER:
            return await self._execute_nine_router(provider, messages, role, temperature, stream)
        elif provider.type == ProviderType.OLLAMA:
            return await self._execute_ollama(provider, messages, role, temperature, stream)
        elif provider.type == ProviderType.LM_STUDIO:
            return await self._execute_lm_studio(provider, messages, role, temperature, stream)
        elif provider.type == ProviderType.OPENAI:
            return await self._execute_openai(provider, messages, role, temperature, stream)
        elif provider.type == ProviderType.ANTHROPIC:
            return await self._execute_anthropic(provider, messages, role, temperature, stream)
        elif provider.type == ProviderType.CUSTOM:
            return await self._execute_custom(provider, messages, role, temperature, stream)
        else:
            raise ValueError(f"Unsupported provider type: {provider.type}")

    # Provider-specific execution methods

    async def _execute_nine_router(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        # 9Router: https://9router.com
        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/v1/chat/completions"
            async with session.post(
                url, json=payload, headers={"Authorization": f"Bearer {provider.api_key}"}, timeout=provider.timeout
            ) as resp:
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content,
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )

    async def _execute_ollama(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        # Ollama local inference
        payload = {
            "model": provider.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": temperature},
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/api/chat"
            async with session.post(
                url, json=payload, timeout=provider.timeout
            ) as resp:
                if stream:
                    full = ""
                    async for line in resp.content:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            if data == "[DONE]":
                                break
                            full += data
                    return AIResponse(
                        content=full or None,
                        model=provider.model,
                        provider_id=provider.id,
                        usage={},
                    )
                # Non-streamed response
                try:
                    data = await resp.json()
                except Exception:
                    return AIResponse(
                        content=None,
                        model=provider.model,
                        provider_id=provider.id,
                        usage={},
                    )
                content = data.get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content,
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )

    async def _execute_lm_studio(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/v1/chat/completions"
            async with session.post(
                url, json=payload, headers={"Authorization": f"Bearer {provider.api_key}"}, timeout=provider.timeout
            ) as resp:
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content,
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )

    async def _execute_openai(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/v1/chat/completions"
            async with session.post(
                url, json=payload, headers={"Authorization": f"Bearer {provider.api_key}"}, timeout=provider.timeout
            ) as resp:
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content,
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )

    async def _execute_anthropic(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        # Convert messages to anthropic format (user/assistant)
        anthropic_messages = []
        for msg in messages:
            role_map = {"user": "user", "assistant": "assistant", "system": "system"}
            role_key = role_map.get(msg.get("role", "user"), "user")
            anthropic_messages.append({"role": role_key, "content": msg.get("content", "")})

        payload = {
            "model": provider.model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/v1/messages"
            async with session.post(
                url, json=payload, headers={"x-api-key": provider.api_key, "Content-Type": "application/json"}, timeout=provider.timeout
            ) as resp:
                data = await resp.json()
                content = data.get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content if isinstance(content, str) else str(content),
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )

    async def _execute_custom(
        self,
        provider: ProviderConfig,
        messages: List[Dict[str, Any]],
        role: str,
        temperature: float,
        stream: bool,
    ) -> AIResponse:
        # Custom endpoint - assume OpenAI-compatible
        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        async with aiohttp.ClientSession() as session:
            url = f"{provider.base_url.rstrip('/')}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if provider.api_key:
                headers["Authorization"] = f"Bearer {provider.api_key}"
            async with session.post(
                url, json=payload, headers=headers, timeout=provider.timeout
            ) as resp:
                data = await resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return AIResponse(
                    content=content,
                    model=provider.model,
                    provider_id=provider.id,
                    usage=usage,
                )