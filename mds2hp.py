CONFIG_FILE = 'config.txt'
MARKDOWNDIR = 'markdowndir'
HTMLDIR = 'htmldir'
TEMPLATE = 'template'
REPLACE = 'replace'
MD = 'md'
MD_HTML = 'md_html'
REPLACE_PATTERN_REGEX = r'<!--:: () ::-->'

import os
import os.path as path
import platform

try:
    if not platform.python_version().startswith('3.'):
        raise
    import markdown
except:
    print('ERROR: This script requires python3 and markdown module')
    exit(1)
print('INFO: Python env is OK')

def cd_to_script_path():
    absfilepath = os.path.abspath(__file__)
    absdirpath = path.dirname(absfilepath)
    os.chdir(absdirpath)
    print('INFO: move to "{}".'.format(absdirpath))

def read_config(config_file):
    config = {}
    config[MD_HTML] = []

    warning_message = 'WARNING: line "{}" has problem'
    def parse_line(line):
        line = line.strip()
        if line.startswith('#'):
            return
        if line == '':
            return

        if ':' not in line:
            print(warning_message.format(line))
            return
        i = line.find(':')
        key = line[:i].strip()
        value = line[i+1:].strip()

        if key == MD:
            if value.count(',') != 1:
                print(warning_message.format(line))
                return
            i = value.find(',')
            markdown_file = value[:i].strip()
            html_file = value[i+1:].strip()
            config[MD_HTML].append((markdown_file, html_file))
            return

        if key in config:
            print('WARNING: detect duplicate key at line "{}"'.format(line))
            print('WARNING: overwrite key "{}"'.format(key))

        config[key] = value

    try:
        with open(config_file, 'r') as fin:
            for line in fin:
                parse_line(line)

        keys = [MARKDOWNDIR, HTMLDIR, TEMPLATE, REPLACE]
        for key in keys:
            if key not in config:
                print('WARNING: config file need to have key "{}"'.format(key))
                raise

    except Exception as e:
        print('ERROR: Unable to load config file "{}"'.format(CONFIG_FILE))
        print(e)
        exit(1)

    print('INFO: config syntax is OK')
    return config

def check_file_exists(config):
    try:
        # TOP Directory
        for dir_key in [MARKDOWNDIR, HTMLDIR]:
            directory = config[dir_key]
            if not path.isdir(directory):
                print('WARNING: directory "{}" doesn\'t exist'.format(directory))
                if not path.isfile(directory):
                    print('INFO: create directory "{}"'.format(directory))
                    os.mkdir(directory)
                else:
                    print('WARNING: non directory file "{}" exists'.format(directory))
                    raise()
            absdirpath = os.path.abspath(directory)
            config[dir_key] = absdirpath

        # Seting files
        markdown_dir = config[MARKDOWNDIR]
        html_dir = config[HTMLDIR]
        for setting_key in [TEMPLATE, REPLACE]:
            absfilepath = path.join(markdown_dir, config[setting_key])
            if not path.isfile(absfilepath):
                print('WARNING: setting file "{}" doesn\'t exist'.format(setting_file))
                raise
            config[setting_key] = absfilepath

        # Markdown files
        abspath_list = []
        for (markdown_file, html_file) in config[MD_HTML]:
            absfilepath_md = path.join(markdown_dir, markdown_file)
            absfilepath_html = path.join(html_dir, html_file)
            if not path.isfile(absfilepath_md):
                print('WARNING: markdown file "{}" doesn\'t exist'.format(markdown_file))
                raise
            abspath_list.append((absfilepath_md, absfilepath_html))
        config[MD_HTML] = abspath_list

    except:
        print("ERROR: file doesn't exist")
        exit(1)

    print('INFO: files are exist')

def load_template(template_path, replace_path):
    try:
        with open(template_path, 'r') as fin:
            template = fin.read()

        replace_pattern = {}
        with open(replace_path, 'r') as fin:
            for line in fin:
                line = line.strip()

                if ',' not in line:
                    print('WARNING: TEMPLATE has problem')
                    continue

                i = line.find(',')
                key = line[:i].strip()
                value = line[i+1:].strip()

                # NEEDS KEY SYNTAX CHECK LATER
                replace_pattern[key] = value
    except:
        print("ERROR: failed to load template and replace pattern files")
        exit(1)

    print('INFO: success to load template and replace-pattern file')
    return (template, replace_pattern)

def convert(config, template, replace_pattern):
    try:
        for (markdown_path, html_path) in config[MD_HTML]:
            with open(markdown_path, 'r') as fin:
                markdown_text = fin.read()

            html_text = markdown_2_html(markdown_text, template, replace_pattern)

            with open(html_path, 'w') as fout:
                fout.write(html_text)
    except:
        print('ERROR: failed convert')
        exit(1)

def markdown_2_html(markdown_text, template, replace_pattern):
    # convert markdown to html
    md = markdown.Markdown()
    html_text = md.convert(markdown_text)

    # include html to template

    # replace

    return html_text

def copy_other_files(config):
    pass

def check_html(config):
    pass

if __name__ == '__main__':
    # PRE PROCESS
    cd_to_script_path()
    config = read_config(CONFIG_FILE)
    check_file_exists(config)

    # CONVERT MARKDOWN AND MAKE HTML PAGES
    template_path = config[TEMPLATE]
    replace_path = config[REPLACE]
    (template, replace_pattern) = load_template(template_path, replace_path)
    convert(config, template, replace_pattern)
    copy_other_files(config)

    # POST PROCESS
