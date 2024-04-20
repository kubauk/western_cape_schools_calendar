import datetime
import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Final, List, Sequence, AnyStr

import bs4


@dataclass
class TermEvent:
    description: str
    date: str


@dataclass
class YearAndTable:
    year: str
    table: bs4.Tag


class Section(IntEnum):
    Term = 0
    Opening = 1
    Closing = 2


TERMS: Final[List[str]] = ['First', 'Second', 'Third', 'Fourth']

YEAR_REG: Final = re.compile(r"^(?:19|20)\d{2}")


def get_calender_date(date_string: str, year: str = 2026) -> datetime.datetime:
    return datetime.datetime.strptime("{} {}".format(date_string, year), "%d %B %Y")


def list_of_text_to_tuple_of_dates(rows: Sequence[Sequence[AnyStr]], year: AnyStr) -> List[TermEvent]:
    assert len(rows) > 0
    dates: List[TermEvent] = []
    for row in rows:
        if len(row) > 0 and row[Section.Term] in TERMS:
            for section in [Section.Opening, Section.Closing]:
                possible_dates: List[AnyStr] = row[section].split("|")
                educator_version: bool = len(possible_dates) > 1

                while len(possible_dates) > 0:
                    date: AnyStr = get_calender_date(possible_dates.pop(0), year).isoformat(" ")
                    number: AnyStr = "" if not educator_version else possible_dates.pop(0)
                    opens_or_closes = "Opens" if section is Section.Opening else "Closes"
                    learners_educators_or_empty = "" if not educator_version else (
                        " for Educators" if number == "1" else " for Learners")
                    message: str = "School {}{}".format(opens_or_closes, learners_educators_or_empty)
                    dates.append(TermEvent(message, date))

    assert len(dates) > 0
    return dates


def extract_dates_from_table(soup, year: str) -> list[TermEvent]:
    found_rows: list[list[str]] = list()
    for row in soup.select("tr"):
        found_columns: list[str] = list()
        for column in row.select("td"):
            found_columns.append(column.get_text(separator="|", strip=True))
        found_rows.append(found_columns)
    return list_of_text_to_tuple_of_dates(found_rows, year)


def extract_events_from_web_page(soup):
    headers = soup.find_all("h5")
    assert len(headers) > 0
    headers = filter(lambda h: "School Calendar:" in h.get_text(), headers)
    tables = map(lambda h: YearAndTable(YEAR_REG.search(h.get_text(strip=True)).group(), h.find_next("table")), headers)
    results = map(lambda y_and_t: extract_dates_from_table(y_and_t.table, y_and_t.year), tables)
    return results
