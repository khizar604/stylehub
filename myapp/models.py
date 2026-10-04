from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
    ]
    TYPE_CHOICES = [
        ('Casual Wear', 'Casual Wear'),
        ('Formal Wear', 'Formal Wear'),
        ('Party Wear', 'Party Wear'),
        ('Seasonal Wear','Seasonal Wear')
    ]
    SUBTYPE_CHOICES = [
        ('Shirts', 'Shirts'),
        ('Pants', 'Pants'),
        ('Coats', 'Coats'),
        ('Jackets', 'Jackets'),
        ('t-Shirts', 't-shirts')
    ]
    SIZE = [
        ('S', 'small'),
        ('M', 'medium'),
        ('L', 'large'),
        ('XL' ,'etra-large')
    ]
    COLOR_CHOICES = [
    ('Dark', 'Dark'),
    ('Light', 'Light'),
]

    name = models.CharField(max_length=255,blank=True, null=True)
    hero_image = models.ImageField(upload_to='product/' )
    image01 = models.ImageField(upload_to='product/')
    image02 = models.ImageField(upload_to='product/')
    image03 = models.ImageField(upload_to='product/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES,blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,blank=True, null=True)
    subtype = models.CharField(max_length=20,choices=SUBTYPE_CHOICES ,blank=True, null=True)

    # image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    introduction = models.TextField(max_length=50, null=True, blank=True)
    features = models.TextField(max_length=50, null=True, blank=True)
    stock = models.IntegerField(blank=True, null=True)
    sku = models.CharField(max_length=50,blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    size = models.CharField(max_length=100,blank=True, null=True) 
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, blank=True, null=True)


    def __str__(self):
        return self.name
        


class Comments(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}-{self.created_at.strftime('%y,%m,%d')}"

    





from django.db import models
from django.utils.timezone import now
import uuid

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.URLField()

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) in Order {self.order.id}"
    



from django.db import models
# from products.models import Product  # Your existing product model

class CustomDesign(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    design_name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    image_data = models.TextField()  # Stores base64 image data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.design_name} - {self.product.name}"









from django.db import models

CATEGORY_CHOICES = [
    ('men', 'Men Clothes'),
    ('women', 'Women Clothes'),
    ('both', 'Both'),
]

DEAL_CHOICES = [
    ('10', '10% Partnership'),
    ('20', '20% Partnership'),
    ('30', '30% Partnership'),
]

class BrandSubmission(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    brand_name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    deal_percentage = models.CharField(max_length=2, choices=DEAL_CHOICES)
    product_image = models.ImageField(upload_to='product_samples/', null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name



from django.db import models

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)