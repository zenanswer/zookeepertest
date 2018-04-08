#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Power by Wang Xuechen2018-04-08 13:07:59

import logging
from logging.handlers import TimedRotatingFileHandler


def enable_default_log():
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(levelname)-8s '
        '[%(threadName)s][%(filename)s:%(lineno)d] %(message)s',
        datefmt='%d-%m-%Y:%H:%M:%S',
        level=logging.INFO)

    logFile = 'test.log'

    log_formatter = logging.Formatter(
        fmt='%(asctime)s,%(msecs)d %(levelname)-8s '
        '[%(threadName)s][%(filename)s:%(lineno)d] %(message)s',
        datefmt='%d-%m-%Y:%H:%M:%S')
    log_handler = TimedRotatingFileHandler(
        logFile, when='midnight', interval=1, backupCount=10,
        encoding='utf-8', delay=False, utc=False)
    log_handler.setFormatter(log_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
