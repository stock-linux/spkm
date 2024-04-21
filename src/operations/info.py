from utils.db import get_pkg_info, is_pkg_installed
from utils.logger import Logger

def info(config: dict, pkg: str):
    '''Displays information about a given package.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: None
    '''
    
    logger = Logger(config)
    
    pkg_info = get_pkg_info(config, pkg)

    if pkg_info:
        logger.log_header('Package info')

        pkg_ver = is_pkg_installed(config, pkg)

        print('name:', pkg_info[1]['name'])
        print('version:', pkg_info[1]['version'], (f'({pkg_ver} installed)' if pkg_ver else ''))
        print('description:', pkg_info[1]['description'])
        print('packager:', pkg_info[1]['packager'])
        
        deps_names = []
        if 'dependencies' in pkg_info[1]:
            for dep in pkg_info[1]['dependencies']:
                deps_names.append(dep['name'])

        if len(deps_names) > 0:
            print('dependencies:', ','.join(deps_names))

        print('group:', pkg_info[0][2])
    else:
        logger.log_err('Package not found.')