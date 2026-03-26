"""LLM API client for intent routing."""

import json
from typing import Any

import httpx

from config import settings


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self):
        self.base_url = settings.llm_api_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model
        self.timeout = 60.0

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_iterations: int = 5,
    ) -> str:
        """Chat with LLM using tool calling.

        Args:
            messages: Conversation history with role/content
            tools: List of tool schemas
            max_iterations: Max tool call iterations

        Returns:
            Final response from LLM
        """
        conversation = messages.copy()

        for _ in range(max_iterations):
            response = await self._call_llm(conversation, tools)

            # Check if LLM wants to call a tool
            if response.get("tool_calls"):
                tool_calls = response["tool_calls"]
                conversation.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls,
                })

                # Execute each tool call
                for tool_call in tool_calls:
                    result = await self._execute_tool(tool_call)
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result),
                    })
            else:
                # LLM returned final answer
                return response.get("content", "")

        return "I couldn't complete that request. Please try rephrasing."

    async def _call_llm(
        self, messages: list[dict], tools: list[dict]
    ) -> dict:
        """Make a chat completion request to the LLM."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]

    async def _execute_tool(self, tool_call: dict) -> Any:
        """Execute a tool call and return the result."""
        from services.lms_api import lms_api

        function = tool_call["function"]
        name = function["name"]
        arguments = json.loads(function["arguments"])

        try:
            if name == "get_items":
                return await lms_api.get_items()
            elif name == "get_learners":
                return await lms_api.get_learners()
            elif name == "get_scores":
                return await lms_api.get_scores(arguments.get("lab"))
            elif name == "get_pass_rates":
                return await lms_api.get_pass_rates(arguments.get("lab"))
            elif name == "get_timeline":
                return await lms_api.get_timeline(arguments.get("lab"))
            elif name == "get_groups":
                return await lms_api.get_groups(arguments.get("lab"))
            elif name == "get_top_learners":
                return await lms_api.get_top_learners(
                    arguments.get("lab"), arguments.get("limit", 5)
                )
            elif name == "get_completion_rate":
                return await lms_api.get_completion_rate(arguments.get("lab"))
            elif name == "trigger_sync":
                return await lms_api.trigger_sync()
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}


# Global client instance
llm_client = LLMClient()
