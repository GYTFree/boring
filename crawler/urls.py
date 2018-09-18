from django.urls import path, include
from crawler import views

urlpatterns = [
    path('', views.product_urls),
    path('regist/', views.regist, name='regist'),
    path('login/', views.login, name='login'),
    path('get_img_code/', views.get_img_code, name='get_img_code'),
    path('product_urls/', views.product_urls, name='product_urls'),
    path('crawle_all/', views.crawle_all, name='crawle_all'),
    path('url_detail/', views.url_detail, name='url_detail'),
    path('add_urls/', views.add_urls, name='add_urls'),
]
