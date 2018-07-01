#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json
import requests
import csv
import datetime
import logging
import urllib
import mysql.connector
import time


cnx = mysql.connector.connect(user='issa', database='contractwork')
cursor = cnx.cursor()
cursor.execute("""select task_receptacle,sum(payment),min(topic),min(completion_date)
               from tasks group by task_receptacle""")

ARTICLES = {x[0]: {"payment": x[1], "topic": x[2],
                   "creation_month": x[3].strftime("%B %Y")}
            for x in cursor.fetchall()}

cursor.close()
cnx.close()

GA_PAGEVIEWS = {}
with open("ga.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        GA_PAGEVIEWS[row['page_path']] = row['pageviews']

def ga_pageviews(pagename):
    """
    Get Google Analytics pageviews for the last 30 days.
    """
    path = "/wiki/" + pagename.replace(" ", "_")
    return int(GA_PAGEVIEWS.get(path, 0))

def payment(pagename):
    return round(ARTICLES.get(pagename, {"payment": 0.0})["payment"], 2)


def topic(pagename):
    if pagename in ARTICLES:
        return ARTICLES[pagename]["topic"]
    return ""


def creation_month(pagename):
    if pagename in ARTICLES:
        return ARTICLES[pagename]["creation_month"]
    return ""

# Modified from https://www.mediawiki.org/wiki/API:Query#Continuing_queries
def query(request, sleep=1):
    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {'continue': ''}
    iteration = 0
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the
        # last result.
        req.update(lastContinue)
        # Call API
        r = requests.get("https://timelines.issarice.com/api.php", params=req)
        result = r.json()
        logging.info("ON ITERATION %s, SLEEPING FOR %s", iteration, sleep)
        time.sleep(sleep)
        iteration += 1
        if 'error' in result:
            raise ValueError(r.url, result['error'])
        if 'warnings' in result:
            logging.warning(result['warnings'])
        if 'query' in result:
            yield result['query']
        if 'continue' not in result:
            break
        lastContinue = result['continue']


def pagename_generator():
    payload = {
            "list": "allpages",
            "apprefix": "Timeline of",
            "apfilterredir": "nonredirects",
            "aplimit": 50,
            }
    for result in query(payload):
        for page in result["allpages"]:
            yield page["title"]


def page_display_name(pagename):
    prefix = "timeline of "
    if pagename.lower().startswith(prefix):
        return pagename[len(prefix)].upper() + pagename[len(prefix)+1:]
    return pagename


def pageviews(pagename):
    """
    Get monthly pageviews data for pagename. creation_month is used to find out
    what months to get the pageviews data for.
    """
    cm = creation_month(pagename)
    if cm in ["Not yet complete", ""]:
        return 0
    today = datetime.date.today()

    # Start getting pageviews data from the month following the creation of the
    # page or 12 months ago, whichever comes later. We want to average over at
    # most twelve months of pageviews data.
    cd = datetime.datetime.strptime(cm, "%B %Y")
    if cd.month == 12:
        start_date = datetime.date(cd.year + 1, 1, 1)
    else:
        start_date = datetime.date(cd.year, cd.month + 1, 1)
    max_back = datetime.date(today.year - 1, today.month, 1)
    start_date = max(start_date, max_back)
    m = str(start_date.month) if start_date.month >= 10 else "0" + \
            str(start_date.month)
    start = str(start_date.year) + m + "01"

    # Stop getting pageviews at the last day of the previous month
    last_day_of_last_month = datetime.date(today.year, today.month, 1) - \
            datetime.timedelta(days=1)
    end = datetime.datetime.strftime(last_day_of_last_month, "%Y%m%d")

    url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/" + \
          "per-article/en.wikipedia.org/all-access/user/" + \
          urllib.parse.quote(pagename, safe="") + \
          "/monthly/" + start + "/" + end

    r = requests.get(url)
    result = r.json()
    views = 0
    if 'items' not in result:
        return 0
    for month in result['items']:
        views += int(month['views'])
    return views / (last_day_of_last_month - start_date).days * 30

def full_timeline_heading(soup):
    """Find and return the "Full timeline" heading."""
    for h2 in soup.find_all("h2"):
        span = h2.find("span", {"class": "mw-headline"})
        if span and (span.text == "Full timeline" or span.text == "Timeline"):
            return h2

def full_timeline_table(soup, h2):
    """
    Find and return the "Full timeline" table tag given the tag soup and the h2
    "Full timeline" heading tag.
    """
    tag = h2
    while tag and (tag.name != "table" or
            "not-full-timeline" in tag.get("class")):
        tag = tag.next_sibling
    if tag:
        return tag

    # Otherwise, we stepped right through the page without finding the table

def number_of_rows(pagename):
    payload = {
        "action": "parse",
        "page": pagename,
        "format": "json",
    }

    r = requests.get("https://timelines.issarice.com/api.php", params=payload)
    result = r.json()
    text = result["parse"]["text"]["*"]
    soup = BeautifulSoup(text, "lxml")

    h2 = full_timeline_heading(soup)
    full_timeline = full_timeline_table(soup, h2)
    if full_timeline:
        return len(full_timeline.find_all("tr")) - 1
    else:
        # Could not find full timeline
        return ""

def print_table():
    print("<!-- WARNING:")
    print("Do not manually edit this table. This table is produced using")
    print("an automated script. The script does not check for manual changes")
    print("to the table, so any changes you make will be overwritten the next")
    print("time the script runs. To make manual changes, the underlying CSV")
    print("file must be edited. For more information, see the script")
    print("repository at")
    print("https://github.com/riceissa/timelines-wiki-main-page-table")
    print('-->{| class="sortable wikitable"')
    print("|-")
    print("! Timeline subject")
    print("! Focus area")
    print("! Creation month")
    print('! data-sort-type="number" | Number of rows')
    print('! data-sort-type="number" | Total payment')
    print('! data-sort-type="number" | Monthly pageviews')
    print('! data-sort-type="number" | Monthly pageviews on Wikipedia')

    for pagename in pagename_generator():
        print("|-")
        print("| [[" + pagename + "|" + page_display_name(pagename)
              + "]]")
        print("| " + topic(pagename))
        if not creation_month(pagename):
            print("| Not yet complete")
        else:
            print("| {{dts|" + creation_month(pagename) + "}}")
        n = number_of_rows(pagename)
        print('| style="text-align:right;" | ' + str(n))
        p = payment(pagename)
        if p > 0:
            print('| style="text-align:right;" | [{} {:.2f}]'.format(
                "https://contractwork.vipulnaik.com/tasks.php?receptacle={}&matching=exact" \
                        .format(urllib.parse.quote_plus(pagename)),
                p
            ))
        else:
            print('| style="text-align:right;" | 0.00')
        print('| style="text-align:right;" | ' + str(ga_pageviews(pagename)))
        wv_pageviews = int(pageviews(pagename))
        if wv_pageviews > 0:
            print('| style="text-align:right;" | [{} {}]'.format(
                "https://wikipediaviews.org/displayviewsformultiplemonths.php?page={}&allmonths=allmonths&language=en&drilldown=human" \
                        .format(urllib.parse.quote_plus(pagename)),
                str(wv_pageviews)
                ))
        else:
            print('| Not on Wikipedia')
    print("|}")

if __name__ == "__main__":
    print_table()
