import json
import time
import pymysql
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from crawler.models import ProductDetail


def get_product_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
    }

    resp = requests.get(url, headers=headers, timeout=30)

    record = {}
    soup = BeautifulSoup(resp.text, 'lxml')

    # get category information from html
    category = soup.find_all('li', itemprop='itemListElement')
    category_path = r' > '.join([cate.string for cate in category])
    record['category_path'] = category_path

    # get product name
    product_name = soup.find('h1', class_='seoDescription')
    product_name = product_name.text
    product_name = ' '.join(product_name.split())
    record['name'] = product_name

    # get currency
    if soup.find('meta', itemprop='priceCurrency'):
        currency = soup.find('meta', itemprop='priceCurrency')
        currency = currency['content']
        record['currency'] = currency
    else:
        record['currency'] = None

    # get price
    price = soup.find_all('span', itemprop='price')
    if price:
        price = price[0].text
    else:
        price = 0
    record['price'] = price

    # get discount_price
    tag_price = soup.select('div.contPrice del')
    if tag_price:
        tag_price = tag_price[0].string.strip().split()[1]
    else:
        tag_price = 0
    record['tag_price'] = tag_price

    # get discount_rate
    discount_rate = soup.find('span', class_='sconto')
    if discount_rate:
        discount_rate = discount_rate.string.strip()
    else:
        discount_rate = 0

    record['discount_rate'] = discount_rate

    # get ean sku and sellerName
    for line in resp.iter_lines():
        if line.decode().strip().startswith('"ean"'):
            line = line.decode().strip()
            line = line.replace('"', '')
            line_ls = line.split()

            if len(line_ls[2]) > 4:
                ean = line_ls[2]
                record['ean'] = ean
            else:
                pass
        elif line.decode().strip().startswith('var _sku'):
            line = line.decode().strip().replace("'", '').split()
            sku = line[3].strip(';')
            record['sku'] = sku

        elif line.decode().strip().startswith('var _sellerName'):
            line = line.decode().strip().replace('"', '').split()
            sellerName = line[3].strip(';')
            record['seller_name'] = sellerName
        else:
            pass
    return record


def crawle_job(urls):
    for url in urls:
        print(url.href)
        result = get_product_info(url.href)
        record = ProductDetail.objects.filter(ean=result['ean'])
        if record:
            update_time = timezone.now()
            result['update_time'] = update_time
            record.update(**result)
        else:
            result['product_url'] = url
            ProductDetail.objects.create(**result)
    return None


if __name__ == '__main__':
    db_info = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'wj@2018',
    }

    try:
        conn = pymysql.connect(**db_info)
        cursor = conn.cursor()
    except Exception as e:
        print(e)

    sql = """insert into example.crawler_productdetail (`ean`,`sku`,`name`,`seller_name`,`category_path`,`currency`,`price`,
    `tag_price`,`discount_rate`) values (%(ean)s,%(sku)s,%(name)s,%(seller_name)s,%(category_path)s,%(currency)s,%(price)s,%(tag_price)s,%(discount_rate)s)
    """

    with open('urls.txt', 'r') as f:
        for line in f:
            print(line.strip())
            record = get_product_info(line.strip())
            cursor.execute(sql, record)
            conn.commit()
    cursor.close()
    conn.close()
