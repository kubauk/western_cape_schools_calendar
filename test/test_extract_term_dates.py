import sys
from typing import AnyStr, Sequence

import pytest

from extract_term_dates import TermEvent, extract_dates_from_table, \
    list_of_text_to_tuple_of_dates, YEAR_REG, YearAndTable


@pytest.mark.parametrize("lines, dates", [
    ([["First", "2 June", "5 August"]],
     [TermEvent("School Opens", "2026-06-02 00:00:00"), TermEvent("School Closes", "2026-08-05 00:00:00")]),
    ([["First", "5 March", "23 May"], ["Second", "3 September", "23 December"]],
     [TermEvent("School Opens", "2026-03-05 00:00:00"), TermEvent("School Closes", "2026-05-23 00:00:00"),
      TermEvent("School Opens", "2026-09-03 00:00:00"),
      TermEvent("School Closes", "2026-12-23 00:00:00")]),
    ([["Second", "5 March|1|6 March|2", "23 May"], ["Third", "3 September", "23 December"]],
     [TermEvent("School Opens for Educators", "2026-03-05 00:00:00"),
      TermEvent("School Opens for Learners", "2026-03-06 00:00:00"),
      TermEvent("School Closes", "2026-05-23 00:00:00"),
      TermEvent("School Opens", "2026-09-03 00:00:00"),
      TermEvent("School Closes", "2026-12-23 00:00:00")]),
    ([["Third", "5 March|1|6 March|2", "23 May"], ["Fourth", "3 September", "23 December|2|24 December|1"]],
     [TermEvent("School Opens for Educators", "2026-03-05 00:00:00"),
      TermEvent("School Opens for Learners", "2026-03-06 00:00:00"),
      TermEvent("School Closes", "2026-05-23 00:00:00"),
      TermEvent("School Opens", "2026-09-03 00:00:00"),
      TermEvent("School Closes for Learners", "2026-12-23 00:00:00"),
      TermEvent("School Closes for Educators", "2026-12-24 00:00:00")])
])
def test_list_of_text_to_tuple_of_dates(lines: Sequence[Sequence[AnyStr]], dates: Sequence[TermEvent]) -> None:
    assert list_of_text_to_tuple_of_dates(lines, "2026") == dates


def test_extract_all_dates_from_sample_table(test_file_soup) -> None:
    events = extract_dates_from_table(test_file_soup("test-files/2024 School Calendar:.html"), "2026")
    assert events == [TermEvent('School Opens for Educators', '2026-01-15 00:00:00'),
                      TermEvent('School Opens for Learners', '2026-01-17 00:00:00'),
                      TermEvent('School Closes', '2026-03-20 00:00:00'),
                      TermEvent('School Opens', '2026-04-03 00:00:00'),
                      TermEvent('School Closes', '2026-06-14 00:00:00'),
                      TermEvent('School Opens', '2026-07-09 00:00:00'),
                      TermEvent('School Closes', '2026-09-20 00:00:00'),
                      TermEvent('School Opens', '2026-10-01 00:00:00'),
                      TermEvent('School Closes for Learners', '2026-12-11 00:00:00'),
                      TermEvent('School Closes for Educators', '2026-12-13 00:00:00')]


def test_extract_dates_from_webpage(test_file_soup) -> None:
    soup = test_file_soup("test-files/School Calendar and Public Holidays _ Western Cape Education Department.html")
    headers = soup.find_all("h5")
    assert len(headers) > 0
    headers = filter(lambda h: "School Calendar:" in h.get_text(), headers)
    tables = map(lambda h: YearAndTable(YEAR_REG.search(h.get_text(strip=True)).group(), h.find_next("table")), headers)
    results = map(lambda y_and_t: extract_dates_from_table(y_and_t.table, y_and_t.year), tables)
    assert next(results) == [TermEvent("School Opens for Educators", "2024-01-15 00:00:00"),
                             TermEvent("School Opens for Learners", "2024-01-17 00:00:00"),
                             TermEvent("School Closes", "2024-03-20 00:00:00"),
                             TermEvent("School Opens", "2024-04-03 00:00:00"),
                             TermEvent("School Closes", "2024-06-14 00:00:00"),
                             TermEvent("School Opens", "2024-07-09 00:00:00"),
                             TermEvent("School Closes", "2024-09-20 00:00:00"),
                             TermEvent("School Opens", "2024-10-01 00:00:00"),
                             TermEvent("School Closes for Learners", "2024-12-11 00:00:00"),
                             TermEvent("School Closes for Educators", "2024-12-13 00:00:00")]

    assert next(results) == [TermEvent("School Opens for Educators", "2025-01-13 00:00:00"),
                             TermEvent("School Opens for Learners", "2025-01-15 00:00:00"),
                             TermEvent("School Closes", "2025-03-28 00:00:00"),
                             TermEvent("School Opens", "2025-04-08 00:00:00"),
                             TermEvent("School Closes", "2025-06-27 00:00:00"),
                             TermEvent("School Opens", "2025-07-22 00:00:00"),
                             TermEvent("School Closes", "2025-10-03 00:00:00"),
                             TermEvent("School Opens", "2025-10-13 00:00:00"),
                             TermEvent("School Closes for Learners", "2025-12-10 00:00:00"),
                             TermEvent("School Closes for Educators", "2025-12-12 00:00:00")]


if __name__ == "__main__":
    pytest.main(sys.argv)
