from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from payment.simple_order_email import send_simple_order_email

# Import Some Paypal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # unique user id for duplictate orders

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# Get the order
		order = Order.objects.get(id=pk)
		# Get the order items
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# Check if true or false
			if status == "true":
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				order.update(shipped=False)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, 'payment/orders.html', {"order":order, "items":items})




	else:
		messages.success(request, "Access Denied")
		return redirect('home')



def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=True, date_shipped=now)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def process_order(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		cart_details = cart.get_cart_details()  # Get complete cart details with sizes
		totals = cart.cart_total()

		# Get Billing Info from the last page
		payment_form = PaymentForm(request.POST or None)
		# Get Shipping Session Data
		my_shipping = request.session.get('my_shipping')

		# Gather Order Info
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Create Shipping Address from session info
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		# Create an Order
		if request.user.is_authenticated:
			# logged in
			user = request.user
			# Create Order
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity and size information from cart
				for key, item_data in cart_details.items():
					if int(key) == product.id:
						quantity = item_data['quantity']
						selected_size = item_data.get('selected_size', '')
						custom_size = item_data.get('custom_size', '')
						
						# Create order item with size information
						create_order_item = OrderItem(
							order_id=order_id, 
							product_id=product_id, 
							user=user, 
							quantity=quantity, 
							price=price,
							selected_size=selected_size,
							custom_size=custom_size
						)
						create_order_item.save()

			# Delete our cart
			send_simple_order_email()
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]

			# Delete Cart from Database (old_cart field)
			current_user = Profile.objects.filter(user__id=request.user.id)
			# Delete shopping cart in database (old_cart field)
			current_user.update(old_cart="")


			messages.success(request, "Order Placed!")
			return redirect('home')

			

		else:
			# not logged in
			# Create Order
			create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity and size information from cart
				for key, item_data in cart_details.items():
					if int(key) == product.id:
						quantity = item_data['quantity']
						selected_size = item_data.get('selected_size', '')
						custom_size = item_data.get('custom_size', '')
						
						# Create order item with size information
						create_order_item = OrderItem(
							order_id=order_id, 
							product_id=product_id, 
							quantity=quantity, 
							price=price,
							selected_size=selected_size,
							custom_size=custom_size
						)
						create_order_item.save()

			# Delete our cart
			send_simple_order_email()

			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]



			messages.success(request, "Order Placed!")
			return redirect('home')


	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		cart_details = cart.get_cart_details()  # Get cart details with sizes
		totals = cart.cart_total()

		# Create a session with Shipping Info
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Get the host
		host = request.get_host()
		# Create Paypal Form Dictionary
		paypal_dict = {
			'business': settings.PAYPAL_RECEIVER_EMAIL,
			'amount': totals,
			'item_name': 'Book Order',
			'no_shipping': '2',
			'invoice': str(uuid.uuid4()),
			'currency_code': 'USD', # EUR for Euros
			'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
			'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
			'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
		}

		# Create acutal paypal button
		paypal_form = PayPalPaymentsForm(initial=paypal_dict)


		# Check to see if user is logged in
		if request.user.is_authenticated:
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {
				"paypal_form": paypal_form, 
				"cart_products": cart_products, 
				"quantities": quantities, 
				"cart_details": cart_details,
				"totals": totals, 
				"shipping_info": request.POST, 
				"billing_form": billing_form
			})

		else:
			# Not logged in
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {
				"paypal_form": paypal_form, 
				"cart_products": cart_products, 
				"quantities": quantities, 
				"cart_details": cart_details,
				"totals": totals, 
				"shipping_info": request.POST, 
				"billing_form": billing_form
			})

		
		shipping_form = request.POST
		return render(request, "payment/billing_info.html", {
			"cart_products": cart_products, 
			"quantities": quantities, 
			"cart_details": cart_details,
			"totals": totals, 
			"shipping_form": shipping_form
		})	
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    cart_details = cart.get_cart_details()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Checkout as logged in user
        try:
            # Try to get existing shipping address
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            # Create new shipping form if doesn't exist
            shipping_user = None
            shipping_form = ShippingForm(request.POST or None)
        
        return render(request, "payment/checkout.html", {
            "cart_products": cart_products, 
            "quantities": quantities, 
            "cart_details": cart_details,
            "totals": totals, 
            "shipping_form": shipping_form 
        })
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {
            "cart_products": cart_products, 
            "quantities": quantities, 
            "cart_details": cart_details,
            "totals": totals, 
            "shipping_form": shipping_form
        })

	

def payment_success(request):
	return render(request, "payment/payment_success.html", {})


def payment_failed(request):
	return render(request, "payment/payment_failed.html", {})

# ========== ADD THESE TWO NEW VIEWS FOR USER ORDER TRACKING ==========

@login_required
def user_orders(request):
    """
    Show all orders for the logged-in user with pagination
    This is for REGULAR USERS to see their own orders
    """
    try:
        # Get user's orders, newest first
        orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
        
        # Pagination: 10 orders per page
        paginator = Paginator(orders, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Calculate order statistics
        total_orders = orders.count()
        shipped_orders = orders.filter(shipped=True).count()
        pending_orders = orders.filter(shipped=False).count()
        
        context = {
            'orders': page_obj,
            'page_obj': page_obj,
            'total_orders': total_orders,
            'shipped_orders': shipped_orders,
            'pending_orders': pending_orders,
        }
        
        return render(request, 'payment/user_orders.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading orders: {str(e)}")
        return redirect('home')

@login_required
def order_detail(request, order_id):
    """
    Show detailed view of a specific order
    This is for REGULAR USERS to see their own order details
    """
    try:
        # IMPORTANT: Get the order, ensuring it belongs to the logged-in user
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Get order items
        order_items = OrderItem.objects.filter(order=order)
        
        # Calculate subtotal
        subtotal = sum(item.price * item.quantity for item in order_items)
        shipping = 0  # Add your shipping logic here if needed
        tax = 0  # Add tax logic if needed
        total = order.amount_paid
        
        context = {
            'order': order,
            'order_items': order_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total,
        }
        
        return render(request, 'payment/order_detail.html', context)
        
    except Exception as e:
        messages.error(request, "Order not found or access denied")
        return redirect('user_orders')