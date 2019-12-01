#!/usr/bin/env python3

import pdb

import csv
import sqlite3
import urllib.parse

import util

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

    for row in reader:
        print("|-")
        print("| [[" + row['pagename'] + "|" + util.page_display_name(row['pagename'])
              + "]]")
        print("| " + row['topic'] if row['topic'] else "|")
        if not row['creation_month']:
            print("| Not yet complete")
        else:
            print("| {{dts|" + row['creation_month'] + "}}")
        print("| {{dts|" + row['last_modified_month'] + "}}")
        print('| style="text-align:right;" | ' + row['number_of_rows'])
        if float(row['payment']) > 0:
            print('| style="text-align:right;" | [{} {:.2f}]'.format(
                "https://contractwork.vipulnaik.com/tasks.php?receptacle={}&matching=exact" \
                        .format(urllib.parse.quote_plus(row['pagename'])),
                float(row['payment'])
            ))
        else:
            print('| style="text-align:right;" | 0.00')
        print('| style="text-align:right;" | ' + row['monthly_pageviews'])
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


def print_summary_tables(reader):
    cnx = sqlite3.connect(":memory:")
    cursor = cnx.cursor()
    cursor.execute("create table t (" + ", ".join(util.fieldnames) + ");")
    rows = []
    for row in reader:
        rows.append(tuple(row[field] for field in util.fieldnames))
    cursor.executemany("insert into t (" + ", ".join(util.fieldnames) + ") values (" + ",".join(["?"] * len(util.fieldnames)) + ");", rows)


    query = cursor.execute("""
        select
            principal_contributors_alphabetical,
            sum(monthly_pageviews),
            sum(monthly_wikipedia_pageviews),
            sum(number_of_rows)
        from t
        group by
            principal_contributors_alphabetical;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Principal contributors')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (principal_contributors, monthly_pageviews, monthly_wikipedia_pageviews,
         number_of_rows) = row
        print("|-")
        print('| ' + principal_contributors)
        print('| style="text-align:right;" | ' + str(monthly_wikipedia_pageviews))
        print('| style="text-align:right;" | ' + str(monthly_wikipedia_pageviews))
        print('| style="text-align:right;" | ' + str(number_of_rows))



    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    with open('front_page_table_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print_table(reader)

    # The main table can just use the CSV as given, but for the summary tables,
    # we want to import into sqlite so we can group things. So re-read the CSV
    # to import into a temporary database.
    with open('front_page_table_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print_summary_tables(reader)
