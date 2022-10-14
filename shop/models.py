from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from twilio.rest import Client 

class User(AbstractUser):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
   
	
	 # USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name','last_name']


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	joined_on = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.first_name + ' ' + self.user.last_name

class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Product(models.Model):
	name = models.CharField(max_length=200)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	STATUS = (('Order Received','Order Received'),('Ready for  Pickup','Ready for  Pickup'))
	status = models.CharField(max_length=50, choices=STATUS, null=True,default='Order Received')

	def __str__(self):
		return "#Order: " + str(self.id)
	
	# Sending sms when payment is completed

	# def save(self, *args, **kwargs):
	# 	if self.complete == True:
	# 		account_sid = 'AC1c51c3361f816c86025c5959fb4c1639' 
	# 		auth_token = '0afd00b31e3bce1679ac101b742bbaeb' 
	# 		client = Client(account_sid, auth_token) 
			
	# 		message = client.messages.create(  
	# 									messaging_service_sid='MGe1b04e835f62fe804cd97889a04cd596', 
	# 									body='Hello Gilbert, thankyou for shopping with us, you will be notified once the Product is ready for pickup',      
	# 									to='+254725060098' 
	# 								) 
			
	# 		print(message.sid)

	# 		return super().save(*args, **kwargs)

		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total
	

	def __str__(self):
		return self.product
		

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address


