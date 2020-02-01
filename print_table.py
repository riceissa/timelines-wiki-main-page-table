#!/usr/bin/env python3

import csv
import sqlite3
import urllib.parse
import dateutil.parser
import datetime

import util

def print_table(reader, previous_month_reader):
    previous_month_data = {}
    for row in previous_month_reader:
        previous_month_data[row['pagename']] = row['monthly_pageviews']

    print("<!-- WARNING:")
    print("Do not manually edit this table. This table is produced using\n"
          "an automated script. The script does not check for manual changes\n"
          "to the table, so any changes you make will be overwritten the next\n"
          "time the script runs. The script automatically finds all pages on\n"
          "the wiki containing \"timeline of\" in the title so any timeline you write will\n"
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
    print('! data-sort-type="number" | Percentage change in monthly pageviews')
    print('! data-sort-type="number" | Monthly pageviews on Wikipedia')
    print('! data-sort-type="text" | Principal contributors')

    for row in reader:
        number_of_rows = int(row['number_of_rows']) if row['number_of_rows'] else 0
        if number_of_rows > 10 or float(row['payment']) > 0:
            print("|-")
            print("| [[" + row['pagename'] + "|" + util.page_display_name(row['pagename'])
                  + "]]")
            print("| " + row['topic'] if row['topic'] else "|")
            if not row['creation_month']:
                print("| Not yet complete")
            else:
                print("| {{dts|" + row['creation_month'] + "}}")
            print("| {{dts|" + row['last_modified_month'] + "}}")
            print('| style="text-align:right;" | ' + str(number_of_rows))
            if float(row['payment']) > 0:
                print('| style="text-align:right;" | [{} {:.2f}]'.format(
                    "https://contractwork.vipulnaik.com/tasks.php?receptacle={}&matching=exact" \
                            .format(urllib.parse.quote_plus(row['pagename'])),
                    float(row['payment'])
                ))
            else:
                print('| style="text-align:right;" | 0.00')
            print('| style="text-align:right;" | ' + row['monthly_pageviews'])
            curr_month_pageviews = int(row['monthly_pageviews'])
            prev_month_pageviews = int(previous_month_data.get(row['pagename'], 0))
            if prev_month_pageviews > 0:
                percentage_change = (curr_month_pageviews - prev_month_pageviews) / prev_month_pageviews * 100
            elif curr_month_pageviews > 0:
                percentage_change = 1000.0
            else:
                percentage_change = 0.0
            if percentage_change > 0:
                print('| style="text-align:right;" | +{:.0f}%'.format(percentage_change))
            else:
                print('| style="text-align:right;" | {:.0f}%'.format(percentage_change))
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


    # Group by principal contributors
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


    # Group by topic
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


    # Group by whether a page exists on Wikipedia
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


    # Group by creation month
    query = cursor.execute("""
        select
            creation_month,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            creation_month;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Creation month')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    rows = sorted([row for row in query], key=lambda x: month_order(x[0]))
    for row in rows:
        (creation_month, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| {{dts|' + str(creation_month) + '}}')
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    # Group by last modification month
    query = cursor.execute("""
        select
            last_modified_month,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            last_modified_month;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Last modification month')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    rows = sorted([row for row in query], key=lambda x: month_order(x[0]))
    for row in rows:
        (last_modified_month, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| {{dts|' + str(last_modified_month) + '}}')
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    # Group by creation year
    query = cursor.execute("""
        select
            substr(creation_month, -4) as creation_year,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            creation_year;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Creation year')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (creation_year, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| ' + str(creation_year))
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    # Group by last modification year
    query = cursor.execute("""
        select
            substr(last_modified_month, -4) as last_modified_year,
            count(*) as num_timelines,
            sum(monthly_pageviews) as sum_views,
            sum(monthly_wikipedia_pageviews) as sum_wp_views,
            sum(number_of_rows) as sum_row_num
        from t
        group by
            last_modified_year;""")
    print('{| class="sortable wikitable"')
    print("|-")
    print('! Last modification year')
    print('! data-sort-type="number" | Number of timelines')
    print('! data-sort-type="number" | Total monthly pageviews')
    print('! data-sort-type="number" | Total monthly pageviews on Wikipedia')
    print('! data-sort-type="number" | Total number of rows')
    for row in query:
        (last_modified_year, num_timelines, sum_views, sum_wp_views, sum_row_num) = row
        print("|-")
        print('| ' + str(last_modified_year))
        print('| style="text-align:right;" | {:,}'.format(num_timelines))
        print('| style="text-align:right;" | {:,}'.format(sum_views))
        print('| style="text-align:right;" | {:,}'.format(sum_wp_views))
        print('| style="text-align:right;" | {:,}'.format(int(sum_row_num)))
    print("|}")


    conn.commit()
    conn.close()


def month_order(month_string):
    try:
        return dateutil.parser.parse(month_string)
    except ValueError:
        # Return a date older than any of our timeline creation dates, so that
        # the blank row appears on top
        return datetime.datetime(2000, 1, 1)


if __name__ == "__main__":
    with open('front_page_table_data.csv', newline='') as csvfile, open('previous_month_front_page_table_data.csv', newline='') as previous_month_csvfile:
        reader = csv.DictReader(csvfile)
        previous_month_reader = csv.DictReader(previous_month_csvfile)
        print_table(reader, previous_month_reader)

    # The main table can just use the CSV as given, but for the summary tables,
    # we want to import into sqlite so we can group things. So re-read the CSV
    # to import into a temporary database.
    with open('front_page_table_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print_summary_tables(reader)
