from store.models import Product, Profile
import json

class Cart():
    def __init__(self, request):
        self.session = request.session
        # Get request
        self.request = request
        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key!  Create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        self.cart = cart

    def db_add(self, product, quantity, selected_size=None, custom_size=None):
        product_id = str(product.id)  # Fixed: use product.id, not product object
        
        # Handle case where quantity is actually a dictionary containing cart item data
        if isinstance(quantity, dict):
            # Extract data from the dictionary
            item_quantity = quantity.get('quantity', 1)
            item_selected_size = quantity.get('selected_size', selected_size)
            item_custom_size = quantity.get('custom_size', custom_size)
        else:
            # Use the provided parameters
            item_quantity = quantity
            item_selected_size = selected_size
            item_custom_size = custom_size
        
        # Logic
        if product_id in self.cart:
            # Update existing item
            self.cart[product_id]['quantity'] += int(item_quantity)
        else:
            # Add new item
            self.cart[product_id] = {
                'quantity': int(item_quantity),
                'selected_size': item_selected_size,
                'custom_size': item_custom_size
            }

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Save cart as proper JSON
            cart_json = json.dumps(self.cart)
            # Save carty to the Profile Model
            current_user.update(old_cart=cart_json)

    def add(self, product, quantity, selected_size=None, custom_size=None):
        product_id = str(product.id)
        # Logic
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {
                'quantity': int(quantity),
                'selected_size': selected_size,
                'custom_size': custom_size
            }

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Save cart as proper JSON
            cart_json = json.dumps(self.cart)
            # Save carty to the Profile Model
            current_user.update(old_cart=cart_json)

    def cart_total(self):
        # Get product IDS
        product_ids = self.cart.keys()
        # lookup those keys in our products database model
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        # Start counting at 0
        total = 0
        
        for key, item_data in quantities.items():
            # Convert key string into into so we can do math
            key = int(key)
            quantity = item_data['quantity']
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * quantity)
                    else:
                        total = total + (product.price * quantity)

        return total

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        # Use ids to lookup products in database model
        products = Product.objects.filter(id__in=product_ids)

        # Return those looked up products
        return products

    def get_quants(self):
        quantities = {}
        for product_id, item_data in self.cart.items():
            quantities[product_id] = item_data['quantity']
        return quantities

    def get_cart_details(self):
        """Get complete cart details including sizes"""
        return self.cart

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        # Get cart
        ourcart = self.cart
        # Update Dictionary/cart
        ourcart[product_id] = {
            'quantity': product_qty,
            'selected_size': ourcart[product_id].get('selected_size', ''),
            'custom_size': ourcart[product_id].get('custom_size', '')
        }

        self.session.modified = True
    
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Save cart as proper JSON
            cart_json = json.dumps(self.cart)
            # Save carty to the Profile Model
            current_user.update(old_cart=cart_json)

        thing = self.cart
        return thing

    def delete(self, product):
        product_id = str(product)
        # Delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Save cart as proper JSON
            cart_json = json.dumps(self.cart)
            # Save carty to the Profile Model
            current_user.update(old_cart=cart_json)

    # New method to restore from saved cart data
    def restore_from_saved(self, saved_cart_dict):
        """
        Restore cart from saved dictionary data
        """
        for product_id, item_data in saved_cart_dict.items():
            try:
                # Skip if product_id is not a valid integer
                if not str(product_id).isdigit():
                    continue
                    
                product_id_int = int(product_id)
                product = Product.objects.get(id=product_id_int)
                
                # Extract data
                if isinstance(item_data, dict):
                    quantity = item_data.get('quantity', 1)
                    selected_size = item_data.get('selected_size', '')
                    custom_size = item_data.get('custom_size', '')
                else:
                    quantity = item_data
                    selected_size = ''
                    custom_size = ''
                
                # Add to cart
                self.add(
                    product=product,
                    quantity=quantity,
                    selected_size=selected_size,
                    custom_size=custom_size
                )
            except (Product.DoesNotExist, ValueError):
                continue