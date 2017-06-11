# LOGGING FUNCTION BEFORE LOGGING MODULE SETUP
def print_logging(message):
    print('PRINT : ' + message)

import logging
import argparse
import configparser

import os
import os.path as path
import shutil
import re
import markdown as markdown_mod
import bs4
import pdfkit

###################
### Version 0.1 ###
###################

CONFIG_TEMPLATE_V0_1 = '''[basic]
version : 0.1

[logging]
level : DEBUG
write_to_file : False
file : log.out

[directory]
markdown : markdown
html : html
template : template

[template]
template : TEMPLATE.template
replace : REPLACE.replace

[01.md]
html : index.html

[02.md]
html : 02.html
template : 02.template
replace : 02.replace
'''

class Md2Html_v0_1:

    def __init__(self, config_path):
        self.config_path = config_path

        # bootstrap
        self.bootstrap_html = False
        self.bootstrap_print = False
        self.bootstrap_pdf = False
        self.bootstrap_pdf_all = False

        # directory
        self.dir_markdown = None
        self.dir_output = None
        self.dir_template = None
        self.dir_pdf = None

        # template and markdown
        self.conv_replace = None
        self.conv_template_html = None
        self.conv_template_print = None
        self.conv_template_pdf = None
        self.conv_template_pdf_all = None
        self.conv_markdown_dict = {}

        # pdf
        self.pdf_output = None
        self.pdf_css = []
        self.pdf_dpi = None
        self.pdf_image_size_dict = {}
        self.pdf_markdowns = []

        # VAL
        self.VERSION = '0.1'
        self.TYPE_HTML = 'html'
        self.TYPE_PRINT = 'print'
        self.TYPE_PDF = 'pdf'
        self.TYPE_PDF_ALL = 'pdf_all'

    def run(self):
        self.cd_to_script_dir()

        #  LOAD CONFIG
        config_text = self.get_config_text(self.config_path)
        config = self.get_config(config_text)
        output_types = self.load_basic_section(config)

        self.load_logging_section(config)
        self.load_bootstrap_section(config)
        self.load_directory_section(config, output_types)
        self.load_template_section(config, output_types)
        self.load_markdown_sections(config, output_types)
        self.load_pdf_section(config, output_types)

        # CHECK FILES
        self.check_directory_exist(output_types)
        self.check_template_exist(output_types)
        self.check_markdown_exist(output_types)
        self.check_pdf_exist(output_types)

        # CONVERT
        if self.TYPE_HTML in output_types:
            self.convert_html()
        if self.TYPE_PRINT in output_types:
            self.convert_print()
        if self.TYPE_PDF_ALL in output_types:
            self.convert_pdf_all()
        if self.TYPE_PDF in output_types:
            self.convert_pdf()
        self.copy_other_files()
        logging.info('CONVERSION FINISHED WITHOUT PROBLEMS!!')



    def cd_to_script_dir(self):
        print_logging('cd to script dir : start')
        try:
            absfilepath = os.path.abspath(__file__)
            absdirpath = path.dirname(absfilepath)
            print_logging('    directory : "{}"'.format(absdirpath))
            os.chdir(absdirpath)
        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('cd to script dir : fail')
            print_logging('abort')
            exit(1)

        print_logging('cd to script dir : success')


    ###################
    ### CONFIG LOAD ###
    ###################

    def get_config_text(self, config_path):
        print_logging('get config text : start')
        try:
            if not path.exists(config_path):
                print_logging('config file doesn\'t exit. "{}"'.format(config_path))
                print_logging('create sample file and abort')
                with open(config_path, 'w') as fout:
                    fout.write(CONFIG_TEMPLATE_V0_1)
                exit(1)

            print_logging('config file exist. "{}"'.format(config_path))

            with open(config_path, 'r') as fin:
                config_text = fin.read()

        except Exception as e:
            print_logging(e)
            print_logging('get config text : fail')
            print_logging('abort')
            exit(1)

        print_logging('get config text : success')
        return config_text


    def get_config(self, config_text):
        print_logging('get config-object from text : start')
        try:
            config = configparser.ConfigParser()
            config.read_string(config_text)

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('get config-object from text : fail')
            print_logging('abort')
            exit(1)

        print_logging('get config-object from text : success')
        return config


    def load_basic_section(self, config):
        print_logging('load config [basic] section : start')
        try:
            # VERSION CHECK
            version = config.get('basic', 'version')
            if version != self.VERSION:
                print_logging('    found version mismatch')
                print_logging('    args : {}'.format(self.VERSION))
                print_logging('    config file : {}'.format(version))
                raise

            # OUTPUT TYPE CHECK
            output_type_str = config.get('basic', 'output_type')
            output_types = []
            for output_type in output_type_str.split(','):
                output_type = output_type.strip().lower()
                if output_type in [self.TYPE_HTML, self.TYPE_PRINT, self.TYPE_PDF, self.TYPE_PDF_ALL]:
                    if output_type not in output_types:
                        output_types.append(output_type)
            if len(output_types) == 0:
                print_logging('    found no correct output type at option output_type')
                print_logging('    needs "html" or "print" or "pdf" or "pdf_all"')
                raise

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('load config [basic] section : fail')
            exit(1)

        print_logging('   config version : {}'.format(version))
        print_logging('   output types : {}'.format(output_types))
        print_logging('load config [basic] section : success')
        return output_types


    def load_logging_section(self, config):
        print_logging('load config [logging] section : start')
        write_to_file = False
        log_file = ''

        try:
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
                print_logging('    option level "{}" is not supported'.format(level_str))
                print_logging('    print chose one of them [CRITICAL, ERROR, WARNING, INFO, DEBUG]')
                raise

            if config.has_option('logging', 'write_to_file'):
                wtf = config.get('logging', 'write_to_file').upper()
                if wtf == 'TRUE':
                    write_to_file = True
                    log_file = config.get('logging', 'file')
                elif wtf == 'FALSE':
                    write_to_file = False
                else:
                    print_logging('   option write_to_file must be "True" or "False"')
                    raise

            if write_to_file:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

            else:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('load config [logging] section : fail')
            print_logging('abort')
            exit(1)

        logging.debug('    level = "{}"'.format(level_upper))
        logging.debug('    write_to_file = "{}"'.format(write_to_file))
        logging.debug('    file = "{}"'.format(log_file))
        logging.info('load config [logging] section : success')


    def load_bootstrap_section(self, config):
        logging.info('load config [bootstrap] section : start')

        def get_bool(text):
            text = text.upper()
            if text == 'TRUE':
                return True
            elif text == 'FALSE':
                return False
            else:
                logging.warning('    option value must be "True" or "False"')
                raise

        try:
            if not config.has_section('bootstrap'):
                logging.info('load config [bootstrap] section : does not exist. skip')
                return

            if config.has_option('bootstrap', 'html'):
                self.bootstrap_html = get_bool(config.get('bootstrap', 'html'))
            if config.has_option('bootstrap', 'print'):
                self.bootstrap_print = get_bool(config.get('bootstrap', 'print'))
            if config.has_option('bootstrap', 'pdf'):
                self.bootstrap_pdf = get_bool(config.get('bootstrap', 'pdf'))
            if config.has_option('bootstrap', 'pdf_all'):
                self.bootstrap_pdf_all = get_bool(config.get('bootstrap', 'pdf_all'))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [bootstrap] section : fail')
            exit(1)

        logging.debug('   html : {}'.format(self.bootstrap_html))
        logging.debug('   print : {}'.format(self.bootstrap_print))
        logging.debug('   pdf : {}'.format(self.bootstrap_pdf))
        logging.debug('   pdf_all : {}'.format(self.bootstrap_pdf_all))
        logging.info('load config [bootstrap] section : success')


    def load_directory_section(self, config, output_types):
        logging.info('load config [directory] section : start')

        try:
            dir_markdown = config.get('directory', 'markdown')
            self.dir_markdown = os.path.abspath(dir_markdown)

            dir_output = config.get('directory', 'output')
            self.dir_output = os.path.abspath(dir_output)

            dir_template = config.get('directory', 'template')
            self.dir_template = os.path.abspath(dir_template)

            if config.has_option('directory', 'pdf'):
                dir_pdf = config.get('directory', 'pdf')
                self.dir_pdf = os.path.abspath(dir_pdf)
            else:
                if (self.TYPE_PDF in output_types) or (self.TYPE_PDF_ALL in output_types):
                    logging.warning('output_type pdf or pdf_all requires pdf option at section directory')
                    raise

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [directory] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    markdown : "{}"'.format(self.dir_markdown))
        logging.debug('    output : "{}"'.format(self.dir_output))
        logging.debug('    template : "{}"'.format(self.dir_template))
        logging.debug('    pdf : "{}"'.format(self.dir_pdf))
        logging.info('load config [directory] section : success')


    def load_template_section(self, config, output_types):
        logging.info('load config [template] section : start')
        try:
            fname = config.get('template', 'replace')
            self.conv_replace = path.join(self.dir_template, fname)

            if self.TYPE_HTML in output_types:
                fname = config.get('template', 'html')
                self.conv_template_html = path.join(self.dir_template, fname)

            if self.TYPE_PRINT in output_types:
                fname = config.get('template', 'print')
                self.conv_template_print = path.join(self.dir_template, fname)

            if self.TYPE_PDF in output_types:
                fname = config.get('template', 'pdf')
                self.conv_template_pdf = path.join(self.dir_template, fname)

            if self.TYPE_PDF_ALL in output_types:
                fname = config.get('template', 'pdf_all')
                self.conv_template_pdf_all = path.join(self.dir_template, fname)

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [template] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    template html : "{}"'.format(self.conv_template_html))
        logging.debug('    template print : "{}"'.format(self.conv_template_print))
        logging.debug('    template pdf : "{}"'.format(self.conv_template_pdf))
        logging.debug('    template pdf_all : "{}"'.format(self.conv_template_pdf_all))
        logging.debug('    replace : "{}"'.format(self.conv_replace))
        logging.info('load config [template] section : success')


    def load_markdown_sections(self, config, output_types):
        logging.info('load config markdown sections : start')
        try:
            dict_markdown = {}
            markdown_sections = filter(lambda text : text.endswith('.md'), config.sections())
            for markdown_section in markdown_sections:
                logging.info('    section [{}] : start'.format(markdown_section))
                d = {}

                # markdown path
                markdown_path = path.join(self.dir_markdown, markdown_section)
                d['markdown'] = markdown_path

                # html
                if self.TYPE_HTML in output_types:
                    fname = config.get(markdown_section, 'html')
                    d['html'] = path.join(self.dir_output, fname)

                    if config.has_option(markdown_section, 'html_template'):
                        fname = config.get(markdown_section, 'html_template')
                        d['html_template'] = path.join(self.dir_template, fname)

                # print
                if self.TYPE_PRINT in output_types:
                    fname = config.get(markdown_section, 'print')
                    d['print'] = path.join(self.dir_output, fname)

                    if config.has_option(markdown_section, 'print_template'):
                        fname = config.get(markdown_section, 'print_template')
                        d['print_template'] = path.join(self.dir_template, fname)

                # pdf
                if self.TYPE_PDF in output_types:
                    fname = config.get(markdown_section, 'pdf')
                    d['pdf'] = path.join(self.dir_output, fname)

                    if config.has_option(markdown_section, 'pdf_template'):
                        fname = config.get(markdown_section, 'pdf_template')
                        d['pdf_template'] = path.join(self.dir_template, fname)

                # replace
                if config.has_option(markdown_section, 'replace'):
                    fname = config.get(markdown_section, 'replace')
                    d['replace'] = path.join(self.dir_template, fname)

                dict_markdown[markdown_section] = d

                for (key, value) in d.items():
                    logging.debug('        {} : {}'.format(key, value))
                logging.info('    section [{}] : success'.format(markdown_section))


            self.conv_markdown_dict = dict_markdown

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config markdown sections : fail')
            logging.critical('abort')
            exit(1)

        logging.info('load config markdown sections : success')


    def load_pdf_section(self, config, output_types):
        logging.info('load [pdf] section : start')
        try:
            if (self.TYPE_PDF not in output_types) and (self.TYPE_PDF_ALL not in output_types):
                logging.info('load [pdf] section : output type does not have pdf and pdf_all. skip')
                return

            # output
            output = config.get('pdf', 'output')
            if not path.isabs(output):
                output = path.join(self.dir_output, output)
            self.pdf_output = output

            # css
            css_str = config.get('pdf', 'css')
            css_files = []
            for css in css_str.split(','):
                css = css.strip()
                css = path.join(self.dir_pdf, css)
                css_files.append(css)
            self.pdf_css = css_files

            # dpi
            dpi = config.get('pdf', 'dpi')
            self.pdf_dpi = int(dpi)

            # markdowns
            markdowns_str = config.get('pdf', 'markdowns')
            markdowns = []
            for markdown in markdowns_str.split(','):
                markdown = markdown.strip()
                markdown_path = path.join(self.dir_markdown, markdown)
                markdowns.append((markdown, markdown_path))
            self.pdf_markdowns = markdowns

            # image
            image_size_file = config.get('pdf', 'image_size')
            image_size_path = path.join(self.dir_pdf, image_size_file)
            config_text = self.get_config_text(image_size_path)
            config = self.get_config(config_text)
            for section in config.sections():
                d = {}
                for option in config.options(section):
                    value = config.get(section, option)
                    d[option] = value
                self.pdf_image_size_dict[section] = d

            print(self.pdf_image_size_dict)

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load [pdf] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    output : {}'.format(self.pdf_output))
        logging.debug('    css : {}'.format(self.pdf_css))
        logging.debug('    dpi : {}'.format(self.pdf_dpi))
        logging.debug('    markdowns : [')
        for markdown in self.pdf_markdowns:
            logging.debug('        {},'.format(markdown))
        logging.debug('    ]')
        logging.info('load [pdf] section : success')




    ########################
    ### CHECK FILE EXIST ###
    ########################

    def check_directory_exist(self, output_types):
        logging.info('check all directory exist : start')
        try:
            # Markdown Directory
            dir_markdown = self.dir_markdown
            if not path.isdir(dir_markdown):
                logging.warning('    markdown : not exist')
                logging.warning('    {}'.format(dir_markdown))
                raise
            logging.info('    markdown : exist')

            # Output Directory
            dir_output = self.dir_output
            if not path.isdir(dir_output):
                if not path.isfile(dir_output):
                    logging.info('    output : not exist. create')
                    logging.info('    {}'.format(dir_output))
                    os.mkdir(dir_output)
                else:
                    logging.warning('    output : directory not exist. but file exist.')
                    logging.warning('    {}'.format(dir_output))
                    raise
            else:
                logging.info('    output : exist'.format())

            # Template Directory
            dir_template = self.dir_template
            if not path.isdir(dir_template):
                logging.warning('    template : not exist')
                logging.warning('    {}'.format(dir_template))
                raise
            logging.info('    template : exist')

            # PDF Directory
            if (self.TYPE_PDF in output_types) or (self.TYPE_PDF_ALL in output_types):
                dir_pdf = self.dir_pdf
                if not path.isdir(dir_pdf):
                    logging.warning('    pdf : not exist')
                    logging.warning('    {}'.format(dir_pdf))
                    raise
                logging.info('    pdf : exist')

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check all directory exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check all directory exist : success')


    def check_template_exist(self, output_types):
        logging.info('check basic template exist : start')
        try:
            replace = self.conv_replace
            if not path.isfile(replace):
                logging.warning('   replace : not exit')
                logging.warning('   {}'.format(replace))
                raise
            logging.info('    replace : exist')

            if self.TYPE_HTML in output_types:
                template = self.conv_template_html
                if not path.isfile(template):
                    logging.warning('   html template : not exit')
                    logging.warning('   {}'.format(template))
                    raise
                logging.info('    html template : exist')

            if self.TYPE_PRINT in output_types:
                template = self.conv_template_print
                if not path.isfile(template):
                    logging.warning('   print template : not exit')
                    logging.warning('   {}'.format(template))
                    raise
                logging.info('    print template : exist')

            if self.TYPE_PDF in output_types:
                template = self.conv_template_pdf
                if not path.isfile(template):
                    logging.warning('   pdf template : not exit')
                    logging.warning('   {}'.format(template))
                    raise
                logging.info('    pdf template : exist')

            if self.TYPE_PDF_ALL in output_types:
                template = self.conv_template_pdf_all
                if not path.isfile(template):
                    logging.warning('   pdf_all template : not exit')
                    logging.warning('   {}'.format(template))
                    raise
                logging.info('    pdf_all template : exist')

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check basic template exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check basic template exist : success')


    def check_markdown_exist(self, output_type):
        logging.info('check markdown files exist : start')
        try:
            for (name, mapping) in self.conv_markdown_dict.items():
                logging.info('    check markdown "{}"'.format(name))
                for (key, value) in mapping.items():
                    if key == 'html':
                        continue
                    if key == 'print':
                        continue
                    if key == 'pdf':
                        continue

                    if not path.isfile(value):
                        logging.warning('        {} : not exist.'.format(key))
                        logging.warning('        {}'.format(value))
                        raise
                    logging.info('        {} : exist.'.format(key))

            if(output_type == self.TYPE_PDF_ALL):
                logging.info('    check pdf markdowns')
                for (md_name, md_path) in self.pdf_markdowns:
                    if not path.isfile(md_path):
                        logging.warning('        {} : not exist.'.format(md_name))
                        logging.warning('        {}'.format(md_path))
                        raise
                    logging.info('        {} : exist'.format(md_name))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check markdown files exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check markdown files exist : success')


    def check_pdf_exist(self, output_types):
        if (self.TYPE_PDF not in output_types) or (self.TYPE_PDF_ALL not in output_types):
            return

        logging.info('check pdf files exist : start')
        try:
            logging.info('    check css files')
            for css in self.pdf_css:
                if not path.isfile(css):
                    logging.warning('        {} : not exist.'.format(css))
                    raise
                logging.info('        {} : exist'.format(css))

            for (file_name, file_path) in self.pdf_markdowns:
                if not path.isfile(file_path):
                    logging.warning('        {} : not exist.'.format(file_path))
                    raise
                logging.info('        {} : exist'.format(file_path))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check pdf files exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check pdf files exist : success')


    ###############
    ### CONVERT ###
    ###############

    def convert_html(self):
        logging.info('convert html : start')
        try:
            for (markdown, d) in self.conv_markdown_dict.items():
                if 'html' not in d:
                    continue

                logging.info('    markdown : {}'.format(markdown))
                path_markdown = d['markdown']
                path_html = d['html']

                path_template = self.conv_template_html
                if 'html_template' in d:
                    path_template = d['html_template']

                path_replaces = [self.conv_replace]
                if 'replace' in d:
                    path_replaces.insert(0, d['replace'])
                logging.debug(('        load path info : success'))

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html_markdown = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap_html:
                    html_markdown = self.modify_html_bootstrap(html_markdown)
                logging.debug(('        convert markdown to content html : success'))

                # include markdown html to template html
                html_template = self.get_template_html(path_template)
                html = self.modify_html_include_markdown_html(html_markdown, html_template)
                logging.debug(('        include content html to template html : success'))

                # replace keywords
                for replace in path_replaces:
                    html = self.modify_html_keyword(html, replace)
                all_changed = self.check_all_keywords_changed(html)
                if not all_changed:
                    raise
                logging.debug(('        replayce keywords : success'))

                html = self.prettify_html(html, 4)
                logging.debug(('        format html : success'))

                # write
                with open(path_html, 'w') as fout:
                    fout.write(html)
                logging.debug(('        write to file : success'))

        except Exception as e:
            logging.critical('   {}'.format(e))
            logging.critical('convert html : fail')
            exit(1)

        logging.info('convert html : success')


    def convert_print(self):
        logging.info('convert print : start')
        try:
            for (markdown, d) in self.conv_markdown_dict.items():
                if 'print' not in d:
                    continue

                logging.info('    markdown : {}'.format(markdown))
                path_markdown = d['markdown']
                path_html = d['print']

                path_template = self.conv_template_print
                if 'print_template' in d:
                    path_template = d['print_template']

                path_replaces = [self.conv_replace]
                if 'replace' in d:
                    path_replaces.insert(0, d['replace'])
                logging.debug(('        load path info : success'))

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html_markdown = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap_print:
                    html_markdown = self.modify_html_bootstrap(html_markdown)
                logging.debug(('        convert markdown to content html : success'))

                # include markdown html to template html
                html_template = self.get_template_html(path_template)
                html = self.modify_html_include_markdown_html(html_markdown, html_template)
                logging.debug(('        include content html to template html : success'))

                # replace keywords
                for replace in path_replaces:
                    html = self.modify_html_keyword(html, replace)
                all_changed = self.check_all_keywords_changed(html)
                if not all_changed:
                    raise
                logging.debug(('        replayce keywords : success'))

                html = self.prettify_html(html, 4)
                logging.debug(('        format html : success'))

                # write
                with open(path_html, 'w') as fout:
                    fout.write(html)
                logging.debug(('        write to file : success'))

        except Exception as e:
            logging.critical('   {}'.format(e))
            logging.critical('convert print : fail')
            exit(1)

        logging.info('convert print : success')

    def convert_pdf(self):
        logging.info('convert pdf : start')
        try:
            for (markdown, d) in self.conv_markdown_dict.items():
                if 'pdf' not in d:
                    continue

                logging.info('    markdown : {}'.format(markdown))
                path_markdown = d['markdown']
                path_html = d['pdf']

                path_template = self.conv_template_pdf
                if 'pdf_template' in d:
                    path_template = d['pdf_template']

                path_replaces = [self.conv_replace]
                if 'replace' in d:
                    path_replaces.insert(0, d['replace'])
                logging.debug(('        load path info : success'))

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html_markdown = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap_pdf:
                    html_markdown = self.modify_html_bootstrap(html_markdown)
                logging.debug(('        convert markdown to content html : success'))

                # change URL to local
                basedir = path.dirname(path_markdown)
                html_markdown = self.modify_html_url_localize(html_markdown, basedir)
                logging.debug(('        change image url to local : success'))

                # include markdown html to template html
                html_template = self.get_template_html(path_template)
                html = self.modify_html_include_markdown_html(html_markdown, html_template)
                logging.debug(('        include content html to template html : success'))

                # replace keywords
                for replace in path_replaces:
                    html = self.modify_html_keyword(html, replace)
                all_changed = self.check_all_keywords_changed(html)
                if not all_changed:
                    raise
                logging.debug(('        replayce keywords : success'))

                #print(html_pdf)
                self.convert_html_to_pdf(html, path_html)
                logging.debug(('        convert html to pdf : success'))

        except Exception as e:
            logging.critical('   {}'.format(e))
            logging.critical('convert html : fail')
            exit(1)

        logging.info('convert html : success')

    def convert_pdf_all(self):
        logging.info('convert pdf : start')
        try:
            html_sum = ''

            for (markdown, path_markdown) in self.pdf_markdowns:
                logging.info('    markdown : {}'.format(markdown))

                path_replaces = [self.conv_replace]
                if markdown in self.conv_markdown_dict:
                    d = self.conv_markdown_dict[markdown]
                    if 'replace' in d:
                        path_replaces.insert(0, d['replace'])
                logging.debug(('        load path info : success'))

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap_pdf_all:
                    html = self.modify_html_bootstrap(html)
                logging.debug(('        convert markdown to content html : success'))

                # replace
                for replace in path_replaces:
                    html = self.modify_html_keyword(html, replace)
                all_changed = self.check_all_keywords_changed(html)
                if not all_changed:
                    raise
                logging.debug(('        replayce keywords : success'))

                # change URL to local
                basedir = path.dirname(path_markdown)
                html = self.modify_pdf_html(html, basedir, markdown)
                logging.debug(('        change image url to local : success'))

                html_sum = '{}\n\n<!-- page -->\n\n{}'.format(html_sum, html)

            # include html_sum to template
            path_template = self.conv_template_pdf_all
            html_template = self.get_template_html(path_template)
            html_pdf = self.modify_html_include_markdown_html(html_sum, html_template)
            logging.debug(('        include content html to template html : success'))

            #print(html_pdf)
            self.convert_html_to_pdf(html_pdf, self.pdf_output)
            logging.debug(('        convert html to pdf : success'))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('convert pdf : fail')
            logging.critical('abort')
            exit(1)

        logging.info('convert pdf : success')


    def copy_other_files(self):
        logging.info('copy other files : start')
        try:
            dir_markdown = self.dir_markdown
            dir_output = self.dir_output
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
                dst_path = path.join(dir_output, file_name)

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

        except Exception as e:
            logging.critical(e)
            logging.critical('copy other files : fail')
            exit(1)

        logging.info('copy other files : success')


    ######################
    ### CONVERT HELPER ###
    ######################

    def read_file(self, file_path):
        if not hasattr(self, '_file_cache'):
            self._file_cache = {}

        if file_path not in self._file_cache:
            with open(file_path, 'r') as fin:
                self._file_cache[file_path] = fin.read()

        return self._file_cache[file_path]


    def convert_markdown_to_html(self, markdown_text):
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite'
        ]

        html = markdown_mod.markdown(markdown_text, extensions=extensions)
        return html


    def modify_html_bootstrap(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')

        # IMAGE
        tags = soup.find_all('img')
        for tag in tags:
            # add img-responsive
            if tag.has_attr('class'):
                attr_list = tag['class']
                if 'img-responsive' not in attr_list:
                    attr_list.append('img-responsive')
                    tag['class'] = attr_list
            else:
                tag['class'] = 'img-responsive'

            # add blog-img
            parent_tag = tag.parent
            if parent_tag.name == 'p':
                if parent_tag.has_attr('class'):
                    attr_list = parent_tag['class']
                    if 'blog-img' not in attr_list:
                        attr_list.append('blog-img')
                        parent_tag['class'] = attr_list
                else:
                    parent_tag['class'] = 'blog-img'

        return soup.prettify(soup.original_encoding)


    def get_template_html(self, path_template):
        html = self.read_file(path_template)
        if '{{ MARKDOWN }}' not in html:
            logging.warning('template "{}" doesn\'t have {{ MARKDOWN }}'.format(path_template))
            raise

        return html


    def modify_html_include_markdown_html(self, markdown_html, template_html):
        before = '\n<!-- GENERATED HTML START -->\n'
        after = '\n<!-- GENERATED HTML END -->\n'
        markdown_html = '{}{}{}'.format(before, markdown_html, after)

        html = template_html.replace('{{ MARKDOWN }}', markdown_html)
        return html


    def modify_html_keyword(self, html, replace_path):

        r = re.compile(r'{{\s+(\w+)\s+}}')
        def replace_line(line, replace_dict):
            m = r.search(line)
            if m:
                keyword = m.group(1)
                if keyword in replace_dict:
                    line = line.replace(m.group(0), replace_dict[keyword])
            return line

        # Load replace pattern
        replace_text = self.read_file(replace_path)
        replace_dict = {}
        exec(replace_text, locals(), replace_dict)

        # Replace line
        new_lines = []
        for line in html.split('\n'):
            new_lines.append(replace_line(line, replace_dict))

        # make new html
        html = '\n'.join(new_lines)
        return html


    def check_all_keywords_changed(self, html_text):
        try:
            r = re.compile(r'{{\s+(\w+)\s+}}')
            for line in html_text.split('\n'):
                m = r.search(line)
                if m:
                    logging.warning('find unreplaced keyword at "{}"'.format(line))
                    return False
            return True

        except Exception as e:
            exit(1)

    def prettify_html(self, html, indent_width):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        html = soup.prettify(soup.original_encoding)
        return html

    def convert_html_to_pdf(self, html, pdf_path):
        options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'no-outline': None,
            'page-width':'800px',
            'minimum-font-size':30,
            'dpi':str(self.pdf_dpi)
        }
        css = self.pdf_css
        pdfkit.from_string(html, pdf_path, options=options, css=css)


    def modify_pdf_html(self, html, basedir, markdown):

        def get_abspath(relative_path):
            p1 = path.join(basedir, relative_path)
            abs_path = path.abspath(p1)
            return abs_path

        def align_center(tag):
            parent_tag = tag.parent
            if parent_tag.name == 'p':
                if parent_tag.has_attr('align'):
                    attr_list = parent_tag['align']
                    if 'center' not in attr_list:
                        attr_list.append('center')
                        parent_tag['align'] = attr_list
                else:
                    parent_tag['align'] = 'center'

        def set_width(tag, abspath):
            fname = path.basename(abspath)
            if markdown in self.pdf_image_size_dict:
                d = self.pdf_image_size_dict[markdown]
                if fname in d:
                    width = d[fname]
                    tag['width'] = width

        soup = bs4.BeautifulSoup(html, 'html.parser')

        #IMAGE
        tags = soup.find_all('img')
        for tag in tags:
            if tag.has_attr('src'):
                abspath = get_abspath(tag['src'])
                tag['src'] = abspath
                align_center(tag)
                set_width(tag, abspath)

        return soup.prettify(soup.original_encoding)


###########
### RUN ###
###########

def run():
    Md2Html_v0_1('html.conf').run()

def test():
    pass

if __name__ == '__main__':
    run()
