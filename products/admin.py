from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, SubCategory, Brand, Product, ProductImage, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['variant_type', 'variant_value', 'price_adjustment', 'stock_quantity', 'is_available']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'brand', 'price', 'discount_price', 
                    'stock_quantity', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'subcategory', 'brand', 'is_available', 'is_featured', 
                   'is_new_arrival', 'is_best_seller', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock_quantity', 'is_available', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory', 'brand')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_price', 'stock_quantity', 'sku')
        }),
        ('Features', {
            'fields': ('is_featured', 'is_available', 'is_new_arrival', 'is_best_seller')
        }),
        ('Additional Info', {
            'fields': ('specifications', 'warranty_info', 'return_policy'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'subcategory', 'brand')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant_type', 'variant_value', 'price_adjustment', 
                    'stock_quantity', 'is_available']
    list_filter = ['variant_type', 'is_available']
    search_fields = ['product__name', 'variant_value']