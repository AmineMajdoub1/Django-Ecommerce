from django.db import models
from django.contrib.auth.models import User
from store.models import Product
import datetime

class Order(models.Model):
	# Foreign Key
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	full_name = models.CharField(max_length=250)
	email = models.EmailField(max_length=250)
	shipping_address = models.TextField(max_length=15000)
	amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
	date_ordered = models.DateTimeField(auto_now_add=True)
	# Shipping
	shipped = models.BooleanField(default=False)
	date_shipped = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return f'Order - #{self.id}'

class OrderItem(models.Model):
	# Foreign Keys
	order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	# Fields
	quantity = models.PositiveBigIntegerField(default=1)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	
	# ADD THESE FIELDS FOR SIZE INFORMATION
	selected_size = models.CharField(max_length=100, blank=True, null=True)
	custom_size = models.CharField(max_length=100, blank=True, null=True)

	def __str__(self):
		return f'Order Item - #{self.id}'

class ShippingAddress(models.Model):
	# Foreign Key
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	# Shipping Info
	shipping_full_name = models.CharField(max_length=255)
	shipping_email = models.CharField(max_length=255)
	shipping_address1 = models.CharField(max_length=255)
	shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
	shipping_city = models.CharField(max_length=255)
	shipping_state = models.CharField(max_length=255, null=True, blank=True)
	shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
	shipping_country = models.CharField(max_length=255)

	class Meta:
		verbose_name_plural = "Shipping Address"

	def __str__(self):
		return f'Shipping Address - {self.id}'

	def get_shipping_address(self):
		address_parts = [
			self.shipping_address1,
			self.shipping_address2,
			f"{self.shipping_city}, {self.shipping_state} {self.shipping_zipcode}",
			self.shipping_country
		]
		# Filter out empty parts and join with newlines
		return '\n'.join(part for part in address_parts if part)