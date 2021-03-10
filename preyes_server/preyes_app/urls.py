from preyes_server.preyes_app import views
from django.urls import path, re_path

urlpatterns = [
    path('customers/', views.customer_list),
    path('customers/<int:pk>/', views.customer_detail),
    path('product_items/', views.product_item_list),
    path('product_items/<int:pk>/', views.product_item_detail),
    path('product_items/category/', views.product_item_list_for_category),
    path('categories/', views.all_categories),
    path('categories/<int:pk>/', views.category_detail),
]
