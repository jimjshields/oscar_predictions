# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import helpers
import pandas as pd


BASE_URL_ALL_CATEGORIES = 'http://www.boxofficemojo.com/oscar/chart/?view=allcategories&yr={year}&p=.htm'
BASE_URL_PICTURE_DETAIL = 'http://www.boxofficemojo.com/oscar/chart/?view=&yr={year}&p=.htm'
EXTRA_CHARS = [u'\u2020', u'\u2021']
WINNER_BGCOLOR = '#ffff7d'
CSV_BASE_FILENAME_PICTURE_DETAILS = 'bom_noms_picture_detail.csv'


def export_all_picture_detail_info_to_csv():
    df = get_df_from_all_picture_detail()
    df.to_csv(CSV_BASE_FILENAME_PICTURE_DETAILS, encoding='utf-8')


def get_df_from_all_picture_detail():
    all_picture_details = get_all_picture_details()
    df = pd.DataFrame(all_picture_details)
    return df


def _compile_table(table_el):
    data = []
    rows = table_el.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    return data


def _is_category_title(tag):
    return tag.name == 'font' and tag.attrs.get('face') == 'Verdana'


def get_all_nominees_by_year(year):
    year_page_url = BASE_URL_ALL_CATEGORIES.format(year=year)
    year_page_bs = helpers.get_page_beautiful_soup(year_page_url)
    all_category_title_elements = year_page_bs.find_all(_is_category_title)
    all_category_row_elements = map(lambda x: {x.text: _compile_table(x.find_next_sibling('table'))}, all_category_title_elements)
    return all_category_row_elements


def get_all_nominees():
    nominees_by_year = map(lambda x: {x: get_all_nominees_by_year(x)}, xrange(1981, 2015))
    return nominees_by_year


def get_all_picture_details():
    all_picture_details = []
    for year in xrange(1981, 2015):
        picture_detail_by_year = get_picture_detail_by_year(year)
        all_picture_details.extend(picture_detail_by_year)
    return all_picture_details


def get_picture_detail_by_year(year):
    picture_detail_url = BASE_URL_PICTURE_DETAIL.format(year=year)
    picture_detail_bs = helpers.get_page_beautiful_soup(picture_detail_url)
    picture_detail_table = picture_detail_bs.find_all("table")[-1]
    table_data = _compile_picture_detail_table(picture_detail_table, year, picture_detail_url)
    return table_data


def _compile_picture_detail_table(picture_detail_table, year, picture_detail_url):
    data = []
    rows = picture_detail_table.find_all('tr')
    
    # Skip headers/summary rows.
    for row in rows[1:-3]:
        tds = row.find_all('td')
        info_columns = map(_format_name, tds)
        row_info = {
            'url': picture_detail_url,
            'year': year,
            'year_rank': info_columns[0],
            'film': info_columns[1],
            'studio': info_columns[2],
            'pre_nom_gross': info_columns[3],
            'pre_nom_num_theaters': info_columns[4],
            'post_nom_gross': info_columns[5],
            'post_nom_num_theaters': info_columns[6],
            'post_awards_gross': info_columns[7],
            'post_awards_num_theaters': info_columns[8],
            'total_gross': info_columns[9],
            'release_date': info_columns[10],
            'is_winner': _is_winner(tds)
        }
        data.append(row_info)
    return data


def _is_first_row(row):
    return len(row.find_all('td')) > 2


def _format_name(column):
    column_text = column.text
    for char in EXTRA_CHARS:
        column_text = column_text.replace(char, '')
    return column_text.strip()


def _is_winner(tds):
    """Check the columns to determine if the row is the winner of the given year."""

    first_col_bgcolor = tds[0].attrs.get('bgcolor')
    return first_col_bgcolor == WINNER_BGCOLOR
