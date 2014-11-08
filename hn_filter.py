#!/usr/bin/env python
from hn_filter_core import get_stories, filter_stories

BOLDON = "\033[1m"
BOLDOFF = "\033[0m"

stories = get_stories()
filtered_stories = filter_stories(stories)

good_stories = filtered_stories['good']
crap_stories = filtered_stories['crap']

if __name__ == '__main__':
    for story in filtered_stories['good']:
        print(BOLDON + story['title'] + BOLDOFF)
        print("  " + story['link'])
        print("")

print("Good: " + str(len(good_stories)))
print("Crap: " + str(len(crap_stories)))
