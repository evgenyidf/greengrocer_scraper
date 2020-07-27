from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.keys import Keys
import time
import csv
from bekfar.products import Product
import pickle
from datetime import datetime

NO_OF_PAGEDOWNS = 50


def browseWithAutoLoading(URL, browser):
    no_of_pd = NO_OF_PAGEDOWNS
    browser.get(URL)
    time.sleep(1)
    elem = browser.find_element_by_tag_name("body")
    while no_of_pd:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        no_of_pd -= 1

    soup = BeautifulSoup(browser.page_source, "html.parser")
    return soup


def openCsvWrite(website, path):
    csvFile = open("{}/{}/all_products.csv".format(path, website), mode='w')
    writer = csv.DictWriter(csvFile, fieldnames=Product.CSV_FIELD_NAMES)
    writer.writeheader()
    return writer


def writeExcel(path, productList):
    date = datetime.now().strftime("%d-%m-%Y")
    writer = pd.ExcelWriter("{}/all_prices_{}.xlsx".format(path, date), engine='xlsxwriter')
    for sitename in productList:
        products = productList[sitename]
        # df = pd.read_csv("{}/{}/{}.csv".format(path, siteName, key))
        df = pd.DataFrame.from_records([p.to_dict() for p in products])
        df.set_index(Product.CSV_FIELD_NAMES[0], inplace=True)
        df.to_excel(writer, sheet_name=sitename)
    writer.close()


def writePriceData(siteName, path, products):
    data = {}
    for p in products:
        data[p.id] = p.price

    with open("{}/{}_old_price.pickle".format(path, siteName), 'wb') as file:
        pickle.dump(data, file)


def readPriceData(siteName, path):
    try:
        with open("{}/{}_old_price.pickle".format(path, siteName), 'rb') as file:
            return pickle.load(file)
    except:
        return {}


def writeAllData(path, productList):
    with open("{}/all_data.pickle".format(path), 'wb') as file:
        for sitename in productList:
            pickle.dump(sitename, file)
            pickle.dump(productList[sitename], file)


def readAllData(path):
    productList = {}
    with open("{}/all_data.pickle".format(path), 'rb') as file:
        while True:
            try:
                sitename = pickle.load(file)
                productList[sitename] = pickle.load(file)
            except EOFError:
                break
    return productList
