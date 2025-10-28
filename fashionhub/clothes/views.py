# Product detail view
from django.shortcuts import get_object_or_404

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category').prefetch_related('images'), slug=slug, is_available=True)
    return render(request, 'product_detail.html', {'product': product})
from django.shortcuts import render
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product


def product_list(request):
    qs = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/product_list.html', {'page_obj': page_obj})

def men(request):
    qs = Product.objects.filter(is_available=True, category__name__iexact='Men').select_related('category').prefetch_related('images').order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'men.html', {'page_obj': page_obj})

def women(request):
    return render(request, 'women.html')

def accessories(request):
    return render(request, 'accessories.html')

