from django.urls import path, include
from crawler import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('get_img_code/', views.get_img_code, name='get_img_code'),
    path('product_urls/', views.product_urls, name='product_urls'),
    path('crawler/', views.crawler, name='crawler'),
    path('url_detail/', views.url_detail, name='url_detail'),
]
