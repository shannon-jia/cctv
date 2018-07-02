# -*- coding: utf-8 -*-

"""Console script for rps."""

import click
from .log import get_log
from .routermq import RouterMQ
from .cctv_zmq import Cctv_Zmq
from .cctv_km import Cctv_Km
# from .api import Api
from . import api_server
import asyncio


def validate_url(ctx, param, value):
    try:
        return value
    except ValueError:
        raise click.BadParameter('url need to be format: tcp://ipv4:port')


@click.command()
@click.option('--cctv_type', default='zmq',
              envvar='CCTV_TYPE',
              help='Service Type, ENV: CCTV_TYPE, default: zmq, \
              option: km|zmq etc')
@click.option('--cctv_svr', default='tcp://*:15570',
              envvar='CCTV_SVR',
              help='CCTV Server URL, \n \
              ENV: CCTV_SVR, default: tcp://*:15570')
@click.option('--amqp', default='amqp://guest:guest@rabbit:5672//',
              callback=validate_url,
              envvar='SVC_AMQP',
              help='Amqp url, also ENV: SVC_AMQP')
@click.option('--port', default=80,
              envvar='SVC_PORT',
              help='Api port, default=80, ENV: SVC_PORT')
@click.option('--qid', default=0,
              envvar='SVC_QID',
              help='ID for amqp queue name, default=0, ENV: SVC_QID')
@click.option('--username', default='admin',
              envvar='SVC_USERNAME',
              help='Api auth username, ENV: SVC_USERNAME')
@click.option('--password', default='admin',
              envvar='SVC_PASSWORD',
              help='Api auth password, ENV: SVC_PASSWORD')
@click.option('--debug', is_flag=True)
def main(cctv_type, cctv_svr, amqp, port, qid, username, password, debug):
    """Publisher for PM-1 with IPP protocol"""

    click.echo("See more documentation at http://www.mingvale.com")

    info = {
        'cctv_type': cctv_type,
        'cctv_svr': cctv_svr,
        'api_port': port,
        'amqp': amqp,
    }
    log = get_log(debug)
    log.info('Basic Information: {}'.format(info))

    loop = asyncio.get_event_loop()
    loop.set_debug(0)

    # main process
    try:
        _cctv_type = cctv_type.upper()
        if _cctv_type == 'ZMQ':
            log.info('Service is ZMQ')
            site = Cctv_Zmq(loop, cctv_svr)
        elif _cctv_type == 'KM':
            log.info('Service is KM')
            site = Cctv_Km(loop, cctv_svr)
        else:
            log.warn('Undefined server type, use default.')
            site = Cctv_Zmq(loop, cctv_svr)
        router = RouterMQ(outgoing_key='Alarms.cctv',
                          routing_keys=['Actions.cctv'],
                          queue_name='cctv_'+str(qid),
                          url=amqp)
        router.set_callback(site.got_command)
        site.set_publish(router.publish)
        # api = Api(loop=loop, port=port, site=site, amqp=router)
        site.start()
        amqp_task = loop.create_task(router.reconnector())
        # api.start()
        api_task = loop.create_task(api_server.start(port=port,
                                                     site=site,
                                                     amqp=router,
                                                     username=username,
                                                     password=password))
        loop.run_forever()
    except OSError as e:
        log.error(e)
    except KeyboardInterrupt:
        if amqp_task:
            amqp_task.cancel()
            loop.run_until_complete(amqp_task)
        if api_task:
            api_task.cancel()
            loop.run_until_complete(api_task)
        site.stop()
    finally:
        loop.stop()
        loop.close()
