import json
import logging
import os

from rich.logging import RichHandler

from settings import DATA_ROOT, IS_DEV, LOG_MODE


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "levelname": record.levelname,
            "msg": record.getMessage(),
        }
        log_record.update({key: value for key, value in record.__dict__.items() if key not in log_record})

        return json.dumps(log_record)


def setup_logger(name):
    logger = logging.getLogger(name)
    
    default_formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    json_formatter = JsonFormatter(datefmt='%Y-%m-%d %H:%M:%S')

    # ファイル出力設定
    if LOG_MODE == "JSON" or LOG_MODE == "BOTH":
        fh_json = logging.FileHandler(os.path.join(DATA_ROOT, "virty-api.json"))
        fh_json.setFormatter(json_formatter)
        logger.addHandler(fh_json)
        
    if LOG_MODE == "TEXT" or LOG_MODE == "BOTH":
        fh_text = logging.FileHandler(os.path.join(DATA_ROOT, "virty-api.log"))
        fh_text.setFormatter(default_formatter)
        logger.addHandler(fh_text)

    if IS_DEV:
        ch_rich = RichHandler()
        logger.addHandler(ch_rich)
    else:
        ch_text = logging.StreamHandler()
        ch_text.setFormatter(default_formatter)
        logger.addHandler(ch_text)
        

    # 全体のログレベル
    logger.setLevel(logging.DEBUG)

    return logger