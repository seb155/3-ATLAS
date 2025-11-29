"""
CORTEX Orchestrator

Main ReAct loop for autonomous task execution.
Pattern: Think → Act → Observe → Repeat
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent execution state."""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_CONFIRMATION = "waiting_confirmation"


@dataclass
class AgentStep:
    """Represents a single step in the ReAct loop."""
    iteration: int
    state: AgentState
    thought: Optional[str] = None
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    error: Optional[str] = None


class Orchestrator:
    """
    Main orchestrator for CORTEX agent execution.

    Implements the ReAct pattern:
    1. THINK - Reason about the current state and next action
    2. ACT - Execute a tool
    3. OBSERVE - Process the result
    4. REPEAT - Continue until task is complete or max iterations
    """

    def __init__(
        self,
        llm_provider,
        tools: List[Any],
        context_manager,
        max_iterations: int = 20,
        require_confirmation: bool = True
    ):
        self.llm = llm_provider
        self.tools = {tool.name: tool for tool in tools}
        self.context = context_manager
        self.max_iterations = max_iterations
        self.require_confirmation = require_confirmation
        self.steps: List[AgentStep] = []

    async def run(self, task: str, context_blocks: List[str] = None) -> Dict[str, Any]:
        """
        Execute a task autonomously.

        Args:
            task: The task description
            context_blocks: Optional list of context block IDs to include

        Returns:
            Dict with result, steps taken, and metadata
        """
        logger.info(f"Starting task: {task}")

        # Assemble context
        assembled_context = await self.context.assemble(task, context_blocks)

        # Build system prompt with context
        system_prompt = self._build_system_prompt(assembled_context)

        # Initialize conversation
        messages = [{"role": "user", "content": task}]

        for iteration in range(self.max_iterations):
            logger.info(f"Iteration {iteration + 1}/{self.max_iterations}")

            # THINK + ACT: Get LLM response
            step = AgentStep(iteration=iteration + 1, state=AgentState.THINKING)

            try:
                response = await self.llm.chat_with_tools(
                    messages=messages,
                    tools=list(self.tools.values()),
                    system_prompt=system_prompt
                )

                # Check if LLM wants to use a tool
                if response.tool_calls:
                    step.state = AgentState.ACTING

                    for tool_call in response.tool_calls:
                        step.action = tool_call.name
                        step.action_input = tool_call.input

                        # Check if confirmation required
                        if self.require_confirmation and self._needs_confirmation(tool_call):
                            step.state = AgentState.WAITING_CONFIRMATION
                            self.steps.append(step)
                            return {
                                "status": "waiting_confirmation",
                                "step": step,
                                "tool_call": tool_call,
                                "message": f"Confirm action: {tool_call.name}"
                            }

                        # OBSERVE: Execute tool and get result
                        step.state = AgentState.OBSERVING
                        result = await self._execute_tool(tool_call)
                        step.observation = result

                        # Add to conversation
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user",
                            "content": f"Tool result for {tool_call.name}: {result}"
                        })

                else:
                    # No tool call = task complete
                    step.state = AgentState.COMPLETED
                    step.thought = response.text
                    self.steps.append(step)

                    return {
                        "status": "completed",
                        "result": response.text,
                        "steps": self.steps,
                        "iterations": iteration + 1
                    }

                self.steps.append(step)

            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {e}")
                step.state = AgentState.FAILED
                step.error = str(e)
                self.steps.append(step)

                return {
                    "status": "failed",
                    "error": str(e),
                    "steps": self.steps,
                    "iterations": iteration + 1
                }

        # Max iterations reached
        return {
            "status": "max_iterations",
            "message": f"Reached maximum iterations ({self.max_iterations})",
            "steps": self.steps,
            "iterations": self.max_iterations
        }

    async def continue_after_confirmation(self, confirmed: bool) -> Dict[str, Any]:
        """Continue execution after user confirmation."""
        # TODO: Implement continuation logic
        pass

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build the system prompt with assembled context."""
        return f"""You are CORTEX, an expert software engineer AI assistant.

## YOUR CAPABILITIES
You can read, write, and modify files. You can search code and execute commands.

## PROJECT CONTEXT
{context.get('repo_map', 'No repo map available')}

## CONTEXT BLOCKS
{context.get('blocks_summary', 'No additional context')}

## RULES
1. ALWAYS read a file BEFORE modifying it
2. NEVER invent code - verify imports, function names, etc.
3. Make MINIMAL and TARGETED modifications
4. After modification, verify with tests or commands if possible
5. If unsure, say so

## PROCESS
1. Analyze the request
2. Explore relevant code (search, read_file)
3. Plan modifications
4. Implement step by step
5. Verify the result

Think step by step and explain your reasoning."""

    def _needs_confirmation(self, tool_call) -> bool:
        """Check if a tool call requires user confirmation."""
        # Write operations typically need confirmation
        dangerous_tools = ["write_file", "edit_file", "run_command", "git_commit"]
        return tool_call.name in dangerous_tools

    async def _execute_tool(self, tool_call) -> str:
        """Execute a tool and return the result."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            return f"ERROR: Unknown tool: {tool_call.name}"

        try:
            result = await tool.execute(**tool_call.input)
            return result
        except Exception as e:
            return f"ERROR: {e}"
