import datetime
import hashlib
import logging
import sys
from logging import Logger
from typing import Final
from urllib import request

import ics
from google.cloud import storage
from extract_term_dates import extract_events_from_web_page

logger: Final[Logger] = logging.getLogger(__name__)


def uid_for(event):
    return hashlib.sha256("{}{}".format(event.description, event.date).encode("utf-8")).hexdigest() + "@WCCal"


def create_ics_for_dates(date_event_years) -> ics.Calendar:
    logger.info("Creating ICS calendar")
    ics_calendar = ics.Calendar()

    update_date = datetime.datetime.now().isoformat(" ")

    for date_year in date_event_years:
        for event in date_year:
            cal_event = ics.Event(name=event.description, begin=event.date, uid=uid_for(event))
            cal_event.description = "Calendar events were updated {}".format(update_date)
            cal_event.make_all_day()
            ics_calendar.events.add(cal_event)

    return ics_calendar


def save_to_cloud_storage(ics_calendar):
    logger.info("Saving calendar to storage")
    save_public_file_to_cloud_storage(ics_calendar, "western_cape_schools_calendar{}.ics".format(datetime.datetime.now().isoformat(" ")))
    return save_public_file_to_cloud_storage(ics_calendar, "western_cape_schools_calendar.ics")


def save_public_file_to_cloud_storage(ics_calendar, object_name):
    client = storage.Client(project="western-cape-schools-calendar")
    bucket = client.get_bucket("school_ics_calendars")
    blob = bucket.blob(object_name)
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
