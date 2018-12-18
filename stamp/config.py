"""Handling of config settings and files."""
import os
import sys
import yaml
import re

from datetime import datetime

from .settings import CONFIG_DIR, CONFIG_FILE, DATA_DIR
from .helpers import error_handler
from .exceptions import ConfigValueError

__all__ = ['Config']


class ConfigValue(object):
    """Template for setting values

    Values from config file trumps all.
    The environment variable will be the same as class name in uppercase with a _ sign between every uppercase letter from the original class name,
    'STAMP_' precedes every name. For example: 'STAMP_DATABASE_PATH'.
    If no environment variable with correct name is found then a default value is used.
    """
    def __init__(self):
        self.env_variable_name = 'STAMP_' + re.sub('(?!^)(?=[A-Z])', '_', self.__class__.__name__).upper()
        self.env_variable_value = os.getenv(self.env_variable_name)
        self.value = self.env_variable_value
        self.choices = None
        self.validated = False
        self.type = str

    def __str__(self):
        return self.value

    def _validate(self):
        if self.choices:
            if self.value not in self.choices:
                raise ConfigValueError('%s is not a valid choice! These are the valid choices: %s.' % (self.value, ', '.join(self.choices)))
        self.validated = True


class Interface(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 'cli' or self.env_variable_value
        self.choices = ['cli', 'curses']


class DatabasePath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = DATA_DIR or self.env_variable_value

    def _validate(self):
        if not os.path.exists(self.value):
            try:
                os.makedirs(self.value)
            except PermissionError:
                error_handler('Permission denied to create path %s!' % self.value)
        super()._validate()


class MinimumHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 2.0 or self.env_variable_value
        self.type = float

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)
        super()._validate()


class StandardHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = '08:00-16:00' or self.env_variable_value

    def _validate(self):
        if re.match('\d\d:\d\d-\d\d:\d\d', self.value) is None:
            raise ConfigValueError('%s is the wrong format! The correct format is HH:MM-HH:MM.' % self.value)
        from_time, to_time = self.value.split('-')
        try:
            if datetime.strptime(from_time, '%H:%M') > datetime.strptime(to_time, '%H:%M'):
                error_handler('From time is higher than to time!')
        except ValueError:
            raise ConfigValueError('Wrong use of 24 hour format!')
        super()._validate()


class LunchHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 0.5 or self.env_variable_value
        self.type = float

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)
        super()._validate()


class WagePerHour(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 300 or self.env_variable_value
        self.type = int

    def _validate(self):
        if not isinstance(self.value, (int, float)):
            raise ConfigValueError('%s is not an integer or float!' % self.value)
        super()._validate()


class Currency(ConfigValue):
    def __init__(self):
        super().__init__()
        self.value = 'NOK' or self.env_variable_value
        self.choices = ['NOK', 'ISK', 'USD']


class OrganizationNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('Organization number must contain only digits!' % self.value)
        super()._validate()


class CompanyName(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        if not isinstance(self.value, (str)):
            raise ConfigValueError('%s is not a string!' % self.value)
        super()._validate()


class CompanyAddress(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        if not isinstance(self.value, (str)):
            raise ConfigValueError('%s is not a string!' % self.value)
        super()._validate()


class CompanyZip(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super()._validate()


class CompanyAccountNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super()._validate()


class PhoneNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super()._validate()


class MailAddress(ConfigValue):
    def __init__(self):
        super().__init__()

    def _validate(self):
        if re.match('^[\S]+@[\S]+.[A-Za-z]$', self.value) is None:
            raise ConfigValueError('%s is not a valid mail address!' % self.value)
        super()._validate()


class ValuesWrapper(object):
    def __repr__(self):
        repr_string = '\n'
        for key, value in self.__dict__.items():
            repr_string += '%s: %s\n' % (str(key), str(value.value))
        return repr_string

    def add(self, value):
        if issubclass(value.__class__, ConfigValue):
            regex = re.compile('(?!^)(?=[A-Z])')
            name = re.sub(regex, '_', value.__class__.__name__).lower()
            setattr(self, name, value)
        else:
            raise ValueError('value argument must be a ConfigValue class!')


class Config(object):
    def __init__(self):
        self.values = ValuesWrapper()

        # Add values
        self.values.add(Interface())
        self.values.add(DatabasePath())
        self.values.add(MinimumHours())
        self.values.add(StandardHours())
        self.values.add(LunchHours())
        self.values.add(WagePerHour())
        self.values.add(Currency())
        self.values.add(OrganizationNumber())
        self.values.add(CompanyName())
        self.values.add(CompanyAddress())
        self.values.add(CompanyZip())
        self.values.add(CompanyAccountNumber())
        self.values.add(PhoneNumber())
        self.values.add(MailAddress())

        self.config_path = os.path.join(CONFIG_DIR, CONFIG_FILE)
        try:
            self.load()
        except ConfigValueError as err_msg:
            error_handler(err_msg)
        self.correct_types()

    def validate_config_values(self):
        for value in self.values.__dict__.values():
            if value.value:
                try:
                    value._validate()
                except ConfigValueError as err_msg:
                    error_handler('Error when validating the %s option in config file!' % value.__class__.__name__, exit_on_error=False)
                    error_handler(err_msg)

    def correct_types(self):
        for value in self.values.__dict__.values():
            if value.value:
                value.value = value.type(value.value)

    def load(self):
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
        for key, value in config.items():
            if key.replace(' ', '_') not in self.values.__dict__.keys():
                raise ConfigValueError('%s is not a valid config setting' % key)
            else:
                self.values.__dict__[key].value = value
        self.validate_config_values()
