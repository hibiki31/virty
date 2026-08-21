from pathlib import Path


def delete_ssh_keys():
    for i in ["id_ed25519","id_ed25519.pub","id_rsa","id_rsa.pub"]:
        file_path = Path.home() / ".ssh" / i
        if file_path.is_file():
            file_path.unlink()
