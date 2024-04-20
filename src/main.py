from urllib import request

import bs4

from extract_term_dates import extract_events_from_web_page


def main():
    resp = request.urlopen("https://wcedonline.westerncape.gov.za/school-calendar-and-public-holidays")
    soup = bs4.BeautifulSoup(resp, "html.parser")
    dates = extract_events_from_web_page(soup)

    pass


if __name__ == "__main__":
    main()