#!/usr/bin/env python

# Derek's Hackernews Crap Filter
# v0.1 - 14-Aug-2013 - warren@sfu.ca
# Initial release.

import re, requests, fileinput
from bs4 import BeautifulSoup
# I like that we have to import a 'bs' library
# to build this kind of thing

SCAN_URL = 'https://news.ycombinator.com/'
VERBOTEN_LIST = 'hn-verboten.txt'
BOLDON = "\033[1m"
BOLDOFF = "\033[0m"

patterns = []
story_rows = []
crap_stories = 0
good_stories = 0

# suck in filter words
for line in fileinput.input(VERBOTEN_LIST):
 	patterns.append(line.strip())
combined_re = "(" + ")|(".join(patterns) + ")"
compiled_re = re.compile(combined_re)

# fetch!
r = requests.get(SCAN_URL, verify=False)
souped_body = BeautifulSoup(r.text)

try:
	storytable_html = souped_body('table')[2]
except IndexError:
	print("Can't find news story table. hackernews HTML format changed.")
	exit(1)

for tr in storytable_html.find_all('tr'):
	row = str(tr) # we (sometimes) want strings, not BeautifulSoup tag objects

	# Skip to next iteration of for loop if you see a superfluous table row.
	# (anything without a 'vote?for=' link which also skips sponsored posts.
	# score!)
	if not re.match(r'.*"vote\?for=.*', row):
		continue

	if compiled_re.match(row):
		crap_stories += 1 
	else:
		story_rows.append(tr)
		good_stories += 1

for story in story_rows:
	print(BOLDON + story.find_all('a')[1].string + BOLDOFF) 
	print("  " + story.find_all('a')[1].get('href'))
	print("")

# 14-Aug-2013 - good:crap ratio is 16:14 this afternoon.
# So many extra free brain resources!
print("Good: " + str(good_stories))
print("Crap: " + str(crap_stories))




# LICENSE
# 
# Derek's Hackernews Crap Filter is distributed under the following
# BSD-style license.
# 
# Copyright (c) 2013 Derek Warren. All Rights Reserved. Redistribution and
# use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
# - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# - The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

