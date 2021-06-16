#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
File name    : log.py
Author       : miaoyc
Create date  : 2021/5/21 6:42 下午
Description  :
"""

import os
import sys
import json
import logging
import logging.handlers

LOGGER_FILE = "logger.json"

'''
Log Level       Numeric value
CRITICAL	    50
ERROR	        40
WARNING	        30
INFO	        20
DEBUG	        10
NOTSET	        0
'''

# config file log level is 0,1,2,3,4,5
LOG_LEVEL_DICT = {
        '0': logging.NOTSET,
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARNING,
        '4': logging.ERROR,
        '5': logging.CRITICAL
        }


class InitLogger(object):
    """
    init logger from /opt/tip/config/logger.json
    file: file handler config, print msg to /var/log/tip/* file
          when enabled is true, add file handler
    console: console handler config, print msg to console
            when enabled is true, add file handler
    """
    def __init__(self):
        self.m_log_file_path = ""
        self.__parse_config()
        self.get_logfile_path()

    def __parse_config(self):
        with open(LOGGER_FILE) as fobj:
            log_config = json.loads(fobj.read())

            # file_handler config
            file_config = log_config['file']
            self.m_file_enabled = file_config['enabled']
            self.m_max_log_size = int(file_config['size'])
            self.m_file_level = file_config['level']
            self.m_file_log_formatter = file_config['format']
            self.m_file_config_path = file_config['file_path']
            self.m_back_up_count = int(file_config['back_up_count'])

            # console_handler config
            console_config = log_config['console']
            self.m_console_enabled = console_config['enabled']
            self.m_console_level = console_config['level']
            self.m_console_format = console_config['format']

            # create path
            if not os.path.exists(self.m_file_config_path):
                os.makedirs(self.m_file_config_path)

    def get_logfile_path(self):
        """
        generate log file path
        :return:
        """
        log_path = os.path.normpath(sys.argv[0] + ".log").replace("../", "++_")
        while log_path[0] == "/":
            path_list = log_path.split('/')
            log_path = path_list[-1]
        if log_path == ".log":
            log_path = "python.log"
        log_path = os.path.join(self.m_file_config_path, log_path)
        self.m_log_file_path = log_path

    def get_logger(self):
        """
        get log logger
        add log handler if enabled is true
        :return:
        """
        logger_ = logging.getLogger('')
        logger_.setLevel(logging.DEBUG)

        # init file log
        if self.m_file_enabled == "true":
            file_formatter = logging.Formatter(self.m_file_log_formatter)
            file_handler = logging.handlers.RotatingFileHandler(self.m_log_file_path, maxBytes=self.m_max_log_size,
                                                                backupCount=self.m_back_up_count)
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(LOG_LEVEL_DICT[self.m_file_level])
            logger.addHandler(file_handler)

        # init console log
        if self.m_console_enabled == "true":
            console_formatter = logging.Formatter(self.m_console_format)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(LOG_LEVEL_DICT[self.m_console_level])
            logger.addHandler(console_handler)

        return logger


# singleton pattern logger
logger = InitLogger().get_logger()
