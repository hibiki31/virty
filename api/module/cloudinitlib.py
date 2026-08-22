import os
import shutil
import subprocess
from pathlib import Path

from settings import DATA_ROOT


class CloudInitManager:
    """cloud-init媒体をtask固有のprivate一時directoryで組み立てる。"""

    def __init__(self, uuid: str, hostname: str) -> None:
        if Path(uuid).name != uuid or uuid in {"", ".", ".."}:
            raise ValueError("cloud-init UUIDが不正です")
        self.uuid = uuid
        self.hostname = hostname
        self.root = Path(DATA_ROOT) / "cloud-init" / uuid
        self.root.mkdir(mode=0o700, parents=True, exist_ok=False)
        self._write_private_text(
            self.root / "meta-data",
            f"instance-id: {hostname}\nlocal-hostname: {hostname}\n",
        )
        self._write_private_text(self.root / "user-data", "#cloud-config\n")

    @staticmethod
    def _write_private_text(path: Path, data: str) -> None:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(data)

    def custom_user_data(self, data: str | bytes) -> None:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self._write_private_text(self.root / "user-data", data)

    def make_iso(self) -> str:
        user_data_path = self.root / "user-data"
        meta_data_path = self.root / "meta-data"
        network_config_path = self.root / "network-config"
        iso_path = self.root / "init.iso"
        command = [
            "genisoimage",
            "-output",
            str(iso_path),
            "-volid",
            "cidata",
            "-joliet",
            "-rock",
            str(user_data_path),
            str(meta_data_path),
        ]
        if network_config_path.exists():
            command.append(str(network_config_path))
        subprocess.run(
            command,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        iso_path.chmod(0o600)
        return str(iso_path)

    def cleanup(self) -> None:
        """平文user-dataと生成ISOをtask完了前に削除する。"""

        shutil.rmtree(self.root)
