#!/usr/bin/env python

# Derek's Hackernews Crap Filter
# v0.4 - 08-Nov-2014 - now Python 2.7/3.4 compatible
# v0.3 - 07-Aug-2013

import re
import requests
import fileinput
from bs4 import BeautifulSoup
# I like that we have to import a 'bs' library
# to build this kind of thing


SCAN_URL = 'https://news.ycombinator.com/'
VERBOTEN_LIST = 'filter.txt'

def get_stories():
    """ Scrapes hackernews stories and filters the collection. """
    story_rows = []
    stories = []

    # fetch!
    r = requests.get(SCAN_URL, verify=True)
    souped_body = BeautifulSoup(r.text)

    try:
        storytable_html = souped_body('table')[2]
    except IndexError:
        raise Exception("Can't find news story table. " +
                        "hackernews HTML format probably changed.")

    raw_stories = storytable_html.find_all('tr')
    for tr in raw_stories:
        # we want strings, not BeautifulSoup tag objects
        row = tr.encode('utf-8')

        # Skip to next iteration of for loop if you see a superfluous table row.
        # (anything without a 'vote?for=' link which also skips sponsored posts.
        # score!)

        if not re.match(r'.*"vote\?for=.*', str(row)):
            continue
        story_rows.append(tr)

    for story_row in story_rows:
        story = {}
        story['title'] = story_row.find_all('a')[1].string
        story['link'] = story_row.find_all('a')[1].get('href')
        # Handle relative HN links
        if not story['link'].startswith('http'):
            story['link'] = SCAN_URL + story['link']
        stories.append(story)
    return stories


def filter_stories(stories):
    """
    Filters HN stories.
    """
    result = {
        'good': [],
        'crap': []
    }
    # suck in filter words
    patterns = []
    for line in fileinput.input(VERBOTEN_LIST):
        line = line.strip()
        # skip blank lines
        if len(line) < 3:
            continue
        # skip comments
        if re.match(r'^#', line):
            continue
        patterns.append(line)
    combined_re = "(" + ")|(".join(patterns) + ")"
    compiled_re = re.compile(combined_re)

    for story in stories:
        if compiled_re.match(story['title']) or compiled_re.match(story['link']):
            result['crap'].append(story)
        else:
            result['good'].append(story)
    return result


# 14-Aug-2013 - good:crap ratio is 16:14 this afternoon.
# So many extra free brain resources!

if __name__ == '__main__':
    print(filter_stories(get_stories()))
