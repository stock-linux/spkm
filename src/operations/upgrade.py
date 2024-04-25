''' This module is the core of SPKM, handling all updates to `world` file. '''

import os
import shutil
import tomllib
import multiprocessing

from utils.download import download
from utils.logger import Logger
from utils.exceptions import PkgNotFoundException, PkgDownloadError, PkgExtractionError
from utils.db import get_pkg_data, write_index_data

def get_adds(config: dict, local_data: dict, world_data: dict) -> list:
    '''
    Gets incoming adds.

    :param dict config: SPKM Configuration
    :param dict local_data: `local` index file data
    :param dict world_data: `world.new` file data

    :return: List of incoming adds
    :rtype: list
    '''

    adds = []

    for package in world_data:
        if package not in local_data:
            for dep in solve_pkg_deps(config, package):
                if dep not in adds and dep['pkg_info']['name'] not in local_data:
                    adds.append(dep)

    return adds

def get_dels(config: dict, local_data: dict, world_data: dict) -> list:
    '''
    Gets incoming deletions.

    :param dict config: SPKM Configuration
    :param dict local_data: `local` index file data
    :param dict world_data: `world.new` file data

    :return: List of incoming deletions
    :rtype: list
    '''

    dels = []

    for package in local_data:
        pkg_data = get_pkg_data(config, package)

        if pkg_data is False:
            raise PkgNotFoundException

        if package not in world_data:
            can_del = True

            if 'reverse-deps' in pkg_data['pkg_info']:
                for reverse_dep in pkg_data['pkg_info']['reverse-deps']:
                    if reverse_dep['name'] in world_data:
                        can_del = False

            if can_del:
                data = {'name': package}
                data.update(local_data[package])

                dels.append(data)

    return dels

def get_ups(config: dict, adds: list, local_data: dict) -> tuple:
    '''
    Gets incoming updates.

    :param dict config: SPKM Configuration
    :param list adds: Incoming adds
    :param dict local_data: `local` index file data

    :return: new_adds, ups
    :rtype: tuple
    '''

    new_adds = []
    ups = []

    for package in local_data:
        pkg_data = get_pkg_data(config, package)

        if pkg_data is False:
            raise PkgNotFoundException

        if (local_data[package]['version'] != pkg_data['pkg_info']['version']
                or local_data[package]['release'] != pkg_data['pkg_info']['release']):
            for dep in solve_pkg_deps(config, package):
                if dep['pkg_info']['name'] not in local_data and dep not in adds:
                    new_adds.append(dep)

            ups.append(
                (
                    {
                        'name': package,
                        'version': local_data[package]['version'],
                        'release': local_data[package]['release']
                    },
                    pkg_data
                )
            )

    return new_adds, ups

def get_ops(config: dict) -> tuple:
    '''Gets incoming operations based on the comparison between the local index and the world.

    :param dict config: SPKM Configuration.

    :return: Incoming operations and local index data.
    :rtype: tuple
    '''

    ops: dict[str, list] = {'up': [], 'adds': [], 'dels': []}

    if not os.path.exists(config['general']['dbpath'] + '/world.new'):
        return ops, {}

    with open(config['general']['dbpath'] + '/local', 'rb') as local:
        local_data = tomllib.load(local)

    with open(config['general']['dbpath'] + '/world.new', 'rb') as world:
        world_data = tomllib.load(world)

    ops['adds'] = get_adds(config, local_data, world_data)
    ops['dels'] = get_dels(config, local_data, world_data)

    new_adds, ups = get_ups(config, ops['adds'], local_data)
    ops['adds'].extend(new_adds)
    ops['up'] = ups

    return ops, local_data

def solve_pkg_deps(config: dict, pkg: str) -> list[dict]:
    '''Finds the dependency tree of a given package.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: Package list
    :rtype: list[dict]
    '''

    pkg_adds = []
    not_found_pkgs = []

    pkg_data = get_pkg_data(config, pkg)

    if pkg_data is False:
        not_found_pkgs.append(pkg)
    elif isinstance(pkg_data, dict):
        if 'dependencies' in pkg_data['pkg_info']:
            for dep in pkg_data['pkg_info']['dependencies']:
                dep_data = get_pkg_data(config, dep['name'])

                if dep_data is False:
                    not_found_pkgs.append(dep['name'])
                elif isinstance(dep_data, dict):
                    pkg_adds.append(dep_data)

        pkg_adds.append(pkg_data)

    if len(not_found_pkgs) > 0:
        raise PkgNotFoundException

    return pkg_adds

extracted_pkgs: list = []
fails: list = []

def extract_pkg_archive(config: dict, archive: str, pkg_data: dict, logger: Logger):
    '''Extracts a package archive into the root directory.

    :param dict config: SPKM Configuration
    :param str archive: Archive path
    :param dict pkg_data: Package data
    :param Logger logger: SPKM Logger

    :return: None
    '''

    root = config['general']['root']
    os.makedirs(root, exist_ok=True)

    ret_code = os.system(f'tar -xhpf {archive} -C {root}')

    pkg_name = pkg_data['pkg_info']['name']

    shutil.copy(
        config['general']['dbpath'] +
        '/dist/' +
        pkg_data['repo']['name'] +
        '/' +
        pkg_data['group'] +
        '/' +
        pkg_name +
        '/tree',

        config['general']['dbpath'] +
        '/trees/' +
        pkg_name +
        '.tree'
    )

    if ret_code != 0:
        raise PkgExtractionError

    logger.log_success(f'Package `{pkg_name}` was successfully added !')

