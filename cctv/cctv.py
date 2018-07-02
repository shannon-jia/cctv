# -*- coding: utf-8 -*-

"""Main module."""

import logging
import time
import asyncio
log = logging.getLogger(__name__)


class CctvV1():
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.actions = {}

    def __str__(self):
        return "cctv"

    def get_info(self):
        return {
            'actions': self.actions
        }

    def set_publish(self, publish):
        if callable(publish):
            self.publish = publish
        else:
            self.publish = None

    def start(self):
        self._auto_loop()

    def stop(self):
        pass

    def km_update(self):
        pass

    def _auto_loop(self):
        self._update_actions()
        self.km_update()
        log.debug('Actions: {}'.format(self.actions))
        self.loop.call_later(1, self._auto_loop)

    def _register(self, act, status, timeout):
        self.actions[act] = {
            'status': status,
            'timeout': int(timeout),
            'timestamp': self._time_stamp()
        }

    def _update_actions(self):
        for act, val in self.actions.items():
            timeout = val.get('timeout', 0)
            _status = val.get('status')
            _time_stamp = val.get('timestamp')
            if timeout >= 1:
                timeout -= 1
                if timeout <= 1:
                    self._release(act)
                    _status = 'Off/Stop'
                    _time_stamp = self._time_stamp()
                self.actions[act] = {
                    'status': _status,
                    'timeout': int(timeout),
                    'timestamp': _time_stamp
                }

    def _time_stamp(self):
        t = time.localtime()
        time_stamp = '%d-%02d-%02d %02d:%02d:%02d' % (t.tm_year,
                                                      t.tm_mon,
                                                      t.tm_mday,
                                                      t.tm_hour,
                                                      t.tm_min,
                                                      t.tm_sec)
        return time_stamp

    async def got_command(self, mesg):
        try:
            log.info('Amqp received: {}'.format(mesg))
            return await self._do_action(mesg)
        except Exception as e:
            log.error('Cctv do_action() exception: {}'.format(e))

    async def _do_action(self, act=None, args=None, status=None):
        raise NotImplementedError

    def _release(self, act=None, args=None, status=None):
        raise NotImplementedError
