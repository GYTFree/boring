import json
import requests
from bs4 import BeautifulSoup


def get_product_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
    }

    resp = requests.get(url, headers=headers)

    record = {}
    with open('resp.html', 'wb') as f:
        for line in resp.iter_lines(chunk_size=4):
            f.write(line)
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
    currency = soup.find('meta', itemprop='priceCurrency')
    currency = currency['content']
    record['currency'] = currency

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
        discount_price = 0
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

