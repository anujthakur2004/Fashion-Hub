from django.contrib import admin
from .models import User
# Register your models here.
admin.site.site_header = "Fashion Hub Admin"
admin.site.site_title = "Fashion Hub Admin Portal"
admin.site.index_title = "Welcome to Fashion Hub Admin Portal"

admin.site.register(User)
