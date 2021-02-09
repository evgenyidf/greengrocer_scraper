#!/usr/bin/env python3
import re
import json
import atexit
from urllib.request import urlopen
from bs4 import BeautifulSoup, element
from bekfar.products import Product as prod
from bekfar import utils
from selenium import webdriver
from difflib import SequenceMatcher
from bidi.algorithm import get_display
import sys

# to avoid Hitting Maximum Recursion Depth Using Pickle
sys.setrecursionlimit(0x100000)

OLD_DATA = {}
WEBDRIVER_PATH = r'./chromedriver'
DATA_PATH = './DATA'
browser = webdriver.Chrome(WEBDRIVER_PATH)
productList = {}

heSiteName = {
    "moshavnik": 'מושבניק',
    "carmella": 'כרמלה',
    "alehonline": 'עלה הביתה',
    "noyhasade": 'נוי השדה',
    "taritari": 'טרי-טרי'
}

URLS = {
    'moshavnik': {
        'ירקות_גינה':      'https://www.moshavnik.co.il/store/veg-garden?up',
        'ירק':            'https://www.moshavnik.co.il/store/veg1?up',
        'פרות':            'https://www.moshavnik.co.il/store/fruits01?up',
        'פיטריות':          'https://www.moshavnik.co.il/%D7%A4%D7%98%D7%A8%D7%99%D7%95%D7%AA?up',
        # 'לקט':            'https://www.moshavnik.co.il/kaluf?up',
        # 'תבלינים':         'https://www.moshavnik.co.il/%D7%AA%D7%91%D7%9C%D7%99%D7%A0%D7%99%D7%9D?up',
        # 'פיצוחים_לא_קלוי':  'https://www.moshavnik.co.il/%D7%9C%D7%90_%D7%A7%D7%9C%D7%95%D7%99?up',
        # 'פיצוחים_קלוי':     'https://www.moshavnik.co.il/%D7%A4%D7%99%D7%A6%D7%95%D7%97%D7%99%D7%9D?up',
        # 'פירות_יבשים':      'https://www.moshavnik.co.il/%D7%99%D7%91%D7%A9%D7%99%D7%9D?up',
        # 'חדפעמי':         'https://www.moshavnik.co.il/%D7%97%D7%93%20%D7%A4%D7%A2%D7%9E%D7%99?up',
        # 'יין':             'https://www.moshavnik.co.il/drinks?up',
        'ביצים':           'https://www.moshavnik.co.il/%D7%91%D7%99%D7%A6%D7%99%D7%9D?up',
        # 'שתיה_קלה':       'https://www.moshavnik.co.il/%D7%A9%D7%AA%D7%99%D7%99%D7%94?up',
        # 'מתוקים':         'https://www.moshavnik.co.il/%D7%9E%D7%AA%D7%95%D7%A7%D7%99%D7%9D?up',
        'שימורים':         'https://www.moshavnik.co.il/%D7%A9%D7%99%D7%9E%D7%95%D7%A8%D7%99%D7%9D?up'
        # 'מעדניה_שמן':      'https://www.moshavnik.co.il/shemen?up',
        # 'מעדניה':          'https://www.moshavnik.co.il/store/%D7%9E%D7%A2%D7%93%D7%A0%D7%99%D7%99%D7%94?up',
        # 'איטלקי':          'https://www.moshavnik.co.il/italy?up',
        # 'מזרחי':           'https://www.moshavnik.co.il/asia?up',
        # 'אפיה':            'https://www.moshavnik.co.il/mtphhv?up'
        },
    'taritari': {
        'ירקות':         'https://tari-tari.co.il/product-category/vegetables/',
        'ירק':           'https://tari-tari.co.il/product-category/greens/',
        'פירות':         'https://tari-tari.co.il/product-category/fruits',
        'נבטים_פיטריות':   'https://tari-tari.co.il/product-category/sprouts-and-mushrooms/'
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
        'מיוחדים': "https://www.alehonline.co.il/cat/69/alehonline-specials"
        # 'יקב_והמבשלה': "https://www.alehonline.co.il/cat/108/alcohol",
        # 'המאפיה': "https://www.alehonline.co.il/cat/109/beard",
        # 'המחלבה': "https://www.alehonline.co.il/cat/110/dairy",
        # 'תבלינים':  "https://www.alehonline.co.il/cat/114/spice-market",
        # 'הבד': "https://www.alehonline.co.il/cat/111/olive-oil",
        # 'המזווה': "https://www.alehonline.co.il/cat/112/pantry"
    },
    'carmella': {
        'ירקות':         'https://www.carmella.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/',
        'פירות':         'https://www.carmella.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%a8%d7%90%d7%a9%d7%99/',
        'ביצים':             'https://www.carmella.co.il/product-category/%D7%9E%D7%A2%D7%93%D7%A0%D7%99%D7%99%D7%AA-%D7%9C%D7%95%D7%99%D7%A0%D7%A1%D7%A7%D7%99/%D7%91%D7%99%D7%A6%D7%99%D7%9D'
        # 'בסטה איטליה':   'https://www.carmella.co.il/product-category/%d7%91%d7%a1%d7%98%d7%94-%d7%a2%d7%95%d7%9c%d7%9e%d7%99%d7%aa/',
        # 'המזווה':        'https://www.carmella.co.il/product-category/%d7%94%d7%9e%d7%96%d7%95%d7%95%d7%94/',
        # 'מעדניית לוינסקי': 'https://www.carmella.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%99%d7%aa-%d7%9c%d7%95%d7%99%d7%a0%d7%a1%d7%a7%d7%99/',
        # 'למטבח שלך':   'https://www.carmella.co.il/product-category/%d7%94%d7%9e%d7%98%d7%91%d7%97-%d7%a9%d7%9c%d7%9a/',
        # 'גבינות-ועוד':    'https://www.carmella.co.il/product-category/%d7%92%d7%91%d7%99%d7%a0%d7%95%d7%aa-%d7%95%d7%a2%d7%95%d7%93/',
        # 'Bakery':       'https://www.carmella.co.il/product-category/bakery/',
        # 'ללא גלוטן':     'https://www.carmella.co.il/product-category/%d7%9c%d7%9c%d7%90-%d7%92%d7%9c%d7%95%d7%98%d7%9f/',
        # 'אורגני':        'https://www.carmella.co.il/product-category/%d7%90%d7%95%d7%a8%d7%92%d7%a0%d7%99/',
        # 'ילדודס':        'https://www.carmella.co.il/product-category/%d7%99%d7%9c%d7%93%d7%95%d7%93%d7%a1/',
        # 'משקאות':       'https://www.carmella.co.il/product-category/%d7%9e%d7%a9%d7%a7%d7%90%d7%95%d7%aa/',
        # 'פרחים':        'https://www.carmella.co.il/product-category/%d7%a4%d7%a8%d7%97%d7%99%d7%9d/'
    },
    'noyhasade': {
        'פירות': 'https://noyhasade.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%98%d7%a8%d7%99%d7%99%d7%9d/',
        'ירקות גינה': 'https://noyhasade.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/%d7%99%d7%a8%d7%a7%d7%95%d7%aa-%d7%92%d7%99%d7%a0%d7%94/',
        'חסות': 'https://noyhasade.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/%d7%97%d7%a1%d7%95%d7%aa-%d7%a0%d7%91%d7%98%d7%99%d7%9d-%d7%a2%d7%9c%d7%99%d7%9d/',
        'עשבי-תיבול': 'https://noyhasade.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/%d7%a2%d7%a9%d7%91%d7%99-%d7%aa%d7%99%d7%91%d7%95%d7%9c/',
        'עשבי-תיבול': 'https://noyhasade.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/%d7%a2%d7%a9%d7%91%d7%99-%d7%aa%d7%99%d7%91%d7%95%d7%9c/',
        'פתריות': 'https://noyhasade.co.il/product-category/%d7%99%d7%a8%d7%a7%d7%95%d7%aa/%d7%a4%d7%98%d7%a8%d7%99%d7%95%d7%aa/',
        'ביצים': 'https://noyhasade.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%94/%d7%91%d7%99%d7%a6%d7%99%d7%9d-%d7%97%d7%9c%d7%91-%d7%95%d7%92%d7%91%d7%99%d7%a0%d7%95%d7%aa/',
        'דבש': 'https://noyhasade.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%94/%d7%98%d7%97%d7%99%d7%a0%d7%94-%d7%97%d7%9c%d7%91%d7%94-%d7%a1%d7%99%d7%9c%d7%90%d7%9f-%d7%95%d7%93%d7%91%d7%a9/',
        'פיצוחים': 'https://noyhasade.co.il/product-category/%d7%94%d7%a7%d7%95%d7%9c%d7%99%d7%a0%d7%a8%d7%99%d7%94-%d7%a9%d7%9c-%d7%a0%d7%95%d7%99/%d7%a4%d7%99%d7%a6%d7%95%d7%97%d7%99%d7%9d/',
        'תבלינים': 'https://noyhasade.co.il/product-category/%d7%94%d7%a7%d7%95%d7%9c%d7%99%d7%a0%d7%a8%d7%99%d7%94-%d7%a9%d7%9c-%d7%a0%d7%95%d7%99/%d7%aa%d7%91%d7%9c%d7%99%d7%a0%d7%99%d7%9d/'
    }

}


