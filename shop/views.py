from itertools import product
from multiprocessing import context
# from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.shortcuts import render,redirect
# from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
# from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from .forms import RegistrationForm
from .email import send_welcome_email
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder



# Authentication views
def register(request):
    page_name = 'Account'

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            request = form.save(commit=False)
            name = request.first_name + ' ' + request.last_name
            email = request.email

            send_welcome_email(name,email)
           

            request.save()
            return redirect("login")
    else:
        form = RegistrationForm()
    
    context = {
        "form":form,
        "page_name":page_name,
		
    
    }

    return render(request, "registration/register.html", context)

# Shop views

def store(request):
	page_name = 'store'
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	product_list =Product.objects.all().order_by('-id')
	categories=Category.objects.all()

	paginator = Paginator(product_list,9)
	page = request.GET.get('page')

	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)



	context = {
	 'products':products,
	 'cartItems':cartItems,
	 'categories':categories,
	 'page_name':page_name,
	 }

	return render(request, 'store.html', context)


def cart(request):
	page_name= 'cart'
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
	 'items':items,
	 'order':order,
	 'cartItems':cartItems,
	 'page_name':page_name,
	 }
	return render(request, 'cart.html', context)

def checkout(request):
	page_name = 'checkout'
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
	'items':items, 
	'order':order, 
	'cartItems':cartItems,
	'page_name':page_name,
	}
	return render(request, 'checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)



def search(request):
	page_name = 'search'
	q = request.GET.get('q') if request.GET.get('q') != None else ''
	results = Product.objects.filter(
        Q(category__title__icontains=q) |
        Q(name__icontains=q)
        
    )

	data = cartData(request)

	cartItems = data['cartItems']
	context={
		'results': results,
		'cartItems':cartItems,
		'page_name':page_name,
	}
	return render(request, 'search.html', context)

def categories(request):
	page_name = 'categories'
	data = cartData(request)

	cartItems = data['cartItems']
	categories=Category.objects.all()

	context = {
	 'cartItems':cartItems,
	 'categories':categories,
	 'page_name':page_name,
	 }

	return render(request, 'category.html', context)


def viewMore(request,pk):
	page_name = 'viewMore'
	product= Product.objects.get(id=pk)

	data = cartData(request)
	cartItems = data['cartItems']

	context = {
	'product':product,
	'cartItems':cartItems,
	'page_name':page_name,
	 }

	return render(request, 'more.html', context)

def profile(request,pk):
	page_name = 'profile'
	customer = Customer.objects.get(id=pk)
	orders = Order.objects.all()
	name = customer.user.first_name + ' ' + customer.user.last_name
	context = {
	'customer': customer,
	'orders':orders,
	'name':name,
	'page_name':page_name,
	 }

	return render(request, 'profile.html', context)

	



