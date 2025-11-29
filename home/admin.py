from django.contrib import admin
from home.models import Contact
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

# Register your models here.
admin.site.register(Contact)
admin.site.register(Product, ProductAdmin)
