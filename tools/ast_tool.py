from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from .file_tool import read_python_files


@dataclass
class ASTFinding:
    line: int
    category: str
    message: str


@dataclass
class ASTReport:
    files: int = 0
    total_lines: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    findings: list[ASTFinding] = field(default_factory=list)

    def to_text(self) -> str:
        lines = [
            f"文件数量：{self.files}",
            f"总行数：{self.total_lines}",
            f"函数数量：{self.functions}",
            f"类数量：{self.classes}",
            f"导入数量：{self.imports}",
        ]

        if not self.findings:
            lines.append("静态分析未发现预设规则问题。")
            return "\n".join(lines)

        lines.append("预设规则发现：")
        for finding in self.findings:
            lines.append(
                f"- L{finding.line} [{finding.category}] {finding.message}"
            )

        return "\n".join(lines)


class _Visitor(ast.NodeVisitor):
    def __init__(self, report: ASTReport) -> None:
        self.report = report

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.report.functions += 1
        end_line = getattr(node, "end_lineno", node.lineno)
        if end_line - node.lineno + 1 > 80:
            self.report.findings.append(
                ASTFinding(
                    node.lineno,
                    "可维护性",
                    "函数超过 80 行，建议拆分职责。",
                )
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.report.functions += 1
        end_line = getattr(node, "end_lineno", node.lineno)
        if end_line - node.lineno + 1 > 80:
            self.report.findings.append(
                ASTFinding(
                    node.lineno,
                    "可维护性",
                    "异步函数超过 80 行，建议拆分职责。",
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.report.classes += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.report.imports += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.report.imports += len(node.names)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.report.findings.append(
                ASTFinding(
                    node.lineno,
                    "异常处理",
                    "发现裸 except，可能吞掉 KeyboardInterrupt 等异常，建议捕获明确异常类型。",
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self.report.findings.append(
                ASTFinding(
                    node.lineno,
                    "安全",
                    f"调用了 {node.func.id}，如果输入可被外部控制可能产生代码执行风险。",
                )
            )
        self.generic_visit(node)


def analyze_source(source: str, path: str = "<string>") -> ASTReport:
    report = ASTReport(files=1, total_lines=len(source.splitlines()))

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        report.findings.append(
            ASTFinding(
                exc.lineno or 0,
                "语法",
                f"Python 语法解析失败：{exc.msg}",
            )
        )
        return report

    visitor = _Visitor(report)
    visitor.visit(tree)

    for number, line in enumerate(source.splitlines(), start=1):
        if "TODO" in line:
            report.findings.append(
                ASTFinding(number, "维护性", "发现 TODO 标记，请确认是否存在未完成逻辑。")
            )

    if report.total_lines > 500:
        report.findings.append(
            ASTFinding(1, "可维护性", "文件超过 500 行，建议考虑拆分模块。")
        )

    return report


def analyze_path(path: Path) -> ASTReport:
    files = read_python_files(path)
    merged = ASTReport()

    for item in files:
        report = analyze_source(item.content, item.path)
        merged.files += report.files
        merged.total_lines += report.total_lines
        merged.functions += report.functions
        merged.classes += report.classes
        merged.imports += report.imports
        merged.findings.extend(
            ASTFinding(
                finding.line,
                f"{item.path} / {finding.category}",
                finding.message,
            )
            for finding in report.findings
        )

    return merged
