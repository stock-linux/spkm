''' This module is a simple function running the "up" operation. '''

from operations.upgrade import upgrade_local

def up(config: dict):
    '''
    Updates the system with the new changes in `world.new`.

    :param dict config: SPKM Configuration

    :return: None
    '''

    upgrade_local(config)
