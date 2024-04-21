import os

from utils.logger import Logger

def config(config: dict):
    logger = Logger(config)

    logger.log_header('Configuration')
    conf_content = open(os.environ['SPKM_CONF'], 'r').read()
    logger.log(conf_content)
