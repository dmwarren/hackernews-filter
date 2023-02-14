#!/usr/bin/env python
from bottle import route, run, template, static_file

from hn_filter_core import get_stories, filter_stories

@route('/')
def index():
	print('Got request')
	stories =  get_stories()
	filtered_stories = filter_stories(stories)
	context = {
		'good_stories':  filtered_stories['good'],
		'crap_stories':  filtered_stories['crap']
	}
	return template('home.tpl', context)

@route('/css/<filename>')
def css_files(filename):
    return static_file(filename, root='views/layoutit/src/css')

@route('/fonts/<filename>')
def fonts_files(filename):
    return static_file(filename, root='views/layoutit/src/fonts')

@route('/js/<filename>')
def js_files(filename):
    return static_file(filename, root='views/layoutit/src/js')

print("Starting...")
run(host='0.0.0.0', port=31337, reloader=True, quiet=True)


