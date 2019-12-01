#!/usr/bin/env python3

def page_display_name(pagename):
    for prefix in ["timeline of the ", "timeline of "]:
        if pagename.lower().startswith(prefix):
            return pagename[len(prefix)].upper() + pagename[len(prefix)+1:]
    return pagename
