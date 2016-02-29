from log import Logger
import os
from ConfigParser import SafeConfigParser
logger = Logger()

def singleton(cls):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return _singleton

@singleton
class ConfigurationHelper(object):
    def __init__(self):
        self.app_home = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.app_home)
        self.config = SafeConfigParser()
        config_file = os.path.join(self.app_home,"config.conf")
        self.config.read(config_file)