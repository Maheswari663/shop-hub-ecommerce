
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, ShippingAddress
from .forms import CheckoutForm, ShippingAddressForm
from cart.models import Cart, CartItem

@login_required
def checkout(request):
    """Checkout page"""
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').prefetch_related('product__images')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    # Get saved addresses
    saved_addresses = ShippingAddress.objects.filter(user=request.user)
    
    # Calculate totals
    subtotal = cart.get_total_price()
    shipping_cost = 0 if subtotal >= 500 else 50
    tax = 0  # You can add tax calculation here
    total = subtotal + shipping_cost + tax
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = Order.objects.create(
                        user=request.user,
                        subtotal=subtotal,
                        shipping_cost=shipping_cost,
                        tax=tax,
                        total_amount=total,
                        payment_method=form.cleaned_data['payment_method'],
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data['email'],
                        address_line1=form.cleaned_data['address_line1'],
                        address_line2=form.cleaned_data['address_line2'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        pincode=form.cleaned_data['pincode'],
                        country=form.cleaned_data['country'],
                        order_notes=form.cleaned_data['order_notes'],
                    )
                    
                    # Create order items
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.get_final_price()
                        )
                        
                        # Update product stock
                        product = cart_item.product
                        product.stock_quantity -= cart_item.quantity
                        product.save()
                    
                    # Save shipping address if requested
                    if form.cleaned_data.get('save_address'):
                        ShippingAddress.objects.create(
                            user=request.user,
                            full_name=form.cleaned_data['full_name'],
                            phone=form.cleaned_data['phone'],
                            address_line1=form.cleaned_data['address_line1'],
                            address_line2=form.cleaned_data['address_line2'],
                            city=form.cleaned_data['city'],
                            state=form.cleaned_data['state'],
                            pincode=form.cleaned_data['pincode'],
                            country=form.cleaned_data['country'],
                        )
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    # Redirect based on payment method
                    if form.cleaned_data['payment_method'] == 'cod':
                        order.payment_status = 'pending'
                        order.save()
                        messages.success(request, 'Order placed successfully!')
                        return redirect('orders:order_confirmation', order_number=order.order_number)
                    else:
                        # Redirect to payment page (we'll implement this later)
                         return redirect('orders:razorpay_dummy', order_number=order.order_number)
                        
            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
                return redirect('cart:cart_detail')
    else:
        # Pre-fill form with user data
        initial_data = {
            'full_name': request.user.get_full_name(),
            'phone': request.user.phone,
            'email': request.user.email,
        }
        
        # If user has a default address, use it
        default_address = saved_addresses.filter(is_default=True).first()
        if default_address:
            initial_data.update({
                'full_name': default_address.full_name,
                'phone': default_address.phone,
                'address_line1': default_address.address_line1,
                'address_line2': default_address.address_line2,
                'city': default_address.city,
                'state': default_address.state,
                'pincode': default_address.pincode,
                'country': default_address.country,
            })
        
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'saved_addresses': saved_addresses,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('product').prefetch_related('product__images')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_list(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('product').prefetch_related('product__images')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def cancel_order(request, order_number):
    """Cancel order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow cancellation for pending and processing orders
    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('orders:order_detail', order_number=order_number)


# Shipping Address Management
@login_required
def address_list(request):
    """List saved addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'orders/address_list.html', context)


@login_required
def add_address(request):
    """Add new shipping address"""
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('orders:address_list')
    else:
        form = ShippingAddressForm()
    
    context = {
        'form': form,
        'title': 'Add New Address',
    }
    return render(request, 'orders/address_form.html', context)


@login_required
def edit_address(request, address_id):
    """Edit shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('orders:address_list')
    else:
        form = ShippingAddressForm(instance=address)
    
    context = {
        'form': form,
        'title': 'Edit Address',
        'address': address,
    }
    return render(request, 'orders/address_form.html', context)


@login_required
def delete_address(request, address_id):
    """Delete shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('orders:address_list')


@login_required
def razorpay_dummy(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/razorpay_dummy.html', {'order': order})


@login_required
def razorpay_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    order.payment_status = 'completed'
    order.status = 'processing'
    order.payment_id = f"rzp_dummy_{order.id}"
    order.save()

    messages.success(request, 'Payment successful!')
    return redirect('orders:order_confirmation', order_number=order.order_number)
