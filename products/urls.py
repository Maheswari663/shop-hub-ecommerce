from django.urls import path
from .import views

app_name = 'products'

urlpatterns = [
    # URLs later add chesthamu
    path('', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
     path('<slug:slug>/', views.product_detail, name='product_detail'),
]