import yaml

CONFIG_DIR = 'config/secrets.yaml'

def _get_yaml():
    with open(CONFIG_DIR, 'r') as file:
        secrets = yaml.safe_load(file)
    return secrets

def vortexa_api_key():
    secrets = _get_yaml()
    return secrets['VORTEXA_API_KEY']

def signal_api_key():
    secrets = _get_yaml()
    return secrets['SIGNAL_API_KEY']

def sendgrid_api_key():
    secrets = _get_yaml()
    return secrets['SENDGRID_API_KEY']
