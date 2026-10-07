from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileContent:
    path: str
    content: str
    lines: int


@dataclass
class ReviewContext:
    user_request: str
    files: list[FileContent] = field(default_factory=list)
    static_analysis: list[str] = field(default_factory=list)


@dataclass
class ChatMessage:
    role: str
    content: str
