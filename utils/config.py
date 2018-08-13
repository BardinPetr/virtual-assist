from utils.logger import Logger
import configparser
import os

l = Logger(__file__)


class Config:
    dirname = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    def __init__(self):
        l.log('Config loading started')
        self.c = configparser.ConfigParser()
        self.c.read(os.path.join(Config.dirname, 'config.ini'))
        l.log('Config loading finished')

    def __setitem__(self, key, value):
        self.c[key] = value

    def __getitem__(self, item):
        return self.c[item]
