#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File name    : tools.py
Author       : miaoyc
Create date  : 2021/6/16 2:31 下午
Description  : 
"""

import os


def check_process_is_alive(process_name):
    """
    检查进程是否存在
    """
    obj = os.popen("ps -ef | grep {0} | grep -v grep | grep -v '/bin/sh -c' | grep -v tail".format(process_name))
    line_list = obj.readlines()
    obj.close()
    if len(line_list) > 1:
        return True
    else:
        return False


def check_disk_usage(file_path_name, disk_usage_rate):
    """
    检查磁盘的使用率,查看指定目录下的磁盘使用率,如果大于磁盘了利用率（disk_usage_rate，示例：90%）则返回False
    """
    disk = os.statvfs(file_path_name)
    percent = (disk.f_blocks - disk.f_bfree) * 100 / (disk.f_blocks - disk.f_bfree + disk.f_bavail)
    percent = '{0}%'.format(int(percent) + 1)   # 转换为百分数
    if percent > disk_usage_rate:
        return False
    return True
