from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactForm
from .models import Product, Category, Profile, Wishlist, HeadSize
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q, Min, Max
import json
from cart.cart import Cart
from django.utils.text import slugify

from django.views.decorators.cache import cache_page

def search(request):
    query = request.GET.get('q', '')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    colors = request.GET.getlist('color')
    head_sizes = request.GET.getlist('head_size')
    materials = request.GET.getlist('material')
    custom_size_available = request.GET.get('custom_size_available')  # New filter for custom size

    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if colors:
        products = products.filter(color__in=colors)
    if head_sizes:
        # Filter products that have the selected head sizes
        products = products.filter(head_sizes__id__in=head_sizes).distinct()
    if materials:
        products = products.filter(material__in=materials)
    if custom_size_available:  # Filter for products that allow custom sizes
        products = products.filter(allow_custom_size=True)

    categories = Category.objects.all()

    # Pagination: 6 products per page
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter data
    head_sizes_db = HeadSize.objects.all().order_by('cm')
    colors_db = Product.objects.values_list('color', flat=True).distinct().order_by('color')
    materials_db = Product.objects.values_list('material', flat=True).distinct().order_by('material')
    min_price_db = Product.objects.aggregate(Min('price'))['price__min'] or 0
    max_price_db = Product.objects.aggregate(Max('price'))['price__max'] or 1000

    context = {
        'products': page_obj,
        'categories': categories,
        'head_sizes_db': head_sizes_db,
        'colors_db': colors_db,
        'materials_db': materials_db,
        'min_price_db': min_price_db,
        'max_price_db': max_price_db,
        'selected_head_sizes': head_sizes,
        'selected_colors': colors,
        'selected_materials': materials,
        'selected_price_min': price_min,
        'selected_price_max': price_max,
        'custom_size_available': custom_size_available,  # Add to context
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, "search.html", context)

