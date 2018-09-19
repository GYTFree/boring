from django.contrib import admin
from crawler.models import ProductUrl


# Register your models here.

class ProductUrlAdmin(admin.ModelAdmin):
    list_display = ('create_by', 'create_time', 'href')
    ordering = ['id']


admin.site.register(ProductUrl, ProductUrlAdmin)
