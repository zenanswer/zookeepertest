#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Power by Wang Xuechen2018-04-08 13:07:59

import logging
import threading

from zkclient import ZKClient


Lock_logger = logging.getLogger(__name__)


class ZKLock(ZKClient):
    def __init__(self, hosts, root, name='Lock'):
        self.root = root
        self.name = name
        self.lock_name = None
        self.condition = threading.Condition(threading.RLock())
        ZKClient.__init__(self, hosts)
        self.start()

        @self.zk.ChildrenWatch(self.root)
        def _on_children_change(children):
            Lock_logger.info(
                '_on_children_change children are[%s]' % children)
            with self.condition:
                self.condition.notifyAll()

    def __enter__(self):
        self.zk.ensure_path(self.root)
        self.lock_name = self.zk.create(
            self.root + '/' + self.name,  None,
            ephemeral=True, sequence=True)
        Lock_logger.info(
            'New node has been created [%s]' % self.name)
        while True:
            with self.condition:
                childern = self.zk.get_children(self.root)
                child0 = self.root + '/' + childern[0]
                Lock_logger.info(
                    'Name [%s], childern[%s]' % (self.lock_name, child0))
                if self.lock_name != child0:
                    Lock_logger.info(
                        'Cannot acquire, wait.')
                    self.condition.wait()
                else:
                    Lock_logger.info('Acquire lock')
                    return

    def __exit__(self, exc_type, exc_value, traceback):
        self.zk.delete(self.lock_name)
        if exc_type is not None:
            Lock_logger.info('Got exception [%s]' % traceback)
            raise Exception((exc_type, exc_value, traceback))


if __name__ == '__main__':
    from threading import Thread
    import time

    import util

    util.enable_default_log()

    def threaded_function(duration):
        zklock = ZKLock(
            hosts='127.0.0.1:2181',
            root='/my_Lock_test')
        with zklock:
            Lock_logger.info('Start to compute...')
            time.sleep(int(duration))
            Lock_logger.info('Exit from compute...')
        Lock_logger.info('Done')

    Lock_logger.info('Starting')
    thread_1 = Thread(target=threaded_function, args=[5])
    thread_1.start()
    Lock_logger.info('Start thread 1')
    thread_2 = Thread(target=threaded_function, args=[10])
    thread_2.start()
    Lock_logger.info('Start thread 2')
    thread_1.join()
    thread_2.join()
