from __future__ import annotations

from pathlib import Path

from .llm import LLMClient
from .memory import ConversationMemory
from .prompts import SYSTEM_PROMPT, build_review_prompt
from .schemas import FileContent, ReviewContext
from tools.ast_tool import analyze_path
from tools.file_tool import read_python_files


class CodeReviewAgent:
    """协调 File Tool、AST Tool、Memory 和 LLM 的核心 Agent。"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
        self.memory = ConversationMemory()

    def review_path(self, path: Path, user_request: str) -> str:
        files = read_python_files(path)
        if not files:
            raise ValueError(f"目标中没有找到可审查的 Python 文件：{path}")

        analysis = analyze_path(path)

        context = ReviewContext(
            user_request=user_request,
            files=files,
            static_analysis=[analysis.to_text()],
        )

        files_text = "\n\n".join(
            f"===== {item.path} =====\n{item.content}"
            for item in context.files
        )

        prompt = build_review_prompt(
            user_request=user_request,
            files_text=files_text,
            static_analysis="\n".join(context.static_analysis),
            memory=self.memory.render(),
        )

        result = self.llm.complete(SYSTEM_PROMPT, prompt)

        self.memory.add("user", user_request)
        self.memory.add("assistant", result)

        return result
