from urllib import request

import ics
from google.cloud import storage

from extract_term_dates import extract_events_from_web_page


def create_ics_for_dates(date_event_years) -> ics.Calendar:
    ics_calendar = ics.Calendar()

    for date_year in date_event_years:
        for event in date_year:
            cal_event = ics.Event(name=event.description, begin=event.date)
            cal_event.make_all_day()
            ics_calendar.events.add(cal_event)

    return ics_calendar


def save_to_cloud_storage(ics_calendar):
    client = storage.Client(project="western-cape-schools-calendar")
    bucket = client.get_bucket("school_ics_calendars")
    blob = bucket.blob("western_cape_schools_calendar.ics")
    blob.upload_from_string(ics_calendar.serialize())


def main():
    date_event_years = extract_events_from_web_page(
        request.urlopen("https://wcedonline.westerncape.gov.za/school-calendar-and-public-holidays"))

    ics_calendar = create_ics_for_dates(date_event_years)

    save_to_cloud_storage(ics_calendar)


if __name__ == "__main__":
    main()
