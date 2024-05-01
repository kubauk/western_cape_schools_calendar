import datetime
import logging
import sys
from logging import Logger
from typing import Final
from urllib import request

import ics
from google.cloud import storage
from extract_term_dates import extract_events_from_web_page

logger: Final[Logger] = logging.getLogger(__name__)


def create_ics_for_dates(date_event_years) -> ics.Calendar:
    logger.info("Creating ICS calendar")
    ics_calendar = ics.Calendar()

    for date_year in date_event_years:
        for event in date_year:
            cal_event = ics.Event(name=event.description, begin=event.date)
            cal_event.make_all_day()
            ics_calendar.events.add(cal_event)

    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    generated_date_event = ics.Event(name="Term Calendar Updated", begin=tomorrow, description=now.isoformat(" "))
    generated_date_event.make_all_day()
    ics_calendar.events.add(generated_date_event)

    return ics_calendar


def save_to_cloud_storage(ics_calendar):
    logger.info("Saving calendar to storage")
    client = storage.Client(project="western-cape-schools-calendar")
    bucket = client.get_bucket("school_ics_calendars")
    blob = bucket.blob("western_cape_schools_calendar.ics")
    blob.upload_from_string(ics_calendar.serialize())
    blob.make_public()
    return blob.public_url


def setup_logger_configuration():
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)


def main():
    setup_logger_configuration()
    logger.info("Started")
    date_event_years = extract_events_from_web_page(
        request.urlopen("https://wcedonline.westerncape.gov.za/school-calendar-and-public-holidays"))

    ics_calendar = create_ics_for_dates(date_event_years)

    calendar_url = save_to_cloud_storage(ics_calendar)
    logger.info("Public URL: {}".format(calendar_url))
    logger.info("Ended")


if __name__ == "__main__":
    main()
