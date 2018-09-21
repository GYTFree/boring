from django import forms
from django.contrib import auth
from django.forms import widgets
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from boring.settings import EMAIL_FROM, EMAIL_LIST
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from crawler.models import ProductUrl, ProductDetail
from crawler.utils.crawler import crawle_job, get_product_info
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
    return redirect(reverse('crawler:login'))


@login_required
def product_urls(request):
    urls = ProductUrl.objects.all().order_by('id')
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
    print(urls)
    # crawle_job(urls)
    for url in urls:
        result = get_product_info(url.href)
        record = ProductDetail.objects.filter(ean=result['ean'])
        if record:
            update_time = timezone.now()
            result['update_time'] = update_time
            record.update(**result)
        else:
            result['product_url'] = url
            ProductDetail.objects.create(**result)
    return redirect(reverse("crawler:url_detail"))


@login_required
def url_detail(request):
    details = ProductDetail.objects.all().order_by('id')
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


@login_required
def add_url(request):
    if request.method == "POST":
        # print(request.POST)
        response = {}
        platform = request.POST.get('platform')
        href = request.POST.get('item').strip()
        create_by = request.POST.get('user')
        try:
            ProductUrl.objects.get(href=href)
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


def send_email(request):
    from django.template import Context, Template
    resp = ProductDetail.objects.exclude(seller_name__in=['JOCASE', 'ePrice']).values('seller_name',
                                                                                      'product_url__platform',
                                                                                      'product_url__href')
    tpl = """
        <h3>以下sku链接需要变更价格</h3>
        <table border="1" cellspacing="0" cellpadding="3">
          <tr>
            <th>Platform</th>
            <th>Provider</th>
            <th>Url</th>
          </tr>
          {% for record in results %}
          <tr><td>{{ record.product_url__platform }}</td><td>{{ record.seller_name }}</td><td>{{ record.product_url__href }}</td></tr>
          {% endfor %}
        </table>
    """
    t = Template(tpl)
    c = Context({'results': resp})
    content = t.render(c)
    msg = EmailMultiAlternatives("待改价SKU链接信息", content, EMAIL_FROM, EMAIL_LIST)
    msg.attach_alternative(content, "text/html")
    try:
        msg.send()
    except Exception as e:
        print(type(e))
    return JsonResponse({"msg": "successful"})
