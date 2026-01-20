
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from products.models import Product

def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock
    if quantity > product.stock_quantity:
        messages.error(request, f'Only {product.stock_quantity} items available in stock.')
        return redirect('products:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            messages.error(request, f'Only {product.stock_quantity} items available in stock.')
            return redirect('cart:cart_detail')
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity to {cart_item.quantity}')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect('cart:cart_detail')


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if quantity > cart_item.product.stock_quantity:
            messages.error(request, f'Only {cart_item.product.stock_quantity} items available.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('cart:cart_detail')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart.')
    return redirect('cart:cart_detail')


def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared successfully!')
    return redirect('cart:cart_detail')


# AJAX Views for dynamic cart updates
@require_POST
def add_to_cart_ajax(request, product_id):
    """Add to cart via AJAX"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock_quantity:
        return JsonResponse({
            'success': False,
            'message': f'Only {product.stock_quantity} items available.'
        })
    
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {product.stock_quantity} items available.'
            })
        cart_item.quantity = new_quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_count': cart.get_total_items(),
        'cart_total': float(cart.get_total_price())
    })