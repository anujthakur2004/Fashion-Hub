from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from clothes.models import Product

# ---------------------------
# Helper: manage session cart
# ---------------------------

def get_cart(request):
    """Retrieve cart dictionary from session."""
    return request.session.get('cart', {})

def save_cart(request, cart):
    """Save the updated cart to session."""
    request.session['cart'] = cart
    request.session.modified = True


# ---------------------------
# Cart Views
# ---------------------------

def cart(request):
    cart_data = get_cart(request)
    cart_items = []
    grand_total = 0
    for key, qty in cart_data.items():
        # key format: "<product_id>:<size>"
        parts = key.split(':', 1)
        try:
            pid = int(parts[0])
        except (ValueError, IndexError):
            continue
        size = parts[1] if len(parts) > 1 and parts[1] != '' else None
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue
        total_price = product.price * qty
        grand_total += total_price
        cart_items.append({
            'product': product,
            'quantity': qty,
            'total_price': total_price,
            'size': size
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'grand_total': grand_total})


def cart_add(request, product_id):
    if request.method != 'POST':
        return redirect('product_list')
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart_data = get_cart(request)
    size = request.POST.get('size', '')
    key = f"{product_id}:{size}"
    cart_data[key] = cart_data.get(key, 0) + 1
    save_cart(request, cart_data)
    messages.success(request, f"Added {product.name} to cart")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def cart_remove(request, product_id):
    if request.method != 'POST':
        return redirect('cart')
    cart_data = get_cart(request)
    size = request.POST.get('size', '')
    key = f"{product_id}:{size}"
    if key in cart_data:
        del cart_data[key]
        save_cart(request, cart_data)
        messages.success(request, 'Item removed from cart')
    return redirect('cart')


def cart_update(request, product_id):
    """Update quantity of a cart item."""
    if request.method != 'POST':
        return redirect('cart')
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size', '')
    key = f"{product_id}:{size}"
    cart_data = get_cart(request)

    if quantity > 0:
        cart_data[key] = quantity
        messages.info(request, f"Updated quantity of {product.name}")
    else:
        if key in cart_data:
            del cart_data[key]
            messages.info(request, f"Removed {product.name} from cart")

    save_cart(request, cart_data)
    return redirect('cart')


def cart_update_size(request, product_id):
    """Update the selected size for a cart item."""
    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})
    old_size = request.POST.get('old_size', '')
    new_size = request.POST.get('size', '')

    old_key = f"{product_id}:{old_size}"
    new_key = f"{product_id}:{new_size}"

    if old_key in cart:
        qty = cart.pop(old_key)  # remove old key and get quantity
        cart[new_key] = qty      # re-add under new key
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Product size updated successfully.')

    return redirect('cart')



def checkout(request):
    messages.info(request, 'Checkout is not implemented yet')
    return redirect('cart')
