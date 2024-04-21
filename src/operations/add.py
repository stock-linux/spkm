import shutil

from operations.upgrade import upgrade_local
from utils.logger import Logger
from utils.db import get_pkg_data, is_pkg_installed
from utils.exceptions import PackagesNotFoundException

from typing import cast

def add(config: dict, pkgs: list[str]):
    '''Adds the given package list to the system.

    :param dict config: SPKM Configuration
    :param list[str] pkgs: Packages to add

    :return: None
    '''
    
    logger = Logger(config)

    shutil.copy(config['general']['dbpath'] + '/local', config['general']['dbpath'] + '/world')

    err = False

    with open(config['general']['dbpath'] + '/world', 'a') as world_file:
        for pkg in pkgs:
            if is_pkg_installed(config, pkg):
                logger.log_info(f'Package `{pkg}` already installed.')
                continue

            pkg_data = get_pkg_data(config, pkg)

            if pkg_data == False:
                logger.log_err(f'Package `{pkg}` not found.')
                err = True
            elif isinstance(pkg_data, dict):
                pkg_name = pkg_data['pkg_info']['name']
                pkg_version = pkg_data['pkg_info']['version']

                world_file.write(f'{pkg_name} = \'{pkg_version}\'\n')

    if err:
        exit(1)
    else:
        try:
            upgrade_local(config)
        except PackagesNotFoundException as err:
            logger.log_err(f'Package(s) not found during dependency computing:')

            for pkg in cast(PackagesNotFoundException, err).pkgs:
                logger.log_err(pkg, err_content=True)

            print()
            logger.log_err('Cannot apply package add operation.')