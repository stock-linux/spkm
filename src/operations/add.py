''' This module is a simple function running the "add" operation. '''

import tomllib
import shutil
import os
import sys

from utils.logger import Logger
from utils.db import get_pkg_data, write_index_data

def add(config: dict, pkgs: list[str]):
    '''Adds the given package list to the system.

    :param dict config: SPKM Configuration
    :param list[str] pkgs: Packages to add

    :return: None
    '''

    logger = Logger(config)

    not_found_pkgs = []
    to_add = []

    for pkg in list(set(pkgs)):
        pkg_data = get_pkg_data(config, pkg)

        if pkg_data is False:
            not_found_pkgs.append(pkg)
        elif isinstance(pkg_data, dict):
            to_add.append(pkg_data)

    if len(not_found_pkgs) > 0:
        logger.log_err('The following package(s) were not found:')
        for pkg in not_found_pkgs:
            logger.log_err(pkg, err_content=True)

        sys.exit(1)

    world_path = config['general']['dbpath'] + '/world'

    if os.path.exists(config['general']['dbpath'] + '/world.new'):
        world_path = config['general']['dbpath'] + '/world.new'

    with open(world_path, 'rb') as world:
        world_data = tomllib.load(world)

    for pkg_data in to_add:
        world_data[pkg_data['pkg_info']['name']] = {
            'version': pkg_data['pkg_info']['version'],
            'release': pkg_data['pkg_info']['release']
        }

    if world_path == config['general']['dbpath'] + '/world':
        shutil.copy(
            config['general']['dbpath'] + '/world',
            config['general']['dbpath'] + '/world.new'
        )

    write_index_data(world_data, config['general']['dbpath'] + '/world.new')

    logger.log_info(
        'Packages were added to `world.new`.'
        'Run `spkm up` to update your system with the new changes.'
    )
