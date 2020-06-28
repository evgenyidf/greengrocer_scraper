#!/usr/bin/env python3
import pandas as pd
import re
from pathlib import Path

from bidi.algorithm import get_display
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
import csv
import json
import time

import atexit

from urllib.request import urlopen
from bs4 import BeautifulSoup, element
from bekfar.products import Product as prod
from bekfar import utils

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

OLD_DATA = {}
WEBDRIVER_PATH = r'./chromedriver'
DATA_PATH = './DATA'
browser = webdriver.Chrome(WEBDRIVER_PATH)


# CSV_FIELD_NAMES = [
#     'Product_ID',
#     'Product_Name',
#     'Description',
#     'Price',
#     'Price_Type',
#     'New_Product',
#     'Sale',
#     'Image_URL',
#     'Prace_Changed']

URLS = {
    'moshavnik': {
        'ביצים':           'https://www.moshavnik.co.il/%D7%91%D7%99%D7%A6%D7%99%D7%9D?up',
        'ירקות_גינה':      'https://www.moshavnik.co.il/store/veg-garden?up',
        'ירק':            'https://www.moshavnik.co.il/store/veg1?up',
        'פרות':            'https://www.moshavnik.co.il/store/fruits01?up',
        'לקט':            'https://www.moshavnik.co.il/kaluf?up',
        'פיטריות':          'https://www.moshavnik.co.il/%D7%A4%D7%98%D7%A8%D7%99%D7%95%D7%AA?up',
        'תבלינים':         'https://www.moshavnik.co.il/%D7%AA%D7%91%D7%9C%D7%99%D7%A0%D7%99%D7%9D?up',
        'פיצוחים_לא_קלוי':  'https://www.moshavnik.co.il/%D7%9C%D7%90_%D7%A7%D7%9C%D7%95%D7%99?up',
        'פיצוחים_קלוי':     'https://www.moshavnik.co.il/%D7%A4%D7%99%D7%A6%D7%95%D7%97%D7%99%D7%9D?up',
        'פירות_יבשים':      'https://www.moshavnik.co.il/%D7%99%D7%91%D7%A9%D7%99%D7%9D?up',
        'חדפעמי':         'https://www.moshavnik.co.il/%D7%97%D7%93%20%D7%A4%D7%A2%D7%9E%D7%99?up',
        'יין':             'https://www.moshavnik.co.il/drinks?up',
        'שתיה_קלה':       'https://www.moshavnik.co.il/%D7%A9%D7%AA%D7%99%D7%99%D7%94?up',
        'מתוקים':         'https://www.moshavnik.co.il/%D7%9E%D7%AA%D7%95%D7%A7%D7%99%D7%9D?up',
        'שימורים':         'https://www.moshavnik.co.il/%D7%A9%D7%99%D7%9E%D7%95%D7%A8%D7%99%D7%9D?up',
        'מעדניה_שמן':      'https://www.moshavnik.co.il/shemen?up',
        'מעדניה':          'https://www.moshavnik.co.il/store/%D7%9E%D7%A2%D7%93%D7%A0%D7%99%D7%99%D7%94?up',
        'איטלקי':          'https://www.moshavnik.co.il/italy?up',
        'מזרחי':           'https://www.moshavnik.co.il/asia?up',
        'אפיה':            'https://www.moshavnik.co.il/mtphhv?up'
        },
    'carmella': {
        'ירקות':         'https://www.carmella.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/',
        'פירות':         'https://www.carmella.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%a8%d7%90%d7%a9%d7%99/',
        'בסטה איטליה':   'https://www.carmella.co.il/product-category/%d7%91%d7%a1%d7%98%d7%94-%d7%a2%d7%95%d7%9c%d7%9e%d7%99%d7%aa/',
        'המזווה':        'https://www.carmella.co.il/product-category/%d7%94%d7%9e%d7%96%d7%95%d7%95%d7%94/',
        'מעדניית לוינסקי': 'https://www.carmella.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%99%d7%aa-%d7%9c%d7%95%d7%99%d7%a0%d7%a1%d7%a7%d7%99/',
        'למטבח שלך':   'https://www.carmella.co.il/product-category/%d7%94%d7%9e%d7%98%d7%91%d7%97-%d7%a9%d7%9c%d7%9a/',
        'גבינות-ועוד':    'https://www.carmella.co.il/product-category/%d7%92%d7%91%d7%99%d7%a0%d7%95%d7%aa-%d7%95%d7%a2%d7%95%d7%93/',
        'Bakery':       'https://www.carmella.co.il/product-category/bakery/',
        'ללא גלוטן':     'https://www.carmella.co.il/product-category/%d7%9c%d7%9c%d7%90-%d7%92%d7%9c%d7%95%d7%98%d7%9f/',
        'אורגני':        'https://www.carmella.co.il/product-category/%d7%90%d7%95%d7%a8%d7%92%d7%a0%d7%99/',
        'ילדודס':        'https://www.carmella.co.il/product-category/%d7%99%d7%9c%d7%93%d7%95%d7%93%d7%a1/',
        'משקאות':       'https://www.carmella.co.il/product-category/%d7%9e%d7%a9%d7%a7%d7%90%d7%95%d7%aa/',
        'פרחים':        'https://www.carmella.co.il/product-category/%d7%a4%d7%a8%d7%97%d7%99%d7%9d/'
    },
    'alehonline': {
        'חסות_ועלים': "https://www.alehonline.co.il/cat/5/leaves-lettuces",
        'עגבניות_ופלפלים': "https://www.alehonline.co.il/cat/62/tomatos-and-peppers",
        'ירקות_ירוקים': "https://www.alehonline.co.il/cat/63/green-vegetables",
        'עשבי_תיבול': "https://www.alehonline.co.il/cat/4/herbs",
        'שורשים_ותפוחי_אדמה': "https://www.alehonline.co.il/cat/6/roots-and-potatoes",
        'ירקות_גינה': "https://www.alehonline.co.il/cat/8/garden-vegetables",
        'בצלים_ושום': "https://www.alehonline.co.il/cat/64/onions-and-garlics",
        'פטריות': "https://www.alehonline.co.il/cat/65/mushrooms",
        'נבטים_פרחי_מאכל_ועלי_מיקרו': "https://www.alehonline.co.il/cat/68/micro-sprouts-and-flowers",
        'פירות': "https://www.alehonline.co.il/cat/66/fruits",
        'יקב_והמבשלה': "https://www.alehonline.co.il/cat/108/alcohol",
        'המאפיה': "https://www.alehonline.co.il/cat/109/beard",
        'המחלבה': "https://www.alehonline.co.il/cat/110/dairy",
        'הבד': "https://www.alehonline.co.il/cat/111/olive-oil",
        'המזווה': "https://www.alehonline.co.il/cat/112/pantry"
    },
    'noyhasade': {
        'פירות': 'https://noyhasade.co.il/product-category/%d7%94%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%a9%d7%9c-%d7%a0%d7%95%d7%99/',
        'ירקות': 'https://noyhasade.co.il/product-category/%d7%94%d7%99%d7%a8%d7%a7%d7%95%d7%aa-%d7%a9%d7%9c-%d7%a0%d7%95%d7%99/',
        'עשבי תיבול': 'https://noyhasade.co.il/product-category/%d7%a2%d7%a9%d7%91%d7%99-%d7%aa%d7%99%d7%91%d7%95%d7%9c/',
        'מהדרין': 'https://noyhasade.co.il/product-category/%d7%a2%d7%a9%d7%91%d7%99-%d7%aa%d7%99%d7%91%d7%95%d7%9c-%d7%9e%d7%94%d7%93%d7%a8%d7%99%d7%9f/',
        'המיוחדים': 'https://noyhasade.co.il/product-category/%d7%94%d7%9e%d7%99%d7%95%d7%97%d7%93%d7%99%d7%9d-%d7%a9%d7%9c-%d7%a0%d7%95%d7%99/',
        'מגשי אירוח': 'https://noyhasade.co.il/product-category/%d7%9e%d7%92%d7%a9%d7%99-%d7%9e%d7%a1%d7%99%d7%91%d7%95%d7%aa/',
        'המעדניה': 'https://noyhasade.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%94/',
        'שטראוס': 'https://noyhasade.co.il/product-category/strauss/'
    }
}


