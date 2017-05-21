CONFIG_FILE = 'config.txt'

def check_python_env():
    try:
        import platform
        version = platform.python_version()
        if not version.startswith('3.'):
            raise
        import markdown
    except:
        print('ERROR: This script requires python3 and markdown module')
        exit(1)

    print('INFO: python env is OK')

def read_config(config_file):
    config = {}
    config['md'] = []

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

        if key == 'md':
            if value.count(',') != 1:
                print(warning_message.format(line))
                return
            i = value.find(',')
            markdown_file = value[:i].strip()
            html_file = value[i+1:].strip()
            config['md'].append((markdown_file, html_file))
            return

        if key in config:
            print('WARNING: detect duplicate key at line "{}"'.format(line))
            print('WARNING: overwrite key "{}"'.format(key))

        config[key] = value

    try:
        with open(config_file, 'r') as fin:
            for line in fin:
                parse_line(line)

        keys = ['markdowndir', 'homepagedir', 'template', 'css', 'replace', 'md']
        for key in keys:
            if key not in config:
                print('WARNING: config file need to have key "{}"'.format(key))
                raise

    except:
        print('ERROR: Unable to load config file "{}"'.formt(CONFIG_FILE))
        exit(1)

    print('INFO: config syntax is OK')
    return config

def check_file_exists(config):
    import os
    import os.path as path

    try:
        top_dirs = [config['markdowndir'], config['homepagedir']]
        for directory in top_dirs:
            if not path.isdir(directory):
                print('WARNING: directory "{}" doesn\'t exist'.format(directory))
                raise

        os.chdir(config['markdowndir'])
        md_setting_files = [config['template'], config['css'], config['replace']]
        for setting_file in md_setting_files:
            if not path.isfile(setting_file):
                print('WARNING: setting file "{}" doesn\'t exist'.format(setting_file))
                raise
        for (markdown, html) in config['md']:
            if not path.isfile(markdown):
                print('WARNING: markdown file "{}" doesn\'t exist'.format(markdown))
                raise
        os.chdir('../')

    except:
        print("ERROR: file doesn't exist")
        exit(1)

if __name__ == '__main__':
    check_python_env()
    config = read_config(CONFIG_FILE)
    print(config)
    check_file_exists(config)
