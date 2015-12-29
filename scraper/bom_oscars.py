# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup


BASE_URL = 'http://www.boxofficemojo.com/oscar/chart/?view=allcategories&yr={year}&p=.htm'


class XPath(object):
    category_title = '//font[@face="Verdana"]'
    category_table = 'following-sibling::*[1][self::table]'


def _get_page_beautiful_soup(url):
    page = requests.get(url).content
    return BeautifulSoup(page, 'lxml')


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
    year_page_url = BASE_URL.format(year=year)
    year_page_bs = _get_page_beautiful_soup(year_page_url)
    all_category_title_elements = year_page_bs.find_all(_is_category_title)
    all_category_row_elements = map(lambda x: {x.text: _compile_table(x.find_next_sibling('table'))}, all_category_title_elements)
    return all_category_row_elements


def get_all_nominees():
    nominees_by_year = map(lambda x: {x: get_all_nominees_by_year(x)}, xrange(1981, 2015))
    return nominees_by_year
