#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Power by Wang Xuechen2018-04-08 13:07:59

import logging
import threading

from zkclient import ZKClient


Barriers_logger = logging.getLogger(__name__)


class ZKBarriers(ZKClient):
    def __init__(self, hosts, root, count):
        self.root = root
        self.name = 'barriers'
        self.count = count
        self.condition = threading.Condition(threading.RLock())
        ZKClient.__init__(self, hosts)
        self.start()

        @self.zk.ChildrenWatch(self.root)
        def _on_children_change(children):
            Barriers_logger.info(
                '_on_children_change children are[%s]' % children)
            with self.condition:
                self.condition.notifyAll()

    def __enter__(self):
        self.zk.ensure_path(self.root)
        self.name = self.zk.create(
            self.root + '/' + self.name,  None,
            ephemeral=True, sequence=True)
        Barriers_logger.info(
            'New node has been created [%s]' % self.name)
        while True:
            with self.condition:
                childern = self.zk.get_children(self.root)
                if (len(childern) < self.count):
                    Barriers_logger.info(
                        'Wait for more node, name is [%s]' % self.name)
                    self.condition.wait()
                else:
                    Barriers_logger.info(
                        'The count of node is enough, name is [%s]'
                        % self.name)
                    return

    def __exit__(self, exc_type, exc_value, traceback):
        self.zk.delete(self.name)
        if exc_type is not None:
            Barriers_logger.info('Got exception [%s]' % traceback)
            raise Exception((exc_type, exc_value, traceback))
        while True:
            with self.condition:
                childern = self.zk.get_children(self.root)
                if (len(childern) > 0):
                    Barriers_logger.info(
                        'Wait for other node leave, childern are [%s]'
                        % childern)
                    self.condition.wait()
                else:
                    Barriers_logger.info(
                        'All node leaved, childern are [%s]'
                        % childern)
                    return


if __name__ == '__main__':
    from threading import Thread
    import time

    import util

    util.enable_default_log()

    def threaded_function(duration):
        barriers = ZKBarriers(
            hosts='127.0.0.1:2181',
            root='/my_barriers_test',
            count=2)
        with barriers:
            Barriers_logger.info('Start to compute...')
            time.sleep(int(duration))
            Barriers_logger.info('Exit from compute...')
        Barriers_logger.info('Done')

    Barriers_logger.info('Starting')
    thread_1 = Thread(target=threaded_function, args=[5])
    thread_1.start()
    Barriers_logger.info('Start thread 1')
    thread_2 = Thread(target=threaded_function, args=[10])
    thread_2.start()
    Barriers_logger.info('Start thread 2')
    thread_1.join()
    thread_2.join()
