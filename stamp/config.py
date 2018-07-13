"""Handling of config settings and files."""
import os
import sys
import yaml

from .settings import CONFIG_DIR, CONFIG_FILE, DB_FILE
from .helpers import default_error_handler


class ConfigValue(object):
    def __init__(self, config):
        self.value = None
        self.choices = list()
        self.validated = False

    def __str__(self):
        return self.value

    def validate(self):
        if self.choices:
            self.validated = self.value in self.choices


class Interface(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 'cli'
        self.choices.append('cli', 'curses')


class DBPath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = DB_FILE


class ConfigPath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE + '.yml'
        self.value = os.path.join(self.config_dir, self.config_file)

    def validate(self):
        if not os.path.isfile(self.value):
            return False


class HandleConfig(object):
    def __init__(self):
        self.values = (Interface(), DBPath(), ConfigPath)
        self.config_path = os.path.join(CONFIG_DIR, CONFIG_FILE)
        self.config = self.load_config()

    def validate_config_values(self, config) -> None:
        """Validate config values."""
        for value in self.values:
            if not value.validate():
                default_error_handler('Error when validating the %s option in config file!' % value.__class__.__name__, exit_on_error=True)

    def load_config(self) -> dict:
        """Load config.

        User defined config files will take precedence over the built in config.
        """
        try:
            with open(self.config_path, 'r') as config_readout:
                try:
                    config = yaml.load(config_readout)
                except yaml.YAMLError as err:
                    print(err)
                    sys.exit(64)
        except FileNotFoundError:
            return None

        return config
