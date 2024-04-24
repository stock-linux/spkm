import os, tomllib

def get_pkg_data(config: dict, pkg: str) -> dict | bool:
    '''Gets specified package information if the given package exists.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: Either the repo containing the package and the package info or False if the package does not exist
    :rtype: tuple | bool
    '''

    for repo in config['repos']:
        for group in os.listdir(config['general']['dbpath'] + '/dist/' + repo['name']):
            if not os.path.exists(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg):
                continue

            with open(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg + '/package.toml', 'rb') as base_toml:
                base_toml_data = tomllib.load(base_toml)
            
            with open(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg + '/infos.toml', 'rb') as infos_toml:
                infos_toml_data = tomllib.load(infos_toml)
            
            pkg_data = base_toml_data

            if 'run' in infos_toml_data:
                pkg_data['dependencies'] = infos_toml_data['run']
            else:
                pkg_data['dependencies'] = []

            if 'reverse-deps' in infos_toml_data:
                pkg_data['reverse-deps'] = infos_toml_data['reverse-deps']

            pkg_data['size'] = infos_toml_data['size']
            pkg_data['md5'] = infos_toml_data['md5']
            
            return {'repo': repo, 'group': group, 'pkg_info': pkg_data}

    return False

def is_pkg_installed(config: dict, pkg: str) -> str | bool:
    '''Checks if the given package is installed or not.

    :param dict config: SPKM Configuration
    :param str pkg: Package name

    :return: Either the package version or False if the package is not installed
    :rtype: str | bool
    '''
    
    with open(config['general']['dbpath'] + '/local', 'rb') as local:
        local_data = tomllib.load(local)

    if pkg in local_data:
        return local_data[pkg]
    else:
        return False

def write_index_data(data: dict, filepath: str):
    ''' Writes index data to a file.

    :param dict data: Data to write
    :param str filepath: Path to the index file
    
    :return: None
    '''
    
    with open(filepath, 'w') as file:
        for key in data:
            file.write('[' + key + ']\n')
            for data_key in data[key]:
                file.write(data_key + ' = ' + f'\'{data[key][data_key]}\'\n')
            
            file.write('\n')