def getMoshavnikScraped(category, URL, path=DATA_PATH):

    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('div', {"class": 'product'})

    # item.find_parents('div', {"class": "category sales_sidebar"})[0]
    csvFile = open("{}/moshavnik/{}.csv".format(path, category), mode='w')

    writer = csv.DictWriter(csvFile, fieldnames=CSV_FIELD_NAMES)
    writer.writeheader()

    for item in all_products:
        # if len(item.findAll('div', {"class": "saleInner"})) != 0:
        if item.find_parents('div', {"class": "category sales_sidebar"}):
            continue

        product_id = item['data-id']

        product_name_block = item.findAll('div', {"class": "name-wrap"})[0]
        product_name = str(product_name_block.findAll('span', {"class": "bold"})[0].contents[0]).strip()
        if len(product_name_block.findAll('span', {"class": "bold small"})) != 0:
            product_name_extra = str(product_name_block.findAll('span', {"class": "bold small"})[0].contents[0]).strip()
        else:
            product_name_extra = ''

        product_price = item.findAll('div', {"class": "price"})[0].findAll('span', {"class": "text36 bold"})[0].contents[0].strip()
        product_price_type = item.findAll('div', {"class": "price"})[0].findAll('span', {"class": "text12"})[0].contents[0].strip()

        product_image_url = item.findAll('div', {"class": "img"})[0].findAll('img')[0]['src']

        try:
            isNew = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons04.png'))
        except:
            isNew = 0
        try:
            isForSale = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons03.png'))
        except:
            isForSale = 0

        print("name: '{}', price: '{}', type: '{}'".format(
            get_display(product_name),
            get_display(product_price),
            get_display(product_price_type)))

        row = {
            'Product_ID': product_id,
            'Product_Name': get_display(product_name),
            'Description': get_display(product_name_extra),
            'Price': product_price,
            'Price_Type': product_price_type,
            'New_Product': isNew,
            'Sale': isForSale,
            'Image_URL': product_image_url,
            'Prace_Changed': ''}

        writer.writerow(row)
    csvFile.close()


