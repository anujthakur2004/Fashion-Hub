# Product detail view
from django.shortcuts import get_object_or_404

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('images'), slug=slug, is_available=True)
    return render(request, 'product_detail.html', {'product': product})

from django.shortcuts import render
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product


def product_list(request):
    qs = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/product_list.html', {'page_obj': page_obj})


def search(request):
    """Search products by name, description, or category"""
    query = request.GET.get('q', '').strip()
    
    if query:
        # Search in product name, description, and category name
        qs = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query),
            is_available=True
        ).select_related('category').prefetch_related('images').order_by('-created_at').distinct()
    else:
        qs = Product.objects.none()
    
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'search_results.html', {
        'page_obj': page_obj,
        'query': query,
        'total_results': qs.count()
    })


def men(request):
    qs = Product.objects.filter(is_available=True, category__name__iexact='Men').select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'men.html', {'page_obj': page_obj})

def women(request):
    qs = Product.objects.filter(is_available=True, category__name__iexact='Men').select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'women.html', {'page_obj': page_obj})

def accessories(request):
    qs = Product.objects.filter(is_available=True, category__name__iexact='Men').select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accessories.html', {'page_obj': page_obj})

