from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_deepseek import ChatDeepSeek


class SoftToolChoiceDeepSeek(ChatDeepSeek):
    """A ChatDeepSeek that never forces a tool choice.

    Thinking mode rejects every forced `tool_choice`, and LangChain sets one
    ("any") as soon as an agent declares a structured output tool. Dropping it
    is what makes thinking mode usable together with ToolStrategy.
    """

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable | BaseTool],
        *,
        tool_choice: dict | str | bool | None = None,
        strict: bool | None = None,
        parallel_tool_calls: bool | None = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, AIMessage]:
        return super().bind_tools(
            tools,
            tool_choice=None,
            strict=strict,
            parallel_tool_calls=parallel_tool_calls,
            **kwargs,
        )
