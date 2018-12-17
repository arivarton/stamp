"""Handling of config settings and files."""
import os
import sys
import yaml
import re

from datetime import datetime

from .settings import CONFIG_DIR, CONFIG_FILE, DATA_DIR
from .helpers import error_handler
from .exceptions import ConfigValueError

__all__ = ['HandleConfig']


class ConfigValue(object):
    def __init__(self):
        self.value = None
        self.choices = list()
        self.validated = False
        if self.value:
            self.validate()

    def __str__(self):
        return self.value

    def _validate(self):
        if self.value not in self.choices:
            raise ConfigValueError('%s is not a valid choice! These are the valid choices: %s.' % (self.value, ', '.join(self.choices)))


class Interface(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 'cli'
        self.choices.extend(['cli', 'curses'])


class DatabasePath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = DATA_DIR

    def _validate(self):
        if not os.path.exists(self.value):
            try:
                os.makedirs(self.value)
            except PermissionError:
                error_handler('Permission denied to create path %s!' % self.value)


class MinimumHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 2

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)


class StandardHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = '08:00-16:00'

    def _validate(self):
        if re.match('\d\d:\d\d-\d\d:\d\d', self.value) is None:
            raise ConfigValueError('%s is the wrong format! The correct format is HH:MM-HH:MM.' % self.value)
        from_time, to_time = self.value.split('-')
        try:
            if datetime.strptime(from_time, '%H:%M') > datetime.strptime(to_time, '%H:%M'):
                error_handler('From time is higher than to time!')
        except ValueError:
            raise ConfigValueError('Wrong use of 24 hour format!')


class LunchHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 0.5

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)


class WagePerHour(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 300

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)


class Currency(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 'NOK'
        self.choices.extend(['NOK', 'ISK', 'USD'])


class ValueWrapper(object):
    def add(self, value):
        if issubclass(value.__class__, ConfigValue):
            regex = re.compile('(?!^)(?=[A-Z])')
            name = re.sub(regex, '_', value.__class__.__name__).lower()
            setattr(self, name, value)
        else:
            raise ValueError('value argument must be a ConfigValue class!')


class HandleConfig(object):
    def __init__(self):
        self.values = ValueWrapper()

        # Add values
        self.values.add(Interface())
        self.values.add(DatabasePath())
        self.values.add(MinimumHours())
        self.values.add(StandardHours())
        self.values.add(LunchHours())
        self.values.add(WagePerHour())
        self.values.add(Currency())

        self.config_path = os.path.join(CONFIG_DIR, CONFIG_FILE)
        self.config = self.load_config()

    def validate_config_values(self, config) -> None:
        for value in self.values.__dict__.values():
            try:
                value._validate()
            except ConfigValueError as err_msg:
                error_handler('Error when validating the %s option in config file!' % value.__class__.__name__, exit_on_error=False)
                error_handler(err_msg)

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
