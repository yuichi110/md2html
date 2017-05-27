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

# CHECK ENVIRONMENT
import platform
if not platform.python_version().startswith('3.'):
    print_logging('Python must be version 3')
    exit(1)
try:
    import markdown as markdown_mod
    #import jinja2
except:
    print_logging('Unable to import markdown module. please install them via pip')
    exit(1)
print_logging('Python env is OK')


############
### MAIN ###
############

import logging
import argparse
import configparser

import os
import os.path as path
import shutil

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
        self.dir_template = None
        self.dict_markdown = None

        # VERSION
        self.VERSION = '0.1'

    def run(self):
        # PRE PROCESS
        print_logging('========= pre process phase start =========')
        self.__cd_to_script_dir()
        self.__load_config()
        self.__dump()
        self.__check_file_exists()
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
        logging.debug('{}'.format(self.dict_markdown))
        #logging.debug('    self.tpt_template = {}'.format(self.tpt_template))
        #logging.debug('    self.template_text = {}'.format(self.template_text))
        #logging.debug('    self.tpt_replace = {}'.format(self.tpt_replace))
        #logging.debug('    self.replace_dict = {}'.format(self.replace_dict))
        #logging.debug('    self.mdhtml = [')
        #for item in self.mdhtml:
        #    logging.debug('        {},'.format(item))
        #logging.debug('    ]')

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


        # CHECK CONFIG EXISTS
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
            print_logging('loading [basic] section success')
            if version != self.VERSION:
                raise
            print_logging('config file version "{}" is same to arg version "{}"'.format(version, self.VERSION))

            # LOGGING
            set_logging(config)
            loaded_logging_setting = True
            logging.info('loading [logging] section done')

            # Directory
            dir_markdown = config.get('directory', 'markdown')
            self.dir_markdown = os.path.abspath(dir_markdown)
            dir_html = config.get('directory', 'html')
            self.dir_html = os.path.abspath(dir_html)
            dir_template = config.get('directory', 'template')
            self.dir_template = os.path.abspath(dir_template)
            logging.info('loading [directory] section done')

            # Template
            abs_template = config.get('template', 'template')
            if not path.isabs(abs_template):
                abs_template = path.join(self.dir_template, abs_template)

            abs_replace = config.get('template', 'replace')
            if not path.isabs(abs_replace):
                abs_replace = path.join(self.dir_template, abs_replace)
            logging.info('loading [template] section done')

            # Markdown
            dict_markdown = {'template':abs_template, 'replace':abs_replace}
            md_sections = filter(lambda text : text.endswith('.md'), config.sections())
            for md_section in md_sections:
                d = {}

                md_path = path.join(self.dir_markdown, md_section)
                d['markdown'] = md_path

                html = config.get(md_section, 'html')
                if not path.isabs(html):
                    html = path.join(self.dir_html, html)
                d['html'] = html

                if config.has_option(md_section, 'template'):
                    template = config.get(md_section, 'template')
                    if not path.isabs(template):
                        template = path.join(self.dir_template, template)
                    d['template'] = template

                if config.has_option(md_section, 'replace'):
                    replace = config.get(md_section, 'replace')
                    if not path.isabs(replace):
                        replace = path.join(self.dir_template, replace)
                    d['replace'] = replace

                dict_markdown[md_section] = d
                logging.info('loading markdown [{}] section done'.format(md_section))

            self.dict_markdown = dict_markdown
            logging.info('loading all markdown sections done')

        except Exception as e:
            if loaded_logging_setting:
                logging.critical('loading config fail. {}'.format(e))
            else:
                print_logging('loading config fail. {}'.format(e))
            exit(1)

        logging.info('loading all sections success')


    def __check_file_exists(self):
        try:
            # Template Directory
            dir_template = self.dir_template
            if not path.isdir(dir_template):
                logging.warning('template directory "{}" doesn\'t exist'.format(dir_template))
                raise
            logging.info('template directory "{}" exist'.format(dir_template))

            if not path.isfile(self.dict_markdown['template']):
                logging.warning('general template file "{}" doesn\'t exist'.format(self.dict_markdown['template']))
                raise
            logging.info('general template file "{}" exist'.format(self.dict_markdown['template']))

            if not path.isfile(self.dict_markdown['replace']):
                logging.warning('general replace file "{}" doesn\'t exist'.format(self.dict_markdown['replace']))
                raise
            logging.info('general replace file "{}" exist'.format(self.dict_markdown['replace']))

            # Markdown Directory
            dir_markdown = self.dir_markdown
            if not path.isdir(dir_markdown):
                logging.warning('directory "{}" doesn\'t exist'.format(dir_markdown))
                raise
            logging.info('markdown directory "{}" exist'.format(dir_markdown))

            # Markdown Files and it's templates
            markdowns = filter(lambda text : text.endswith('.md'), self.dict_markdown.keys())
            for markdown in markdowns:
                for (key, value) in self.dict_markdown[markdown].items():
                    if key == 'html':
                        continue
                    if not path.isfile(value):
                        logging.warning('"{}" doesn\'t exist.'.format(value))
                        logging.warning('please check config section "[{}]" and files'.format(markdown))
                        raise
                logging.info('all files for "{}" exist'.format(markdown))
            logging.info('template and markdown files are exist')

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

        except Exception as e:
            print(e)
            print("ERROR: file doesn't exist")
            exit(1)

        logging.info('all directories and files in config exist.')


    def __convert_from_markdown_to_html(self):

        logging.info('start converting.')

        _file_content = {}
        def get_file_content(file_path):
            if file_path not in _file_content:
                with open(file_path, 'r') as fin:
                    _file_content[file_path] = fin.read()

            return _file_content[file_path]

        def replace_keywords(html_text, json_text):
            return html_text

        def all_keywords_changed(html_text):
            return True

        try:
            markdowns = filter(lambda text : text.endswith('.md'), self.dict_markdown.keys())
            for markdown in markdowns:
                logging.info('start converting {}.'.format(markdown))
                dict_md = self.dict_markdown[markdown]
                print(dict_md)

                # CONVERT
                md = markdown_mod.Markdown()
                path_md = dict_md['markdown']
                text_md = get_file_content(path_md)
                content_html = md.convert(text_md)
                content_html = '\n<!-- GENERATED HTML START -->\n {} \n<!-- GENERATED HTML END -->\n'.format(content_html)
                logging.debug('    convert done')

                # TEMPLATE
                path_template = dict_md.get('template', self.dict_markdown['template'])
                template_text = get_file_content(path_template)
                if '{{ MARKDOWN }}' not in template_text:
                    logging.warning('template "{}" doesn\'t have {{ MARKDOWN }}'.format(path_template))
                    raise
                logging.debug('   load template done')

                # INCLUDE
                html = template_text.replace('{{ MARKDOWN }}', content_html)
                logging.debug('   include done')

                # REPLACE
                if 'replace' in dict_md:
                    path_replace = dict_md['replace']
                    json_text = get_file_content(path_replace)
                    html = replace_keywords(html, json_text)

                path_replace = self.dict_markdown['replace']
                json_text = get_file_content(path_replace)
                html = replace_keywords(html, json_text)

                if not all_keywords_changed(html):
                    raise
                logging.debug('   replace done')

                path_html = dict_md['html']
                with open(path_html, 'w') as fout:
                    fout.write(html)

                logging.info('convert markdown [{}] done'.format(markdown))
            logging.info('all markdown convert done')

        except Exception as e:
            logging.debug('Failed converting from markdown to html. {}'.format(e))
            exit(1)

    def __copy_other_files(self):
        try:
            dir_markdown = self.dir_markdown
            dir_html = self.dir_html
            files = os.listdir(dir_markdown)

            def is_copy_target(file_name):
                if file_name.endswith('.md'):
                    return False
                if file_name in ['.DS_Store']:
                    return False
                return True

            files = filter(is_copy_target, files)
            for file_name in files:
                src_path = path.join(dir_markdown, file_name)
                dst_path = path.join(dir_html, file_name)

                if path.isfile(src_path):
                    shutil.copyfile(src_path, dst_path)
                elif path.isdir(src_path):
                    if path.isfile(dst_path):
                        os.remove(dst_path)
                    elif path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    raise

                print(src_path, dst_path)
        except Exception as e:
            logging.warning(e)
            logging.critical('Copy files fail')
            exit(1)


    def __check_html(self):
        pass

if __name__ == '__main__':
    (version, config_path) = get_args()
    m2h = get_instance(version, config_path)
    m2h.run()
