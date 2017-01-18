#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import requests
from bs4 import BeautifulSoup
import logging
from .data import City, add_aqi


logger = logging.getLogger(__name__)
ORIG_AQI_SCHEMA_LIST = ['日期', 'AQI', '范围', '质量等级',
                        'PM2.5', 'PM10', 'SO2', 'CO', 'NO2', 'O3', '排名']
AQI_SCHEMA_LIST = ['date_aqi', 'avgAQI', 'range', 'severitylevel',
                   'pm2_5', 'pm10', 'so2', 'co', 'no2', 'o3', 'ranking']

SEVERITY_LV_MAPPING = {
    '优': 1,
    '良': 2,
    '轻度污染': 3,
    '中度污染': 4,
    '重度污染': 5,
    '严重污染': 6
}


def proc_range(dict_aqi):

    dict_aqi['minAQI'], dict_aqi['maxAQI'] = dict_aqi.pop('range').split('~')
    level = dict_aqi.pop('severitylevel')

    if SEVERITY_LV_MAPPING.get(level):
        dict_aqi['severitylevel'] = SEVERITY_LV_MAPPING.get(level)
    else:
        logger.warning(
            'Unknown severitylevel {} in {}'.format(level, dict_aqi))
        dict_aqi['severitylevel'] = 0
    return dict_aqi


def scrape_aqi(city='', month=''):

    url = "https://www.aqistudy.cn/historydata/daydata.php"
    payload = {'city': city, 'month': month}
    page = requests.get(url, params=payload)
    soup = BeautifulSoup(page.text, 'lxml')

    if len(soup.find_all("table", class_='table-bordered')) == 1:
        soup_table = soup.find_all("table", class_='table-bordered')[0]
        if soup_table.find_all('tr')[0].text.strip().split("\n") == \
                ORIG_AQI_SCHEMA_LIST and (len(soup_table.find_all('tr')) > 1):
            for entry in soup_table.find_all('tr')[1:]:
                values = [i.text.strip() for i in entry.find_all('td')]
                if len(values) == len(AQI_SCHEMA_LIST):
                    dict_aqi = dict(zip(AQI_SCHEMA_LIST, values))
                    dict_aqi = proc_range(dict_aqi)
                    dict_aqi['city'] = City.get(ch_name=city)
                    add_aqi(**dict_aqi)
                else:
                    logger.error(
                        "{} can't map to AQI_SCHEMA_LIST".format(values))
        else:
            logger.error(
                "ORIG_AQI_SCHEMA_LIST not found! City:{}, Month:{}.".format(city, month))

    else:
        logger.error("Table not found! City:{}, Month:{}.".format(city, month))


def test():
    scrape_aqi('上海', '2013-12')