from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name']

# admin.register(Product_images)

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'is_cancelled')
    list_filter = ('is_cancelled', 'created_at')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'quantity', 'order')



from django.contrib import admin
from .models import BrandSubmission

@admin.register(BrandSubmission)
class BrandSubmissionAdmin(admin.ModelAdmin):
    list_display = ('brand_name','first_name', 'last_name',  'category', 'deal_percentage', 'whatsapp_number', 'is_approved', 'created_at')
    list_filter = ('category', 'deal_percentage', 'is_approved')



@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')