import datetime
import sys

import pytest
import bs4

A_VALID_YEAR: str = "2026"


def is_valid_calender_date(possible_date: str) -> bool:
    try:
        the_date = get_calender_date(possible_date, A_VALID_YEAR)
    except ValueError:
        return False
    return the_date is not None


def get_calender_date(date_string: str, year: str) -> datetime.datetime:
    return datetime.datetime.strptime("{} {}".format(date_string, year), "%d %B %Y")


@pytest.mark.parametrize("value, expected_result",
                         [("1 March", True), ("1", False), ("1 March 2023", False), ("31 June", False),
                          ("30 June", True), ("First", False)])
def test_is_date(value: str, expected_result: str) -> None:
    assert is_valid_calender_date(value) == expected_result


def extract_dates_from_table(soup, year: str) -> None:
    text = soup.get_text(separator='\n', strip=True).splitlines()
    list_of_text_to_tuple_of_dates(text, year)


SCHOOL_OPENS = "School Opens"
SCHOOL_CLOSES = "School Closes"


def list_of_text_to_tuple_of_dates(text: list[str], year: str) -> list[tuple[str, str]]:
    assert len(text) > 0
    dates: list[tuple[str, str]] = list()
    current = SCHOOL_OPENS
    for line in text:
        if is_valid_calender_date(line):
            cal_date = get_calender_date(line, year).isoformat(sep=' ')
            dates.append((current, cal_date))
            current = SCHOOL_CLOSES if current == SCHOOL_OPENS else SCHOOL_OPENS
    return dates


@pytest.mark.parametrize("lines, dates", [
    (["2 June", "5 August"], [("School Opens", "2026-06-02 00:00:00"), ("School Closes", "2026-08-05 00:00:00")]),
    (["5 March", "23 May", "3 September", "23 December"],
     [("School Opens", "2026-03-05 00:00:00"), ("School Closes", "2026-05-23 00:00:00"), ("School Opens", "2026-09-03 00:00:00"),
      ("School Closes", "2026-12-23 00:00:00")])])
def test_list_of_text_to_tuple_of_dates(lines, dates):
    assert list_of_text_to_tuple_of_dates(lines, "2026") == dates


def test_extract_all_dates_from_sample_table() -> None:
    with open("2024 School Calendar:.html", "r") as input:
        soup = bs4.BeautifulSoup(input)
        extract_dates_from_table(soup, "2026")


def test_extract_this_years_dates() -> None:
    with open("School Calendar and Public Holidays _ Western Cape Education Department.html", "r") as input:
        soup = bs4.BeautifulSoup(input)
        headers = soup.find_all("h5")
        assert len(headers) > 0
        for header in headers:
            if "2024 School Calendar" in header.get_text():
                table = header.find_next("table")
                with open("{}.html".format(header.get_text()), "w+") as output:
                    output.write(str(table))

                assert table is not None
                print(table.get_text())

                return

    pytest.fail()


if __name__ == "__main__":
    pytest.main(sys.argv)