def exec_processes(threads: int, processes: list) -> int:
    '''
    Starts each process of the given list.

    :param int threads: Number of threads
    :param list processes: List of processes to start

    :return: Status
    :rtype: int
    '''

    for i in range(len(processes)):
        if (i + 1) % threads == 0:
            i_start = i - threads + 1
            i_end = i + 1
        elif i + 1 == len(processes):
            i_start = i - ((i + 1) % threads) + 1
            i_end = len(processes)
        else:
            continue

        for process in processes[i_start:i_end]:
            process.start()

        for process in processes[i_start:i_end]:
            process.join()

    for process in processes:
        if process.exitcode != 0:
            return 1

    return 0

def add_pkg(config: dict, logger: Logger, local_data: dict, adds: list):
    '''Adds a package (and its dependencies) to the system.

    :param dict config: SPKM Configuration
    :param Logger logger: SPKM logger
    :param dict local_data: local index data
    :param str pkg: Package name
    '''

    extract_processes = []

    for add in adds:
        # Get the useful package infos

        pkg_name = add['pkg_info']['name']
        pkg_version = add['pkg_info']['version']
        pkg_release = add['pkg_info']['release']
        pkg_md5 = add['pkg_info']['md5']


        filename = (add['group'] +
                    '/' +
                    add['pkg_info']['name'] +
                    '/' +
                    add['pkg_info']['name'] +
                    '-' +
                    add['pkg_info']['version'] +
                    '.tar.zst')

        src_path = add['repo']['url'] + '/' + filename
        dest_path = config['general']['cache']  + '/' + add['repo']['name'] + '/' + filename

        logger.log_info(f'Adding package `{pkg_name}`...')

        # Create the cache directory as it can be inexistant

        os.makedirs('/'.join(dest_path.split('/')[:-1]), exist_ok=True)

        local_data[pkg_name] = {
            'version': pkg_version,
            'release': pkg_release
        }

        extract_processes.append(
            multiprocessing.Process(
                target=extract_pkg_archive,
                args=(config, dest_path, add, logger)
            )
        )

        if os.path.exists(dest_path):
            continue

        if os.path.exists(add['repo']['url']):
            # No need to download a file, just need to copy it

            shutil.copy(src_path, dest_path)
            continue

        hash_md5 = download(
            src_path,
            dest_path,
            add['pkg_info']['size'],
            f'{pkg_name}-{pkg_version}'
        )

        print()

        # Incorrect md5, we raise an error

        if hash_md5 != pkg_md5:
            os.remove(dest_path)
            raise PkgDownloadError

    os.makedirs(config['general']['dbpath'] + '/trees/', exist_ok=True)
    status = exec_processes(config['general']['threads'], extract_processes)

    return status

def del_pkg(config: dict, local_data: dict, dels: list):
    ''' Deletes a package (and its dependencies) from the system.

    :param dict config: SPKM Configuration
    :param dict local_data: local index data
    :param str pkg: Package name

    :return: None
    '''

    logger = Logger(config)

    for deletion in dels:
        pkg_name = deletion['name']

        logger.log_info(f'Deleting package `{pkg_name}`...')

        with open(
                config['general']['dbpath'] + '/trees/' + pkg_name + '.tree', 'r',
                encoding='utf-8'
            ) as tree:
            files = tree.readlines()

        dirs_to_remove = []

        for line in files:
            line = line.strip()

            if not os.path.exists(config['general']['root'] + '/' + line):
                continue

            if (not os.path.isdir(config['general']['root'] + '/' + line)
                    and not os.path.islink(config['general']['root'] + '/' + line)):
                os.remove(config['general']['root'] + '/' + line)
            else:
                dirs_to_remove.append(line)

        for directory in dirs_to_remove:
            if len(os.listdir(config['general']['root'] + '/' + directory)) == 0:
                os.removedirs(config['general']['root'] + '/' + directory)

        del local_data[pkg_name]
        os.remove(config['general']['dbpath'] + '/trees/' + pkg_name + '.tree')

        logger.log_success(f'Package `{pkg_name}` was successfully deleted !')

def upgrade_local(config: dict):
    '''
    Upgrades the local system by applying the correct operations.

    :param dict config: SPKM Configuration.

    :return: None
    '''

    logger = Logger(config)

    ops, local_data = get_ops(config)

    if len(ops['dels']) == 0 and len(ops['adds']) == 0 and len(ops['up']) == 0:
        print('No change to apply.')
        return

    print('----- Operations Summary -----')
    print()

    for deletion in ops['dels']:
        logger.log_del(deletion['name'] +  '-' + deletion['version'])

    for add in ops['adds']:
        logger.log_add(add['pkg_info']['name'] +  '-' + add['pkg_info']['version'])

    for up in ops['up']:
        logger.log_up(
            up[0]['name'] +  '-' + up[0]['version'] +
            ' => ' +
            up[1]['pkg_info']['name'] + '-' + up[1]['pkg_info']['version']
        )

    print()

    if input('Do you really want to apply these changes to your system ? (Y/N) ').lower() != 'y':
        return

    shutil.copy(config['general']['dbpath'] + '/world', config['general']['dbpath'] + '/world.old')

    shutil.copy(config['general']['dbpath'] + '/world.new', config['general']['dbpath'] + '/world')
    os.remove(config['general']['dbpath'] + '/world.new')

    del_pkg(config, local_data, ops['dels'])
    add_status = add_pkg(config, logger, local_data, ops['adds'])

    write_index_data(local_data, config['general']['dbpath'] + '/local')

    if add_status != 0:
        shutil.copy(
            config['general']['dbpath'] + '/world.old',
            config['general']['dbpath'] + '/world.new'
        )
        upgrade_local(config)

        raise PkgExtractionError
