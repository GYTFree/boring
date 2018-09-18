from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserInfo(AbstractUser):
    """
    用户信息表
    """

    id = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.username


class ProductUrl(models.Model):
    """
    产品详情页面url链接地址
    """

    id = models.AutoField(primary_key=True)
    platform = models.CharField(max_length=64)
    href = models.CharField(max_length=255, unique=True)
    create_by = models.CharField(max_length=64)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.href


class ProductDetail(models.Model):
    """
    页面抓取信息存储
    """

    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    seller_name = models.CharField(max_length=64)
    category_path = models.CharField(max_length=255)
    currency = models.CharField(max_length=16)
    price = models.CharField(max_length=16)
    tag_price = models.CharField(max_length=16, default=0)
    discount_rate = models.CharField(max_length=16, default=0)
    old_price = models.CharField(max_length=16, default=0)
    old_discount_price = models.CharField(max_length=16, default=0)
    old_discount_rate = models.CharField(max_length=16, default=0)
    product_url = models.OneToOneField(to='ProductUrl', to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return (self.ean, self.name)
