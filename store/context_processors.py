from .models import Wishlist, Product

def wishlist_count(request):
    # Authenticated: count from DB
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        count = wishlist.products.count()
    # Guest: count from session
    else:
        product_ids = request.session.get('wishlist', [])
        count = len(product_ids)
    return {'wishlist_count': count}
