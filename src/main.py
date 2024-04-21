from urllib import request

import ics

from extract_term_dates import extract_events_from_web_page


def create_ics_for_dates(date_event_years):
    cal = ics.Calendar()

    for date_year in date_event_years:
        for event in date_year:
            cal_event = ics.Event(name=event.description, begin=event.date)
            cal_event.make_all_day()
            cal.events.add(cal_event)


def main():
    date_event_years = extract_events_from_web_page(
        request.urlopen("https://wcedonline.westerncape.gov.za/school-calendar-and-public-holidays"))

    create_ics_for_dates(date_event_years)


if __name__ == "__main__":
    main()
