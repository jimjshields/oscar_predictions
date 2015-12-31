# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import helpers
import pandas as pd

AWARDS_URLS = {
    'dga': 'https://en.wikipedia.org/wiki/Directors_Guild_of_America_Award_for_Outstanding_Directing_%E2%80%93_Feature_Film',
    'pga_theatrical': 'https://en.wikipedia.org/wiki/Producers_Guild_of_America_Award_for_Best_Theatrical_Motion_Picture',
    'sag_ensemble': 'https://en.wikipedia.org/wiki/Screen_Actors_Guild_Award_for_Outstanding_Performance_by_a_Cast_in_a_Motion_Picture'
}
WINNER_BACKGROUND = 'background:#B0C4DE;'
EXTRA_CHARS = [u'\u2020', u'\u2021']
CSV_BASE_FILENAME = 'wiki_noms.csv'


def export_all_nominee_info_to_csv():
    all_info = []
    for awards in AWARDS_URLS:
        awards_nominee_info = get_nominee_info_from_tables(awards)
        all_info.extend(awards_nominee_info)
    df = pd.DataFrame(all_info)
    df.to_csv(CSV_BASE_FILENAME, encoding='utf-8')


def get_nominee_info_from_tables(awards):
    awards_url = AWARDS_URLS[awards]
    table_elements = _get_nominee_tables(awards_url)
    compiled_tables = map(lambda t: _compile_table(t, awards), table_elements)
    all_nominee_info = []
    for c_t in compiled_tables:
        all_nominee_info.extend(c_t)
    return all_nominee_info


def _compile_table(table_el, awards):
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
                'awards': awards,
                'url': AWARDS_URLS[awards],
                'year': year,
                'film': _format_name(info_columns[0]),
                'winner(s)': _format_name(info_columns[1]),
                'is_winner': _is_winner(info_columns)
            }
            data.append(row_info)
    return data


def _is_header_row(row):
    return len(row.find_all('td')) == 0


def _is_first_row(row):
    return len(row.find_all('td')) > 2


def _get_year_from_first_row(row):
    return row.find_all('td')[0].text.strip()


def _format_name(column):
    column_text = column.text
    for char in EXTRA_CHARS:
        column_text = column_text.replace(char, '')
    return column_text.strip()


def _is_winner(info_columns):
    """Check the columns to determine if the row is the winner of the given year."""

    first_col_style = info_columns[0].attrs.get('style')
    return first_col_style == WINNER_BACKGROUND


def _get_nominee_tables(url):
    page_bs = helpers.get_page_beautiful_soup(url)
    nominee_tables = page_bs.find_all("table", {"class": "wikitable"})
    return nominee_tables
