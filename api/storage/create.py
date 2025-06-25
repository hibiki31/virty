from module.ansiblelib import AnsibleManager
from module.virtlib import VirtManager
from module.xmllib import XmlEditor
from node.models import NodeModel
from storage.function import is_safe_fullpath


def create_storage(storage_name:str, storage_path:str, node:NodeModel):
    # XMLを定義、設定
    editor = XmlEditor("static","storage_dir")
    editor.storage_base_edit(name=storage_name, path=storage_path)

    am = AnsibleManager(user=node.user_name, domain=node.domain)
    
    if not is_safe_fullpath(storage_path):
        raise Exception(f"The specified path is not a safe full path. {storage_path}")
    am.run(
        playbook_name="commom/make_dir_recurse",
        extravars={"path": storage_path}
    )

    # ソイや！
    manager = VirtManager(node_model=node)
    manager.storage_define(xml_str=editor.dump_str())