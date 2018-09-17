from django.urls import path, include
from crawler import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('get_img_code/', views.get_img_code, name='get_img_code'),
]
