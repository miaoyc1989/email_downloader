#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
File name    : pop3lib_connect.py
Author       : miaoyc
Create date  : 2021/5/26 21:26 下午
Description  :
"""

import poplib
from log import logger


def open_connection(hostname='', port='', username='', password=''):
    # Read the config file
    try:
        # 连接到POP3服务器
        connection = poplib.POP3_SSL(hostname, port)
    except Exception as err:
        logger.error("connect error %s", str(err))
        return False
    try:
        # 身份认证
        connection.user(username)
        connection.pass_(password)
    except Exception as err:
        logger.error("auth error: %s", str(err))
        return False
    return connection
