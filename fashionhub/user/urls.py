
from . import views
from django.urls import path

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
    path('logout', views.logout, name='logout'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('update_address', views.update_address, name='update_address'),
    path('address/add', views.add_address, name='address_add'),
    path('address/<int:addr_id>/edit', views.edit_address, name='address_edit'),
    path('address/<int:addr_id>/delete', views.delete_address, name='address_delete'),
    path('change_password', views.change_password, name='change_password'),
] 
