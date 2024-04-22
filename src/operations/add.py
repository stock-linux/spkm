import shutil

from operations.upgrade import upgrade_local
from utils.logger import Logger
from utils.db import get_pkg_data, is_pkg_installed
from utils.exceptions import PackagesNotFoundException, PkgDownloadError, PkgExtractionError

from typing import cast

def add(config: dict, pkgs: list[str]):
    '''Adds the given package list to the system.

    :param dict config: SPKM Configuration
    :param list[str] pkgs: Packages to add

    :return: None
    '''
    
    logger = Logger(config)

    err = False

    for pkg in list(set(pkgs)):
        if is_pkg_installed(config, pkg):
            logger.log_info(f'Package `{pkg}` already installed.')
            continue

        pkg_data = get_pkg_data(config, pkg)

        if pkg_data == False:
            logger.log_err(f'Package `{pkg}` not found.')
            err = True
        elif isinstance(pkg_data, dict):
            with open(config['general']['dbpath'] + '/world', 'a') as world_file:
                pkg_name = pkg_data['pkg_info']['name']
                pkg_version = pkg_data['pkg_info']['version']
                pkg_release = pkg_data['pkg_info']['release']

                world_file.write(f'[{pkg_name}]\n')
                world_file.write(f'version = \'{pkg_version}\'\n')
                world_file.write(f'release = {pkg_release}\n\n')

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
            
            exit(1)
        except PkgDownloadError:
            logger.log_err(f'An error occured during the download. Exiting.')
            
            exit(1)
        except PkgExtractionError:
            logger.log_err(f'One or multiple package decompression processes failed. Check the logs and be careful.')

            exit(1)