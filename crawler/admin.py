from django.contrib import admin
from crawler.models import ProductUrl


# Register your models here.

class ProductUrlAdmin(admin.ModelAdmin):
    ordering = ['id']


admin.site.register(ProductUrl, ProductUrlAdmin)
