import logging
from settings import DATA_ROOT


# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


def setup_logger(name, logfile=f'{DATA_ROOT}/api.log'):
    logger = logging.getLogger(name)

    # ファイル出力設定
    fh = logging.FileHandler(logfile)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)

    # ファイル出力設定
    fh_info = logging.FileHandler(f'{DATA_ROOT}/api_info.log')
    fh_info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh_info.setFormatter(fh_info_formatter)

    # コンソール出力設定
    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_formatter)

    logger.addHandler(fh)
    logger.addHandler(fh_info)
    logger.addHandler(ch)

    # 全体のログレベル
    logger.setLevel(logging.DEBUG)
    # ファイル出力のログレベル
    fh.setLevel(logging.DEBUG)
    fh_info.setLevel(logging.INFO)
    # コンソール出力のログレベル
    ch.setLevel(logging.INFO)

    return logger