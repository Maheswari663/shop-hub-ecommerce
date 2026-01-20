from django.urls import path
from .import views

app_name = 'cart'

urlpatterns = [
    # URLs later add chesthamu
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),

    # AJAX URLs
    path('ajax/add/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
]