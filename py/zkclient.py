#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Power by Wang Xuechen2018-04-08 13:07:59

import threading
import logging

from kazoo.client import KazooClient
from kazoo.client import KazooState


ZKClient_logger = logging.getLogger(__name__)


class ZKClient:
    def __init__(self, hosts):
        self.zk = KazooClient(hosts=hosts)
        self.closed = True
        self.kazoo_state = None
        self.condition = threading.Condition(threading.RLock())

        @self.zk.add_listener
        def _on_state_change(state):
            if state == KazooState.CONNECTED:
                pass
            elif state == KazooState.LOST:
                # Register somewhere that the session was lost
                pass
            elif state == KazooState.SUSPENDED:
                # Handle being disconnected from Zookeeper
                pass
            else:
                # Handle being connected/reconnected to Zookeeper
                pass
            self.kazoo_state = state
            ZKClient_logger.info('KazooState [%s]' % str(state))
            with self.condition:
                ZKClient_logger.info('Tyr to notifyAll')
                self.condition.notifyAll()

    def stop(self):
        if self.closed is True:
            return
        with self.condition:
            self.condition.notifyAll()
        ZKClient_logger.info('Try to stop')
        self.zk.stop()
        ZKClient_logger.info('Tyr to close')
        self.zk.close()
        self.closed = True

    def start(self):
        if self.closed is not True:
            return
        ZKClient_logger.info('Try to start')
        with self.condition:
            self.zk.start()
            while True:
                self.condition.wait()
                if self.kazoo_state == KazooState.CONNECTED:
                    self.closed = False
                    ZKClient_logger.info('started')
                    break
                if self.closed is True:
                    break


if __name__ == '__main__':
    import time

    import util

    util.enable_default_log()

    zkc = ZKClient('127.0.0.1:2181')
    zkc.start()
    time.sleep(2)
    zkc.stop()
    time.sleep(1)
