#!/usr/bin/env python3

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
    print('! data-sort-type="text" | Principal contributors')

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
    conn = sqlite3.connect('timelines.db')
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    rows = []
    for row in reader:
        rows.append(tuple(row[field] for field in util.fieldnames))
    cursor.executemany("insert into t (" + ", ".join(util.fieldnames) + ") values (" + ",".join(["?"] * len(util.fieldnames)) + ");", rows)


    query = cursor.execute("""
        select
            principal_contributors_alphabetical,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            principal_contributors_alphabetical;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Principal contributors')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (principal_contributors, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| ' + principal_contributors)
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        # For some reason, the row number total changes from an integer to a
        # float for the blank principal contributor, even when the field is
        # explicitly set to integer in the schema. See
        # https://timelines.issarice.com/index.php?title=User:Issa/test&oldid=35031
        # for how that looks. I can't figure out why this happens, so just
        # force it to an int before printing.
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    query = cursor.execute("""
        select
            topic,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            topic;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Topic')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (topic, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| ' + topic)
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    query = cursor.execute("""
        select
            case when cast(monthly_wikipedia_pageviews as decimal) > 0 then 'yes' else 'no' end as exists_on_wikipedia,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            exists_on_wikipedia;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Exists on Wikipedia?')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (exists_on_wikipedia, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| ' + str(exists_on_wikipedia))
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    conn.commit()
    conn.close()


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