def moshavnik(category, URL, path=DATA_PATH):
    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('div', {"class": 'product'})

    for item in all_products:
        product = prod(item['data-id'])
        if product in productList['moshavnik']:
            continue

        product_block = item.findAll('div', {"class": "name-wrap"})[0]

        product.name = str(product_block.findAll('span', {"class": "bold"})[0].contents[0]).strip()
        if len(product_block.findAll('span', {"class": "bold small"})) != 0:
            product.description = str(product_block.findAll('span', {"class": "bold small"})[0].contents[0]).strip()
        else:
            product.description = ''
        product.category = category
        # product.sub_category = item.find_parents('div', {"class": 'subcat_with_items'})[0]['name']
        product.price = item.findAll('div', {"class": "price"})[0].findAll('span', {"class": "text36 bold"})[0].contents[0].strip()
        product.unit_type = item.findAll('div', {"class": "price"})[0].findAll('span', {"class": "text12"})[0].contents[0].strip()

        try:
            product.isForSale = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons03.png'))
        except:
            None
        try:
            product.isNew = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons04.png'))
        except:
            None

        product.image = item.findAll('div', {"class": "img"})[0].findAll('img')[0]['src']

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]
            product.print_terminal()

        productList['moshavnik'].append(product)


def alehonline(category, URL, path=DATA_PATH):
    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('a', {"class": 'prodLink'})

    for item in all_products:
        product = prod(re.search('.*/([0-9]+)/.*', item['href']).group(1))
        if product in productList['alehonline']:
            continue

        product_block = item.find_parent()
        product.name = product_block.findAll('div', {"class": "prodPrice"})[0].contents[0]

        try:
            product.description = product_block.findAll('span', {"class": "amDesc"})[0].contents[0].strip().replace('(', '').replace(')', '')
        except:
            None
        product.category = category
        product.price = product_block.findAll('div', {"class": "prodName"})[0].contents[0].strip().replace('₪', '')
        product.unit_type = product_block.findAll('span')[0].contents[0]
        product.image = "https://www.alehonline.co.il/{}".format(product_block.findAll('img')[0]['src'])

        try:
            product.isNew = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons04.png'))
        except:
            None
        try:
            product.isForSale = int(item.findAll('div', {"class": "saleInner"})[0].findAll('img')[0]['src'].endswith('icons03.png'))
        except:
            None

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]
            product.print_terminal()

        productList['alehonline'].append(product)


