
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Category, SubCategory, Brand, Product, ProductImage
from products.models import Product
from reviews.models import Review

def home_view(request):
    """Home page view."""
    featured_products = Product.objects.filter(is_featured=True,is_available=True).select_related('category').prefetch_related('images')[:8]
    print(f"Featured Products count: {featured_products.count()}")
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'home.html', context)

def product_list(request):
    """Display all products with filters"""
    products = Product.objects.filter(is_available=True).select_related(
        'category', 'subcategory', 'brand'
    ).prefetch_related('images')
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    brand_slug = request.GET.get('brand')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'newest')
    
    # Apply filters
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Get all categories, subcategories, brands for filters
    categories = Category.objects.filter(is_active=True)
    subcategories = SubCategory.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'products': products_page,
        'categories': categories,
        'subcategories': subcategories,
        'brands': brands,
        'search_query': search_query,
        'current_category': category_slug,
        'current_subcategory': subcategory_slug,
        'current_brand': brand_slug,
        'sort_by': sort_by,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Display single product details"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory', 'brand')
        .prefetch_related('images', 'variants'),
        slug=slug,
        is_available=True
    )
    
    # Increment view count
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Get related products (same category, exclude current)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id).select_related('category', 'brand')[:4]
    
    # Get product images
    product_images = product.images.all()
    
    # Get product variants
    product_variants = product.variants.filter(is_available=True)
    
    context = {
        'product': product,
        'product_images': product_images,
        'product_variants': product_variants,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)


def category_products(request, slug):
    """Display products by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        category=category,
        is_available=True
    ).select_related('category', 'subcategory', 'brand').prefetch_related('images')
    
    # Get subcategories for this category
    subcategories = category.subcategories.filter(is_active=True)
    
    # Apply subcategory filter if exists
    subcategory_slug = request.GET.get('subcategory')
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products_page,
        'subcategories': subcategories,
        'sort_by': sort_by,
    }
    
    return render(request, 'products/category_products.html', context)


def search_products(request):
    """Search products"""
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query),
            is_available=True
        ).select_related('category', 'brand').prefetch_related('images')
    else:
        products = Product.objects.none()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'query': query,
        'total_results': products.count(),
    }
    
    return render(request, 'products/search_results.html', context)