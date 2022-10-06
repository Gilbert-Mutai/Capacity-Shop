from itertools import product
from multiprocessing import context
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from .forms import RegistrationForm,LoginForm
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder



# Authentication views
class RegistrationView(CreateView):
    template_name = "shop/auth/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("store")


class LoginView(FormView):
    template_name = "shop/auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("store")

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


			# Shop views

def store(request):
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
	 'categories':categories
	 }

	return render(request, 'shop/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'shop/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'shop/checkout.html', context)

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
	}
	return render(request, 'shop/search.html', context)

def categories(request):
	data = cartData(request)

	cartItems = data['cartItems']
	categories=Category.objects.all()

	context = {
	 'cartItems':cartItems,
	 'categories':categories
	 }

	return render(request, 'shop/category.html', context)


def viewMore(request,pk):

	product= Product.objects.get(id=pk)

	data = cartData(request)
	cartItems = data['cartItems']

	context = {
	'product':product,
	'cartItems':cartItems,
	 }

	return render(request, 'shop/more.html', context)

	



