from django.urls import path, include
from crawler import views


app_name = 'crawler'
urlpatterns = [
    path('', views.login),
    path('regist/', views.regist, name='regist'),
    path('login/', views.login, name='login'),
    path('accounts/login/',views.login),
    path('logout/', views.my_logout, name='logout'),
    path('get_img_code/', views.get_img_code, name='get_img_code'),
    path('product_urls/', views.product_urls, name='product_urls'),
    path('crawle_all/', views.crawle_all, name='crawle_all'),
    path('url_detail/', views.url_detail, name='url_detail'),
    path('add_url/', views.add_url, name='add_url'),
    path('send_email/', views.send_email, ),
]
