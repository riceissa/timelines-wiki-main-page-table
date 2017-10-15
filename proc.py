#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json
import requests
import csv
import datetime
import urllib


def pageviews(pagename, creation_month):
    """
    Get monthly pageviews data for pagename. creation_month is used to find out
    what months to get the pageviews data for.
    """
    # Start getting pageviews data from the month following the creation of the
    # page
    cd = datetime.datetime.strptime(creation_month, "%B %Y")
    if cd.month == 12:
        start = str(cd.year + 1) + "0101"
    else:
        m = str(cd.month + 1) if cd.month + 1 >= 10 else "0" + str(cd.month + 1)
        start = str(cd.year) + m + "01"
    # Stop getting pageviews at the last day of the previous month
    today = datetime.date.today()
    last_day_of_last_month = datetime.date(today.year, today.month, 1) - \
            datetime.timedelta(days=1)
    end = datetime.datetime.strftime(last_day_of_last_month, "%Y%m%d")

    url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/" + \
          "per-article/en.wikipedia.org/all-access/user/" + \
          urllib.parse.quote(pagename, safe="") + \
          "/monthly/" + start + "/" + end
    return url

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
    while tag and tag.name != "table":
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
    print("==Table of timelines==")
    print("<!-- WARNING:")
    print("Do not manually edit this table. This table is produced using")
    print("an automated script. The script does not check for manual changes")
    print("to the table, so any changes you make will be overwritten the next")
    print("time the script runs. To make manual changes, the underlying CSV")
    print("file must be edited. For more information, see the script")
    print("repository at")
    print("https://github.com/riceissa/timelines-wiki-main-page-table")
    print("-->")
    print('{| class="sortable wikitable"')
    print("! Timeline subject !! Focus area !! Creation month "
          "!! Number of rows !! Monthly pageviews !! "
          "Monthly pageviews on Wikipedia")
    with open("pages.csv", newline='') as f:
        reader = csv.DictReader(f)

        for row in reader:
            print("|-")
            print("| [[" + row['page_name'] + "|" + row['page_display_name']
                  + "]]")
            print("| " + row['focus_area'])
            if row['creation_month'] == 'Not yet complete':
                print("| Not yet complete")
            else:
                print("| {{dts|" + row['creation_month'] + "}}")
            n = number_of_rows(row['page_name'])
            print('| style="text-align:right;" | ' + str(n))
            print('| style="text-align:right;" |')  # Monthly pageviews (Google Analytics)
            print('| style="text-align:right;" |')  # Monthly pageviews on Wikipedia
        print("|}")

if __name__ == "__main__":
    print_table()
