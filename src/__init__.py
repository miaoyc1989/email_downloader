#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File name    : __init__.py
Author       : miaoyc
Create date  : 2021/5/21 6:42 下午
Description  : 邮件客户端
"""

import json

EMAIL_CLIENT_CONF = "../config/email_client_conf.json"


def read_email_client_conf():
    email_client_conf = json.load(file(EMAIL_CLIENT_CONF))
    options = {
        "path": email_client_conf.get("common", {}).get("path", ""),
        "pop3": email_client_conf.get("pop3", []),
        "imap": email_client_conf.get("imap", [])
    }
    return options
