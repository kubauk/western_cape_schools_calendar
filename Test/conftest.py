import os.path
from typing import AnyStr

import bs4
from _pytest.fixtures import fixture

TEST_DIRECTORY: AnyStr = os.path.dirname(os.path.realpath(__file__))


@fixture
def test_file_soup():
    def open_file_as_soup(filename: AnyStr):
        file_path = os.path.join(TEST_DIRECTORY, filename)
        with open(file_path, "r") as in_file:
            soup = bs4.BeautifulSoup(in_file, "html.parser")
            return soup
    return open_file_as_soup
