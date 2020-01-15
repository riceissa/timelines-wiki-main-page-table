#!/usr/bin/env python3

import re

def page_display_name(pagename):
    for prefix in ["timeline of the ", "timeline of "]:
        if pagename.lower().startswith(prefix):
            return pagename[len(prefix)].upper() + pagename[len(prefix)+1:]
    m = re.match(r"(.+?) timeline of (?:the )?(.+)", pagename)
    if m:
        adj = m.group(1)
        obj = m.group(2)
        return "%s (%s)" % (obj[0].upper() + obj[1:], adj[0].lower() + adj[1:])
    return pagename


fieldnames = ['pagename', 'topic', 'creation_month', 'last_modified_month',
              'number_of_rows', 'payment', 'monthly_pageviews',
              'monthly_wikipedia_pageviews', 'principal_contributors_by_amount',
              'principal_contributors_alphabetical',
              'principal_contributors_by_amount_html']
