import tomllib

from utils.exceptions import PackagesNotFoundException
from utils.db import get_pkg_data, is_pkg_installed

def get_ops(config: dict) -> dict[str, list]:
    '''Gets incoming operations based on the comparison between the local index and the world.

    :param dict config: SPKM Configuration.

    :return: Incoming operations.
    :rtype: list[tuple]
    '''

    local = open(config['general']['dbpath'] + '/local', 'rb')
    local_data = tomllib.load(local)

    world = open(config['general']['dbpath'] + '/world', 'rb')
    world_data = tomllib.load(world)

    ops: dict[str, list] = {'up': [], 'add': [], 'del': []}

    for package in local_data:
        if package not in world_data:
            ops['del'].append(package)
        elif local_data[package] != world_data[package]:
            ops['up'].append(((package, local_data[package]), (package, world_data[package])))

    for package in world_data:
        if package not in local_data:
            ops['add'].append((package, world_data[package]))

    return ops

pkg_adds = []
not_found_pkgs = []

def solve_pkg_deps(config: dict, pkg: str) -> list[dict]:
    '''Finds the dependency tree of a given package.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: Package list
    :rtype: list[dict]
    '''

    pkg_data = get_pkg_data(config, pkg)

    if pkg_data == False:
        not_found_pkgs.append(pkg)
    elif isinstance(pkg_data, dict):
        pkg_adds.append(pkg_data)

        if 'dependencies' in pkg_data['pkg_info']:
            for dep in pkg_data['pkg_info']['dependencies']:
                if dep not in pkg_adds and not is_pkg_installed(config, dep['name']):
                    solve_pkg_deps(config, dep['name'])

    if len(not_found_pkgs) > 0:
        raise PackagesNotFoundException(not_found_pkgs)

    return pkg_adds

def add_pkg(config: dict, pkg: str):
    '''Adds a package (and its dependencies) to the system.

    :param dict config: SPKM Configuration
    :param str pkg: Package name
    '''

    adds = solve_pkg_deps(config, pkg)
    print(adds)

def upgrade_local(config: dict):
    '''Upgrades the local system by comparing the given world file with the local index and applying the correct operations.

    :param dict config: SPKM Configuration.
    '''
    
    ops = get_ops(config)

    for package in ops['del']:
        pass

    for package in ops['up']:
        pass

    for package in ops['add']:
        add_pkg(config, package[0])