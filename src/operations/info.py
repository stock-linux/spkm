''' This module is a simple function running the "delete" operation. '''

from utils.db import get_pkg_data, is_pkg_installed
from utils.logger import Logger

def info(config: dict, pkg: str):
    '''Displays information about a given package.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: None
    '''

    logger = Logger(config)

    pkg_data = get_pkg_data(config, pkg)

    if isinstance(pkg_data, dict):
        pkg_info = pkg_data['pkg_info']

        logger.log_header('Package info')

        pkg_ver = is_pkg_installed(config, pkg)

        print('name:', pkg_info['name'])
        print('version:', pkg_info['version'], (f'({pkg_ver} installed)' if pkg_ver else ''))
        print('description:', pkg_info['description'])
        print('packager:', pkg_info['packager'])

        deps_names = []
        if 'dependencies' in pkg_info:
            for dep in pkg_info['dependencies']:
                deps_names.append(dep['name'])

        if len(deps_names) > 0:
            print('dependencies:', ','.join(deps_names))

        print('group:', pkg_data['group'])
    else:
        logger.log_err('Package not found.')
