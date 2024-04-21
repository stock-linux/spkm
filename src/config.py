import os, tomllib

def get_config() -> dict:
    if 'SPKM_CONF' not in os.environ:
        os.environ['SPKM_CONF'] = '/etc/spkm.conf'

    with open(os.environ['SPKM_CONF'], 'rb') as conf_file:
        return tomllib.load(conf_file)

def get_db_path(config: dict) -> str:
    return config['general']['dbpath']
