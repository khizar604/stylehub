"""
URL configuration for StyleHub01 project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', first_page, name = 'first_page'),
    path('partner_page/', partner_page, name = 'partner_page'),
    path('register/', registration, name="register"),
    path("user_login/", user_login, name='user_login'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),  # fixed
    path('reset-password/', reset_password, name='reset_password'),
    # path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('user_logout/', user_logout, name="user_logout"),
    path('index/', index,name='index'),
    path('index/<str:category>/', index, name='filtered_women_products'),
    path('index/<str:category>/', index, name='filtered_men_products'),
    path('men_clothes/', men_clothes, name="men_clothes"),
    path('women_clothes/', women_clothes, name="women_clothes"),
    path("AI_design/", AI_design, name='AI_design'),
    path('shop/', shop, name="shop"),
    path('contact/', contact, name="contact"),
    path('shopping_cart/', shopping_cart, name="shopping_cart"),
    path('check_out/', check_out, name="check_out"),
    path('women_clothes/<str:product_name>/', product_detail, name="product_detail"),
    path('cart/<int:product_id>/', cart, name='cart'),

    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('filter-dresses-women/', filter_dresses_women, name='filter_dresses_women'),
    path('filter-dresses-men/', filter_dresses_men, name='filter_dresses_men'),

    path('chatbot/', chatbot_view, name='chatbot'),
    path('place-order/', place_order, name='place_order'),
    path('cancel-order/<uuid:order_id>/', cancel_order, name='cancel_order'),
    path('order-confirmation/<uuid:order_id>/', order_confirmation, name='order_confirmation'),
    path('design/', tshirt_designer, name='design'),
    path("chatbot/", chatbot_view, name="chatbot"),
    path("chatbot01/", chatbot_view_recomm, name="chatbot01"),
    path("recommendation/", recommendation, name="recommendation"),

    path('search/', search_products, name='search_products'),

    path('sidebar/', product_list, name='product_list'),
    path('submit_brand/', submit_brand, name='submit_brand'),
    path('api/', include('myapp.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
