"""Handling of config settings and files."""

import os
import sys
import re
from datetime import datetime

import yaml

from .settings import DATA_DIR, INVOICE_DIR
from .helpers import error_handler
from .exceptions import ConfigValueError

__all__ = ['Config']


class ConfigValue(object):
    """Template for setting values

    Values from config file trumps all.
    The environment variable will be the same as class name in uppercase
    with a _ sign between every uppercase letter from the original class name,
    'STAMP_' precedes every name. For example: 'STAMP_DATABASE_PATH'.
    If no environment variable with correct name is found then a default value is used.
    """
    def __init__(self):
        self.env_variable_name = 'STAMP_' + re.sub('(?!^)(?=[A-Z])', '_',
                                                   self.__class__.__name__).upper()
        self.env_variable_value = os.getenv(self.env_variable_name)
        self.value = None
        self.choices = None
        self.validated = False
        self.validation_type = None
        self.type = str
        self.add_default_value(self.env_variable_value)

    def __str__(self):
        return self.value

    def validate(self):
        if self.choices:
            if self.value not in self.choices:
                raise ConfigValueError('%s is not a valid choice! These are the valid choices: %s.'
                                       % (self.value, ', '.join(self.choices)))

        if self.validation_type == 'path':
            if not os.path.exists(self.value):
                try:
                    os.makedirs(self.value)
                except PermissionError:
                    error_handler('Permission denied to create path %s!' % self.value)
        if self.validation_type == 'email':
            if re.match(r'^[\S]+@[\S]+.[A-Za-z]$', self.value) is None:
                raise ConfigValueError('%s is not a valid mail address!' % self.value)
        elif self.type is float:
            if not isinstance(self.value, (float)):
                raise ConfigValueError('%s is not a float!' % self.value)
        elif self.type is int:
            if not isinstance(self.value, (int)):
                raise ConfigValueError('%s is not an integer!' % self.value)
        elif self.type is str:
            if not isinstance(self.value, (str)):
                raise ConfigValueError('%s is not a string!' % self.value)

        self.validated = True

    def replace_value(self, value):
        if value:
            value = self.type(value)
        self.value = value

    def set_validation_type(self, val_type):
        valid_choices = ('path', 'email')
        if val_type in valid_choices:
            self.validation_type = val_type
        else:
            raise AttributeError('%s is not a valid validation type!' % val_type)

    def add_default_value(self, default_value):
        self.replace_value(self.env_variable_value or self.type(default_value))


class Interface(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value('cli')
        self.choices = ['cli', 'curses']


class DatabasePath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value(DATA_DIR)
        self.set_validation_type('path')


class LogoPath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value(DATA_DIR)
        self.set_validation_type('path')


class InvoicePath(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value(INVOICE_DIR)
        self.set_validation_type('path')


class MinimumHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.type = float
        self.add_default_value(2.0)


class StandardHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value('08:00-16:00')

    def validate(self):
        if re.match(r'\d\d:\d\d-\d\d:\d\d', self.value) is None:
            raise ConfigValueError('%s is the wrong format! The correct format is HH:MM-HH:MM.'
                                   % self.value)
        from_time, to_time = self.value.split('-')
        try:
            if datetime.strptime(from_time, '%H:%M') > datetime.strptime(to_time, '%H:%M'):
                error_handler('From time is higher than to time!')
        except ValueError:
            raise ConfigValueError('Wrong use of 24 hour format!')
        super().validate()


class LunchHours(ConfigValue):
    def __init__(self):
        super().__init__()
        self.type = float
        self.add_default_value(0.5)


class WagePerHour(ConfigValue):
    def __init__(self):
        super().__init__()
        self.type = int
        self.add_default_value(300)


class Currency(ConfigValue):
    def __init__(self):
        super().__init__()
        self.add_default_value('NOK')
        self.choices = ['NOK', 'ISK', 'USD']


class OrganizationNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('Organization number must contain only digits!' % self.value)
        super().validate()


class CompanyName(ConfigValue):
    def __init__(self):
        super().__init__()


class CompanyAddress(ConfigValue):
    def __init__(self):
        super().__init__()


class CompanyZip(ConfigValue):
    def __init__(self):
        super().__init__()

    def validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super().validate()


class CompanyAccountNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super().validate()


class PhoneNumber(ConfigValue):
    def __init__(self):
        super().__init__()

    def validate(self):
        try:
            int(self.value.replace(' ', ''))
        except ValueError:
            raise ConfigValueError('%s is not an integer!' % self.value)
        super().validate()


class MailAddress(ConfigValue):
    def __init__(self):
        super().__init__()
        self.set_validation_type('email')


class ValuesWrapper(object):
    def __repr__(self):
        repr_string = '\n'
        for key, value in self.__dict__.items():
            repr_string += '%s: %s\n' % (str(key.replace('_', ' ')), str(value.value))
        return repr_string

    def add(self, value):
        if issubclass(value.__class__, ConfigValue):
            regex = re.compile('(?!^)(?=[A-Z])')
            name = re.sub(regex, '_', value.__class__.__name__).lower()
            setattr(self, name, value)
        else:
            raise ValueError('value argument must be a ConfigValue class!')


class Config(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.values = ValuesWrapper()
        self.file_exists = False

        # Add values
        self.values.add(Interface())
        self.values.add(DatabasePath())
        self.values.add(LogoPath())
        self.values.add(InvoicePath())
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

        if config_path:
            try:
                self.load()
            except ConfigValueError as err_msg:
                error_handler(err_msg)

    def validate_config_values(self):
        for value in self.values.__dict__.values():
            if value.value:
                try:
                    value.validate()
                except ConfigValueError as err_msg:
                    error_handler('Error when validating the %s option in config file!' % value.__class__.__name__, exit_on_error=False)
                    error_handler(err_msg)

    def load(self):
        """Load config.

        User defined config files will take precedence over the built in config.
        """
        try:
            with open(self.config_path, 'r') as config_readout:
                try:
                    config = yaml.load(config_readout)
                    self.file_exists = True
                except yaml.YAMLError as err:
                    print(err)
                    sys.exit(64)
        except FileNotFoundError:
            return None
        for key, value in config.items():
            key = key.replace(' ', '_')
            if key not in self.values.__dict__.keys():
                raise ConfigValueError('%s is not a valid config setting' % key)
            else:
                config_setting = self.values.__dict__[key]
                config_setting.replace_value(value)
                # Validate
                if value:
                    try:
                        config_setting.validate()
                    except ConfigValueError as err_msg:
                        error_handler('Error when validating the %s option in config file!' % config_setting.__class__.__name__, exit_on_error=False)
                        error_handler(err_msg)

    def write(self, value):
        if not os.path.exists(os.path.dirname(self.config_path)):
            os.makedirs(os.path.dirname(self.config_path))
        with open(self.config_path, 'w') as config_readout:
            try:
                yaml.dump(value, config_readout, default_flow_style=False)
            except yaml.YAMLError as err:
                print(err)
                sys.exit(64)
