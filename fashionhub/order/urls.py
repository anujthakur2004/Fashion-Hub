from .import views
from django.urls import path

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/update-size/<int:product_id>/', views.cart_update_size, name='cart_update_size'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

]
