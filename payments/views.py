
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.utils import timezone
#import razorpay
import json

from .models import Payment, Refund
from orders.models import Order

# Initialize Razorpay Client
#razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def initiate_payment(request, order_number):
    """Initiate Razorpay payment"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Check if order already has a completed payment
    if hasattr(order, 'payment') and order.payment.status == 'completed':
        messages.error(request, 'Payment already completed for this order.')
        return redirect('orders:order_detail', order_number=order.order_number)
    
    # Create or get payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'user': request.user,
            'amount': order.total_amount,
            'payment_method': order.payment_method,
        }
    )
    
    # For COD, mark as pending and complete order
    if order.payment_method == 'cod':
        payment.status = 'pending'
        payment.save()
        
        order.payment_status = 'pending'
        order.save()
        
        messages.success(request, 'Order placed successfully! Pay on delivery.')
        return redirect('orders:order_confirmation', order_number=order.order_number)
    # For online payments - redirect to configured payment gateway
    messages.info(request, 'Online payment integration will be added soon. Please use COD.')
    return redirect('orders:order_detail', order_number=order.order_number)
        



@csrf_exempt
def payment_callback(request):
    """Handle payment callback"""
    return HttpResponseBadRequest('payment gateway not configured')


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_failure(request):
    """Payment failure page"""
    return render(request, 'payments/payment_failure.html')


@login_required
def payment_history(request):
    """User's payment history"""
    payments = Payment.objects.filter(user=request.user).select_related('order')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def request_refund(request, payment_id):
    """Request refund for a payment"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Refund can only be requested for completed payments.')
        return redirect('orders:order_detail', order_number=payment.order.order_number)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        
        if not reason:
            messages.error(request, 'Please provide a reason for refund.')
            return redirect('orders:order_detail', order_number=payment.order.order_number)
        
        # Create refund request
        refund = Refund.objects.create(
            payment=payment,
            amount=payment.amount,
            reason=reason,
        )
        
        messages.success(request, 'Refund request submitted successfully. We will process it within 5-7 business days.')
        return redirect('orders:order_detail', order_number=payment.order.order_number)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/request_refund.html', context)