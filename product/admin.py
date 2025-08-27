from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_url')
    search_fields = ('name',)
    list_filter = ('price',)        
    ordering = ('name',)