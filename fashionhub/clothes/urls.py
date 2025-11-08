from . import views
from django.urls import path

urlpatterns = [
    path('search/', views.search, name='search'),
    path('men', views.men, name='men'),
    path('women', views.women, name='women'),
    path('accessories', views.accessories, name='accessories'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('', views.product_list, name='product_list'), 
]
