from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent.agent import CodeReviewAgent
from agent.llm import LLMClient


def build_agent() -> CodeReviewAgent:
    return CodeReviewAgent(LLMClient.from_env())


def cmd_review(agent: CodeReviewAgent, target: str, requirement: str) -> int:
    path = Path(target)
    try:
        result = agent.review_path(path, requirement)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


def cmd_ast(target: str) -> int:
    from tools.ast_tool import analyze_path

    try:
        result = analyze_path(Path(target))
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(result.to_text())
    return 0


def cmd_chat(agent: CodeReviewAgent) -> int:
    print("Code Review Agent")
    print("输入 review <文件/目录> [要求] 开始审查，输入 exit 退出。")

    while True:
        try:
            line = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            return 0

        parts = line.split(maxsplit=2)
        if parts[0].lower() != "review" or len(parts) < 2:
            print("用法：review <文件/目录> [审查要求]")
            continue

        requirement = parts[2] if len(parts) == 3 else "全面检查潜在 Bug、代码质量和可维护性。"
        print("\nAgent:")
        try:
            print(agent.review_path(Path(parts[1]), requirement))
        except Exception as exc:
            print(f"[ERROR] {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Review Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="审查 Python 文件或目录")
    review.add_argument("target")
    review.add_argument(
        "--requirement",
        "-r",
        default="全面检查潜在 Bug、代码质量和可维护性。",
    )

    ast_cmd = sub.add_parser("ast", help="只运行 Python AST 静态分析")
    ast_cmd.add_argument("target")

    sub.add_parser("chat", help="进入交互式审查模式")

    args = parser.parse_args()

    if args.command == "ast":
        return cmd_ast(args.target)

    agent = build_agent()

    if args.command == "review":
        return cmd_review(agent, args.target, args.requirement)

    if args.command == "chat":
        return cmd_chat(agent)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
