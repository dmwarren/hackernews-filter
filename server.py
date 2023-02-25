#!/usr/bin/env python
import os
import json
import random
from io import BytesIO

import bottle
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from PIL import Image

from hn_filter_core import get_stories, filter_stories


app = bottle.Bottle()


@app.route("/")
def index():
    print(f"Got index request")
    bottle.response.headers["Content-Type"] = "text/html"
    return bottle.static_file("home_ws.html", root="views")
    # return bottle.template(
    #     "home_ws.html", ws=os.environ.get("APP_PORT", "31337"))


@app.route("/ws")
def data_processing():
    print(f"Got ws request: {bottle.request.environ}")
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
            print(f"From page {page} got {len(page_stories)} stories")

        print(f"Total stories {len(stories)}")
        # Send the data as a JSON object
        data = filter_stories(stories)
        wsock.send(json.dumps({"type": "data", "data": data}))

    except WebSocketError:
        pass


@app.route("/css/<filename>")
def css_files(filename):
    return bottle.static_file(filename, root="views/layoutit/src/css")


@app.route("/fonts/<filename>")
def fonts_files(filename):
    return bottle.static_file(filename, root="views/layoutit/src/fonts")


@app.route("/js/<filename>")
def js_files(filename):
    return bottle.static_file(filename, root="views/layoutit/src/js")


@app.route('/favicon.ico')
def favicon():
    # Generate a random 16x16 image
    image = Image.new(
        'RGB', (32, 32),
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    )

    # convert the image to bytes and serve it as the response
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_stream.seek(0)

    bottle.response.set_header('Content-type', 'image/x-icon')
    bottle.response.set_header('Cache-Control', 'no-cache')
    bottle.response.set_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT')

    # Return the image bytes
    return byte_stream.read()


if __name__ == "__main__":
    print("Starting...")
    server = pywsgi.WSGIServer(
        ("0.0.0.0", int(os.environ.get("APP_PORT", "31337"))),
        app,
        handler_class=WebSocketHandler,
    )
    server.serve_forever()
