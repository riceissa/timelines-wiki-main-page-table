#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json
import requests
import sys
import csv
import datetime
import dateutil.parser
import logging
import urllib
import mysql.connector
import time

import util

logging.basicConfig(level=logging.INFO)


# By checking the contractwork database, we can tell most of the time whether a
# timeline is complete or not by looking at the total payment (if it's zero,
# it's incomplete; otherwise it's complete). The exceptions are timelines that
# are "non-paid", meaning someone made it outside of contract work and it won't
# ever receive payment. Since the contractwork database doesn't track these
# timelines, we have to list them out here.
ARTICLES = {
        "Timeline of Bay Area Rapid Transit":
            {"topic": "Transportation", "creation_month": "May 2017"},
        "Timeline of Carl Shulman publications":
            {"topic": "Rationality", "creation_month": "June 2017"},
        "Timeline of Chinese immigration to the United States":
            {"topic": "Migration", "creation_month": "May 2017"},
        "Timeline of DOS operating systems":
            {"topic": "Miscellaneous technology", "creation_month": "October 2008"},
        "Timeline of genetic engineering in humans":
            {"topic": "Miscellaneous technology", "creation_month": "December 2018"},
        "Timeline of Google Search":
            {"topic": "Miscellaneous technology", "creation_month": "February 2014"},
        "Timeline of H-1B":
            {"topic": "Migration", "creation_month": "August 2017"},
        "Timeline of HTTPS adoption":
            {"topic": "Miscellaneous technology", "creation_month": "November 2017"},
        "Timeline of immigrant processing and visa policy in Canada":
            {"topic": "Migration", "creation_month": "November 2017"},
        "Timeline of immigrant processing and visa policy in the United Kingdom":
            {"topic": "Migration", "creation_month": "November 2017"},
        "Timeline of immigrant processing and visa policy in the United States":
            {"topic": "Migration", "creation_month": "March 2017"},
        "Timeline of immigration detention in the United States":
            {"topic": "Migration", "creation_month": "November 2017"},
        "Timeline of immigration enforcement in the United Kingdom":
            {"topic": "Migration", "creation_month": "November 2017"},
        "Timeline of immigration enforcement in the United States":
            {"topic": "Migration", "creation_month": "March 2017"},
        "Timeline of IPv6 adoption":
            {"topic": "Miscellaneous technology", "creation_month": "November 2017"},
        "Timeline of machine translation":
            {"topic": "Miscellaneous technology", "creation_month": "February 2014"},
        "Timeline of online dating services":
            {"topic": "Miscellaneous technology", "creation_month": "June 2015"},
        "Timeline of online job search and professional networking":
            {"topic": "Miscellaneous technology", "creation_month": "May 2017"},
        "Timeline of site search":
            {"topic": "Miscellaneous technology", "creation_month": "May 2017"},
        "Timeline of student visa policy in the United States":
            {"topic": "Migration", "creation_month": "November 2017"},
        "Timeline of TempleOS":
            {"topic": "Miscellaneous technology", "creation_month": "March 2017"},
        "Timeline of Wei Dai publications":
            {"topic": "Rationality", "creation_month": "February 2018"},
        "Timeline of web search engines":
            {"topic": "Miscellaneous technology", "creation_month": "February 2014"},
        }


cnx = mysql.connector.connect(user='issa', database='contractwork')
cursor = cnx.cursor()
cursor.execute("""select task_receptacle,sum(payment),min(topic),min(completion_date)
               from tasks group by task_receptacle""")

ARTICLES.update({x[0]: {"payment": x[1], "topic": x[2],
                        "creation_month": x[3].strftime("%B %Y")}
                 for x in cursor.fetchall()})

PRINCIPAL_CONTRIBUTORS = {}
cursor.execute("""select task_receptacle, worker, sum(payment) from tasks
                  group by task_receptacle, worker""")
for task_receptacle, worker, total_payment in cursor.fetchall():
    if task_receptacle not in PRINCIPAL_CONTRIBUTORS:
        PRINCIPAL_CONTRIBUTORS[task_receptacle] = []
    PRINCIPAL_CONTRIBUTORS[task_receptacle].append((worker, total_payment))

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


