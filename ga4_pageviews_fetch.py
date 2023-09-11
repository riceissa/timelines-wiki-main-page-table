#!/usr/bin/env python3

import datetime
import sys
# import mysql.connector
import time

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


# KEY_FILE_LOCATION = sys.argv[1]
KEY_FILE_LOCATION = "timelines-key.json"

LIMIT = 10000

def quote(x):
    """CSV-quote x."""
    x = x.replace('"', '""')
    return '"' + x + '"'


def main():
    client = BetaAnalyticsDataClient.from_service_account_json(KEY_FILE_LOCATION)

    # It would be ideal to use proc.pageviews_date_range in this script here,
    # because even though the GA API will just get the pageviews for the entire
    # valid period (thus it's no problem to specify a start date that is too
    # early), some pages may nevertheless get a few pageviews from before they
    # were fully created, and we ideally wouldn't want to count those
    # pageviews. However, using proc.pageviews_date_range to get the exact
    # valid range for each page's URL will require an API call for each URL and
    # I haven't done the math to see if GA API's usage limits allow this.  But
    # in any case, a page shouldn't be getting too many pageviews before it's
    # been marked as created (since logged in views don't count), so doing
    # things the easy way should not overestimate pageviews by very much (and
    # if a page is more than a year old, will yield identical results).
    today = datetime.date.today()
    start_date = max(datetime.date(today.year - 1, today.month, 1),
                     datetime.date(2023, 5, 1))
    # Stop getting pageviews at the last day of the previous month
    end_date = datetime.date(today.year, today.month, 1) - \
            datetime.timedelta(days=1)

    pageviews = pageviews_for_project(client, "364967470",
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    print("page_path,pageviews")
    for row in pageviews:
        path, views = row
        print(f"{quote(path)},{views}")


def get_report(client, property_id, start_date, end_date, offset=0):
    """Queries the Google Analytics 4 Data API v1."""
    print("Doing PropertyID=%s [%s, %s] (offset: %s)" % (
                property_id, start_date, end_date, offset), file=sys.stderr)

    # For pagination, see
    # https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePathPlusQueryString")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        offset=offset,
        limit=LIMIT,
    )
    response = client.run_report(request)
    return response


def extracted_pageviews(response):
    """Extract the GA response into a list of tuples containing pageviews data,
    e.g. [('/wiki/Timeline_of_ChatGPT', 2201),
          ('/wiki/Timeline_of_online_food_delivery', 1189),
          ('/wiki/Timeline_of_OpenAI', 659), ...]."""
    result = []
    for row in response.rows:
        dimensions = row.dimension_values  # the pagepath
        pagepath = dimensions[0].value
        pageviews_values = row.metric_values
        assert len(pageviews_values) == 1, pageviews_values
        pageviews = int(pageviews_values[0].value)
        result.append((pagepath, pageviews))
    return result


def pageviews_for_project(client, property_id, start_date, end_date):
    result = []
    if start_date > end_date:
        # This means we already have all the most recent data, so don't query
        return result

    offset = 0
    while True:
        time.sleep(1)
        response = get_report(client, property_id, start_date,
                              end_date, offset)
        result.extend(extracted_pageviews(response))
        offset += LIMIT
        if offset >= response.row_count:
            # The comparison >= is the correct one here (not >) because
            # the first row is considered row 0 according to
            # https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport#body.request_body.FIELDS.offset
            # So e.g. if there are five rows, they will be rows 0,1,2,3,4, and
            # if offset is >=5 then there will be no more rows to fetch. (I
            # also empirically checked that this is the actual behavior of the
            # API.)
            break
    return result


if __name__ == "__main__":
    main()
