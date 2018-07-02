# SAM-CCTV

`SAM－CCTV` is the message transponder for the `SAM-LITE` platform, which is transmitted in two ways by receiving messages sent from the sam-lite platform to achieve the purpose of controlling external hardware devices. Two ways of message forwarding: one, ZMQ communication protocol; two. HTTP communication protocol.

## preparation

- Python 3.5.3+.

## Install the environment and dependencies

- Create and enter a virtual environment.

```
$ cd cctv
$ python3 -m venv env
$ source env/bin/activate
```

- Install dependency module.

```
(env)$ pip install -e .
```

## How to perform？

`cctv` is run via the `sam-cctv` command. Run the `--help` subcommand to see the list of options:

```
(env)$ sam-cctv --help
Usage: sam-cctv [OPTIONS]

  Publisher for PM-1 with IPP protocol

Options:
  --cctv_type TEXT  Service Type, ENV: CCTV_TYPE, default: zmq,
                    option: km|zmq etc
  --cctv_svr TEXT   CCTV Server URL,
                    ENV: CCTV_SVR, default: tcp://*:15570
  --amqp TEXT       Amqp url, also ENV: SVC_AMQP
  --port INTEGER    Api port, default=80, ENV: SVC_PORT
  --qid INTEGER     ID for amqp queue name, default=0, ENV: SVC_QID
  --username TEXT   Api auth username, ENV: SVC_USERNAME
  --password TEXT   Api auth password, ENV: SVC_PASSWORD
  --debug
  --help            Show this message and exit.
```

*note*: if `--cctv_type` equal to `km`, The way the message is forwarded is an HTTP communication protocol, it's equal to `zmq`, using the ZMQ communication protocol.

### Start to perform!

Sending messages can be done using the `sam-cctv` command.

- example1: Send the message using the `HTTP communication protocol`.

```
(env)$ sam-cctv --cctv_type=km --cctv_svr=http://192.168.1.163:7080 --amqp=amqp://guest:guest@192.168.1.162:5672

See more documentation at http://www.mingvale.com
2018-05-14 16:19:18,561 INFO [log] Start Runing...
2018-05-14 16:19:18,562 INFO [cli] Basic Information: {'cctv_type': 'km', 'cctv_svr': 'http://192.168.1.163:7080', 'api_port': 80, 'amqp': 'amqp://guest:guest@192.168.1.162:5672'}
2018-05-14 16:19:18,562 INFO [cli] Service is KM
2018-05-14 16:19:18,564 INFO [routermq] Connecting to rabbitmq [amqp://guest:guest@192.168.1.162:5672/] ...
[2018-05-14 16:19:18 +0800] [15968] [INFO] Goin' Fast @ http://0.0.0.0:80
2018-05-14 16:19:18,565 INFO [app] Goin' Fast @ http://0.0.0.0:80
2018-05-14 16:19:18,627 INFO [routermq] RabbitMQ Successfully connected.

```
The return result is：

```
2018-05-14 16:29:44,441 INFO [cctv] Amqp received: {'status': 'AUTO', 'name': 'CAM_04-J18_1', 'type': 'CAMERA', 'args': 5}
2018-05-14 16:29:44,524 INFO [cctv_km] Routing endpoint link?camera=CAM_04-J18_1&preset=5&startTime=2018-05-14 16:29:44 return message is {'camera': 'CAM_04-J18_1', 'status': '8001'}.
```

- example2: Send the message using the `ZMQ communication protocol`.

```
(env)$ sam-cctv --cctv_type=km --cctv_svr=tcp://192.168.1.150.15570 --amqp=amqp://guest:guest@192.168.1.162:5672

See more documentation at http://www.mingvale.com
2018-05-14 16:41:07,111 INFO [log] Start Runing...
2018-05-14 16:41:07,111 INFO [cli] Basic Information: {'cctv_type': 'zmq', 'cctv_svr': 'tcp://192.168.1.150:15570', 'api_port': 80, 'amqp': 'amqp://guest:guest@192.168.1.162:5672'}
2018-05-14 16:41:07,111 INFO [cli] Service is ZMQ
2018-05-14 16:41:07,115 INFO [routermq] Connecting to rabbitmq [amqp://guest:guest@192.168.1.162:5672/] ...
[2018-05-14 16:41:07 +0800] [16407] [INFO] Goin' Fast @ http://0.0.0.0:80
2018-05-14 16:41:07,115 INFO [app] Goin' Fast @ http://0.0.0.0:80
2018-05-14 16:41:07,168 INFO [routermq] RabbitMQ Successfully connected.

```
The return result is：

```
2018-05-14 16:41:09,997 INFO [cctv] Amqp received: {'status': 'AUTO', 'name': 'CAM_05-J01_1', 'type': 'CAMERA', 'args': 1}
2018-05-14 16:41:09,997 INFO [async_zmq] Transmit to Dealer: {'status': 'AUTO', 'name': 'CAM_05-J01_1', 'type': 'CAMERA', 'args': 1}
```
