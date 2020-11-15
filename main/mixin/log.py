import logging


def setup_logger(name, logfile='data/api.log'):
    logger = logging.getLogger(name)

    # ファイル出力設定
    fh = logging.FileHandler(logfile)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)

    # コンソール出力設定
    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # 全体のログレベル
    logger.setLevel(logging.DEBUG)
    # ファイル出力のログレベル
    fh.setLevel(logging.INFO)
    # コンソール出力のログレベル
    ch.setLevel(logging.DEBUG)

    return logger