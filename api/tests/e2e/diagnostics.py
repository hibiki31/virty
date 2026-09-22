"""task logから実在するsource位置と例外型だけを取り出す。"""

import re
from pathlib import Path
from typing import TypedDict


class DiagnosticFrame(TypedDict):
    file: str
    line: int


class TaskDiagnostic(TypedDict):
    exceptionType: str | None
    frames: list[DiagnosticFrame]


def _exception_names() -> set[str]:
    names: set[str] = set()
    seen: set[type[BaseException]] = set()
    pending = [BaseException]
    while pending:
        exception = pending.pop()
        if exception in seen:
            continue
        seen.add(exception)
        names.add(exception.__name__)
        names.add(f"{exception.__module__}.{exception.__qualname__}")
        pending.extend(exception.__subclasses__())
    return names


def task_diagnostic(log: str | None, source_root: Path) -> TaskDiagnostic:
    """本文・source code・外部pathを診断artifactへ出さない。"""

    result: TaskDiagnostic = {"exceptionType": None, "frames": []}
    if not log:
        return result
    allowed_directories = {"agent", "ansible", "auth", "dashboard", "domain", "exporter", "flavor", "images", "mixin", "module", "network", "node", "project", "storage", "task", "user"}
    root = source_root.resolve()
    allowed_types = _exception_names()
    for line in log.splitlines():
        frame = re.fullmatch(r'  File "([^"\n]+)", line ([0-9]+), in .*', line)
        if frame:
            path = Path(frame[1]).resolve()
            if not path.is_relative_to(root):
                continue
            relative = path.relative_to(root)
            is_source = len(relative.parts) == 1 or relative.parts[0] in allowed_directories or relative.parts[:2] == ("tests", "e2e")
            if is_source and path.suffix == ".py" and path.is_file():
                result["frames"].append({"file": relative.as_posix(), "line": int(frame[2])})
        else:
            candidate = line.partition(":")[0]
            if candidate in allowed_types:
                result["exceptionType"] = candidate
    return result
