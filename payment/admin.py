from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User

# Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price", "selected_size", "custom_size"]
    fields = ["product", "quantity", "price", "selected_size", "custom_size"]

# Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]
    list_display = ["id", "user", "full_name", "email", "amount_paid", "shipped", "date_ordered"]
    list_filter = ["shipped", "date_ordered"]

# Register ShippingAddress with custom display
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "shipping_full_name", "shipping_city", "shipping_country"]
    list_filter = ["shipping_country"]

# Register OrderItem with custom display
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price", "selected_size", "custom_size"]
    list_filter = ["order__shipped"]
    readonly_fields = ["selected_size", "custom_size"]

# Register models with custom admin
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)