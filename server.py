#!/usr/bin/env python
from bottle import route, run, template, static_file, request, Bottle
from paste import httpserver

from hn_filter_core import get_stories, filter_stories


app = Bottle()

@app.route('/')
def index():
	print(f'Got request: {request.environ}')
	stories =  get_stories()
	filtered_stories = filter_stories(stories)
	context = {
		'good_stories':  filtered_stories['good'],
		'crap_stories':  filtered_stories['crap']
	}
	print(f'All done. Rendering template')
	return template('home.tpl', context)

@app.route('/css/<filename>')
def css_files(filename):
    return static_file(filename, root='views/layoutit/src/css')

@app.route('/fonts/<filename>')
def fonts_files(filename):
    return static_file(filename, root='views/layoutit/src/fonts')

@app.route('/js/<filename>')
def js_files(filename):
    return static_file(filename, root='views/layoutit/src/js')

print("Starting...")
#run(host='0.0.0.0', port=9090, reloader=True, quiet=True, server="cgi")
httpserver.serve(app, host='0.0.0.0', port=31337)


