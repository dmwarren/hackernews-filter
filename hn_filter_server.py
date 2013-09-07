#!/usr/bin/env python
from bottle import route, run, template

from hn_filter_core import get_stories, filter_stories

@route('/')
def index():
	stories =  get_stories()
	filtered_stories = filter_stories(stories)
	context = {
		'good_stories':  filtered_stories['good'],
		'crap_stories':  filtered_stories['crap']
	}
	return template('home.tpl', context)

run(host='localhost', port=31337, reloader=True)


