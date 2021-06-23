#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File name    : download_pop3.py
Author       : miaoyc
Create date  : 2021/5/21 6:57 下午
Description  : 下载pop3邮箱邮件
"""

import os
import sys
import json
from log import logger
from src import pop3lib_connect

reload(sys)
sys.setdefaultencoding('utf-8')


def fetch_process(mail_client, index, mailbox_folder):
    try:
        resp, lines, octets = mail_client.retr(index)
        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        file_ = os.path.join(mailbox_folder, str(index) + ".eml")
        with open(file_, 'wb') as f:
            f.write(msg_content)
    except Exception as err:
        logger.error("%s %s", fetch_process, err)
        return False
    return True


def fetch_mail(options, download_progress_):
    for account in options['account']:
        if "protocol" in account:
            del account["protocol"]
        if "mail" in account:
            uid = account["mail"]
            del account["mail"]
        else:
            uid = account["username"]
        client = pop3lib_connect.open_connection(False, **account)
        path = options['path']
        username_path = os.path.join(path, account["username"])
        if not os.path.isdir(username_path):
            os.mkdir(username_path)

        # 可以查看返回的列表类似[b'1 2123', b'2 2124', ...]
        # 获取最新一封邮件, 注意索引号从1开始:
        resp, mails, octets = client.list()
        num_msgs = len(mails)
        if num_msgs <= 0:
            continue

        # 比较下载进度
        download_progress_key = "{0}_pop3".format(uid)
        current_no = download_progress_.get(download_progress_key, 1)
        if num_msgs + 1 <= current_no:
            continue

        logger.info("%s %s", account["username"], "download {0} mails!".format(num_msgs + 1 - current_no))
        try:
            mail_client = pop3lib_connect.open_connection(False, **account)
            for index in range(current_no, num_msgs + 1):
                try:
                    if not fetch_process(mail_client, index, username_path):
                        continue
                except Exception as e:
                    logger.error("error: %s", str(e))
            # 记录下载进度
            download_progress_[download_progress_key] = num_msgs
        except Exception as e_info:
            logger.error("%s %s %s", uid, account["username"], str(e_info))


def run(options_):
    save_path = options_["path"]
    download_progress_file = "{0}/download_progress.json".format(save_path)
    if os.path.exists(download_progress_file):
        download_progress = json.load(file(download_progress_file))
    else:
        download_progress = {}
    fetch_mail(options_, download_progress)
    with open(download_progress_file, 'w') as f_obj:
        json.dump(download_progress, f_obj)


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        logger.error("download pop3 error: %s", str(e))