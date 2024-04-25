''' This module is a simple function to read the SPKM config file. '''

import os
import tomllib

def get_config() -> dict:
    '''
    Gets the SPKM configuration and returns it into a dictionnary.

    :return: SPKM Configuration data
    :rtype: dict
    '''

    if 'SPKM_CONF' not in os.environ:
        os.environ['SPKM_CONF'] = '/etc/spkm.conf'

    with open(os.environ['SPKM_CONF'], 'rb') as conf_file:
        return tomllib.load(conf_file)
