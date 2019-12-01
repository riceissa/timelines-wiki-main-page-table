#!/usr/bin/env python3

import csv

def print_table():
    print("<!-- WARNING:")
    print("Do not manually edit this table. This table is produced using\n"
          "an automated script. The script does not check for manual changes\n"
          "to the table, so any changes you make will be overwritten the next\n"
          "time the script runs. The script automatically finds all pages on\n"
          "the wiki starting with \"Timeline of\" so any timeline you write will\n"
          "automatically be included in the table the next time the script\n"
          "runs. For more information, see the script repository at\n"
          "https://github.com/riceissa/timelines-wiki-main-page-table")
    print('-->{| class="sortable wikitable"')
    print("|-")
    print("! Timeline subject")
    print("! Focus area")
    print("! Creation month")
    print("! Last modification month")
    print('! data-sort-type="number" | Number of rows')
    print('! data-sort-type="number" | Total payment')
    print('! data-sort-type="number" | Monthly pageviews')
    print('! data-sort-type="number" | Monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Principal contributors')

    for pagename in sorted(pagename_generator(), key=dictionary_ordering):
        print("|-")
        print("| [[" + pagename + "|" + page_display_name(pagename)
              + "]]")
        print("| " + topic(pagename) if topic(pagename) else "|")
        if not creation_month(pagename):
            print("| Not yet complete")
        else:
            print("| {{dts|" + creation_month(pagename) + "}}")
        print("| {{dts|" + last_modified_month(pagename) + "}}")
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
        wp_pv = int(wp_pageviews(pagename))
        if wp_pv > 0:
            print('| style="text-align:right;" | [{} {}]'.format(
                "https://wikipediaviews.org/displayviewsformultiplemonths.php?page={}&allmonths=allmonths&language=en&drilldown=human" \
                        .format(urllib.parse.quote_plus(pagename)),
                str(wp_pv)
                ))
        else:
            print('| Not on Wikipedia')
        try:
            contributors = list(sorted(PRINCIPAL_CONTRIBUTORS[pagename],
                                       key=lambda x: x[1],
                                       reverse=True))
            print('| ' + ", ".join('<span title="%s">%s</span>' % ("$" + str(payment), worker)
                                   for worker, payment in contributors))
        except KeyError:
            print('|')
    print("|}")


if __name__ == "__main__":
    print_table()
