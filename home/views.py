from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate , login
from datetime import datetime
from home.models import Contact
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Product, Cart, Wishlist
import razorpay
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import time


# Create your views here.
def index(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'index.html', {"products": products})
def about(request):
    return render(request,'about.html')
   
def services(request):
    return render(request,'services.html')
        
def contact(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        desc=request.POST.get('desc')
        contact=Contact(name=name,email=email,phone=phone,desc=desc,date=datetime.today())
        contact.save()
        messages.success(request, 'Your message has been sent!')
        
    return render(request,'contact.html')

def register(request):
    if request.method=="POST":
        Fname=request.POST.get('Fname')
        Lname=request.POST.get('Lname')
        Uemail=request.POST.get('Uemail')
        Upassword=request.POST.get('Upassword')
        if User.objects.filter(username=Uemail).exists():
            messages.error(request, 'Email already registered!')
            return render(request,'register.html')
        user = User.objects.create_user(username=Uemail, email=Uemail, password=Upassword, first_name=Fname, last_name=Lname)
        user.save()
        messages.success(request, 'You have successfully Registered!')
        return redirect('/login')

    return render(request,'register.html')


def loginUser(request):
    if request.method=="POST":
        Username=request.POST.get('Username')
        Upassword=request.POST.get('Upassword')
        user = authenticate(username=Username, password=Upassword)
        if user is not None:
            login(request,user)
            messages.success(request, 'You have successfully Logged In!')
            return redirect('/')
        else:
            messages.error(request, 'Invalid credentials, Please try again')
            return render(request,'login.html')
    return render(request,'login.html')


def logoutUser(request):
    logout(request)
    messages.success(request, 'You have successfully Logged Out!')
    return redirect('/')

def python(request):
    return render(request,'python.html')

def java(request):
    return render(request,'java.html')

def product_detail(request, id):
    if request.user.is_anonymous:
        return redirect('/login')
    product = Product.objects.prefetch_related('images').get(id=id)
    if request.method == "POST":
        if 'add_to_cart' in request.POST:
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            messages.success(request, 'Product added to cart!')
        elif 'add_to_wishlist' in request.POST:
            Wishlist.objects.get_or_create(user=request.user, product=product)
            messages.success(request, 'Product added to wishlist!')
        return redirect('product_detail', id=id)
    return render(request, "product_detail.html", {"product": product})

def cart(request):
    if request.user.is_anonymous:
        return redirect('/login')

    if request.method == 'POST':
        if 'add_quantity' in request.POST:
            cart_item_id = request.POST.get('cart_item_id')
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            cart_item.quantity += 1
            cart_item.save()
            # messages.success(request, 'Quantity increased!')
        elif 'remove_quantity' in request.POST:
            cart_item_id = request.POST.get('cart_item_id')
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                # messages.success(request, 'Quantity decreased!')
            else:
                cart_item.delete()
                # messages.success(request, 'Item removed from cart!')
        return redirect('cart')

    cart_items_qs = Cart.objects.filter(user=request.user)

    cart_items = []
    grand_total = 0
    for item in cart_items_qs:
        total_price = item.product.price * item.quantity
        grand_total += total_price
        cart_items.append({
            'id': item.id,
            'product': item.product,
            'quantity': item.quantity,
            'total_price': total_price
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'grand_total': grand_total})

def wishlist(request):
    if request.user.is_anonymous:
        return redirect('/login')

    if request.method == 'POST':
        if 'remove_from_wishlist' in request.POST:
            wishlist_item_id = request.POST.get('wishlist_item_id')
            Wishlist.objects.filter(id=wishlist_item_id, user=request.user).delete()
            messages.success(request, 'Item removed from wishlist!')
        return redirect('wishlist')

    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@csrf_exempt
def create_razorpay_order(request):
    if request.method == "POST":
        # check for presence of Razorpay API keys in settings
        if not settings.RAZORPAY_KEY_ID or settings.RAZORPAY_KEY_ID == "your_razorpay_key_id_here":
            return JsonResponse({"error": "Razorpay API Key ID not configured"}, status=400)
        if not settings.RAZORPAY_KEY_SECRET or settings.RAZORPAY_KEY_SECRET == "your_razorpay_key_secret_here":
            return JsonResponse({"error": "Razorpay API Key Secret not configured"}, status=400)
        try:
            data = json.loads(request.body)
            amount_str = data.get("amount")
            if not amount_str:
                return JsonResponse({"error": "Amount is required"}, status=400)
            try:
                amount = int(amount_str)
            except ValueError:
                return JsonResponse({"error": "Amount must be a valid integer"}, status=400)
            if amount <= 0:
                return JsonResponse({"error": "Amount must be greater than 0"}, status=400)
            currency = data.get("currency", "INR")
            receipt = data.get("receipt", f"order_rcptid_{int(time.time())}")

            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            except Exception as e:
                return JsonResponse({"error": f"Failed to initialize Razorpay client: {str(e)}"}, status=400)

            order = client.order.create({
                "amount": amount,
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1
            })

            return JsonResponse(order)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            order_id = data.get('order_id')
            signature = data.get('signature')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'failed', 'error': 'Invalid JSON'}, status=400)

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Payment successful - you can save order details here
            messages.success(request, 'Payment successful! Your order has been placed.')
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'failed'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

