#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The Application Interface."""

from sanic import Sanic
from sanic.response import json
from sanic_jwt import exceptions
from sanic_jwt import initialize
from sanic_jwt.decorators import protected

app = Sanic('Cctv Api Server V1.0')


class User(object):
    def __init__(self, id, username, password):
        self.user_id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.user_id

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
        }


users = []

username_table = {u.username: u for u in users}
userid_table = {u.user_id: u for u in users}


async def authenticate(request, *args, **kwargs):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise exceptions.AuthenticationFailed(
            "Incorrect username or password.")

    username_table = {u.username: u for u in users}
    user = username_table.get(username, None)
    if user is None:
        raise exceptions.AuthenticationFailed(
            "Incorrect username or password.")

    if password != user.password:
        raise exceptions.AuthenticationFailed(
            "Incorrect username or password.")

    return user


@app.route("/")
async def index(request):
    return json({
        'info': str(app.site),
        'amqp': app.amqp.get_info(),
        'api_version': 'V1',
        'api': ['v2/actions'],
        'modules version': 'IPP-I'
    })


@app.route("/v2/devices")
async def sys_info(request):
    return json(app.site.info())


@app.route("/v2/actions")
@protected()
async def handle_system(request):
    return json(app.site.get_info())


def start(port, site, amqp, username='admin',
          password='admin'):
    app.site = site
    app.amqp = amqp
    users.append(User(2, username, password))
    initialize(app, authenticate=authenticate)
    return app.create_server(host="0.0.0.0",
                             port=port,
                             access_log=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