def dictionary_ordering(x):
    """Sorting key as a string would be ordered in an English dictionary."""
    # Strip out the "the" from the beginning of page names
    for prefix in ["timeline of the ", "timeline of "]:
        if x.lower().startswith(prefix):
            x = x[len(prefix):]
            break

    return "".join(char for char in x.lower() if char.isalpha())


def payment(pagename):
    return round(ARTICLES.get(pagename, {"payment": 0.0}).get("payment", 0.0), 2)


def topic(pagename):
    if pagename in ARTICLES:
        return ARTICLES[pagename]["topic"]
    return ""


def creation_month(pagename):
    # These are timelines where the initial work took place without payment,
    # but then paid work took place for updates. In these cases, the first
    # payment date is misleading so we override them.
    overrides = {
            "Timeline of Airbnb": "August 2014",
            "Timeline of Facebook": "July 2010",
            "Timeline of GitHub": "July 2016",
            "Timeline of Pinterest": "August 2014",
            "Timeline of Snapchat": "September 2014",
            "Timeline of Twitter": "January 2014",
            }
    if pagename in overrides:
        return overrides[pagename]

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
        logging.info("QUERY: ON ITERATION %s, SLEEPING FOR %s", iteration, sleep)
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


def wp_pageviews(pagename):
    """
    Get monthly Wikipedia pageviews data for pagename.
    """
    # creation_month is used to find out what months to get the pageviews data
    # for
    cm = creation_month(pagename)
    # If the page isn't done, it won't be on Wikipedia so don't bother getting
    # pageviews
    if not cm:
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

    logging.info("Querying Wikipedia pageviews for %s", pagename)
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

def last_modified_month(pagename):
    """Find the most recent month in which the page was modified, according to
    the last edit date on the page (so even minor typo fixes can bump the
    date)."""
    payload = {
            "action": "query",
            "prop": "revisions",
            "titles": pagename,
            "rvprop": "timestamp",
            "rvlimit": 1,
            "rvdir": "older",  # confusingly, "older" gets the most recent revisions first
            "format": "json",
            }
    logging.info("Querying last modified month for %s", pagename)
    r = requests.get("https://timelines.issarice.com/api.php", params=payload)
    result = r.json()
    return dateutil.parser.parse(list(result['query']['pages'].values())[0]['revisions'][0]['timestamp']).strftime("%B %Y")


def number_of_rows(pagename):
    payload = {
        "action": "parse",
        "page": pagename,
        "format": "json",
    }

    logging.info("Querying number of rows for %s", pagename)
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

def write_csv(csvfile):
    writer = csv.DictWriter(csvfile, fieldnames=util.fieldnames)
    writer.writeheader()
    for pagename in sorted(pagename_generator(), key=dictionary_ordering):
        row_dict = {'pagename': pagename,
                    'topic': topic(pagename),
                    'creation_month': creation_month(pagename),
                    'last_modified_month': last_modified_month(pagename),
                    'number_of_rows': number_of_rows(pagename),
                    'payment': payment(pagename),
                    'monthly_pageviews': ga_pageviews(pagename),
                    'monthly_wikipedia_pageviews': int(wp_pageviews(pagename))}
        if pagename in PRINCIPAL_CONTRIBUTORS:
            contributors = list(sorted(PRINCIPAL_CONTRIBUTORS[pagename],
                                       key=lambda x: x[1],
                                       reverse=True))
            row_dict['principal_contributors_by_amount'] = ", ".join(
                    worker for worker, _ in contributors)
            row_dict['principal_contributors_by_amount_html'] = ", ".join(
                    '<span title="%s">%s</span>' % ("$" + str(payment), worker)
                    for worker, payment in contributors)
            contributors = list(sorted(PRINCIPAL_CONTRIBUTORS[pagename],
                                       key=lambda x: x[0]))
            row_dict['principal_contributors_alphabetical'] = ", ".join(
                    worker for worker, _ in contributors)
        else:
            row_dict['principal_contributors_by_amount'] = ""
            row_dict['principal_contributors_alphabetical'] = ""
            row_dict['principal_contributors_by_amount_html'] = ""
        writer.writerow(row_dict)


if __name__ == "__main__":
    write_csv(sys.stdout)