def noyhasade_old(category, URL, path=DATA_PATH):
    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('li', {"class": 'product'})

    for item in all_products:
        product = prod(item.findAll('product_archive')[0][':product_id'])
        if product in productList['noyhasade']:
            continue

        try:
            if type(item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]) is element.NavigableString:
                product.name = item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]
        except:
            product.name = item.findAll('h2')[0].contents[0]
            product.description = item.findAll('p')[0].contents[0]
        try:
            product.description = item.findAll('div', {"class": "description"})[0].findAll('p')[0].contents[0]
        except:
            None
        product.category = category

        price_data = json.loads(item.findAll('product_archive')[0][':product_variations'])
        # products that doesn't have few units
        if type(price_data) is str:
            search = re.search('^([0-9.]+) .*class=.*\>(.*)\<.*', price_data)
            # when search is problematic and we have deleted price with new one
            try:
                product.price = search.group(1)
            except:
                search = re.search('.*span>([0-9.]+).*<\/span><\/del>.*span>([0-9.]+).*', price_data)
                product.price = search.group(2)
                product.isForSale = True
                product.unit_type = ''
            if search.group(2) == '':
                product.unit_type = "ק״ג"
            else:
                product.unit_type = search.group(2)
        # products that have few units
        elif type(price_data) is dict:
            for key in price_data:
                try:
                    search = re.search('.*span\>([0-9.]+).*for_kilo.*>(.*)\<.*', price_data[key]['display_price'])
                    product.price = search.group(1)
                    product.unit_type = search.group(2)
                except:
                    product.price = price_data[key]['price']
                    product.unit_type = price_data[key]['name']
                break

        try:
            if type(item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]) is element.Tag:
                product.name = item.findAll('h2', {"class": "woocommerce-loop-product__title"})[0].contents[0]['title']
                product.image = item.findAll('div', {"class": "thumb"})[0].contents[0].findAll()[0]['src']
            else:
                product.image = item.findAll('div', {"class": "thumb"})[0].contents[0]['src']
        except:
            product.name = item.findAll('h2')[0].contents[0]
            product.description = item.findAll('p')[0].contents[0]
            try:
                product.image = item.findAll('div', {"class": "thumb"})[0].contents[0]['src']
            except:
                product.image = item.findAll('div', {"class": "thumb"})[0].contents[0].findAll('img')[0]['src']

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]
            product.print_terminal()

        productList['noyhasade'].append(product)



