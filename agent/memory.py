from __future__ import annotations

from collections import deque

from .schemas import ChatMessage


class ConversationMemory:
    """进程级短期记忆，防止单次会话无限增长。"""

    def __init__(self, max_messages: int = 10) -> None:
        self._messages: deque[ChatMessage] = deque(maxlen=max_messages)

    def add(self, role: str, content: str) -> None:
        self._messages.append(ChatMessage(role, content))

    def render(self) -> str:
        if not self._messages:
            return "(无历史上下文)"

        return "\n".join(
            f"{message.role.upper()}: {message.content}"
            for message in self._messages
        )

    def clear(self) -> None:
        self._messages.clear()
