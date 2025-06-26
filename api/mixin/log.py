import logging
import os

from rich.logging import RichHandler

from settings import DATA_ROOT, IS_DEV


def setup_logger(name):
    logger = logging.getLogger(name)

    # ファイル出力設定
    fh = logging.FileHandler(os.path.join(DATA_ROOT, "virty-api.log"))
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)

    if IS_DEV:
        ch = RichHandler()
    else:
        ch = logging.StreamHandler()
        ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        ch.setFormatter(ch_formatter)
  
    logger.addHandler(fh)
    logger.addHandler(ch)

    # 全体のログレベル
    logger.setLevel(logging.DEBUG)
    # 個別のログレベル
    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.INFO)

    return logger