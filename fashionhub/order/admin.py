from django.contrib import admin
from django.contrib.auth.models import  Group
from .models import Order, OrderItem

admin.site.unregister(Group)

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	fields = ("product", "product_name", "size", "quantity", "unit_price", "line_total")
	readonly_fields = ("line_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "total_amount", "is_paid", "created_at")
	list_filter = ("is_paid", "created_at")
	search_fields = ("id", "user__username")
	ordering = ("-created_at",)
	inlines = [OrderItemInline]
