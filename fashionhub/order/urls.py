from .import views
from django.urls import path

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/update-size/<int:product_id>/', views.cart_update_size, name='cart_update_size'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    # Payment routes
    path('payment/', views.payment_process, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('confirm/', views.order_confirm, name='order_confirm'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
]
