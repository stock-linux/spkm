import os, sys, shutil, tomllib, datetime, hashlib, multiprocessing

from urllib.request import urlopen

from utils.exceptions import PackagesNotFoundException, PkgDownloadError, PkgExtractionError
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
        elif local_data[package]['version'] != world_data[package]['version'] or local_data[package]['release'] != world_data[package]['release']:
            ops['up'].append(((package, local_data[package]['version'], local_data[package]['release']), (package, world_data[package]['version'], world_data[package]['release'])))

    for package in world_data:
        if package not in local_data:
            ops['add'].append((package, world_data[package]))

    return ops

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

    if pkg_data == False:
        not_found_pkgs.append(pkg)
    elif isinstance(pkg_data, dict):
        if 'dependencies' in pkg_data['pkg_info']:
            for dep in pkg_data['pkg_info']['dependencies']:
                dep_data = get_pkg_data(config, dep['name'])
                
                if dep_data == False:
                    not_found_pkgs.append(dep['name'])
                elif isinstance(dep_data, dict):
                    pkg_adds.append(dep_data)

        pkg_adds.append(pkg_data)

    if len(not_found_pkgs) > 0:
        raise PackagesNotFoundException(not_found_pkgs)

    return pkg_adds

extracted_pkgs = []
fails = []

def extract_pkg_archive(config: dict, pkg_info: dict, archive: str):
    '''Extracts a package archive into the root directory.

    :param dict config: SPKM Configuration
    :param str pkg: Package name
    :param str archive: Archive path

    :return: None
    '''
    
    pkg = pkg_info['name']
    root = config['general']['root']
    os.makedirs(root, exist_ok=True)

    ret_code = os.system(f'tar -xhpf {archive} -C {root}')
    
    if ret_code != 0:
        raise PkgExtractionError

def add_pkg(config: dict, pkg: str):
    '''Adds a package (and its dependencies) to the system.

    :param dict config: SPKM Configuration
    :param str pkg: Package name
    '''

    adds = solve_pkg_deps(config, pkg)
  
    # We actually reverse the list to install dependencies first
    adds.reverse()

    extract_processes = []
    
    for add in adds:
        # Get the useful package infos

        pkg_name = add['pkg_info']['name']
        pkg_version = add['pkg_info']['version']
        pkg_release = add['pkg_info']['release']
        pkg_md5 = add['pkg_info']['md5']

        filename = add['group'] + '/' + add['pkg_info']['name'] + '/' + add['pkg_info']['name'] + '-' + add['pkg_info']['version'] + '.tar.zst'
            
        src_path = add['repo']['url'] + '/' + filename
        dest_path = config['general']['cache']  + '/' + add['repo']['name'] + '/' + filename

        # Create the cache directory as it can be inexistant

        os.makedirs('/'.join(dest_path.split('/')[:-1]), exist_ok=True)

        if not (os.path.exists(dest_path) and hashlib.md5(open(dest_path, 'rb').read()).hexdigest() == pkg_md5):
            if os.path.exists(add['repo']['url']):
                # Since we use a local repo, no need to download a file, just need to copy it
                
                shutil.copy(src_path, dest_path)
            else:
                # Get the size of the file to download

                total_length = add['pkg_info']['size']
                total_length_kb = int(total_length / 1024)
                total_length_mb = int(total_length / 1024 / 1024)

                # Set a convenient display of the size

                total_length_display = ''

                if total_length_mb > 0:
                    total_length_display = str(total_length_mb) + 'M'
                else:
                    total_length_display = str(total_length_kb) + 'K'

                # Initialize request
                
                req = urlopen(src_path)
                CHUNK_SIZE = 2 * 1024 * 1024
                dl = 0

                start_time = datetime.datetime.now()
                end_time = start_time
                diff = end_time - start_time

                # Initialize md5 hash
                
                hash_md5 = hashlib.md5()

                # Download the file

                with open(dest_path, 'wb') as f:
                    while True:
                        start_time = datetime.datetime.now()
                        
                        if diff.total_seconds() > 0:
                            speed = CHUNK_SIZE / diff.total_seconds()
                        else:
                            speed = 0

                        speed_kb = int(speed / 1024)
                        speed_mb = int(speed / 1024 / 1024)

                        dl += CHUNK_SIZE

                        if dl > total_length:
                            dl = total_length

                        dl_kb = int(dl / 1024)
                        dl_mb = dl / 1024 / 1024

                        dl_display = ''
                        speed_display = ''

                        # Set a convenient display for download size display and speed rate
                        
                        if total_length_mb > 0:
                            dl_display = str(int(dl_mb)) + 'M'
                        else:
                            dl_display = str(int(dl_kb)) + 'K'

                        if speed_mb > 0:
                            speed_display = str(speed_mb) + 'M/s'
                        else:
                            speed_display = str(speed_kb) + 'K/s'

                        chunk = req.read(CHUNK_SIZE)
                        if not chunk:
                            break

                        f.write(chunk)
                        done = int(50 * dl / total_length)

                        # Display the progress bar

                        sys.stdout.write(f"\x1b[1K\r{pkg_name}-{pkg_version} [%s%s] ({dl_display}/{total_length_display} - {speed_display})" % ('=' * done, ' ' * (50-done)) )    
                        sys.stdout.flush()
                        
                        end_time = datetime.datetime.now()
                        diff = end_time - start_time
                        
                        # Update md5 hash

                        hash_md5.update(chunk)
                
                print()

                # If the downloaded file's hash is not the same as in the package infos, we raise an error

                if hash_md5.hexdigest() != pkg_md5:
                    raise PkgDownloadError

        extract_processes.append(multiprocessing.Process(target=extract_pkg_archive, args=(config, add['pkg_info'], dest_path)))

    for i in range(len(extract_processes)):
        if (i + 1) % config['general']['threads'] == 0:
            for process in extract_processes[i - config['general']['threads'] + 1:i + 1]:
                process.start()

            for process in extract_processes[i - config['general']['threads'] + 1:i + 1]:
                process.join()
        elif i + 1 == len(extract_processes):
            for process in extract_processes[i - ((i + 1) % config['general']['threads']) + 1:]:
                process.start()

            for process in extract_processes[i - ((i + 1) % config['general']['threads']) + 1:]:
                process.join()

    for i in range(len(extract_processes)):
        # Copy the package tree to a 'local' storage
        
        os.makedirs(config['general']['dbpath'] + '/trees/', exist_ok=True)
        shutil.copy(config['general']['dbpath'] + '/dist/' + add['repo']['name'] + '/' + add['group'] + '/' + add['pkg_info']['name'] + '/tree', config['general']['dbpath'] + '/trees/' + add['pkg_info']['name'] + '.tree')
        
        if extract_processes[i].exitcode != 0:
            fails.append(adds[i])
        else:
            extracted_pkgs.append(adds[i]['pkg_info'])

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

        with open(config['general']['dbpath'] + '/local', 'a') as f:
            for pkg in extracted_pkgs:
                f.write('[' + pkg['name'] + ']\n')
                f.write('version = \'' + pkg['version'] + '\'\n')
                f.write('release = ' + str(pkg['release']) + '\n\n')
        
        if len(fails) > 0:
            # TODO: WE MUST DELETE THE EXTRACTED PACKAGES.
            raise PkgExtractionError
