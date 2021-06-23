#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File name    : download_imap.py
Author       : miaoyc
Create date  : 2021/5/21 9:40 下午
Description  : 下载imap邮箱邮件
"""

import os
import re
import json
import imap_utf7
import multiprocessing
from log import logger
from src import imaplib_connect

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


list_response_pattern = re.compile(
    r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)'
)


def parse_list_response(line):
    match = list_response_pattern.match(line.decode('utf-8'))
    flags, delimiter, mailbox_name = match.groups()
    mailbox_name = mailbox_name.strip('"')
    return flags, delimiter, mailbox_name


def fetch_process(*p):
    i = p[0]
    mailbox_folder = p[3]
    account = p[1]
    mailbox_name = p[2]
    try:
        c = imaplib_connect.open_connection(False, **account)
        c.select(mailbox_name)
        typ, msg_data = c.fetch(str(i + 1), '(RFC822)')
        file_ = os.path.join(mailbox_folder, str(i) + ".eml")
        with open(file_, 'wb') as f:
            f.write(msg_data[0][1])
    except Exception as err:
        logger.error("%s %s", mailbox_name, err)
        return False, i
    return True, i


def fetch_mail(options, download_progress_):
    for account in options['account']:
        if "protocol" in account:
            del account["protocol"]
        if "mail" in account:
            uid = account["mail"]
            del account["mail"]
        else:
            uid = account["username"]
        client = imaplib_connect.open_connection(False, **account)
        path = options['path']
        username_path = os.path.join(path, account["username"])
        if not os.path.isdir(username_path):
            os.mkdir(username_path)

        typ, data = client.list()
        for line in data:
            try:
                flags, delimiter, mailbox_name = parse_list_response(line)
                # 输入参数是bytes类型，返回str类型
                try:
                    mailbox_name_utf8 = imap_utf7.decode(mailbox_name.encode("UTF-7"))
                except Exception:
                    # 暂时忽略该错误
                    mailbox_name_utf8 = "INBOX"

                mailbox_folder = os.path.join(username_path, mailbox_name_utf8)
                if not os.path.isdir(mailbox_folder):
                    os.mkdir(mailbox_folder)

                typ2, data2 = client.select(mailbox_name, readonly=False)
                num_msgs = int(data2[0])
                if num_msgs <= 0:
                    continue

                # 比较下载进度
                download_progress_key = "{0}_imap".format(uid)
                current_no = download_progress_.get(download_progress_key, {}).get(mailbox_name_utf8, 0)
                if num_msgs <= current_no:
                    continue

                logger.info("%s %s", mailbox_name_utf8, "download {0} mails!".format(num_msgs - current_no))
                pool_size = multiprocessing.cpu_count() * 2
                pool = multiprocessing.Pool(
                    processes=pool_size,
                    maxtasksperchild=20
                )
                for i in range(current_no-1, num_msgs):
                    ob = pool.apply_async(fetch_process, args=(
                        i, account, mailbox_name, mailbox_folder))
                    try:
                        ob.get(timeout=10)
                    except multiprocessing.TimeoutError:
                        ob.terminate()
                        logger.error("error: %s", i)

                # 记录下载进度
                if download_progress_key not in download_progress_:
                    download_progress_[download_progress_key] = {}
                download_progress_[download_progress_key][mailbox_name_utf8] = num_msgs

                # exit
                pool.close()
                pool.join()
            except Exception as e_info:
                logger.error("%s %s %s", uid, mailbox_name_utf8, str(e_info))
                continue


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
        logger.error("download imap error: %s", str(e))
