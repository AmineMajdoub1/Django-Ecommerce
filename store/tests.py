from django.test import TestCase

# Create your tests here.
# store/views.py - Add this for testing
def test_cart_restoration(request):
    """Test view to check cart restoration status"""
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            return JsonResponse({
                'user': request.user.username,
                'saved_cart': profile.old_cart,
                'session_cart': request.session.get('session_key', {}),
                'cart_restored': request.session.get('cart_restored_from_social', False)
            })
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'No profile'})
    return JsonResponse({'error': 'Not authenticated'})