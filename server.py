#!/usr/bin/env python
import os
import json
import sys
import logging

import click
import bottle
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

from hn_filter_core import get_stories, filter_stories, get_filter


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s %(levelname)-8s "
        "%(pathname)s::%(funcName)s:%(lineno)d: %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
# disable all loggers from different files
bottle_logger = logging.getLogger("bottle").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("asyncio.coroutines").setLevel(logging.ERROR)
logging.getLogger("websockets.server").setLevel(logging.ERROR)
logging.getLogger("websockets.protocol").setLevel(logging.ERROR)

log = logging.getLogger("hn-filter")

app = bottle.Bottle()
filter_file = "filter.txt"


def require_uuid(is_post=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def valid_uuid(uuid_string):
                try:
                    UUID(uuid_string)
                    return True
                except ValueError:
                    log.info(f"Invalid uuid: {uuid_string}")
                    return False

            if bottle.request.method == "POST":
                uuid = bottle.request.forms.get("uuid")
                log.info(f"POST {uuid}")
            else:
                uuid = bottle.request.query.get("uuid")
                log.info(f"GET {uuid}")
                if not uuid:
                    uuid = bottle.request.get_cookie("uuid")
                    log.info(f"Cookie {uuid}")

            if not uuid or not valid_uuid(uuid):
                log.info("Invalid or not set uuid")
                bottle.abort(bottle.redirect("/uuidindex"))

            return func(*args, **kwargs)

        return wrapper

    return decorator

@app.route("/")
@require_uuid()
def index():
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("home_ws.html", root="views")


@app.route("/uuidindex")
def gen_uuid_index():
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("generate.html", root="views")


@app.route("/ws")
@require_uuid()
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
        app.crap_stories = data["crap"]
        wsock.send(json.dumps({"type": "data", "data": data}))

    except WebSocketError:
        pass


@app.route("/addcrap/<url>")
@require_uuid()
def add_crap(url):
    bottle.response.headers["Content-Type"] = "application/json"
    return {"url": url, "filter": get_filter(filter_file)}


@app.route("/editcrap")
@require_uuid()
def edit_crap():
    bottle.response.headers["Content-Type"] = "application/json"
    return {"filter": get_filter(filter_file)}

@app.route("/getuuid")
def gen_actual_uuid():
    bottle.response.headers["Content-Type"] = "application/json"
    return {"filter": get_filter(filter_file, None), "uuid": str(uuid4())}

@app.route("/savecrap", method="POST")
@require_uuid()
def save_crap():
    # data = bottle.request.json

    new_filter = bottle.request.forms.get("filter")
    # save_filter(new_filter)

    return {"success": "success"}


@app.route("/newuuid", method="POST")
@require_uuid()
def save_new_uuid():
    new_filter = bottle.request.forms.get("filter")
    new_uuid = bottle.request.forms.get("uuid")
    log.info(f"uuid: {new_uuid}")
    # save_filter(new_filter, new_uuid)
    bottle.response.set_cookie(
        'uuid',
        new_uuid,
        max_age=31536000  # 1 year in seconds
    )

    return {"success": "success"}


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
def img_files(filename):
    return bottle.static_file(filename, root="views/img")


@app.route("/favicon.ico")
def favicon():
    return bottle.static_file("y18.ico", root="views/img")


@app.route("/showwhy", method="POST")
def show_why():
    return


def get_filter(filterfile):
    return filterfile


@click.command()
@click.option(
    "--filterfile",
    type=click.Path(exists=True),
    default="filter.txt",
    help="File path for filter.txt file",
)
def main(filterfile):
    app_port = os.environ.get("APP_PORT", "31337")
    filter_file = filterfile

    log.info(f"Listening on {app_port}. Filter is {filter_file}")

    server = pywsgi.WSGIServer(
        ("0.0.0.0", int(app_port)),
        app,
        handler_class=WebSocketHandler,
        log=pywsgi._NoopLog(),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
