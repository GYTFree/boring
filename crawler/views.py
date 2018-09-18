from django.shortcuts import render, HttpResponse
from crawler.models import ProductUrl, ProductDetail
from crawler.crawler import get_product_info, get_urls


# Create your views here.

def login(request):
    return render(request, 'crawler/login.html')


def get_img_code(request):
    import random
    def get_random_color():
        return (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    def get_font_color():
        return (random.randint(10, 150), random.randint(10, 150), random.randint(10, 150))

    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    f = BytesIO()
    img = Image.new('RGB', (155, 33), color=get_random_color())
    font = ImageFont.truetype("static/crawler/fonts/Sunnydale.ttf", size=25)
    draw = ImageDraw.Draw(img)

    for var in range(5):
        random_num = str(random.randint(0, 9))
        random_lower_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        char = random.choice([random_num, random_lower_alpha, random_upper_alpha])
        draw.text((8 + 30 * var, 8), char, get_font_color(), font=font)

    width = 155
    height = 33

    for i in range(3):
        x1 = random.randint(5, 10)
        x2 = random.randint(100, width)
        y1 = random.randint(5, 30)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_font_color())

    img.save(f, 'png')
    data = f.getvalue()
    return HttpResponse(data)


def product_urls(request):
    urls = ProductUrl.objects.all()
    platforms = ProductUrl.objects.values('platform').distinct()
    from django.core.paginator import Paginator, EmptyPage
    pageinator = Paginator(urls, per_page=20)
    total_pages = pageinator.num_pages
    try:
        curr_page = int(request.GET.get('page', 1))
        results = pageinator.page(curr_page)
    except EmptyPage:
        results = pageinator.page(1)
    if pageinator.num_pages < 11:
        page_range = pageinator.page_range
    elif curr_page - 5 < 1:
        page_range = range(1, 12)
    elif curr_page + 5 > pageinator.num_pages:
        page_range = range(pageinator.num_pages - 10, pageinator.num_pages + 1)
    else:
        page_range = range(curr_page - 5, curr_page + 6)

    context = {
        'urls': results,
        'page_range': page_range,
        'curr_page': curr_page,
        'platforms': platforms,
        'total_pages': total_pages,
    }

    return render(request, 'crawler/product_urls.html', context=context)


def crawle_all(request):
    urls = ProductUrl.objects.filter(platform='eprice')
    for url in urls:
        print(url.href)
        result = get_product_info(url.href)
        result['product_url'] = url
        record = ProductDetail.objects.filter(ean=result['ean'])
        if record:
            pass
        else:
            ProductDetail.objects.create(**result)
    return HttpResponse('OK')


def url_detail(request):
    details = ProductDetail.objects.all()
    from django.core.paginator import Paginator, EmptyPage
    pageinator = Paginator(details, per_page=20)
    total_pages = pageinator.num_pages
    try:
        curr_page = int(request.GET.get('page', 1))
        results = pageinator.page(curr_page)
    except EmptyPage:
        results = pageinator.page(1)
    if pageinator.num_pages < 11:
        page_range = pageinator.page_range
    elif curr_page - 5 < 1:
        page_range = range(1, 12)
    elif curr_page + 5 > pageinator.num_pages:
        page_range = range(pageinator.num_pages - 10, pageinator.num_pages + 1)
    else:
        page_range = range(curr_page - 5, curr_page + 6)

    context = {
        'details': results,
        'page_range': page_range,
        'curr_page': curr_page,
        'total_pages': total_pages
    }
    return render(request, 'crawler/urls_detail.html', context=context)


def add_urls(request):
    urls = []
    for url in get_urls():
        pro_url = {}
        pro_url['href'] = url
        pro_url['platform'] = 'eprice'
        pro_url['create_by'] = 'promise'
        obj_url = ProductUrl(**pro_url)
        urls.append(obj_url)
    try:
        ProductUrl.objects.bulk_create(urls)
    except Exception as e:
        print(e)
    return HttpResponse('OK')
