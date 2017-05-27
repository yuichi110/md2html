'''
This program will generate html webpage from markdown files and template.
It requires
 - python3
 - markdown module (able to install via pip)

Example:
    $ python md2html.py -v <PROGRAM_VERSION> -c <CONFIG_PATH> -l <LOGGING_LEVEL> -f <LOGGING_FILE>

Supported version:
 - 0.1

Author : Yuichi Ito
Version : 0.1
'''

import logging
import argparse
import configparser

import os
import os.path as path
import shutil
import re

# LOGGING FUNCTION BEFORE LOGGING MODULE SETUP
def print_logging(message):
    print('PRINT : ' + message)

# CHECK ENVIRONMENT
import platform
if not platform.python_version().startswith('3.'):
    print_logging('Python must be version 3')
    exit(1)
try:
    import markdown as markdown_mod
except:
    print_logging('Unable to import markdown module. please install them via pip')
    exit(1)
print_logging('Python env is OK')


###############
### UTILITY ###
###############

def get_args():
    description = '''description'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', help='software version. supported "0.1"', required=True)
    parser.add_argument('-c', '--config', help='configuration file name', required=True)
    args = parser.parse_args()
    return (args.version, args.config)

def get_instance(version, config_path):
    if version == '0.1':
        return Md2Html_v0_1(config_path)
    else:
        raise

####################################
### Version 0.1                  ###
### UNDER DEVELOPMENT AT SANDBOX ###
####################################



if __name__ == '__main__':
    (version, config_path) = get_args()
    m2h = get_instance(version, config_path)
    m2h.run()
