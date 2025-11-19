from django.contrib import admin 
from django.urls import path, include
from home import views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "DJango Shubham Admin"
admin.site.site_title = "DJango Shubham Admin Portal"
admin.site.index_title = "Welcome to DJango Shubham Portal"


urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('services', views.services, name='services'),
    path('contact', views.contact, name='contact'),
    path('admin/', admin.site.urls),
    path('register', views.register, name='register'),
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('python', views.python, name='python'),
    path('java', views.java, name='java'),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment-success/', views.payment_success, name='payment_success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)