def is_logged_in(request):
    """Expose login state to templates using Django auth.

    Uses request.user.is_authenticated so navbar and other templates
    reflect the actual authentication state.
    """
    return {'is_logged_in': bool(getattr(request, 'user', None) and request.user.is_authenticated)}


def cart_item_count(request):
    """Calculate and expose the total number of items in the cart."""
    cart = request.session.get('cart', {})
    # Sum all quantities across all cart items
    total_items = sum(cart.values())
    return {'cart_item_count': total_items}
