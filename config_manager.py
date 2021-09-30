import time
import configparser
import os
from re import search


class ConfigManager:

    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(current_dir, 'config.ini')
        self.read_file()

    def read_file(self):
        try:
            self.config_parser.read(self.filename)
            self.timeout = self.config_parser.getint('Default', 'config_update_time')
            self.last_update_time = time.time()
        except Exception as e:
            print(e)


    def get_config_by_key(self, section, key):
        if (time.time()) >= (self.last_update_time + self.timeout):
            self.read_file()

        self.result = ''
        try:
            reply = self.config_parser.get(str(section), str(key))
        except Exception as e:
            print(e)
            if search('No section', str(e)):
                self.result = f'exception:Section {section} not Found'
            elif search('No option', str(e)):
                self.result = f'exception:option {key} not Found'

        if search('exception:', str(self.result)):
            res = self.result.split(':')
            return False, res[1]
        else:
            return True, reply
