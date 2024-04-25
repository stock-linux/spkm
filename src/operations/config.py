''' This module is a simple function running the "config" command. '''

import os

from utils.logger import Logger

def config(config: dict):
    '''
    Displays the SPKM configuration.

    :param dict config: SPKM Configuration

    :return: None
    '''

    logger = Logger(config)

    logger.log_header('Configuration')
    with open(os.environ['SPKM_CONF'], 'r', encoding='utf-8') as conf:
        conf_content = conf.read()
    logger.log(conf_content)
