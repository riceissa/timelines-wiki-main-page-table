#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json
import requests


def full_timeline_heading(soup):
    """Find and return the "Full timeline" heading."""
    for h2 in soup.find_all("h2"):
        span = h2.find("span", {"class": "mw-headline"})
        if span and span.text == "Full timeline":
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
        "page": "Timeline of Cato Institute",
        "format": "json",
    }

    r = requests.get("https://timelines.issarice.com/api.php", params=payload)
    result = r.json()
    text = result["parse"]["text"]["*"]
    soup = BeautifulSoup(text, "lxml")
    tables = soup.find_all("table")

    # subtract one from number of rows to compensate for header row
    print(list(map(lambda t: len(t.find_all("tr")) - 1, tables)))

    # soup.find_all("h2")[1].find("span", {"class": "mw-headline"}).text
    # soup.find_all("h2")[1].next_sibling.next_sibling.next_sibling.next_sibling


    h2 = full_timeline_heading(soup)
    full_timeline = full_timeline_table(soup, h2)
    if full_timeline:
        print("Number of rows", len(full_timeline.find_all("tr")) - 1)
    else:
        print("Could not find full timeline.")
