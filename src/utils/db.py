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
            if os.path.exists(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg):
                base_toml_data = tomllib.load(open(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg + '/package.toml', 'rb'))
                infos_toml_data = tomllib.load(open(config['general']['dbpath'] + '/dist/' + repo['name'] + '/' + group + '/' + pkg + '/infos.toml', 'rb'))
                
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
    
    local = open(config['general']['dbpath'] + '/local', 'rb')
    local_data = tomllib.load(local)

    if pkg in local_data:
        return local_data[pkg]
    else:
        return False