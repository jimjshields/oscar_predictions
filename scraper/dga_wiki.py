# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import helpers
import pandas as pd


BASE_URL = 'https://en.wikipedia.org/wiki/Directors_Guild_of_America_Award_for_Outstanding_Directing_%E2%80%93_Feature_Film'
WINNER_BACKGROUND = 'background:#B0C4DE;'
EXTRA_CHARS = [u'\u2020', u'\u2021']
CSV_BASE_FILENAME = 'dga_noms.csv'


def export_nominee_info_to_csv():
    all_nominee_info = get_nominee_info_from_tables()
    df = pd.DataFrame(all_nominee_info)
    df.to_csv(CSV_BASE_FILENAME, encoding='utf-8')
    print 'DGA nominee info exported!'


def get_nominee_info_from_tables():
    table_elements = _get_nominee_tables()
    compiled_tables = map(_compile_table, table_elements)
    all_nominee_info = []
    for c_t in compiled_tables:
        all_nominee_info.extend(c_t)
    return all_nominee_info


def _compile_table(table_el):
    data = []
    rows = table_el.find_all('tr')
    year = None
    for row in rows:
        if _is_header_row(row):
            pass
        else:
            if _is_first_row(row):

                # If it's the first row, reset the year to the most recently found one.
                year = _get_year_from_first_row(row)

                # Get the remaining columns.
                info_columns = row.find_all('td')[1:]
            else:
                info_columns = row.find_all('td')
            row_info = {
                'year': year,
                'film': info_columns[0].text.strip(),
                'director': _format_director_name(info_columns),
                'winner': _is_winner(info_columns)
            }
            data.append(row_info)
    return data


def _is_header_row(row):
    return len(row.find_all('td')) == 0


def _is_first_row(row):
    return len(row.find_all('td')) > 2


def _get_year_from_first_row(row):
    return row.find_all('td')[0].text.strip()


def _format_director_name(info_columns):
    director_text = info_columns[1].text
    for char in EXTRA_CHARS:
        director_text = director_text.replace(char, '')
    return director_text.strip()


def _is_winner(info_columns):
    """Check the columns to determine if the row is the winner of the given year."""

    first_col_style = info_columns[0].attrs.get('style')
    return first_col_style == WINNER_BACKGROUND


def _get_nominee_tables():
    page_bs = helpers.get_page_beautiful_soup(BASE_URL)
    nominee_tables = page_bs.find_all("table", {"class": "wikitable"})
    return nominee_tables
