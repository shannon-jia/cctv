# -*- coding: utf-8 -*-

"""Main module."""

import time
import aiohttp
import async_timeout
import asyncio
from .cctv import CctvV1
from .async_zmq import Zmq_Router
import logging
log = logging.getLogger(__name__)


class Cctv_Km(CctvV1):
    def __init__(self, loop, url):
        super().__init__(loop)
        self.url = url
        self.message = []
        self.times = 0

    def __str__(self):
        return "cctv to zmq"

    def info(self):
        return self.message

    def _preset_value(self, preset):
        if preset == "":
            return '1'
        return str(preset)

    def km_update(self):
        self.times = self.times + 1
        if self.times == 60:
            self.preset("cameras")
        elif self.times >= 65:
            self.preset("monitors")
            self.times = 0
        else:
            pass

    async def _do_action(self, mesg):
        self.times = 0
        _msg = {}
        _msg["camera"] = mesg.get('name')

        if "playBack" in mesg:
            _msg["startTime"] = mesg.get('startTime')
            _msg["delta"] = mesg.get('delta', "60")
            _msg["monitor"] = mesg.get('monitor', 'mon_l_01')
        elif "status" in mesg:
            _msg["preset"] = self._preset_value(mesg.get('args'))
            if mesg.get('status') == 'AUTO':
                _msg["startTime"] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                 time.localtime(time.time()))
            elif (mesg.get('status') == 'ON') and ('playBack' not in mesg):
                if isinstance(mesg.get('name'), list):
                    _mon_num = 0
                    for _name in mesg.get('name'):
                        _mon_num = _mon_num + 1
                        if _mon_num > 48:
                            _mon_num = 1
                        _msg["camera"] = _name
                        _msg["preset"] = self._preset_value(mesg.get('args'))
                        _msg["monitor"] = mesg.get('monitor', 'mon_l_{:02d}'.format(_mon_num))
                        endpoint = self._endpoint(_msg)
                        self.preset(endpoint)
                    return
                _msg["monitor"] = mesg.get('monitor', 'mon_l_01')
            else:
                return
        else:
            return
        endpoint = self._endpoint(_msg)
        self.preset(endpoint)

    def _parameter(self, msg):
        _params = []
        for _k, _v in msg.items():
            _param = '='.join([_k, _v])
            _params.append(_param)
        return '&'.join(_params)

    def _endpoint(self, msg):
        _link = ['camera', 'preset', 'startTime']
        _switch = ['camera', 'preset', 'monitor']
        _play = ['camera', 'startTime', 'delta', 'monitor']

        if not self._compare(_link, list(msg.keys())):
            parameter = self._parameter(msg)
            endpoint = 'link?' + parameter
        elif not self._compare(_switch, list(msg.keys())):
            parameter = self._parameter(msg)
            endpoint = 'switch?' + parameter
        elif not self._compare(_play, list(msg.keys())):
            parameter = self._parameter(msg)
            endpoint = 'play?' + parameter
        # elif 'name' in msg:
        #     if msg.get('name')[:3] == 'cam':
        #         parameter = self._parameter(msg)
        #         endpoint = 'cameras?' + parameter
        #         return endpoint
        #     if msg.get('name')[:3] == 'mon':
        #         parameter = self._parameter(msg)
        #         endpoint = 'monitors?' + parameter
        #         return endpoint
        #     else:
        #         return None
        return endpoint

    def _compare(self, send_param, recv_param):
        return [False for _item in send_param if _item not in recv_param]

    async def get_data(self, session, endpoint):
        try:
            async with async_timeout.timeout(10):
                async with session.get('{}/{}'.format(self.url,
                                                      endpoint)) as response:
                    res = await response.json()
                    log.info('Routing endpoint {} return message is {}. '.format(endpoint, res))
                    if endpoint in ("cameras", "monitors"):
                        if len(self.message) >= 2:
                            self.message.pop(0)
                        self.message.append(res)
        except Exception:
            log.error('Failed to obtain information! Please check the send data routing!')

    async def fetch(self, endpoint):
        async with aiohttp.ClientSession() as session:
            await self.get_data(session, endpoint)

    def preset(self, endpoint):
        asyncio.ensure_future(self.fetch(endpoint))

    def uploads(self, msg):
        log.info('Send to Amqp: {}'.format(msg))

        # return info from zmq to amqp
        # self.publish(msg)

    def _release(self, act=None, args=None, status=None):
        pass
