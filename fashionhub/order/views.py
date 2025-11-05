from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from clothes.models import Product
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from user.models import Address
import stripe
from django.utils import timezone
from datetime import datetime
from .models import Order, OrderItem

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



@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for key, qty in cart.items():
        pid, *rest = key.split(':')
        size = rest[0] if rest else ''
        product = Product.objects.get(id=pid)
        total_price = product.price * qty
        cart_total += total_price
        cart_items.append({
            'product': product,
            'quantity': qty,
            'total_price': total_price,
            'size': size
        })

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'addresses': addresses
    })

@login_required
def payment_process(request):
    # Only accept POST from checkout
    if request.method != 'POST':
        return redirect('checkout')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    # Build cart summary
    cart_items = []
    cart_total = 0
    for key, qty in cart.items():
        pid, *rest = key.split(':')
        size = rest[0] if rest else ''
        product = get_object_or_404(Product, id=int(pid))
        total_price = product.price * qty
        cart_total += total_price
        cart_items.append({
            'product': product,
            'quantity': qty,
            'total_price': total_price,
            'size': size
        })

    payment_method = request.POST.get('paymentMethod')
    # capture selected address (optional)
    selected_address_id = request.POST.get('selected_address')
    address_obj = None
    if selected_address_id:
        try:
            address_obj = Address.objects.get(id=selected_address_id, user=request.user)
        except Address.DoesNotExist:
            address_obj = None

    # Build a pending order snapshot in session so we can show confirmation
    order_id = timezone.now().strftime('FH%Y%m%d%H%M%S') + f"-{request.user.id}"
    pending_order = {
        'order_id': order_id,
        'items': [
            {
                'product_id': i['product'].id,
                'name': i['product'].name,
                'size': i['size'] or '',
                'quantity': int(i['quantity']),
                'unit_price': float(i['product'].price),
                'total_price': float(i['total_price']),
            } for i in cart_items
        ],
        'total': float(cart_total),
        'address': {
            'address1': getattr(address_obj, 'address1', None),
            'address2': getattr(address_obj, 'address2', None),
            'city': getattr(address_obj, 'city', None),
            'state': getattr(address_obj, 'state', None),
            'pincode': getattr(address_obj, 'pincode', None),
        } if address_obj else None,
        'placed_at': timezone.now().isoformat(),
    }
    request.session['pending_order'] = pending_order
    request.session.modified = True
    if payment_method == 'stripe':
        # Create a Stripe Checkout Session for simple redirect-based payment
        stripe.api_key = getattr(settings, 'STRIPE_API_KEY', None)
        if not stripe.api_key:
            messages.error(request, 'Payment is temporarily unavailable. Please try Cash on Delivery or try again later.')
            return redirect('checkout')

        line_items = []
        for item in cart_items:
            unit_amount = int(float(item['product'].price) * 100)  # INR in paise
            if unit_amount < 1:
                unit_amount = 1
            name = f"{item['product'].name}"
            if item['size']:
                name += f" (Size: {item['size'].upper()})"
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': name},
                    'unit_amount': unit_amount,
                },
                'quantity': int(item['quantity']),
            })

        try:
            # Build absolute URLs for success/cancel
            success_url = request.build_absolute_uri(reverse('payment_success'))
            cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return redirect(session.url)
        except Exception as e:
            messages.error(request, f'Unable to start payment: {e}')
            return redirect('checkout')

    elif payment_method == 'cod':
        # Read pending snapshot first (created above)
        pending = request.session.get('pending_order')

        # Place order in DB as unpaid
        order = Order.objects.create(
            user=request.user,
            total_amount=cart_total,
            is_paid=False,
        )
        # Create order items from pending snapshot
        if pending and pending.get('items'):
            for it in pending['items']:
                prod = None
                pid = it.get('product_id')
                if pid:
                    try:
                        prod = Product.objects.get(id=pid)
                    except Product.DoesNotExist:
                        prod = None
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_name=it.get('name', ''),
                    size=it.get('size') or '',
                    quantity=int(it.get('quantity', 1)),
                    unit_price=it.get('unit_price', 0) or 0,
                    line_total=it.get('total_price', 0) or 0,
                )
        # enrich and move pending->last_order, clear cart and go to confirm page
        if pending is None:
            pending = {}
        pending['db_id'] = order.id
        request.session['last_order'] = pending
        request.session['pending_order'] = None
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Order placed successfully! Pay on delivery.')
        return redirect('order_confirm')
    else:
        messages.error(request, 'Invalid payment method selected.')
        return redirect('checkout')


@login_required
def payment_success(request):
    # Create paid order record in DB and move pending order to last_order
    pending = request.session.get('pending_order')
    total = 0
    try:
        total = float(pending.get('total', 0)) if pending else 0
    except Exception:
        total = 0
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        is_paid=True,
    )
    # Create order items
    if pending and pending.get('items'):
        for it in pending['items']:
            prod = None
            pid = it.get('product_id')
            if pid:
                try:
                    prod = Product.objects.get(id=pid)
                except Product.DoesNotExist:
                    prod = None
            OrderItem.objects.create(
                order=order,
                product=prod,
                product_name=it.get('name', ''),
                size=it.get('size') or '',
                quantity=int(it.get('quantity', 1)),
                unit_price=it.get('unit_price', 0) or 0,
                line_total=it.get('total_price', 0) or 0,
            )
    if pending is None:
        pending = {}
    pending['db_id'] = order.id
    request.session['last_order'] = pending
    request.session['pending_order'] = None
    request.session['cart'] = {}
    request.session.modified = True
    messages.success(request, 'Payment successful! Thank you for your order.')
    return redirect('order_confirm')


@login_required
def payment_cancel(request):
    messages.info(request, 'Payment was canceled. You can try again or choose Cash on Delivery.')
    return redirect('checkout')


@login_required
def order_confirm(request):
    last_order = request.session.get('last_order')
    if not last_order:
        messages.info(request, 'No recent order to show.')
        return redirect('home')
    # Parse placed_at (ISO string) to datetime so template can format nicely
    placed_iso = last_order.get('placed_at') if isinstance(last_order, dict) else None
    if placed_iso:
        try:
            iso = placed_iso.replace('Z', '+00:00')
            dt = datetime.fromisoformat(iso)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            last_order['placed_at_dt'] = dt
        except Exception:
            # leave as-is; template will fallback to raw string
            pass
    
    # Enrich items with product objects for image display
    items_with_products = []
    for item in last_order.get('items', []):
        product_obj = None
        if 'product_id' in item:
            try:
                product_obj = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                pass
        items_with_products.append({
            **item,
            'product': product_obj
        })
    last_order['items_enriched'] = items_with_products
    
    # We can keep last_order for the page refresh; optionally clear it after render
    return render(request, 'orderconfirm.html', {
        'order': last_order,
    })


@login_required
def orders(request):
    """List all orders placed by the current user, newest first."""
    user_orders = (Order.objects
                   .filter(user=request.user)
                   .order_by('-created_at')
                   .prefetch_related('items', 'items__product', 'items__product__images'))
    return render(request, 'orders.html', {
        'orders': user_orders,
    })


@login_required
def order_detail(request, order_id):
    """Show detailed view of a single order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product').prefetch_related('product__images').all()
    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
    })

