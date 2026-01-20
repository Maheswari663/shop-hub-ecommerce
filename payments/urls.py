from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Initiation
    path('initiate/<str:order_number>/', views.initiate_payment, name='initiate_payment'),
    
    # Payment Callback
    path('callback/', views.payment_callback, name='payment_callback'),
    
    # Payment Status Pages
    path('success/<str:payment_id>/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
    
    # Payment History
    path('history/', views.payment_history, name='payment_history'),
    
    # Refund
    path('refund/<str:payment_id>/', views.request_refund, name='request_refund'),
]