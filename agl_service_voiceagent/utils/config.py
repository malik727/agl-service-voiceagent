import os
import configparser

# Get the absolute path to the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the config.ini file located in the base directory
config_path = os.path.join(current_dir, '..', 'config.ini')

config = configparser.ConfigParser()
config.read(config_path)

def update_config_value(value, key, group="General"):
    config.set(group, key, value)
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def get_config_value(key, group="General"):
    return config.get(group, key)
