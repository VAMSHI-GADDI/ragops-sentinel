from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


DEFAULT_ALLOWED_TOOLS = {
    "ragops_retrieval_tool",
    "ragops_diagnosis_tool",
    "ragops_repair_tool",
}


BLOCKED_TOOL_KEYWORDS = {
    "delete",
    "remove",
    "trash",
    "shell",
    "bash",
    "powershell",
    "terminal",
    "exec",
    "subprocess",
    "credential",
    "secret",
    "token",
    "env",
}


@dataclass(frozen=True)
class ToolPolicyResult:
    is_allowed: bool
    tool_name: str
    reason: str


def validate_tool_call(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    *,
    allowed_tools: set[str] | None = None,
) -> ToolPolicyResult:
    allowed = allowed_tools or DEFAULT_ALLOWED_TOOLS
    args_text = str(arguments or {}).lower()
    tool_text = tool_name.lower()

    if tool_name not in allowed:
        return ToolPolicyResult(
            is_allowed=False,
            tool_name=tool_name,
            reason="tool_not_allowlisted",
        )

    for keyword in BLOCKED_TOOL_KEYWORDS:
        if keyword in tool_text or keyword in args_text:
            return ToolPolicyResult(
                is_allowed=False,
                tool_name=tool_name,
                reason=f"blocked_keyword:{keyword}",
            )

    return ToolPolicyResult(
        is_allowed=True,
        tool_name=tool_name,
        reason="allowed",
    )


def validate_tool_call_dict(tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, object]:
    return asdict(validate_tool_call(tool_name, arguments))
