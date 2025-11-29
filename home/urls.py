from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('python/', views.python, name='python'),
    path('java/', views.java, name='java'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # Razorpay order creation endpoint
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),

    # Razorpay payment success endpoint
    path('payment-success/', views.payment_success, name='payment_success'),
]
