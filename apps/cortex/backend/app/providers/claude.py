"""
Claude Provider

Anthropic Claude API integration.
"""

from typing import List, Dict, Any, Optional
import logging

from .base import LLMProvider, LLMResponse, ToolCall

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (as of 2024)
CLAUDE_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude provider.

    Supports:
    - Claude 3.5 Sonnet (default)
    - Claude 3 Opus
    - Claude 3 Haiku
    - Tool use
    - Long context (200K tokens)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_tools(self) -> bool:
        return True

    @property
    def max_context_tokens(self) -> int:
        return 200000  # Claude supports 200K context

    @property
    def client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat request to Claude."""
        try:
            # Build request
            request_kwargs = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": messages,
            }

            if system_prompt:
                request_kwargs["system"] = system_prompt

            if tools:
                request_kwargs["tools"] = self._format_tools(tools)

            # Make request
            response = self.client.messages.create(**request_kwargs)

            # Parse response
            text = None
            tool_calls = []

            for block in response.content:
                if hasattr(block, 'text'):
                    text = block.text
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block.id,
                        name=block.name,
                        input=block.input
                    ))

            # Calculate cost
            cost = self.calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            return LLMResponse(
                text=text,
                tool_calls=tool_calls,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                model=self.model,
                cost_usd=cost
            )

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """
        Claude doesn't have native embeddings.
        This method raises an error - use OpenAI or local embeddings instead.
        """
        raise NotImplementedError(
            "Claude doesn't support embeddings. Use OpenAI or local embeddings."
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on Claude pricing."""
        pricing = CLAUDE_PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def _format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict]:
        """Format tools for Claude API."""
        formatted = []
        for tool in tools:
            formatted.append({
                "name": tool.name if hasattr(tool, 'name') else tool.get('name'),
                "description": tool.description if hasattr(tool, 'description') else tool.get('description'),
                "input_schema": tool.input_schema if hasattr(tool, 'input_schema') else tool.get('input_schema')
            })
        return formatted
