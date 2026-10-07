from __future__ import annotations

from pathlib import Path

from agent.schemas import FileContent

MAX_FILE_BYTES = 256 * 1024
MAX_FILES = 20


def _read_one(path: Path) -> FileContent:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(
            f"文件过大：{path}，单文件限制为 {MAX_FILE_BYTES // 1024} KB。"
        )

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"文件不是 UTF-8 文本：{path}") from exc

    return FileContent(
        path=str(path),
        content=content,
        lines=len(content.splitlines()),
    )


def read_python_files(target: Path) -> list[FileContent]:
    target = target.resolve()

    if not target.exists():
        raise FileNotFoundError(f"目标不存在：{target}")

    if target.is_file():
        if target.suffix != ".py":
            raise ValueError("当前版本只审查 Python 文件（.py）。")
        return [_read_one(target)]

    if not target.is_dir():
        raise ValueError(f"目标不是文件或目录：{target}")

    files = sorted(
        path
        for path in target.rglob("*.py")
        if path.is_file() and ".venv" not in path.parts
    )

    if len(files) > MAX_FILES:
        raise ValueError(
            f"目录包含 {len(files)} 个 Python 文件，最多一次审查 {MAX_FILES} 个。"
        )

    return [_read_one(path) for path in files]
