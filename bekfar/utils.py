from urllib.request import urlopen
from bs4 import BeautifulSoup, element
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
from bekfar.products import Product
import pickle

NO_OF_PAGEDOWNS = 70


def browseAllProducts(URL, browser):
    no_of_pd = NO_OF_PAGEDOWNS
    browser.get(URL)
    time.sleep(1)
    elem = browser.find_element_by_tag_name("body")
    while no_of_pd:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        no_of_pd -= 1

    soup = BeautifulSoup(browser.page_source, "html.parser")
    return soup.find_all('div', {"class": 'product_wrap'})


def openCsvWrite(website, path):
    csvFile = open("{}/{}/all_products.csv".format(path, website), mode='w')
    writer = csv.DictWriter(csvFile, fieldnames=Product.CSV_FIELD_NAMES)
    writer.writeheader()
    return writer


# def writeExcel(siteName, path):
#     writer = pd.ExcelWriter("{}/{}/all_{}.xlsx".format(path, siteName, siteName), engine='xlsxwriter')
#     for key in URLS[siteName]:
#         df = pd.read_csv("{}/{}/{}.csv".format(path, siteName, key))
#         df.set_index('Product_ID', inplace=True)
#         df.to_excel(writer, sheet_name=key)
#     writer.close()


def writeSavedData(data, siteName, path):
    with open("{}/{}/old_data.pickle".format(path, siteName), 'wb') as file:
        pickle.dump(data, file)


def readSavedData(siteName, path):
    with open("{}/{}/old_data.pickle".format(path, siteName), 'rb') as file:
        return pickle.load(file)
