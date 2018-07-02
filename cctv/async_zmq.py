# -*- coding: utf-8 -*-

"""AioZmq Router."""

import asyncio
import aiozmq
import zmq
import json
import logging
log = logging.getLogger(__name__)


class Protocol(aiozmq.ZmqProtocol):

    def __init__(self, queue, cb=None):
        self.queue = queue
        self.wait_ready = asyncio.Future()
        self.wait_closed = asyncio.Future()
        self.callback = cb

    def connection_made(self, transport):
        self.transport = transport
        self.wait_ready.set_result(True)

    def connection_lost(self, exc):
        self.wait_closed.set_result(exc)

    def msg_received(self, data):
        log.info('Received from Zmq: {}'.format(data))
        if callable(self.callback):
            self.queue.put_nowait(data)
            self.callback()


class Zmq_Router():

    def __init__(self,
                 out_socket='tcp://*:15570',
                 identity=b'SAM-CCTV',
                 callback=None):
        self.identity = identity
        self.out_socket = out_socket
        self.transport = None
        self.queue = asyncio.Queue()
        self.callback = callback

    async def config(self):
        router, _sp = await aiozmq.create_zmq_connection(
            lambda: Protocol(self.queue, self.received),
            zmq.ROUTER,
            bind=self.out_socket)
        await _sp.wait_ready
        self.transport = router

    def received(self):
        msg = None
        try:
            data = self.queue.get_nowait()
            if len(data) == 2:
                [ident, mesg] = data
                msg = json.loads(mesg.decode('utf-8'))
                log.info('Router from {} received: {}'.format(ident, msg))
        except asyncio.QueueEmpty:
            pass
        if msg and callable(self.callback):
            self.callback(msg)

    def transmit(self, msg, identity=None):
        if self.transport:
            log.info('Transmit to Dealer: {}'.format(msg))
            self.transport.write([identity or self.identity,
                                  json.dumps(msg).encode('utf-8')])
        else:
            log.error('Invalid zmq transport.')


class Zmq_Dealer():

    def __init__(self,
                 addr='tcp://127.0.0.1:15570',
                 identity=b'SAM-CCTV'):
        self.identity = identity
        self.addr = addr
        self.transport = None
        self.queue = asyncio.Queue()

    async def config(self):
        dealer, _p = await aiozmq.create_zmq_connection(
            lambda: Protocol(self.queue, self.received),
            zmq.DEALER)
        await _p.wait_ready
        dealer.setsockopt(zmq.IDENTITY, self.identity)
        dealer.connect(self.addr)
        self.transport = dealer
        log.debug('zmq connection complete.')

    def received(self):
        try:
            data = self.queue.get_nowait()
            [mesg] = data
            msg = json.loads(mesg.decode('utf-8'))
            log.info('Dealer received: {}'.format(msg))
            self.transmit(msg)
        except asyncio.QueueEmpty:
            pass

    def transmit(self, msg):
        if self.transport:
            self.transport.write([json.dumps(msg).encode('utf-8')])
        else:
            log.error('Invalid zmq transport.')


if __name__ == '__main__':
    if (zmq.zmq_version_info() < (4,) or
            zmq.pyzmq_version_info() < (14, 4,)):
        raise NotImplementedError(
            "Socket monitor requires libzmq >= 4 and pyzmq >= 14.4, "
            "have libzmq:{}, pyzmq:{}".format(
                zmq.zmq_version(), zmq.pyzmq_version()))

    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # ch.setLevel(logging.ERROR)
    # ch.setLevel(logging.CRITICAL)
    # ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # create zmq dealer to test
    loop = asyncio.get_event_loop()
    dealer = Zmq_Dealer('tcp://192.168.1.162:15570')
    loop.run_until_complete(dealer.config())
    loop.run_forever()
