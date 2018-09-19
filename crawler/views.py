from django import forms
from django.contrib import auth
from django.forms import widgets
from django.http import JsonResponse
from crawler.models import ProductUrl, ProductDetail
from crawler.crawler import get_product_info, get_urls
from django.shortcuts import render, HttpResponse, redirect, reverse


# Create your views here.

class UserForm(forms.Form):
    user = forms.CharField(max_length=32)
    password = forms.CharField(widget=widgets.PasswordInput, min_length=8)
    re_password = forms.CharField(widget=widgets.PasswordInput, min_length=8)
    email = forms.EmailField()


def get_img_code(request):
    from crawler.utils import validCode
    data = validCode.get_img_code(request)
    return HttpResponse(data)


def regist(request):
    form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'crawler/regist.html', context=context)


def login(request):
    if request.method == 'POST':
        response = {'user': None, 'msg': None}
        user = request.POST.get('user')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')

        if valid_code.upper() == request.session.get('valid_code').upper():
            user = auth.authenticate(username=user, password=password)
            if user:
                auth.login(request, user)
                response['user'] = user.username
            else:
                response['msg'] = '用户名或密码错误!'
        else:
            response['msg'] = '验证码错误!'
        return JsonResponse(response)
    return render(request, 'crawler/login.html')


def my_logout(request):
    auth.logout(request)
    return redirect(reverse('login'))


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
        'username': request.user.username,
    }

    return render(request, 'crawler/product_urls.html', context=context)


def crawle_all(request):
    urls = ProductUrl.objects.filter(platform='eprice')
    for url in urls:
        print(url.href)
        result = get_product_info(url.href)
        record = ProductDetail.objects.filter(ean=result['ean'])
        if record:
            record.update(**result)
        else:
            result['product_url'] = url
            ProductDetail.objects.create(**result)
    return redirect(reverse("url_detail"))


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
        'total_pages': total_pages,
        'username': request.user.username,
    }
    return render(request, 'crawler/urls_detail.html', context=context)


def add_url(request):
    if request.method == "POST":
        # print(request.POST)
        response = {}
        platform = request.POST.get('platform')
        href = request.POST.get('item').strip()
        create_by = request.POST.get('user')
        try:
            record = ProductUrl.objects.get(href=href)
            response['msg'] = '该URL已存在！'
            return JsonResponse(response)
        except:
            if all([platform, href, create_by]):
                ProductUrl.objects.create(platform=platform, href=href, create_by=create_by)
                response['msg'] = '添加URL成功！'
            else:
                response['msg'] = '平台和URL链接信息不能为空！'
        return JsonResponse(response)
    return redirect(reverse("product_urls"))
