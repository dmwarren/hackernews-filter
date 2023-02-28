import re
import logging
import time
import requests
import fileinput
import traceback
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# I like that we have to import a 'bs' library
# to build this kind of thing


HN_URL = "https://news.ycombinator.com/news?p="
log = logging.getLogger(__name__)


def get_stories(page):
    """Scrapes hackernews stories and filters the collection."""
    log.debug("in")
    story_rows = []
    stories = []

    # fetch!
    hn_page = HN_URL + str(page)
    start_time = time.time()
    r = requests.get(hn_page, verify=True)
    end_time = time.time()
    log.info(f"{hn_page} response "
             f"in {end_time - start_time:.2f} seconds")

    souped_body = BeautifulSoup(r.text, "lxml")

    try:
        storytable_html = souped_body("table")[2]
    except IndexError:
        raise Exception(
            "Can't find news story table. "
            "hackernews HTML format probably changed."
        )

    raw_stories = storytable_html.find_all("tr")

    story_duo = []
    for tr in raw_stories:
        # we want strings, not BeautifulSoup tag objects
        row = tr.encode("utf-8").decode("utf-8")
        if 'class="spacer"' in row:
            continue

        if 'class="morespace"' in row:
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
            links_in_line = len(link_line.find_all("a"))
            if links_in_line == 3:
                story["title"] = link_line.find_all("a")[1].string
                story["link"] = link_line.find_all("a")[1].get("href")
            else:
                # YC announcement
                story["title"] = link_line.find_all("a")[0].string
                story["link"] = link_line.find_all("a")[0].get("href")
                if not story["title"]:
                    # ASK HN
                    story["title"] = link_line.find_all("a")[1].string
                    story["link"] = link_line.find_all("a")[1].get("href")

            all_links = meta_line.find_all("a")
            if len(all_links) >= 3:
                story["comments_num"] = all_links[3].string.replace(
                    "\xa0comments", ""
                )
                story[
                    "comments_link"
                ] = "https://news.ycombinator.com/" + all_links[3].get("href")
            else:
                story["comments_num"] = 0
                story["comments_link"] = ""

            parsed_link = urlparse(story["link"])
            story["host"] = "{uri.netloc}".format(uri=parsed_link)
            if len(meta_line.find_all("span")) >= 2:
                story["points"] = meta_line.find_all("span")[1].string.replace(
                    " points", ""
                )
            else:
                story["points"] = "0"

        except IndexError as ie:
            log.info("IndexError on ", link_line, ie)
            traceback.log.info_exc()
            continue

        # Handle relative HN links
        if not story["link"].startswith("http"):
            story["link"] = HN_URL + story["link"]
        stories.append(story)

    log.debug("out")
    return stories


def filter_stories(stories, filter_file):
    """
    Filters HN stories.
    """
    result = {"good": [], "crap": []}
    log.debug("in")
    # suck in filter words
    patterns = []
    for line_num, line in enumerate(fileinput.input(filter_file)):
        line = line.strip()
        # skip blank lines
        if len(line) < 3:
            continue
        # skip comments
        if re.match(r"^#", line):
            continue
        if re.match(r"^>", line):
            why = line

        patterns.append({
            "compiled": re.compile(line),
            "why": why,
            "line_num": line_num
        })

    # combined_re = "(" + ")|(".join(patterns) + ")"
    # compiled_re = re.compile(combined_re)

    for story in stories:
        crapFound = False
        for pattern in patterns:
            compiled_re = pattern["compiled"]
            try:
                if compiled_re.match(story["title"]) or compiled_re.match(
                    story["link"]
                ):
                    story["why"] = pattern["why"]
                    story["line_num"] = pattern["line_num"]
                    result["crap"].append(story)
                    crapFound = True
                    break
            except:
                continue

        if not crapFound:
            result["good"].append(story)

    result["gl"] = f"{len(result['good'])}"
    result["cl"] = f"{len(result['crap'])}"

    return result


if __name__ == "__main__":
    log.info(filter_stories(get_stories()))
