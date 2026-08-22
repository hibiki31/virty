import os
import tempfile
from pathlib import Path

from module.xmllib import redact_domain_xml_secrets


def scrub_domain_xml_directory(data_root: str) -> int:
    """既存domain XMLのconsole credentialを起動時に原子的に除去する。"""

    directory = Path(data_root) / "xml" / "domain"
    if not directory.exists():
        return 0

    changed = 0
    for path in directory.glob("*.xml"):
        source = path.read_text(encoding="utf-8")
        sanitized = redact_domain_xml_secrets(source)
        if sanitized == source:
            continue
        descriptor, temporary_path = tempfile.mkstemp(
            dir=directory,
            prefix=f".{path.name}.",
        )
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                file.write(sanitized)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, path)
            directory_descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
            raise
        changed += 1
    return changed
