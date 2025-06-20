import os


def delete_ssh_keys():
    for i in ["id_ed25519","id_ed25519.pub","id_rsa","id_rsa.pub"]:
        file_path = f"/root/.ssh/{i}"
        if os.path.isfile(file_path):
            os.remove(file_path)