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

# LOGGING FUNCTION BEFORE LOGGING MODULE SETUP
def print_logging(message):
    print('PRINT : ' + message)

# CHECK ENV
import platform
if not platform.python_version().startswith('3.'):
    print_logging('Python must be version 3')
    exit(1)
try:
    import markdown
except:
    print_logging('Unable to import markdown module. please install it via pip')
    exit(1)
print_logging('Python env is OK')

############
### MAIN ###
############

import os
import os.path as path
import logging
import argparse
import configparser

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

###################
### Version 0.1 ###
###################

CONFIG_TEMPLATE_V0_1 = '''[basic]
version : 0.1
logging_level : INFO
logging_file : False
logfile : log.out

[directory]
markdown : markdown
html : html

[template]
template : template.html
replace : replace.txt

[md_html]
01.md : index.html
02.md : html02.html
'''

class Md2Html_v0_1:

    def __init__(self, config_file):
        self.config_file = config_file
        self.dir_markdown = None
        self.dir_html = None
        self.tpt_template = None
        self.template_text = None
        self.tpt_replace = None
        self.replace_dict = None
        self.mdhtml = None

        # VERSION
        self.VERSION = '0.1'

    def run(self):
        # PRE PROCESS
        print_logging('========= pre process phase start =========')
        self.__cd_to_script_dir()
        self.__load_config()
        self.__check_file_exists()
        self.__load_template()
        self.__dump()
        logging.info('========= pre process phase end =========')

        # CONVERT MARKDOWN AND MAKE HTML PAGES
        logging.info('========= convert phase start =========')
        self.__convert_from_markdown_to_html()
        self.__copy_other_files()
        logging.info('========= convert phase end =========')


        '''
        self.__template_path = config[self.TEMPLATE]
        replace_path = config[self.REPLACE]
        (template, replace_pattern) = load_template(template_path, replace_path)
        convert(config, template, replace_pattern)
        copy_other_files(config)
        '''

        # POST PROCESS

    def __dump(self):
        logging.debug('    self.config_file = {}'.format(self.config_file))
        logging.debug('    self.dir_markdown = {}'.format(self.dir_markdown))
        logging.debug('    self.dir_html = {}'.format(self.dir_html))
        logging.debug('    self.tpt_template = {}'.format(self.tpt_template))
        logging.debug('    self.template_text = {}'.format(self.template_text))
        logging.debug('    self.tpt_replace = {}'.format(self.tpt_replace))
        logging.debug('    self.replace_dict = {}'.format(self.replace_dict))
        logging.debug('    self.mdhtml = [')
        for item in self.mdhtml:
            logging.debug('        {},'.format(item))
        logging.debug('    ]')

    def __cd_to_script_dir(self):
        absfilepath = os.path.abspath(__file__)
        absdirpath = path.dirname(absfilepath)
        os.chdir(absdirpath)
        print_logging('cd to script dir "{}".'.format(absdirpath))

    def __load_config(self):
        print_logging('loading config start')

        def set_logging(config):
            level_str = config.get('logging', 'level').upper()
            level_upper = level_str.upper()
            if level_upper == 'CRITICAL':
                level = logging.CRITICAL
            elif level_upper == 'ERROR':
                level = logging.ERROR
            elif level_upper == 'WARNING':
                level = logging.WARNING
            elif level_upper == 'INFO':
                level = logging.INFO
            elif level_upper == 'DEBUG':
                level = logging.DEBUG
            else:
                print_logging('log level {} is not defined'.format(level_str))
                raise

            if not config.has_option('logging', 'write_to_file'):
                write_to_file = False
                log_file = ''
            else:
                wtf = config.get('logging', 'write_to_file').upper()
                if wtf == 'TRUE':
                    write_to_file = True
                    log_file = config.get('logging', 'file')
                elif wtf == 'FALSE':
                    write_to_file = False
                    log_file = ''
                else:
                    print_logging('option write_to_file must be "True" or "False"')
                    raise

            if write_to_file:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

            else:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

        if not path.exists(self.config_file):
            with open(self.config_file, 'w') as fout:
                fout.write(CONFIG_TEMPLATE_V0_1)
            exit(1)
        print_logging('config file {} exist.'.format(self.config_file))

        loaded_logging_setting = False
        try:
            # READ
            config = configparser.ConfigParser()
            config.read(self.config_file)
            print_logging('config file read succes')

            # VERSION CHECK
            version = config.get('basic', 'version')
            if version != self.VERSION:
                raise
            print_logging('config file version "{}" is same.'.format(version))

            # LOGGING
            set_logging(config)
            loaded_logging_setting = True
            logging.info('loading logging setting done')

            # Directory
            dir_markdown = config.get('directory', 'markdown')
            self.dir_markdown = os.path.abspath(dir_markdown)
            dir_html = config.get('directory', 'html')
            self.dir_html = os.path.abspath(dir_html)
            logging.info('loading directory setting done')

            # Template
            tpt_template = config.get('template', 'template')
            if not path.isabs(tpt_template):
                tpt_template = path.join(self.dir_markdown, tpt_template)
            self.tpt_template = tpt_template

            tpt_replace = config.get('template', 'replace')
            if not path.isabs(tpt_replace):
                tpt_replace = path.join(self.dir_markdown, tpt_replace)
            self.tpt_replace = tpt_replace
            logging.info('loading template setting done')

            # Markdown_Html
            mdhtml = config.items('md_html')
            abs_list = []
            for(markdown, html) in mdhtml:
                if not path.isabs(markdown):
                    markdown = path.join(self.dir_markdown, markdown)
                if not path.isabs(html):
                    html = path.join(self.dir_html, html)
                abs_list.append((markdown, html))
            self.mdhtml = abs_list
            logging.info('loading "markdown to html" mapping setting done')

        except Exception as e:
            if loaded_logging_setting:
                logging.critical('loading config fail. {}'.format(e))
            else:
                print_logging('loading config fail. {}'.format(e))
            exit(1)

        logging.info('loading all config success')

    def __check_file_exists(self):
        try:
            # Markdown Directory
            dir_markdown = self.dir_markdown
            if not path.isdir(dir_markdown):
                print('WARNING: directory "{}" doesn\'t exist'.format(dir_markdown))
                raise
            logging.info('markdown directory "{}" exist'.format(dir_markdown))

            # HTML Directory
            dir_html = self.dir_html
            if not path.isdir(dir_html):
                if not path.isfile(dir_html):
                    logging.info('html directory "{}" doesn\'t exist. create'.format(dir_html))
                    os.mkdir(dir_html)
                else:
                    print('WARNING: non directory file "{}" exists'.format(dir_html))
                    raise
            else:
                logging.info('html directory "{}" exist'.format(dir_html))

            files = [tup[0] for tup in self.mdhtml]
            files.append(self.tpt_template)
            files.append(self.tpt_replace)
            for f in files:
                if not path.isfile(f):
                    raise
            logging.info('template and markdown files are exist')

        except Exception as e:
            print(e)
            print("ERROR: file doesn't exist")
            exit(1)

        logging.info('all directories and files in config exist.')

    def __load_template(self):
        try:
            with open(self.tpt_template, 'r') as fin:
                self.template_text = fin.read()
            logging.info('load template success')

            replace_pattern = {}
            with open(self.tpt_replace, 'r') as fin:
                # LATER
                pass
            logging.info('load replace pattern success')

        except:
            print("ERROR: failed to load template and replace pattern files")
            exit(1)

    def __convert_from_markdown_to_html(self):

        def apply_template(html_text):
            return html_text

        def replace_keywords(html_text):
            return html_text

        try:
            for (markdown_path, html_path) in self.mdhtml:
                logging.info('converting from {} to {}'.format(markdown_path, html_path))
                with open(markdown_path, 'r') as fin:
                    markdown_text = fin.read()

                md = markdown.Markdown()
                html_text = md.convert(markdown_text)
                html_text = apply_template(html_text)
                html_text = replace_keywords(html_text)

                with open(html_path, 'w') as fout:
                    fout.write(html_text)

            logging.info('all convert finished')

        except Exception as e:
            logging.debug('Failed converting from markdown to html. {}'.format(e))
            exit(1)

    def __copy_other_files(self):
        pass

    def __check_html(self):
        pass

if __name__ == '__main__':
    (version, config_path) = get_args()
    m2h = get_instance(version, config_path)
    m2h.run()
