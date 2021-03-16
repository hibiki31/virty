import os
import pathlib
from mixin.log import setup_logger


logger = setup_logger(__name__)


# アプリケーションルートは絶対パスで最後に/なしに自動で変換
virty_root_env = os.getenv('VIRTY_ROOT', None)
if virty_root_env == None:
    is_dev = False
    virty_root = str(pathlib.Path('./').resolve())
else:
    virty_root = str(pathlib.Path(virty_root_env).resolve())

os.environ['ANSIBLE_LIBRARY'] = virty_root + "/ansible"