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


def extract_dates_from_table(soup, year: str) -> list[TermEvent]:
    found_rows: list[list[str]] = list()
    for row in soup.select("tr"):
        found_columns: list[str] = list()
        for column in row.select("td"):
            found_columns.append(column.get_text(separator="|", strip=True))
        found_rows.append(found_columns)
    return list_of_text_to_tuple_of_dates(found_rows, year)


def list_of_text_to_tuple_of_dates(rows: Sequence[Sequence[AnyStr]], year: AnyStr) -> List[TermEvent]:
    assert len(rows) > 0
    dates: List[TermEvent] = []
    for row in rows:
        if len(row) > 0 and row[Section.Term] in TERMS:
            for section in [Section.Opening, Section.Closing]:
                possible_dates: List[AnyStr] = row[section].split("|")
                if len(possible_dates) > 1:
                    while len(possible_dates) > 0:
                        date: AnyStr = get_calender_date(possible_dates.pop(0), year).isoformat(" ")
                        number: AnyStr = possible_dates.pop(0)
                        dates.append(
                            TermEvent("School {} for {}".format("Opens" if section is Section.Opening else "Closes",
                                                                           "Educators" if number == "1" else "Learners"),
                                      date))
                else:
                    dates.append(TermEvent("School {}".format("Opens" if section is Section.Opening else "Closes"),
                                           get_calender_date(possible_dates[0], year).isoformat(" ")))
    return dates
