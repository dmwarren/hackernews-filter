#!/usr/bin/env python

# Derek's Hackernews Crap Filter
# v0.4 - 08-Nov-2014 - now Python 2.7/3.4 compatible
# v0.3 - 07-Aug-2013

import re
import requests
import fileinput
import traceback
from urllib.parse import urlparse
from bs4 import BeautifulSoup
# I like that we have to import a 'bs' library
# to build this kind of thing


SCAN_URL = 'https://news.ycombinator.com/news?p='
VERBOTEN_LIST = 'filter.txt'

def get_stories():
    """ Scrapes hackernews stories and filters the collection. """
    print("get_stories in")
    story_rows = []
    stories = []

    # fetch!
    for page in [1, 2, 3]:
        r = requests.get(SCAN_URL + str(page), verify=True)
        souped_body = BeautifulSoup(r.text, 'lxml')

        try:
            storytable_html = souped_body('table')[2]
        except IndexError:
            raise Exception("Can't find news story table. " +
                            "hackernews HTML format probably changed.")

        raw_stories = storytable_html.find_all('tr')
        story_duo = []
        for tr in raw_stories:
            # we want strings, not BeautifulSoup tag objects
            row = tr.encode('utf-8').decode('utf-8')
            if 'spacer' in row:
                continue

            if 'More' in row:
                break

            story_duo.append(tr)
            if len(story_duo) == 2:
                story_rows.append(story_duo)
                story_duo = []


    for story_row in story_rows:
        story = {}
        link_line = story_row[0]
        meta_line = story_row[1]

        try:
            story['title'] = link_line.find_all('a')[1].string
            story['link'] = link_line.find_all('a')[1].get('href')
            all_links = meta_line.find_all('a')
            if len(all_links) >= 3:
                story['comments_num'] = all_links[3].string.replace('\xa0comments', '')
                story['comments_link'] = 'https://news.ycombinator.com/' + all_links[3].get('href')
            else:
                story['comments_num'] = 0
                story['comments_link'] = ''
            parsed_link = urlparse(story['link'])
            story['host'] = '{uri.netloc}'.format(uri=parsed_link)
            if len(meta_line.find_all('span')) >= 2:
                story['points'] = meta_line.find_all('span')[1].string.replace(' points', '')
            else:
                story['points'] = "unknown"
        except IndexError as ie:
            print('IndexError on ', link_line, ie)
            traceback.print_exc()
            continue

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
        'good': {},
        'crap': {}
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
        if re.match(r'^>', line):
            why = line

        patterns.append({'regex': line, 'why': why})

    # combined_re = "(" + ")|(".join(patterns) + ")"
    # compiled_re = re.compile(combined_re)

    for story in stories:
        for pattern in patterns:
            compiled_re = re.compile(pattern['regex'])
            if compiled_re.match(story['title']) or compiled_re.match(story['link']):
                result['crap'].update({story['link']: {'story': story, 'why': pattern['why']}})
            else:
                result['good'].update({story['link']: {'story': story, 'why': None}})
        if story['link'] in result['crap']:
             del result['good'][story['link']]

    return result

if __name__ == '__main__':
    print(filter_stories(get_stories()))