def about(request):
    """
    Show about page and handle contact form POST on the same URL.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()  # saves ContactMessage
            # prepare recipients from ADMINS or fallback
            admins = getattr(settings, 'ADMINS', [])
            recipient_list = [email for _name, email in admins] or [getattr(settings, 'DEFAULT_FROM_EMAIL', None)]

            subject = f"New contact from {msg.name}"
            body = f"Name: {msg.name}\nEmail: {msg.email}\n\nMessage:\n{msg.message}"
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            except Exception as e:
                # keep user flow working even if email fails; you can log e
                pass

            from django.contrib import messages
            messages.success(request, "Message sent. We'll contact you soon.")
            return redirect('about')
    else:
        form = ContactForm()

    return render(request, 'about.html', {'contact_form': form})

def update_info(request):
    if request.user.is_authenticated:
        # Get Current User
        current_user = Profile.objects.get(user__id=request.user.id)
        
        # FIXED: Get or create ShippingAddress
        try:
            shipping_user = ShippingAddress.objects.get(user=request.user)
        except ShippingAddress.DoesNotExist:
            # Create a default shipping address
            shipping_user = ShippingAddress.objects.create(
                user=request.user,
                shipping_full_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                shipping_email=request.user.email
            )
        
        # Get original User Form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Get User's Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if request.method == 'POST':
            if form.is_valid() and shipping_form.is_valid():
                # Save original form
                form.save()
                # Save shipping form
                shipping_form.save()

                messages.success(request, "Your Info Has Been Updated!!")
                return redirect('home')
            else:
                messages.error(request, "Please correct the errors below.")
        
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method  == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated!!")
            return redirect('home')
        return render(request, "update_user.html", {'user_form':user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})    

def category(request, foo):
    # ------------------ Find Category ------------------
    cat = None
    if str(foo).isdigit():
        cat = Category.objects.filter(id=int(foo)).first()
    if not cat:
        cat = Category.objects.filter(name__iexact=foo).first()
    if not cat:
        name_candidate = foo.replace('-', ' ')
        cat = Category.objects.filter(name__iexact=name_candidate).first()
    if not cat:
        for c in Category.objects.all():
            if slugify(c.name) == foo:
                cat = c
                break
    if not cat:
        messages.error(request, "That Category Doesn't Exist...")
        return redirect('home')

    # ------------------ Products with Pagination ------------------
    product_list = Product.objects.filter(category=cat).order_by('-id')
    paginator = Paginator(product_list, 4)  # 4 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {
        'category': cat,
        'products': page_obj,   # paginated products
        'page_obj': page_obj,   # for pagination controls
    })

def product(request, pk):
    product = Product.objects.get(id=pk)
    
    # Get related products (same category, exclude current product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]  # Limit to 4 products
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product.html', context)

def home(request):
    # ---------------- PRODUCTS ----------------
    product_list = Product.objects.all().order_by('-id')  # newest first
    paginator = Paginator(product_list, 8)  # 8 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # ---------------- CATEGORIES ----------------
    category_list = Category.objects.all().order_by('name')
    cat_paginator = Paginator(category_list, 8)  # 8 categories per page
    cat_page_number = request.GET.get('cat_page', 1)
    cat_page_obj = cat_paginator.get_page(cat_page_number)

    return render(request, "home.html", {
        "products": page_obj,       # paginated products
        "categories": cat_page_obj, # paginated categories
        "page_obj": page_obj,       # for product pagination
        "cat_page_obj": cat_page_obj, # for category pagination
    })

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart and saved_cart.strip():  # Check if cart is not empty
                try:
                    # Convert to dictionary using JSON
                    converted_cart = json.loads(saved_cart)
                    # Add the loaded cart dictionary to our session
                    # Get the cart
                    cart = Cart(request)
                    # Loop thru the cart and add the items from the database
                    for product_id, item_data in converted_cart.items():
                        try:
                            # Skip if product_id is not a valid integer
                            if not str(product_id).isdigit():
                                print(f"Skipping invalid product ID: {product_id}")
                                continue
                                
                            # Convert to integer
                            product_id_int = int(product_id)
                            
                            # Get the product
                            product = Product.objects.get(id=product_id_int)
                            
                            # Extract the individual values from the item_data dictionary
                            # Handle both old format (just quantity) and new format (dictionary)
                            if isinstance(item_data, dict):
                                quantity = item_data.get('quantity', 1)
                                selected_size = item_data.get('selected_size', '')
                                custom_size = item_data.get('custom_size', '')
                            else:
                                # Old format where item_data was just the quantity
                                quantity = item_data
                                selected_size = ''
                                custom_size = ''
                            
                            # Add to cart using db_add with individual parameters
                            cart.db_add(
                                product=product, 
                                quantity=quantity, 
                                selected_size=selected_size, 
                                custom_size=custom_size
                            )
                            
                        except Product.DoesNotExist:
                            # Product might have been deleted, skip it
                            continue
                        except ValueError as e:
                            # Handle conversion errors
                            continue
                        except Exception as e:
                            # Handle any other errors
                            continue
                            
                except json.JSONDecodeError as e:
                    # If JSON is invalid, start with empty cart
                    print(f"JSON decode error: {e}")
                    pass
                except Exception as e:
                    print(f"Unexpected error restoring cart: {e}")
                    # Continue with empty cart

            messages.success(request, ("You Have Been Logged In!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, please try again..."))
            return redirect('login')

    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out...Thanks for stopping by..."))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
        else:
            messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})

def search_live(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    collections = Category.objects.filter(name__icontains=query)

    products_data = [
        {
            'id': product.id,
            'name': product.name,
            'price': f"${product.price}",
            'image': product.image.url,
        }
        for product in products
    ]

    collections_data = [
        {
            'id': collection.id,
            'name': collection.name,
            'slug': slugify(collection.name),
            'description': collection.description,
            'image': collection.image.url if collection.image else '/static/images/placeholder.png',
        }
        for collection in collections
    ]

    return JsonResponse({'products': products_data, 'collections': collections_data})

# Show wishlist (works for auth & guest)
def wishlist_view(request):
    if request.user.is_authenticated:
        # Get or create wishlist for user
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        products = wishlist.products.all()
    else:
        # For guests: get product IDs from session
        product_ids = request.session.get('wishlist', [])
        products = Product.objects.filter(id__in=product_ids)
    return render(request, 'wishlist.html', {'products': products})

# Add product to wishlist
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id not in wishlist:
            wishlist.append(product_id)
            request.session['wishlist'] = wishlist
        messages.success(request, f"{product.name} added to your wishlist.")

    return redirect('wishlist')

# Remove product from wishlist
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.remove(product)
        messages.info(request, f"{product.name} removed from your wishlist.")
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session['wishlist'] = wishlist
        messages.info(request, f"{product.name} removed from your wishlist.")

    return redirect('wishlist')

def shipping_policy(request):
    """
    View to display the shipping policy page
    """
    context = {
        'title': 'Shipping Policy',
    }
    return render(request, 'shipping_policy.html', context)

def returns(request):
    """
    View to display the Returns & Refunds page
    """
    context = {
        'title': 'Returns & Refunds',
    }
    return render(request, 'returns.html', context)

def term(request):
    """
    View to display the Returns & Refunds page
    """
    context = {
        'title': 'Terms of Service',
    }
    return render(request, 'term.html', context)

def privacy_policy(request):
    """
    View to display the Privacy Policy page
    """
    context = {
        'title': 'Privacy Policy',
    }
    return render(request, 'privacy.html', context)

# Debug view to check cart data (remove in production)
def debug_cart(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        saved_cart = current_user.old_cart
        print("Saved cart data:", saved_cart)
        
        if saved_cart:
            try:
                converted_cart = json.loads(saved_cart)
                print("Converted cart:", converted_cart)
                print("Cart items:")
                for key, value in converted_cart.items():
                    print(f"  Key: {key} (type: {type(key)})")
                    print(f"  Value: {value} (type: {type(value)})")
            except Exception as e:
                print("Error:", e)
        
        return JsonResponse({"status": "checked"})
    return JsonResponse({"status": "not authenticated"})

# View to reset corrupted cart data
def reset_cart(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        current_user.old_cart = "{}"
        current_user.save()
        
        # Also clear session cart
        if 'session_key' in request.session:
            del request.session['session_key']
        
        messages.success(request, "Cart has been reset.")
        return redirect('home')
    return redirect('login')