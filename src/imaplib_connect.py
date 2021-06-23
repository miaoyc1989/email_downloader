#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
File name    : imaplib_connect.py
Author       : miaoyc
Create date  : 2021/5/21 6:42 下午
Description  :
"""

import imaplib
from log import logger


def open_connection(hostname='', port='', username='', password=''):
    try:
        connection = imaplib.IMAP4_SSL(hostname, port)
    except Exception as err:
        logger.error("connect error %s", str(err))
        return False

    try:
        connection.login(username, password)
    except Exception as err:
        logger.error("auth error: %s", str(err))
        return False
    return connection
