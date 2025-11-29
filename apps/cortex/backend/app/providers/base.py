"""
Base LLM Provider

Abstract interface for AI providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    input: Dict[str, Any]


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    text: Optional[str]
    tool_calls: List[ToolCall]
    stop_reason: str
    usage: Dict[str, int]  # input_tokens, output_tokens
    model: str
    cost_usd: float = 0.0


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All AI providers (Claude, Gemini, OpenAI, Ollama) implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def supports_tools(self) -> bool:
        """Whether this provider supports tool use."""
        pass

    @property
    @abstractmethod
    def max_context_tokens(self) -> int:
        """Maximum context window size."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Send a chat request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            tools: Optional list of tool definitions
            **kwargs: Provider-specific options

        Returns:
            LLMResponse with text and/or tool calls
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for token usage.

        Override in subclasses with provider-specific pricing.
        """
        return 0.0


class AIRouter:
    """
    Intelligent router for selecting AI providers.

    Selection criteria:
    - Cost optimization
    - Latency requirements
    - Context size needs
    - Capability requirements (tools, reasoning, etc.)
    """

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None

    def register(self, provider: LLMProvider, default: bool = False):
        """Register a provider."""
        self.providers[provider.name] = provider
        if default or self.default_provider is None:
            self.default_provider = provider.name

    def select(
        self,
        context_tokens: int = 0,
        needs_tools: bool = False,
        prefer_local: bool = False,
        max_cost_per_call: float = None
    ) -> LLMProvider:
        """
        Select the best provider based on requirements.

        Args:
            context_tokens: Estimated context size
            needs_tools: Whether tool use is required
            prefer_local: Prefer local models (Ollama)
            max_cost_per_call: Maximum cost budget

        Returns:
            Selected LLMProvider
        """
        candidates = list(self.providers.values())

        # Filter by capabilities
        if needs_tools:
            candidates = [p for p in candidates if p.supports_tools]

        # Filter by context size
        candidates = [p for p in candidates if p.max_context_tokens >= context_tokens]

        if not candidates:
            # Fall back to default
            return self.providers[self.default_provider]

        # TODO: Implement more sophisticated selection
        # - Cost optimization
        # - Latency tracking
        # - Load balancing

        # For now, just return first candidate
        return candidates[0]

    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Route chat to appropriate provider."""
        provider = self.select(
            context_tokens=kwargs.get('context_tokens', 0),
            needs_tools=kwargs.get('tools') is not None
        )
        return await provider.chat(messages, **kwargs)
