# store/social_cart_middleware.py
import json
from django.utils.deprecation import MiddlewareMixin
from store.models import Profile, Product
from cart.cart import Cart

class SocialLoginCartMiddleware(MiddlewareMixin):
    """
    Middleware to restore cart for social login users
    This works independently without affecting existing logic
    """
    
    def process_request(self, request):
        # Only process authenticated users
        if not request.user.is_authenticated:
            return
        
        # Check if this is a fresh login (no cart restoration yet)
        if hasattr(request, 'session') and not request.session.get('cart_restored_from_social'):
            
            # Check if user has a profile with cart data
            try:
                profile = Profile.objects.get(user=request.user)
                saved_cart = profile.old_cart
                
                # If there's saved cart data and current session cart is empty
                if saved_cart and saved_cart.strip() and self.is_session_cart_empty(request):
                    try:
                        self.restore_cart(request, saved_cart)
                        # Mark as restored to prevent multiple restorations
                        request.session['cart_restored_from_social'] = True
                        print(f"Cart restored for social login user: {request.user.username}")
                    except Exception as e:
                        print(f"Error restoring cart: {e}")
                        
            except Profile.DoesNotExist:
                # Create profile if it doesn't exist (for social login users)
                Profile.objects.create(user=request.user)
    
    def is_session_cart_empty(self, request):
        """Check if session cart is empty"""
        cart = request.session.get('session_key', {})
        return not bool(cart)
    
    def restore_cart(self, request, saved_cart):
        """Restore cart from saved data"""
        try:
            converted_cart = json.loads(saved_cart)
            
            # Initialize cart
            cart = Cart(request)
            
            # Restore each item
            for product_id, item_data in converted_cart.items():
                try:
                    # Skip invalid product IDs
                    if not str(product_id).isdigit():
                        continue
                    
                    product_id_int = int(product_id)
                    product = Product.objects.get(id=product_id_int)
                    
                    # Extract item data
                    if isinstance(item_data, dict):
                        quantity = item_data.get('quantity', 1)
                        selected_size = item_data.get('selected_size', '')
                        custom_size = item_data.get('custom_size', '')
                    else:
                        quantity = item_data
                        selected_size = ''
                        custom_size = ''
                    
                    # Add to cart using the existing add method
                    cart.add(
                        product=product,
                        quantity=quantity,
                        selected_size=selected_size,
                        custom_size=custom_size
                    )
                    
                except Product.DoesNotExist:
                    print(f"Product {product_id} not found, skipping...")
                    continue
                except Exception as e:
                    print(f"Error adding product {product_id}: {e}")
                    continue
                    
            print("Cart restoration completed successfully")
            
        except json.JSONDecodeError as e:
            print(f"Invalid cart data format: {e}")
        except Exception as e:
            print(f"Unexpected error during cart restoration: {e}")