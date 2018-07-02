# -*- coding: utf-8 -*-

"""Main module."""

from .cctv import CctvV1
from .async_zmq import Zmq_Router
import logging
log = logging.getLogger(__name__)


class Cctv_Zmq(CctvV1):
    def __init__(self, loop, out_socket):
        super().__init__(loop)
        self.router = Zmq_Router(out_socket, callback=self.uploads)
        self.loop.run_until_complete(self.router.config())

    def __str__(self):
        return "cctv to zmq"

    async def _do_action(self, mesg):
        self.router.transmit(mesg)

        # register actions
        action = mesg.get('name')
        if action is None:
            return None
        args = mesg.get('args', 0)
        status = mesg.get('status', 'ON')
        if status is '':
            status = None
        else:
            status = status.upper()
        if type(action) is list:
            x_action = action
        else:
            x_action = [action]
        for act in x_action:
            x_act = '{}_[{}]'.format(act, args)
            if status == 'AUTO':
                dt = 100
            else:
                dt = 0
            self._register(x_act, status, dt)

    def uploads(self, msg):
        log.info('Send to Amqp: {}'.format(msg))

        # return info from zmq to amqp
        # self.publish(msg)

    def _release(self, act=None, args=None, status=None):
        pass
