# Stamp introduction
Register work hours in cli.
Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.
Hours are saved to a sqlite database and exportable to pdf.
PDF is currently in Norwegian, needs to be translated.


# Table of Contents
<!-- vim-markdown-toc GitLab -->

+ [Environment variables](#environment-variables)
+ [Install](#install)
        - [(Optional) Create virtual python environment](#optional-create-virtual-python-environment)
        - [Download the "stable" version which is currently 0.1.8](#download-the-stable-version-which-is-currently-018)
+ [Config](#config)
+ [Usage](#usage)
+ [Development](#development)
+ [Contribute](#contribute)
    * [Translations](#translations)
        - [(Optional) Create virtual python environment](#optional-create-virtual-python-environment-1)
        - [Install development requirements](#install-development-requirements)
        - [Add locale](#add-locale)
        - [Create locale](#create-locale)
        - [Translate po](#translate-po)
+ [Disclaimer](#disclaimer)
+ [Version change summary](#version-change-summary)

<!-- vim-markdown-toc -->

# Environment variables

See stamp/settings.py.


# Install
### (Optional) Create virtual python environment
Download and install 'virtualenv' for your distribution.

```bash
mkvirtualenv 'stamp-0.1.8'
workon 'stamp-0.1.8'
```

### Download the "stable" version which is currently 0.1.8

```bash
wget https://gitlab.com/arivarton/stamp/-/archive/0.1.8/stamp-0.1.8.tar.gz
tar -xvzf stamp-0.1.8.tar.gz
cd stamp-0.1.8
python3 setup.py install
```


# Config
Config file location should be in $XDG_CONFIG_HOME/.config/stamp/config. If the XDG environment variable is not set then the directory is ~/.config/stamp/config.

```bash
# See available config options and their current values 
stamp config show
# See available values to edit
stamp config edit --help
# Edit values AND create config file if not present
stamp config edit --value 'my option'
# Provision a config file with current config values
stamp config provision
```

To set config values it's possible to use either a config file or environment variables.
The config file has the highest priority.

The environment variables take the same name as in the config file but with a preceding 'STAMP_' and the rest in uppercase. For example: 'STAMP_DATABASE_PATH'.


# Usage
Run `stamp --help`


# Development
Look in stamp/main.py to get a quick overview.

When changing code for mappings, any old databases will be uncompatible with the changes. 
A manual fix by entering the hours again to a new database will be required.


# Contribute

## Translations

### (Optional) Create virtual python environment
```bash
mkvirtualenv 'stamp-dev'
workon 'stamp-dev'
```

### Install development requirements
```bash
pip install -r dev-requirements.txt
```

### Add locale
To create a new translation add the locale name to the 'SUPPORTED_LANGUAGES' constant in stamp/__init__.py.

### Create locale
```bash
invoke translate
```
This will create a po file in the locale/ folder which has the same name as the locale specified in SUPPORTED_LANGUAGES.

### Translate po
Now the po can be translated. The mo file will be automatically installed when running setup.py.



# Disclaimer
This software is still in alpha and is therefore not recommended for daily usage as any changes of versions can make the old database unreadable.


# Version change summary
- 0.1.8: 
   - (995797c) Changed the way hours and wage is calculcated and displayed. Using decimals instead of the hours and minutes approach.
   - (08d16e1) Implemented the ability to change project assigned to workday.
- 0.1.7: 
   - Config has been implemented.
