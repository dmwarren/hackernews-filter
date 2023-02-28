#!/usr/bin/env python
import os
import json
import random
import sys
import logging

import click
import bottle
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

from hn_filter_core import get_stories, filter_stories


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s %(levelname)-8s "
        "%(pathname)s::%(funcName)s:%(lineno)d: %(message)s"
    ),
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
# disable all loggers from different files
bottle_logger = logging.getLogger('bottle').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('asyncio.coroutines').setLevel(logging.ERROR)
logging.getLogger('websockets.server').setLevel(logging.ERROR)
logging.getLogger('websockets.protocol').setLevel(logging.ERROR)

log = logging.getLogger("hn-filter")

app = bottle.Bottle()
filter_file = "filter.txt"

@app.route("/")
def index():
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("home_ws.html", root="views")


@app.route("/ws")
def data_processing():
    wsock = bottle.request.environ.get("wsgi.websocket")
    if not wsock:
        bottle.abort(400, "Expected WebSocket request.")
    try:
        stories = []
        # Send progress updates until the data is ready
        for page in [1, 2, 3]:
        # for page in [1]:
            page_stories = get_stories(page)
            stories += page_stories
            wsock.send(json.dumps({"type": "progress", "data": page}))

        # Send the data as a JSON object
        data = filter_stories(stories, filter_file)
        wsock.send(json.dumps({"type": "data", "data": data}))

    except WebSocketError:
        pass


@app.route("/css/<filename>")
def css_files(filename):
    return bottle.static_file(filename, root="views/css")


@app.route("/webfonts/<filename>")
def fonts_files(filename):
    return bottle.static_file(filename, root="views/fonts")


@app.route("/js/<filename>")
def js_files(filename):
    return bottle.static_file(filename, root="views/js")

@app.route("/img/<filename>")
def js_files(filename):
    return bottle.static_file(filename, root="views/img")


@app.route('/favicon.ico')
def favicon():
    return bottle.static_file("y18.ico", root="views/img")


def get_filter(filterfile):
    return filterfile


@click.command()
@click.option('--filterfile', type=click.Path(exists=True),
              default="filter.txt",
              help='File path for filter.txt file')
def main(filterfile):
    app_port = os.environ.get("APP_PORT", "31337")
    filter_file = filterfile

    log.info(f"Listening on {app_port}. Filter is {filter_file}")

    server = pywsgi.WSGIServer(
        ("0.0.0.0", int(app_port)),
        app,
        handler_class=WebSocketHandler,
        log=pywsgi._NoopLog()
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
