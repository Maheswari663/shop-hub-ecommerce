from django.urls import path
from .import views

app_name = 'orders'

urlpatterns = [
    # URLs later add chesthamu
     path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    
    # Order Management
    path('', views.order_list, name='order_list'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Address Management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('razorpay/<str:order_number>/', views.razorpay_dummy, name='razorpay_dummy'),
    path('razorpay/<str:order_number>/success/', views.razorpay_success, name='razorpay_success'),
]