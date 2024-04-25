''' This module is a simple function running the "delete" operation. '''

import tomllib
import os
import sys

from utils.logger import Logger
from utils.db import write_index_data

def delete(config: dict, pkgs: list[str]):
    '''
    Deletes the given package list from the system.

    :param dict config: SPKM Configuration
    :param list[str] pkgs: Package list

    :return: None
    '''

    world_path = config['general']['dbpath'] + '/world'

    if os.path.exists(config['general']['dbpath'] + '/world.new'):
        world_path = config['general']['dbpath'] + '/world.new'

    with open(world_path, 'rb') as world:
        world_data = tomllib.load(world)

    logger = Logger(config)

    to_delete = []
    not_installed_pkgs = []

    for pkg in list(set(pkgs)):
        if pkg in world_data:
            to_delete.append(pkg)
            del world_data[pkg]
        else:
            not_installed_pkgs.append(pkg)

    if len(not_installed_pkgs) > 0:
        logger.log_err(
            'The following package(s) are not installed or already deleted from `world.new`:'
        )

        for pkg in not_installed_pkgs:
            logger.log_err(pkg, err_content=True)

        sys.exit(1)

    write_index_data(world_data, config['general']['dbpath'] + '/world.new')

    logger.log_info(
        'Packages were deleted from `world.new`.'
        'Run `spkm up` to update your system with the new changes.'
    )
