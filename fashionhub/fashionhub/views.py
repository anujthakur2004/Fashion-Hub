from django.http import HttpResponse
from django.shortcuts import render    

from clothes.models import Product

def home(request):
    all_products = Product.objects.filter(is_available=True).prefetch_related('images').order_by('-created_at')
    featured_products = all_products[:3]
    new_arrivals = all_products[3:7]
    accessories = all_products[7:10]
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'accessories': accessories,
    })

def contact(request):
    return render(request, 'contact.html')
