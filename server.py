#!/usr/bin/env python
import os
import json
import sys
import logging

import click
import bottle

from passlib.context import CryptContext

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from bottle_login import LoginPlugin

from hn_filter_core import (
    get_stories, filter_stories, get_filter, find_user,
    register_user, save_filter_file, why_crap
)


CONFIG_PATH = "./"
DEFAULT_FILTER_FILE = "filter.txt"
USER_FILE = "users.json"

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
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "not_a_secret_at_all")
app.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
login = app.install(LoginPlugin())


@login.load_user
def load_user(user_id):
    return find_user(user_id, USER_FILE)


def filter_file_name():
    user = login.get_user()
    if user:
        return user["filter_file"]

    return DEFAULT_FILTER_FILE


@app.route("/")
def index():
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("home_ws.html", root="views")


@app.route("/uuidindex")
def gen_uuid_index():
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("generate.html", root="views")


@app.route("/ws/<num_pages>")
def data_processing(num_pages):
    log.info(f"num pages: {num_pages}")
    wsock = bottle.request.environ.get("wsgi.websocket")
    if not wsock:
        bottle.abort(400, "Expected WebSocket request.")
    try:
        stories = []
        # Send progress updates until the data is ready
        for page in range(1, int(num_pages) + 1):
            log.info(f"Reading page {page}")
            page_stories = get_stories(page)
            stories.extend(page_stories)
            wsock.send(json.dumps({"type": "progress", "data": page}))

        data = filter_stories(stories, filter_file_name())

        wsock.send(json.dumps({"type": "data", "data": data}))

    except WebSocketError:
        pass


@app.route("/editcrap")
def edit_crap():
    bottle.response.headers["Content-Type"] = "application/json"

    return {"filter": get_filter(filter_file_name())}


@app.route("/savecrap", method="POST")
def save_filter():
    bottle.response.headers["Content-Type"] = "application/json"
    filter_lines = bottle.request.forms.get("filter_lines")

    save_filter_file(filter_file_name(), filter_lines)
    return {"success": True}


@app.route("/showwhy", method="POST")
def show_why():
    descr = bottle.request.forms.get("story")
    url =  bottle.request.forms.get("url")

    why = why_crap(descr, url, filter_file_name())
    bottle.response.headers["Content-Type"] = "application/json"
    return {"why": why}


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


@app.route("/check_login_status")
def check_login_status():
    user = login.get_user()
    if user:
        data = {"logged_in": True, "email": user["email"]}
    else:
        data = {"logged_in": False, "email": ""}

    bottle.response.headers["Content-Type"] = "application/json"
    return data


@app.route("/register", method="POST")
def do_register():
    user_id = bottle.request.forms.get("email")
    pw = bottle.request.forms.get("pass")
    hashed_pw = app.pwd_context.hash(pw)

    register_user(
        user_id, hashed_pw, USER_FILE, DEFAULT_FILTER_FILE, CONFIG_PATH
    )
    login.login_user(user_id)

    bottle.response.headers["Content-Type"] = "application/json"
    return {"success": True}


@app.route("/login", method="POST")
def do_login():
    user_id = bottle.request.forms.get("email")
    pw = bottle.request.forms.get("pass")
    bottle.response.headers["Content-Type"] = "application/json"

    reg_user = find_user(user_id, USER_FILE)
    if reg_user:
        if app.pwd_context.verify(pw, reg_user["password"]):
            login.login_user(user_id)
            return {"success": True}

    return {"success": False}


@app.route("/logout")
def do_logout():
    login.logout_user()
    bottle.response.headers["Content-Type"] = "application/json"

    return {"success": True}


@click.command()
@click.option(
    "--configpath",
    type=click.Path(exists=True),
    default=CONFIG_PATH,
    help="File path for filter.txt and user.json files",
)
def main(configpath):
    app_port = os.environ.get("APP_PORT", "31337")
    global CONFIG_PATH
    global DEFAULT_FILTER_FILE
    global USER_FILE

    CONFIG_PATH = configpath
    DEFAULT_FILTER_FILE = os.path.join(configpath, "filter.txt")
    USER_FILE = os.path.join(configpath, "users.json")

    log.info(f"Listening on {app_port}. Config path is {configpath}")

    server = pywsgi.WSGIServer(
        ("0.0.0.0", int(app_port)),
        app,
        handler_class=WebSocketHandler,
        log=pywsgi._NoopLog(),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