def getAlehonlineScraped(category, URL, path=DATA_PATH):
    csvFile = open("{}/alehonline/{}.csv".format(path, category), mode='w')

    writer = csv.DictWriter(csvFile, fieldnames=CSV_FIELD_NAMES)
    writer.writeheader()

    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('a', {"class": 'prodLink'})

    for item in all_products:
        product_id = re.search('.*/([0-9]+)/.*', item['href']).group(1)
        product_block = item.find_parent()

        product_name = product_block.findAll('div', {"class": "prodPrice"})[0].contents[0]
        try:
            product_name_extra = product_block.findAll('span', {"class": "amDesc"})[0].contents[0].strip().replace('(', '').replace(')', '')
        except:
            product_name_extra = ''
        product_price = product_block.findAll('div', {"class": "prodName"})[0].contents[0].strip().replace('₪', '')

        product_price_type = product_block.findAll('span')[0].contents[0]

        product_image_url = "https://www.alehonline.co.il/{}".format(product_block.findAll('img')[0]['src'])

        try:
            isNew = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons04.png'))
        except:
            isNew = 0
        try:
            isForSale = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons03.png'))
        except:
            isForSale = 0

        print("name: '{}', price: '{}', type: '{}'".format(
            get_display(product_name),
            get_display(product_price),
            get_display(product_price_type)))

        row = {
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Description': product_name_extra,
            'Price': product_price,
            'Price_Type': product_price_type,
            'New_Product': isNew,
            'Sale': isForSale,
            'Image_URL': product_image_url,
            'Prace_Changed': ''}

        writer.writerow(row)
    csvFile.close()


