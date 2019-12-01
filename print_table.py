#!/usr/bin/env python3

import csv

def print_table(reader):
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

    # for pagename in sorted(pagename_generator(), key=dictionary_ordering):
    for row in reader:
        print("|-")
        print("| [[" + row['pagename'] + "|" + page_display_name(row['pagename'])
              + "]]")
        print("| " + row['topic'] if row['topic'] else "|")
        if not row['creation_month']:
            print("| Not yet complete")
        else:
            print("| {{dts|" + row['creation_month'] + "}}")
        print("| {{dts|" + row['last_modified_month'] + "}}")
        # n = number_of_rows(pagename)
        print('| style="text-align:right;" | ' + row['number_of_rows'])
        # p = payment(pagename)
        if row['payment'] > 0:
            print('| style="text-align:right;" | [{} {:.2f}]'.format(
                "https://contractwork.vipulnaik.com/tasks.php?receptacle={}&matching=exact" \
                        .format(urllib.parse.quote_plus(row['pagename'])),
                row['payment']
            ))
        else:
            print('| style="text-align:right;" | 0.00')
        print('| style="text-align:right;" | ' + row['monthly_pageviews'])
        # wp_pv = int(wp_pageviews(pagename))
        if int(row['monthly_wikipedia_pageviews']) > 0:
            print('| style="text-align:right;" | [{} {}]'.format(
                "https://wikipediaviews.org/displayviewsformultiplemonths.php?page={}&allmonths=allmonths&language=en&drilldown=human" \
                        .format(urllib.parse.quote_plus(row['pagename'])),
                row['monthly_wikipedia_pageviews']
                ))
        else:
            print('| Not on Wikipedia')
        try:
            print('| ' + row['principal_contributors_by_amount_html'])
        except KeyError:
            print('|')
    print("|}")


if __name__ == "__main__":
    with open('front_page_table_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print_table(reader)
