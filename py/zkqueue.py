#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Power by Wang Xuechen2018-04-08 16:09:03

import logging
import threading

from zkclient import ZKClient
from zklock import ZKLock


ZKQueue_logger = logging.getLogger(__name__)


class ZKQueue(ZKClient):
    def __init__(self, hosts, root):
        self.root = root
        self.name = 'queue'
        self.condition = threading.Condition(threading.RLock())
        ZKClient.__init__(self, hosts)
        self.start()

        @self.zk.ChildrenWatch(self.root)
        def _on_children_change(children):
            ZKQueue_logger.info(
                '_on_children_change children are[%s]' % children)
            with self.condition:
                self.condition.notifyAll()

        self.zklock = ZKLock(hosts='127.0.0.1:2181', root='/my_Lock_test')

    def put(self, task):
        self.zk.ensure_path(self.root)
        self.zk.create(
            self.root + '/' + self.name, task,
            ephemeral=False, sequence=True)
        ZKQueue_logger.info(
            'New task has been created [%s]' % self.name)

    def get(self):
        while True:
            with self.zklock:
                childern = self.zk.get_children(self.root)
                if (len(childern) == 0):
                    ZKQueue_logger.info(
                        'No task, and wait, childern are [%s]'
                        % childern)
                else:
                    child0 = self.root + '/' + childern[0]
                    data, stat = self.zk.get(child0)
                    ZKQueue_logger.info(
                        'Got task [%s][%s][%s]'
                        % (childern, data, stat))
                    self.zk.delete(child0)
                    return data


if __name__ == '__main__':
    from threading import Thread
    from datetime import datetime
    import time

    import util

    util.enable_default_log()

    logging.getLogger().setLevel(logging.WARNING)

    def producer():
        ZKQueue_logger.warning('Start Producer')
        zkqueue = ZKQueue(
            hosts='127.0.0.1:2181',
            root='my_queue_test')
        for i in range(0, 5):
            task = str(datetime.now()).encode()
            ZKQueue_logger.warning('Add Task [%s]' % task)
            zkqueue.put(task)
            time.sleep(2)
        ZKQueue_logger.warning('Producer Done')

    def consumer():
        zkqueue = ZKQueue(
            hosts='127.0.0.1:2181',
            root='my_queue_test')
        for i in range(0, 5):
            task = zkqueue.get().decode()
            ZKQueue_logger.warning('Got Task [%s]' % task)
            time.sleep(2)
        ZKQueue_logger.warning('Consumer Done')

    def start_thread(target):
        thread = Thread(target=target, args=[])
        thread.start()
        return thread

    thread_list = []
    thread_list.append(start_thread(producer))
    thread_list.append(start_thread(producer))
    thread_list.append(start_thread(consumer))
    thread_list.append(start_thread(consumer))

    for item in thread_list:
        item.join()
