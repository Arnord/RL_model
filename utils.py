import os
import configparser
# from tzlocal import get_localzone
# from datetime import datetime, timedelta
# import numpy as np
# from functools import wraps
# import requests
import logging

logger = logging.getLogger('main')

configFilePath = os.path.abspath('config.ini')


def get_config_dict(section):
    config = configparser.ConfigParser()
    config.read(configFilePath)
    dic = dict(config._sections[section])
    return dic

