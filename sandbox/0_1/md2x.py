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

        self.dir_markdown = None
        self.dir_output = None
        self.dir_template = None
        self.dir_pdf = None

        self.conv_template = None
        self.conv_replace = None
        self.conv_markdown_dict = {}

        self.pdf_output = None
        self.pdf_css = None
        self.pdf_dpi = None
        self.pdf_markdowns = []

        # VERSION
        self.VERSION = '0.1'
        self.TYPE_HTML = 'HTML'
        self.TYPE_PDF = 'PDF'

    def run(self):
        self.cd_to_script_dir()

        #  LOAD CONFIG
        config_text = self.get_config_text(self.config_path)
        config = self.get_config(config_text)
        output_type = self.load_basic_section(config)
        output_type = output_type.lower()
        if output_type == 'html':
            output_type = self.TYPE_HTML
        elif output_type == 'pdf':
            output_type = self.TYPE_PDF
        else:
            print_logging('Critical : section [output_type] must be "html" or "pdf"')
            print_logging('abort')
            exit(1)

        self.load_logging_section(config)
        self.load_directory_section(config, output_type)
        self.load_template_section(config)
        self.load_markdown_sections(config, output_type)
        if(output_type == self.TYPE_PDF):
            self.load_pdf_section(config)

        '''
        # CHECK FILES
        self.check_directory_exists(output_type)
        self.check_template_files()
        self.check_markdown_files()
        if(output_type == self.TYPE_PDF):
            self.check_pdf_files()

        # DEBUG
        self.dump_loaded_config()

        # CONVERT
        if(output_type == self.TYPE_HTML):
            self.convert_markdown_2_html()
            self.copy_other_files()
        elif(output_type == self.TYPE_PDF):
            self.convert_markdown_2_pdf()
        '''


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
            version = config.get('basic', 'version')
            output_type = config.get('basic', 'output_type')
            print_logging('loading [basic] section success')

            if version != self.VERSION:
                print_logging('    found version mismatch')
                print_logging('    args {}'.format(self.VERSION))
                print_logging('    config file {}'.format(version))
                raise

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('load config [basic] section : fail')
            exit(1)

        print_logging('load config [basic] section : success')
        return output_type


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


    def load_directory_section(self, config, output_type):
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
                if output_type == self.TYPE_PDF:
                    logging.warning('output_type pdf requires pdf option at section directory')
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

    def load_template_section(self, config):
        logging.info('load config [template] section : start')
        try:
            abs_template = config.get('template', 'template')
            if not path.isabs(abs_template):
                abs_template = path.join(self.dir_template, abs_template)
            self.conv_template = abs_template

            abs_replace = config.get('template', 'replace')
            if not path.isabs(abs_replace):
                abs_replace = path.join(self.dir_template, abs_replace)
            self.conv_replace = abs_replace

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [template] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    template : "{}"'.format(self.conv_template))
        logging.debug('    replace : "{}"'.format(self.conv_replace))
        logging.info('load config [template] section : success')


    def load_markdown_sections(self, config, output_type):
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

                # html path
                if config.has_option(markdown_section, 'html'):
                    html_path = config.get(markdown_section, 'html')
                    if not path.isabs(html_path):
                        html_path = path.join(self.dir_output, html_path)
                    d['html'] = html_path
                else:
                    if output_type == self.TYPE_HTML:
                        logging.warning('    output_type "html" needs html option at markdown section')
                        raise

                # specific template path
                if config.has_option(markdown_section, 'template'):
                    template = config.get(markdown_section, 'template')
                    if not path.isabs(template):
                        template = path.join(self.dir_template, template)
                    d['template'] = template

                # specific replace path
                if config.has_option(markdown_section, 'replace'):
                    replace = config.get(markdown_section, 'replace')
                    if not path.isabs(replace):
                        replace = path.join(self.dir_template, replace)
                    d['replace'] = replace

                dict_markdown[markdown_section] = d

                for (key, value) in d.items():
                    logging.debug('        {} : {}'.format(key, value))
                logging.info('    section [{}] : success'.format(markdown_section))

            self.dict_markdown = dict_markdown

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config markdown sections : fail')
            logging.critical('abort')
            exit(1)

        logging.info('load config markdown sections : success')


    def load_pdf_section(self, config):
        logging.info('load [pdf] section : start')
        try:
            output = config.get('pdf', 'output')
            if not path.isabs(output):
                output = path.join(self.dir_output, output)
            self.pdf_output = output

            css = config.get('pdf', 'css')
            if not path.isabs(css):
                css = path.join(self.dir_pdf, css)
            self.pdf_css = output

            dpi = config.get('pdf', 'dpi')
            self.pdf_dpi = int(dpi)

            markdowns_str = config.get('pdf', 'markdowns')
            markdowns = []
            for markdown in markdowns_str.split(','):
                markdown = markdown.strip()
                markdown_path = path.join(self.dir_markdown, markdown)
                markdowns.append((markdown, markdown_path))
            self.markdowns = markdowns

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load [pdf] section : start')
            logging.critical('abort')
            exit(1)

        logging.debug('    output : {}'.format(self.pdf_output))
        logging.debug('    css : {}'.format(self.pdf_css))
        logging.debug('    dpi : {}'.format(self.pdf_dpi))
        logging.debug('    markdowns : [')
        for markdown in self.markdowns:
            logging.debug('        {},'.format(markdown))
        logging.debug('    ]')
        logging.info('load [pdf] section : success')


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

    '''
    def get_config(self, )
    def __load_config(self):
        print_logging('loading config start')




        # CHECK CONFIG EXISTS
        if not path.exists(self.config_file):
            print_logging('config file {} doesn\'t exit. create sample'.format(self.config))
            with open(self.config_file, 'w') as fout:
                fout.write(CONFIG_TEMPLATE_V0_1)
            exit(1)
        print_logging('config file {} exist.'.format(self.config_file))


        loaded_logging_setting = False
        try:


            # VERSION CHECK


            # LOGGING
            set_logging(config)
            loaded_logging_setting = True


            # Directory


            # Template
            abs_template = config.get('template', 'template')
            if not path.isabs(abs_template):
                abs_template = path.join(self.dir_template, abs_template)

            abs_replace = config.get('template', 'replace')
            if not path.isabs(abs_replace):
                abs_replace = path.join(self.dir_template, abs_replace)
            logging.info('loading [template] section done')

            # Markdown


        except Exception as e:
            if loaded_logging_setting:
                logging.critical('loading config fail. {}'.format(e))
            else:
                print_logging('loading config fail. {}'.format(e))
            exit(1)

        logging.info('loading all sections success')
    '''


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
                    logging.warning('non directory file "{}" exists'.format(dir_html))
                    raise
            else:
                logging.info('html directory "{}" exist'.format(dir_html))

        except Exception as e:
            logging.critical(e)
            logging.critical("ERROR: file doesn't exist")
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

        def add_bootstrap_class(html):
            soup = bs4.BeautifulSoup(html, 'html.parser')

            # IMAGE
            tags = soup.find_all('img')
            for tag in tags:
                if tag.has_attr('class'):
                    attr_list = tag['class']
                    if 'img-responsive' not in attr_list:
                        attr_list.append('img-responsive')
                        tag['class'] = attr_list
                else:
                    tag['class'] = 'img-responsive'

            return soup.prettify(soup.original_encoding)

        def replace_keywords(html_text, path_replace):
            replace_text = get_file_content(path_replace)
            try:
                replace_dict = {}
                exec(replace_text, locals(), replace_dict)
            except Exception as e:
                logging.warning('Unable to load replace definition file "{}". please check format'.format(path_replace))
                raise

            r = re.compile(r'{{\s+(\w+)\s+}}')

            new_lines = []
            for line in html_text.split('\n'):
                new_line = line
                m = r.search(line)
                if m:
                    keyword = m.group(1)
                    if keyword in replace_dict:
                        new_line = line.replace(m.group(0), replace_dict[keyword])
                new_lines.append(new_line)

            return '\n'.join(new_lines)

        def all_keywords_changed(html_text):
            r = re.compile(r'{{\s+(\w+)\s+}}')
            for line in html_text.split('\n'):
                m = r.search(line)
                if m:
                    logging.warning('find unreplaced keyword at "{}"'.format(line))
                    return False
            return True

        try:
            markdowns = filter(lambda text : text.endswith('.md'), self.dict_markdown.keys())
            for markdown in markdowns:
                logging.info('start converting {}.'.format(markdown))
                dict_md = self.dict_markdown[markdown]

                # CONVERT
                path_md = dict_md['markdown']
                text_md = get_file_content(path_md)
                content_html = markdown_mod.markdown(text_md, extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite'])

                #content_html = md.convert(text_md)
                content_html = add_bootstrap_class(content_html)
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
                    html = replace_keywords(html, path_replace)

                path_replace = self.dict_markdown['replace']
                html = replace_keywords(html, path_replace)

                if not all_keywords_changed(html):
                    logging.warning('template "{}" for markdown "{}"'.format(path_template, path_md))
                    raise
                logging.debug('   replace done')

                path_html = dict_md['html']
                with open(path_html, 'w') as fout:
                    fout.write(html)

                logging.info('convert markdown [{}] done'.format(markdown))
            logging.info('all markdown convert done')

        except Exception as e:
            logging.critical('Failed converting from markdown to html. {}'.format(e))
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


###########
### RUN ###
###########

def run():
    Md2Html_v0_1('html.conf').run()
    print('\n\n\n')
    Md2Html_v0_1('print.conf').run()
    print('\n\n\n')
    Md2Html_v0_1('pdf.conf').run()

def test():
    pass

if __name__ == '__main__':
    run()
