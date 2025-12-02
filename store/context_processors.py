from .models import Wishlist, Product, Category

def categories(request):
    """
    Context processor to make categories available in all templates
    """
    try:
        return {'categories': Category.objects.all()}
    except Exception as e:
        # If there's an error (like database not ready), return empty
        return {'categories': []}

def wishlist_count(request):
    """
    Context processor for wishlist count
    """
    # Authenticated: count from DB
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        count = wishlist.products.count()
    else:
        # Guest: count from session
        product_ids = request.session.get('wishlist', [])
        count = len(product_ids)
    return {'wishlist_count': count}