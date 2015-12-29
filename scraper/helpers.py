# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup


def get_page_beautiful_soup(url):
    page = requests.get(url).content
    return BeautifulSoup(page, 'lxml')
