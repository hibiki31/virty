import ast
from pathlib import Path

import pytest


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
API_ROOT = Path(__file__).resolve().parents[2]


def _exact_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith(("#", "-")):
            continue
        name, separator, version = line.partition("==")
        assert separator and name and version, f"{path.name}:{line_number} はexact pinではありません"
        normalized_name = name.lower().replace("_", "-")
        assert normalized_name not in pins, f"{path.name}で{name}が重複しています"
        pins[normalized_name] = version
    return pins


def test_external_python_sources_parse() -> None:
    sources = list((API_ROOT / "tests" / "external").rglob("*.py"))
    assert sources

    for source in sources:
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))


@pytest.mark.parametrize(
    ("manifest_name", "lock_name"),
    [
        ("requirements.txt", "requirements.lock"),
        ("requirements-dev.txt", "requirements-dev.lock"),
    ],
)
def test_direct_dependencies_match_lock(manifest_name: str, lock_name: str) -> None:
    manifest = _exact_pins(API_ROOT / manifest_name)
    lock = _exact_pins(API_ROOT / lock_name)

    assert manifest
    assert manifest.items() <= lock.items()
