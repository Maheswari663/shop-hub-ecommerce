
# Register your models here.
from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']
    fields = ['product', 'quantity', 'get_total_price', 'added_at']
    
    def get_total_price(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'get_total_items', 'get_total_price', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_unit_price', 'get_total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name', 'cart__user__username']
    
    def get_unit_price(self, obj):
        return f"₹{obj.get_unit_price()}"
    get_unit_price.short_description = 'Unit Price'
    
    def get_total_price(self, obj):
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'