def getNoyhasadeScraped(category, URL, path=DATA_PATH):
    global NO_OF_PAGEDOWNS
    global OLD_DATA

    csvFile = open("{}/noyhasade/{}.csv".format(path, category), mode='w')
    writer = csv.DictWriter(csvFile, fieldnames=CSV_FIELD_NAMES)
    writer.writeheader()

    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('li', {"class": 'product'})

    for item in all_products:
        isNew = 0
        isForSale = 0
        product_name_extra = ''
        product_id = item.findAll('product_archive')[0][':product_id']

        try:
            if type(item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]) is element.NavigableString:
                product_name = item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]
        except:
            product_name = item.findAll('h2')[0].contents[0]
            product_name_extra = item.findAll('p')[0].contents[0]

        try:
            product_name_extra = item.findAll('div', {"class": "description"})[0].findAll('p')[0].contents[0]
        except:
            None

        price_data = json.loads(item.findAll('product_archive')[0][':product_variations'])
        # products that doesn't have few units
        if type(price_data) is str:
            search = re.search('^([0-9.]+) .*class=.*\>(.*)\<.*', price_data)
            # when search is problematic and we have deleted price with new one
            try:
                product_price = search.group(1)
            except:
                search = re.search('.*span>([0-9.]+)<\/span><\/del>.*span>([0-9.]+).*', price_data)
                product_price = search.group(2)
                isForSale = 1
                product_price_type = ''
            if search.group(2) is '':
                product_price_type = "לק״ג"
            else:
                product_price_type = search.group(2)
        # products that have few units
        elif type(price_data) is dict:
            for key in price_data:
                try:
                    search = re.search('.*span\>([0-9.]+).*for_kilo.*>(.*)\<.*', price_data[key]['display_price'])
                    product_price = search.group(1)
                    product_price_type = search.group(2)
                except:
                    product_price = price_data[key]['price']
                    product_price_type = price_data[key]['name']
                break

        try:
            if type(item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]) is element.Tag:
                product_name = item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]['title']
                product_image_url = item.findAll('div', {"class": "thumb"})[0].contents[0].findAll()[0]['src']
            else:
                product_image_url = item.findAll('div', {"class": "thumb"})[0].contents[0]['src']
        except:
            product_name = item.findAll('h2')[0].contents[0]
            product_name_extra = item.findAll('p')[0].contents[0]
            try:
                product_image_url = item.findAll('div', {"class": "thumb"})[0].contents[0]['src']
            except:
                product_image_url = item.findAll('div', {"class": "thumb"})[0].contents[0].findAll('img')[0]['src']

        print("id: {}, name: '{}', description: {}, price: '{}', type: '{}', {}, {}, {}".format(
            product_id,
            get_display(product_name),
            get_display(product_name_extra),
            get_display(str(product_price)),
            get_display(product_price_type),
            isNew, isForSale, product_image_url))

        row = {
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Description': product_name_extra,
            'Price': product_price,
            'Price_Type': product_price_type,
            'New_Product': isNew,
            'Sale': isForSale,
            'Image_URL': product_image_url,
            'Prace_Changed': ''}

        writer.writerow(row)
    csvFile.close()


def getCarmellaScraped(category, URL, path=DATA_PATH):
    writer = utils.openCsvWrite('carmella', path)
    all_products = utils.browseAllProducts(URL, browser)

    for item in all_products:
        product = prod(item['data-product-id'])
        product_block = item.find_all('div', {"class": 'prod_bottom'})[0]
        product.name = product_block.find_all('h3', {"class": 'pr_title'})[0].contents[0]
        product.category = category
        product.sub_category = item.find_parents('div', {"class": 'subcat_with_items'})[0]['name']
        product.price = product_block.find_all('span', {"class": 'pr_price'})[0].contents[0].strip()
        product.unit_type = product_block.find_all('span', {"class": 'pr_price_kilo'})[0].contents[0].replace('/', '').strip()

        if (len(product_block.find_all('span', {"class": 'pr_title_sale'})) or
                len(product_block.find_all('span', {"class": 'pr_price_old'}))):
            product.isForSale = True

        if len(product_block.find_all('span', {"class": 'pr_title_note'})):
            product.description = product_block.find_all('span', {"class": 'pr_title_note'})[0].contents[0]

        if len(item.find_all('div', {"class": 'product_img'})):
                product.image = item.find_all('div', {"class": 'product_img'})[0].find_all('img')[0]['data-src']

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]

        print(product.to_csv())
        writer.writerow(product.to_csv())
    # writer.close()


def closeAll():
    browser.close()


if __name__ == "__main__":
    atexit.register(closeAll)

    siteURLS = URLS['carmella']
    OLD_DATA = utils.readSavedData('carmella', path=DATA_PATH)
    for category in siteURLS:
        print('Starting: {}'.format(category))
        getCarmellaScraped(category, siteURLS[category])
    # utils.writeExcel('carmella', DATA_PATH)
    # utils.writeSavedData('carmella', path=DATA_PATH)

    # for key in URLS:
    #     Path("{}/{}".format(DATA_PATH, key)).mkdir(parents=True, exist_ok=True)

    # siteURLS = URLS['moshavnik']
    # for key in siteURLS:
    #     getMoshavnikScraped(key, siteURLS[key])
    # writeExcel("moshavnik", DATA_PATH)

    # siteURLS = URLS['alehonline']
    # for key in siteURLS:
    #     getAlehonlineScraped(key, siteURLS[key])
    # writeExcel("alehonline", DATA_PATH)

    # siteURLS = URLS['noyhasade']
    # for key in siteURLS:
    #     getNoyhasadeScraped(key, siteURLS[key])
    # writeExcel("noyhasade", DATA_PATH)


