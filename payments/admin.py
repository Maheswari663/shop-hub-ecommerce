from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'user', 'amount', 'payment_method', 
                    'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_id', 'order__order_number', 'user__username', 
                     'razorpay_payment_id', 'razorpay_order_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at', 'paid_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'order', 'user', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Additional Info', {
            'fields': ('payment_response', 'failure_reason', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['refund_id', 'payment__payment_id', 'razorpay_refund_id']
    readonly_fields = ['refund_id', 'created_at', 'processed_at']