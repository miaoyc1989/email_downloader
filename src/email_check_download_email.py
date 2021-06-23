#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
File name    : email_check_download_email.py
Author       : miaoyc
Create date  : 2021/5/21 9:40 下午
Description  : 下载邮件主入口，会在内部分别调用imap和pop3邮箱的下载工具
"""

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from log import logger
from common.tools import check_disk_usage, check_process_is_alive
from src import read_email_client_conf
from src import download_imap, download_pop3


class DownloadEmail(object):
    """
    下载邮件原始文件
    """
    def __init__(self):
        self.email_client_conf = read_email_client_conf()
        self.eml_path = self.email_client_conf.get("path", "")
        self.imap_client = download_imap
        self.pop3_client = download_pop3
        self.init_path()

    def init_path(self):
        """
        初始化目录的操作,检查对应的目录是否存在,若不存在则创建
        """
        if not os.path.exists(self.eml_path):
            os.makedirs(self.eml_path)

    def run(self):
        """
        入口函数
        """
        # start
        logger.info("start!")
        # check process exist
        if check_process_is_alive("email_check_download_email.py"):
            logger.info('the process of the email_check_download_email.py is alive!')
            sys.exit()

        # 校验磁盘容量
        if not check_disk_usage("/", "80%"):
            logger.error('the disk_usage_rate is more than 90%!')
            sys.exit()

        # download
        logger.info("download!")
        imap_options = {
            "path": self.eml_path,
            "account": self.email_client_conf["imap"]
        }
        self.imap_client.run(imap_options)
        pop3_options = {
            "path": self.eml_path,
            "account": self.email_client_conf["pop3"]
        }
        self.pop3_client.run(pop3_options)
        #
        logger.info("exit!")


if __name__ == '__main__':
    download_obj = DownloadEmail()
    download_obj.run()
