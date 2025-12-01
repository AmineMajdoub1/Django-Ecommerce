from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
	# Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	cart_details = cart.get_cart_details()  # Get complete cart details with sizes
	totals = cart.cart_total()
	return render(request, "cart_summary.html", {
		"cart_products": cart_products, 
		"quantities": quantities, 
		"totals": totals,
		"cart_details": cart_details
	})




def cart_add(request):
	# Get the cart
	cart = Cart(request)
	# test for POST
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))
		selected_size = request.POST.get('selected_size', '')
		custom_size = request.POST.get('custom_size', '')

		# lookup product in DB
		product = get_object_or_404(Product, id=product_id)
		
		# Validate size selection for products that require sizes
		if (product.head_sizes.exists() or product.allow_custom_size) and not selected_size and not custom_size:
			return JsonResponse({'error': 'Please select a head size or choose custom size'}, status=400)
		
		if selected_size == 'custom' and not custom_size:
			return JsonResponse({'error': 'Please enter your custom measurements'}, status=400)
		
		# Save to session
		cart.add(product=product, quantity=product_qty, selected_size=selected_size, custom_size=custom_size)

		# Get Cart Quantity
		cart_quantity = cart.__len__()

		# Return resonse
		# response = JsonResponse({'Product Name: ': product.name})
		response = JsonResponse({'qty': cart_quantity})
		messages.success(request, ("Product Added To Cart..."))
		return response

def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		# Call delete Function in Cart
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		#return redirect('cart_summary')
		messages.success(request, ("Item Deleted From Shopping Cart..."))
		return response


def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)

		response = JsonResponse({'qty':product_qty})
		#return redirect('cart_summary')
		messages.success(request, ("Your Cart Has Been Updated..."))
		return response