def noyhasade(category, URL, path=DATA_PATH):
    browsedData = utils.browseWithAutoLoading(URL, browser)
    all_products = browsedData.find_all('div', {"class": 'product_item'})

    for item in all_products:
        product = prod(item['data-product_id'])
        if product in productList['noyhasade']:
            continue

        if len(item.find_all('div', {"class": 'prod_title'})) != 0:
            product.name = item.find_all('div', {"class": 'prod_title'})[0].contents[0].strip()
        else:
            product.name = item.find_all('h3', {"class": 'prod_title'})[0].contents[0].strip()
        product.category = category
        # product.sub_category = item.find_parents('div', {"class": 'subcat_with_items'})[0]['name']
        product.price = item['data-product_price'].strip()
        product.unit_type = item.find_all('span', {"class": 'prod_price_kilo'})[0].contents[0].strip()

        if (item['data-sale_price'] != 0):
            product.isForSale = True

        if len(item.find_all('span', {"class": 'tag'})):
            product.isNew = True


        if len(item.find_all('div', {"class": 'prod_desc'})) and item.find_all('div', {"class": 'prod_desc'})[0].text != '':
            product.description = item.find_all('div', {"class": 'prod_desc'})[0].contents[0].strip()

        if len(item.find_all('img', {"class": 'attachment-woocommerce_single'})):
                product.image = item.find_all('img', {"class": 'attachment-woocommerce_single'})[0]['src']

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]
            product.print_terminal()

        productList['noyhasade'].append(product)



def carmella(category, URL, path=DATA_PATH):
    browsedData = utils.browseWithAutoLoading(URL, browser)
    all_products = browsedData.find_all('div', {"class": 'product_wrap'})

    for item in all_products:
        product = prod(item['data-product-id'])
        if product in productList['carmella']:
            continue
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
            product.print_terminal()

        productList['carmella'].append(product)


def taritari(category, URL, path=DATA_PATH):
    soup = BeautifulSoup(urlopen(URL), 'lxml')
    all_products = soup.find_all('li', {"class": 'product'})

    for item in all_products:
        product = prod(item.findAll('li', {"class": "btn-wrap clr"})[0].contents[0]["data-product_id"])
        if product in productList['taritari']:
            continue

        product_block = item.findAll('div', {"class": "product-inner clr"})[0]
        product.name = str(product_block.findAll('li', {"class": "title"})[0].contents[0].contents[0]).strip()

        try:
            product.description = product_block.findAll('div', {"class": "yith-wcbm-badge-text"})[0].contents[0].strip()
        except:
            None

        product.category = category
        # product.sub_category = item.find_parents('div', {"class": 'subcat_with_items'})[0]['name']
        try:
            product.price = product_block.findAll('span', {"class": "woocommerce-Price-amount"})[0].contents[1].strip()
        except:
            None
        product.unit_type = item.findAll('span', {"class": "ivpa_text"})[0].contents[0].strip()
        product.image = product_block.findAll('img')[0]['src']

        if product.id in OLD_DATA and OLD_DATA[product.id] != product.price:
            product.old_price = OLD_DATA[product.id]
            product.print_terminal()

        productList['taritari'].append(product)


def closeAll():
    browser.close()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


if __name__ == "__main__":
    atexit.register(closeAll)

    for sitename in URLS:
        siteURLS = URLS[sitename]
        productList[sitename] = []
        OLD_DATA = utils.readPriceData(sitename, path=DATA_PATH)
        for category in siteURLS:
            print('{} --- {}'.format(heSiteName[sitename], category))
            method = eval(sitename)
            method(category, siteURLS[category])
        utils.writePriceData(sitename, DATA_PATH, productList[sitename])
    utils.writeExcel(DATA_PATH, productList)
    # utils.writeAllData(DATA_PATH, productList)

    # productList = {}
    # productList = utils.readAllData(DATA_PATH)

    # for tari in productList['taritari']:
    #     for msvk in productList['moshavnik']:
    #         if similar(tari.name, msvk.name) > 0.8:
    #             print("{} <--> {}".format(get_display(tari.name), get_display(msvk.name)), end='\n')
    #     for nhsd in productList['noyhasade']:
    #         if similar(tari.name, nhsd.name) > 0.8:
    #             print("{} <--> {}".format(get_display(tari.name), get_display(nhsd.name)), end='\n')
    #     for aleh in productList['alehonline']:
    #         if similar(tari.name, aleh.name) > 0.8:
    #             print("{} <--> {}".format(get_display(tari.name), get_display(aleh.name)), end='\n')
