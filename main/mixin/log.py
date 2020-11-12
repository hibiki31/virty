import logging

def setup_logger(name, logfile='data/api.log'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even DEBUG messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)

    # create console handler with a INFO log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger